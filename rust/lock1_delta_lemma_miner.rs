use std::cmp::Ordering;
use std::collections::{BTreeMap, HashMap};
use std::env;
use std::fs::{create_dir_all, File};
use std::io::{BufWriter, Write};
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering as AtomicOrdering};
use std::sync::Arc;
use std::thread;

const ALPHA: f64 = 1.584_962_500_721_156_3;

#[derive(Clone, Copy, Eq, PartialEq)]
enum Scope {
    All,
    Line,
}

#[derive(Clone)]
struct Config {
    max_k: usize,
    max_a: usize,
    min_k: usize,
    scope: Scope,
    line_window: usize,
    line_offset: i64,
    max_total_a: Option<usize>,
    start_word: u64,
    end_word: Option<u64>,
    max_words: Option<u64>,
    threads: usize,
    job_chunk_words: u64,
    sample_limit: usize,
    progress_every: u64,
    out_dir: PathBuf,
}

#[derive(Default, Clone)]
struct Counters {
    words_scanned: u64,
    d_le_zero_rejects: u64,
    overflow_rejects: u64,
    identity_failures: u64,
    all_zero_prefix_paths: u64,
    nonzero_prefix_paths: u64,
    normalized_residue_zero: u64,
    nontrivial_normalized_residue_zero: u64,
    stopped_early: bool,
}

impl Counters {
    fn add_assign(&mut self, other: &Self) {
        self.words_scanned += other.words_scanned;
        self.d_le_zero_rejects += other.d_le_zero_rejects;
        self.overflow_rejects += other.overflow_rejects;
        self.identity_failures += other.identity_failures;
        self.all_zero_prefix_paths += other.all_zero_prefix_paths;
        self.nonzero_prefix_paths += other.nonzero_prefix_paths;
        self.normalized_residue_zero += other.normalized_residue_zero;
        self.nontrivial_normalized_residue_zero += other.nontrivial_normalized_residue_zero;
        self.stopped_early |= other.stopped_early;
    }
}

#[derive(Clone)]
struct Job {
    k: usize,
    total_a: usize,
    start_word: u64,
    end_word: u64,
    scan_start_word: u64,
    scan_end_word: u64,
}

#[derive(Clone)]
struct AffineData {
    a_sum: usize,
    k: usize,
    b: u128,
    three_k: u128,
    two_a: u128,
}

#[derive(Clone)]
struct DeltaCertificate {
    word: Vec<usize>,
    a_sum: usize,
    k: usize,
    b: u128,
    d: u128,
    d_factorization: String,
    delta_sign: i8,
    delta_abs: u128,
    delta_gcd: u128,
    delta_q: u128,
    witness_prime: u128,
    witness_modulus: u128,
    h: usize,
    min_prefix_e: i64,
    max_prefix_e: i64,
    final_prefix_e: i64,
    first_nonzero_prefix_index: isize,
    first_nonzero_prefix_value: i64,
    last_nonzero_prefix_index: isize,
    last_nonzero_prefix_value: i64,
    normalized_delta_residue: u128,
    identity_residue: u128,
    all_zero_prefix: bool,
    deviation_word: Vec<i64>,
    prefix_e_word: Vec<i64>,
    normalized_prefix_h_word: Vec<i64>,
}

#[derive(Clone, Eq, PartialEq, Ord, PartialOrd)]
struct FamilyKey {
    k: usize,
    a_sum: usize,
    final_prefix_e: i64,
    min_prefix_e: i64,
    max_prefix_e: i64,
    first_nonzero_prefix_index: isize,
    first_nonzero_prefix_value: i64,
    last_nonzero_prefix_index: isize,
    last_nonzero_prefix_value: i64,
}

#[derive(Default, Clone)]
struct FamilyStats {
    count: u64,
    residue_zero: u64,
    nontrivial_residue_zero: u64,
    min_delta_q: Option<u128>,
    min_witness_prime: Option<u128>,
    min_witness_modulus: Option<u128>,
    min_delta_abs: Option<u128>,
    min_normalized_residue: Option<u128>,
    delta_q_counts: BTreeMap<u128, u64>,
    witness_prime_counts: BTreeMap<u128, u64>,
    witness_modulus_counts: BTreeMap<u128, u64>,
    examples: Vec<String>,
}

impl FamilyStats {
    fn add(&mut self, cert: &DeltaCertificate) {
        self.count += 1;
        self.residue_zero += u64::from(cert.normalized_delta_residue == 0);
        self.nontrivial_residue_zero +=
            u64::from(cert.normalized_delta_residue == 0 && !cert.all_zero_prefix);
        self.min_delta_q = Some(
            self.min_delta_q
                .map_or(cert.delta_q, |value| value.min(cert.delta_q)),
        );
        self.min_witness_prime = Some(
            self.min_witness_prime
                .map_or(cert.witness_prime, |value| value.min(cert.witness_prime)),
        );
        self.min_witness_modulus = Some(
            self.min_witness_modulus
                .map_or(cert.witness_modulus, |value| {
                    value.min(cert.witness_modulus)
                }),
        );
        self.min_delta_abs = Some(
            self.min_delta_abs
                .map_or(cert.delta_abs, |value| value.min(cert.delta_abs)),
        );
        self.min_normalized_residue = Some(
            self.min_normalized_residue
                .map_or(cert.normalized_delta_residue, |value| {
                    value.min(cert.normalized_delta_residue)
                }),
        );
        *self.delta_q_counts.entry(cert.delta_q).or_insert(0) += 1;
        *self
            .witness_prime_counts
            .entry(cert.witness_prime)
            .or_insert(0) += 1;
        *self
            .witness_modulus_counts
            .entry(cert.witness_modulus)
            .or_insert(0) += 1;
        if self.examples.len() < 4 {
            self.examples.push(word_string(&cert.word));
        }
    }
}

#[derive(Clone, Eq, PartialEq, Ord, PartialOrd)]
struct FactorClassKey {
    k: usize,
    a_sum: usize,
    d: u128,
}

#[derive(Default, Clone)]
struct FactorClassStats {
    d_factorization: String,
    count: u64,
    all_zero_prefix: u64,
    nonzero_prefix: u64,
    residue_zero: u64,
    nontrivial_residue_zero: u64,
    missing_witness_modulus: u64,
    witness_prime_counts: BTreeMap<u128, u64>,
    witness_modulus_counts: BTreeMap<u128, u64>,
    examples: Vec<String>,
}

impl FactorClassStats {
    fn add(&mut self, cert: &DeltaCertificate) {
        if self.d_factorization.is_empty() {
            self.d_factorization = cert.d_factorization.clone();
        }
        self.count += 1;
        self.all_zero_prefix += u64::from(cert.all_zero_prefix);
        self.nonzero_prefix += u64::from(!cert.all_zero_prefix);
        self.residue_zero += u64::from(cert.normalized_delta_residue == 0);
        self.nontrivial_residue_zero +=
            u64::from(cert.normalized_delta_residue == 0 && !cert.all_zero_prefix);
        self.missing_witness_modulus += u64::from(
            !cert.all_zero_prefix
                && cert.normalized_delta_residue != 0
                && cert.witness_modulus <= 1,
        );
        *self
            .witness_prime_counts
            .entry(cert.witness_prime)
            .or_insert(0) += 1;
        *self
            .witness_modulus_counts
            .entry(cert.witness_modulus)
            .or_insert(0) += 1;
        if self.examples.len() < 4 {
            self.examples.push(word_string(&cert.word));
        }
    }
}

#[derive(Default)]
struct WorkerResult {
    counters: Counters,
    samples: Vec<DeltaCertificate>,
    danger_rows: Vec<DeltaCertificate>,
    families: BTreeMap<FamilyKey, FamilyStats>,
    factor_classes: BTreeMap<FactorClassKey, FactorClassStats>,
    factor_cache: HashMap<u128, (Vec<(u128, u128)>, String)>,
}

fn parse_args() -> Config {
    let mut max_k = None;
    let mut max_a = None;
    let mut min_k = 1usize;
    let mut scope = Scope::Line;
    let mut line_window = 0usize;
    let mut line_offset = 1i64;
    let mut max_total_a = None;
    let mut start_word = 1u64;
    let mut end_word = None;
    let mut max_words = None;
    let mut threads = 1usize;
    let mut job_chunk_words = 250_000u64;
    let mut sample_limit = 1000usize;
    let mut progress_every = 0u64;
    let mut out_dir = None;

    let args: Vec<String> = env::args().collect();
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--max-k" => {
                i += 1;
                max_k = Some(args[i].parse().expect("--max-k integer"));
            }
            "--max-a" => {
                i += 1;
                max_a = Some(args[i].parse().expect("--max-a integer"));
            }
            "--min-k" => {
                i += 1;
                min_k = args[i].parse().expect("--min-k integer");
            }
            "--scope" => {
                i += 1;
                scope = match args[i].as_str() {
                    "all" => Scope::All,
                    "line" => Scope::Line,
                    other => panic!("unknown --scope {}", other),
                };
            }
            "--line-window" => {
                i += 1;
                line_window = args[i].parse().expect("--line-window integer");
            }
            "--line-offset" => {
                i += 1;
                line_offset = args[i].parse().expect("--line-offset integer");
            }
            "--max-total-a" => {
                i += 1;
                max_total_a = Some(args[i].parse().expect("--max-total-a integer"));
            }
            "--start-word" => {
                i += 1;
                start_word = args[i].parse().expect("--start-word integer");
            }
            "--end-word" => {
                i += 1;
                end_word = Some(args[i].parse().expect("--end-word integer"));
            }
            "--max-words" => {
                i += 1;
                max_words = Some(args[i].parse().expect("--max-words integer"));
            }
            "--threads" => {
                i += 1;
                threads = args[i].parse().expect("--threads integer");
            }
            "--job-chunk-words" => {
                i += 1;
                job_chunk_words = args[i].parse().expect("--job-chunk-words integer");
            }
            "--sample-limit" => {
                i += 1;
                sample_limit = args[i].parse().expect("--sample-limit integer");
            }
            "--progress-every" => {
                i += 1;
                progress_every = args[i].parse().expect("--progress-every integer");
            }
            "--out-dir" => {
                i += 1;
                out_dir = Some(PathBuf::from(&args[i]));
            }
            other => panic!("unknown arg: {}", other),
        }
        i += 1;
    }

    let config = Config {
        max_k: max_k.expect("--max-k is required"),
        max_a: max_a.expect("--max-a is required"),
        min_k,
        scope,
        line_window,
        line_offset,
        max_total_a,
        start_word,
        end_word,
        max_words,
        threads,
        job_chunk_words,
        sample_limit,
        progress_every,
        out_dir: out_dir.expect("--out-dir is required"),
    };
    if config.max_k == 0 || config.max_a == 0 || config.min_k == 0 {
        panic!("--max-k, --max-a, and --min-k must be positive");
    }
    if config.min_k > config.max_k {
        panic!("--min-k cannot exceed --max-k");
    }
    if config.threads == 0 {
        panic!("--threads must be positive");
    }
    if config.job_chunk_words == 0 {
        panic!("--job-chunk-words must be positive");
    }
    if config.start_word == 0 {
        panic!("--start-word is 1-based and must be positive");
    }
    if let Some(end_word) = config.end_word {
        if end_word < config.start_word {
            panic!("--end-word cannot be less than --start-word");
        }
    }
    config
}

fn checked_pow(mut base: u128, mut exponent: usize) -> Option<u128> {
    let mut acc = 1u128;
    while exponent > 0 {
        if exponent & 1 == 1 {
            acc = acc.checked_mul(base)?;
        }
        exponent >>= 1;
        if exponent > 0 {
            base = base.checked_mul(base)?;
        }
    }
    Some(acc)
}

fn affine_data(word: &[usize]) -> Option<AffineData> {
    let mut a_sum = 0usize;
    let mut b = 0u128;
    for &exponent in word {
        if exponent == 0 {
            return None;
        }
        if a_sum >= 128 {
            return None;
        }
        b = b.checked_mul(3)?.checked_add(1u128 << a_sum)?;
        a_sum = a_sum.checked_add(exponent)?;
    }
    if a_sum >= 128 {
        return None;
    }
    Some(AffineData {
        a_sum,
        k: word.len(),
        b,
        three_k: checked_pow(3, word.len())?,
        two_a: 1u128 << a_sum,
    })
}

fn gcd(mut lhs: u128, mut rhs: u128) -> u128 {
    while rhs != 0 {
        let next = lhs % rhs;
        lhs = rhs;
        rhs = next;
    }
    lhs
}

fn prime_power_factors(mut value: u128) -> Vec<(u128, u128)> {
    let mut factors = Vec::new();
    if value <= 1 {
        return factors;
    }
    if value % 2 == 0 {
        let mut power = 1u128;
        while value % 2 == 0 {
            value /= 2;
            power *= 2;
        }
        factors.push((2, power));
    }
    let mut factor = 3u128;
    while factor <= value / factor {
        if value % factor == 0 {
            let mut power = 1u128;
            while value % factor == 0 {
                value /= factor;
                power *= factor;
            }
            factors.push((factor, power));
        }
        factor += 2;
    }
    if value > 1 {
        factors.push((value, value));
    }
    factors
}

fn factorization_string(factors: &[(u128, u128)]) -> String {
    if factors.is_empty() {
        return "1".to_string();
    }
    factors
        .iter()
        .map(|(prime, prime_power)| format!("{}:{}", prime, prime_power))
        .collect::<Vec<_>>()
        .join(";")
}

fn select_non_circular_witness(
    factors: &[(u128, u128)],
    normalized_delta_residue: u128,
) -> (u128, u128) {
    if normalized_delta_residue == 0 {
        return (1, 1);
    }
    for &(prime, prime_power) in factors {
        if normalized_delta_residue % prime_power != 0 {
            return (prime, prime_power);
        }
    }
    (0, 0)
}

fn add_mod(lhs: u128, rhs: u128, modulus: u128) -> u128 {
    if lhs >= modulus - rhs {
        lhs - (modulus - rhs)
    } else {
        lhs + rhs
    }
}

fn mul_mod(mut lhs: u128, mut rhs: u128, modulus: u128) -> u128 {
    if modulus == 1 {
        return 0;
    }
    lhs %= modulus;
    rhs %= modulus;
    let mut acc = 0u128;
    while rhs > 0 {
        if rhs & 1 == 1 {
            acc = add_mod(acc, lhs, modulus);
        }
        rhs >>= 1;
        if rhs > 0 {
            lhs = add_mod(lhs, lhs, modulus);
        }
    }
    acc
}

fn pow_mod(mut base: u128, mut exponent: usize, modulus: u128) -> u128 {
    if modulus == 1 {
        return 0;
    }
    let mut acc = 1u128 % modulus;
    base %= modulus;
    while exponent > 0 {
        if exponent & 1 == 1 {
            acc = mul_mod(acc, base, modulus);
        }
        exponent >>= 1;
        if exponent > 0 {
            base = mul_mod(base, base, modulus);
        }
    }
    acc
}

fn word_string<T: ToString>(word: &[T]) -> String {
    word.iter()
        .map(|value| value.to_string())
        .collect::<Vec<_>>()
        .join(" ")
}

fn csv_escape(value: &str) -> String {
    if value.contains(',') || value.contains('"') || value.contains('\n') {
        format!("\"{}\"", value.replace('"', "\"\""))
    } else {
        value.to_string()
    }
}

fn deviation_and_prefix(word: &[usize]) -> (Vec<i64>, Vec<i64>) {
    let mut deviations = Vec::with_capacity(word.len());
    let mut prefixes = Vec::with_capacity(word.len() + 1);
    let mut running = 0i64;
    prefixes.push(0);
    for &exponent in word {
        let deviation = exponent as i64 - 2;
        deviations.push(deviation);
        running += deviation;
        prefixes.push(running);
    }
    (deviations, prefixes)
}

fn prefix_stats(prefixes: &[i64]) -> (i64, i64, usize, isize, i64, isize, i64, bool) {
    let min_prefix = *prefixes.iter().min().expect("prefix exists");
    let max_prefix = *prefixes.iter().max().expect("prefix exists");
    let h = if min_prefix < 0 {
        (-min_prefix) as usize
    } else {
        0
    };
    let mut first_idx = -1isize;
    let mut first_value = 0i64;
    let mut last_idx = -1isize;
    let mut last_value = 0i64;
    for (idx, &value) in prefixes.iter().enumerate() {
        if value != 0 {
            if first_idx < 0 {
                first_idx = idx as isize;
                first_value = value;
            }
            last_idx = idx as isize;
            last_value = value;
        }
    }
    (
        min_prefix,
        max_prefix,
        h,
        first_idx,
        first_value,
        last_idx,
        last_value,
        first_idx < 0,
    )
}

fn signed_delta_residue(delta_sign: i8, delta_abs: u128, h: usize, d: u128) -> u128 {
    let scaled_abs = mul_mod(delta_abs % d, pow_mod(2, h, d), d);
    if delta_sign >= 0 {
        scaled_abs
    } else if scaled_abs == 0 {
        0
    } else {
        d - scaled_abs
    }
}

fn identity_residue(prefixes: &[i64], h: usize, k: usize, d: u128) -> Option<u128> {
    let pow_h = pow_mod(2, h, d);
    let mut residue = 0u128;
    for (j, prefix) in prefixes.iter().take(k).enumerate() {
        let h_j = (*prefix + h as i64) as usize;
        let term = (pow_mod(2, h_j, d) + d - pow_h) % d;
        let coeff = mul_mod(pow_mod(3, k - 1 - j, d), pow_mod(4, j, d), d);
        residue = add_mod(residue, mul_mod(coeff, term, d), d);
    }
    let h_k = (*prefixes.get(k)? + h as i64) as usize;
    let final_term = (pow_mod(2, h_k, d) + d - pow_h) % d;
    let final_coeff = pow_mod(4, k, d);
    let subtract = mul_mod(final_coeff, final_term, d);
    if residue >= subtract {
        Some(residue - subtract)
    } else {
        Some(d - (subtract - residue))
    }
}

fn make_certificate(
    word: &[usize],
    data: &AffineData,
    d: u128,
    d_factors: &[(u128, u128)],
    d_factorization: &str,
) -> Option<DeltaCertificate> {
    let delta_sign = match data.b.cmp(&d) {
        Ordering::Greater => 1,
        Ordering::Equal => 0,
        Ordering::Less => -1,
    };
    let delta_abs = if data.b >= d { data.b - d } else { d - data.b };
    let delta_gcd = gcd(delta_abs, d);
    let delta_q = d / delta_gcd;
    let (deviation_word, prefix_e_word) = deviation_and_prefix(word);
    let (
        min_prefix_e,
        max_prefix_e,
        h,
        first_nonzero_prefix_index,
        first_nonzero_prefix_value,
        last_nonzero_prefix_index,
        last_nonzero_prefix_value,
        all_zero_prefix,
    ) = prefix_stats(&prefix_e_word);
    let normalized_delta_residue = signed_delta_residue(delta_sign, delta_abs, h, d);
    let (witness_prime, witness_modulus) =
        select_non_circular_witness(d_factors, normalized_delta_residue);
    let identity_residue = identity_residue(&prefix_e_word, h, word.len(), d)?;
    let normalized_prefix_h_word = prefix_e_word
        .iter()
        .map(|value| value + h as i64)
        .collect::<Vec<_>>();
    Some(DeltaCertificate {
        word: word.to_vec(),
        a_sum: data.a_sum,
        k: data.k,
        b: data.b,
        d,
        d_factorization: d_factorization.to_string(),
        delta_sign,
        delta_abs,
        delta_gcd,
        delta_q,
        witness_prime,
        witness_modulus,
        h,
        min_prefix_e,
        max_prefix_e,
        final_prefix_e: *prefix_e_word.last().expect("prefix exists"),
        first_nonzero_prefix_index,
        first_nonzero_prefix_value,
        last_nonzero_prefix_index,
        last_nonzero_prefix_value,
        normalized_delta_residue,
        identity_residue,
        all_zero_prefix,
        deviation_word,
        prefix_e_word,
        normalized_prefix_h_word,
    })
}

fn family_key(cert: &DeltaCertificate) -> FamilyKey {
    FamilyKey {
        k: cert.k,
        a_sum: cert.a_sum,
        final_prefix_e: cert.final_prefix_e,
        min_prefix_e: cert.min_prefix_e,
        max_prefix_e: cert.max_prefix_e,
        first_nonzero_prefix_index: cert.first_nonzero_prefix_index,
        first_nonzero_prefix_value: cert.first_nonzero_prefix_value,
        last_nonzero_prefix_index: cert.last_nonzero_prefix_index,
        last_nonzero_prefix_value: cert.last_nonzero_prefix_value,
    }
}

fn factor_class_key(cert: &DeltaCertificate) -> FactorClassKey {
    FactorClassKey {
        k: cert.k,
        a_sum: cert.a_sum,
        d: cert.d,
    }
}

fn add_sample(samples: &mut Vec<DeltaCertificate>, limit: usize, cert: &DeltaCertificate) {
    if limit == 0 {
        return;
    }
    samples.push(cert.clone());
    samples.sort_by(|lhs, rhs| {
        lhs.delta_q
            .cmp(&rhs.delta_q)
            .then_with(|| {
                lhs.normalized_delta_residue
                    .cmp(&rhs.normalized_delta_residue)
            })
            .then_with(|| lhs.k.cmp(&rhs.k))
            .then_with(|| word_string(&lhs.word).cmp(&word_string(&rhs.word)))
    });
    samples.truncate(limit);
}

fn scan_word(word: &[usize], result: &mut WorkerResult, config: &Config) {
    result.counters.words_scanned += 1;
    let Some(data) = affine_data(word) else {
        result.counters.overflow_rejects += 1;
        return;
    };
    if data.two_a <= data.three_k {
        result.counters.d_le_zero_rejects += 1;
        return;
    }
    let d = data.two_a - data.three_k;
    let (d_factors, d_factorization) = result
        .factor_cache
        .entry(d)
        .or_insert_with(|| {
            let factors = prime_power_factors(d);
            let factorization = factorization_string(&factors);
            (factors, factorization)
        })
        .clone();
    let Some(cert) = make_certificate(word, &data, d, &d_factors, &d_factorization) else {
        result.counters.identity_failures += 1;
        return;
    };
    if cert.normalized_delta_residue != cert.identity_residue {
        result.counters.identity_failures += 1;
        result.danger_rows.push(cert);
        return;
    }
    result.counters.all_zero_prefix_paths += u64::from(cert.all_zero_prefix);
    result.counters.nonzero_prefix_paths += u64::from(!cert.all_zero_prefix);
    result.counters.normalized_residue_zero += u64::from(cert.normalized_delta_residue == 0);
    result.counters.nontrivial_normalized_residue_zero +=
        u64::from(cert.normalized_delta_residue == 0 && !cert.all_zero_prefix);

    result
        .families
        .entry(family_key(&cert))
        .or_default()
        .add(&cert);
    result
        .factor_classes
        .entry(factor_class_key(&cert))
        .or_default()
        .add(&cert);
    if cert.normalized_delta_residue == 0 {
        result.danger_rows.push(cert.clone());
    }
    add_sample(&mut result.samples, config.sample_limit, &cert);
}

fn enumerate_compositions_range<F>(
    remaining_slots: usize,
    remaining_total: usize,
    max_part: usize,
    prefix: &mut Vec<usize>,
    cursor: &mut u64,
    range_start: u64,
    range_end: u64,
    memo: &mut HashMap<(usize, usize), u64>,
    callback: &mut F,
) -> std::io::Result<bool>
where
    F: FnMut(&[usize]) -> std::io::Result<bool>,
{
    if remaining_slots == 0 {
        let word_index = *cursor;
        *cursor = cursor.saturating_add(1);
        if word_index < range_start {
            return Ok(true);
        }
        if word_index > range_end {
            return Ok(false);
        }
        return callback(prefix);
    }
    if remaining_total < remaining_slots || remaining_total > remaining_slots * max_part {
        return Ok(true);
    }
    let low = 1usize.max(remaining_total.saturating_sub((remaining_slots - 1) * max_part));
    let high = max_part.min(remaining_total - (remaining_slots - 1));
    for value in low..=high {
        let branch_count =
            count_compositions_memo(remaining_slots - 1, remaining_total - value, max_part, memo);
        if branch_count == 0 {
            continue;
        }
        let branch_start = *cursor;
        let branch_end = branch_start.saturating_add(branch_count).saturating_sub(1);
        if branch_end < range_start {
            *cursor = branch_end.saturating_add(1);
            continue;
        }
        if branch_start > range_end {
            return Ok(false);
        }
        prefix.push(value);
        let keep_going = enumerate_compositions_range(
            remaining_slots - 1,
            remaining_total - value,
            max_part,
            prefix,
            cursor,
            range_start,
            range_end,
            memo,
            callback,
        )?;
        prefix.pop();
        if !keep_going {
            return Ok(false);
        }
    }
    Ok(true)
}

fn count_compositions(length: usize, total: usize, max_part: usize) -> u64 {
    let mut memo = HashMap::new();
    count_compositions_memo(length, total, max_part, &mut memo)
}

fn count_compositions_memo(
    length: usize,
    total: usize,
    max_part: usize,
    memo: &mut HashMap<(usize, usize), u64>,
) -> u64 {
    if length == 0 {
        return u64::from(total == 0);
    }
    if total < length || total > length * max_part {
        return 0;
    }
    if let Some(value) = memo.get(&(length, total)) {
        return *value;
    }
    let low = 1usize.max(total.saturating_sub((length - 1) * max_part));
    let high = max_part.min(total - (length - 1));
    let mut count = 0u64;
    for value in low..=high {
        count = count.saturating_add(count_compositions_memo(
            length - 1,
            total - value,
            max_part,
            memo,
        ));
    }
    memo.insert((length, total), count);
    count
}

fn total_a_values(config: &Config, k: usize) -> Vec<usize> {
    match config.scope {
        Scope::All => {
            let max_total = config.max_total_a.unwrap_or(k * config.max_a);
            (k..=max_total.min(k * config.max_a)).collect()
        }
        Scope::Line => {
            let center = (k as f64 * ALPHA).floor() as i64 + config.line_offset;
            let low = center - config.line_window as i64;
            let high = center + config.line_window as i64;
            (low..=high)
                .filter(|value| *value >= k as i64 && *value <= (k * config.max_a) as i64)
                .map(|value| value as usize)
                .collect()
        }
    }
}

fn build_jobs(config: &Config) -> Vec<Job> {
    let mut jobs = Vec::new();
    let mut next_start = 1u64;
    for k in config.min_k..=config.max_k {
        for total_a in total_a_values(config, k) {
            let count = count_compositions(k, total_a, config.max_a);
            if count == 0 {
                continue;
            }
            let end_word = next_start.saturating_add(count).saturating_sub(1);
            let requested_end = config.end_word.unwrap_or(u64::MAX);
            if end_word >= config.start_word && next_start <= requested_end {
                let overlap_start = next_start.max(config.start_word);
                let overlap_end = end_word.min(requested_end);
                let mut chunk_start = overlap_start;
                while chunk_start <= overlap_end {
                    let chunk_end = chunk_start
                        .saturating_add(config.job_chunk_words)
                        .saturating_sub(1)
                        .min(overlap_end);
                    jobs.push(Job {
                        k,
                        total_a,
                        start_word: next_start,
                        end_word,
                        scan_start_word: chunk_start,
                        scan_end_word: chunk_end,
                    });
                    if chunk_end == u64::MAX {
                        break;
                    }
                    chunk_start = chunk_end.saturating_add(1);
                }
            }
            next_start = end_word.saturating_add(1);
        }
    }
    jobs
}

fn run_worker(
    worker_id: usize,
    config: Arc<Config>,
    jobs: Arc<Vec<Job>>,
    next_job: Arc<AtomicUsize>,
    scanned_words: Arc<AtomicU64>,
    stop: Arc<AtomicBool>,
) -> WorkerResult {
    let mut result = WorkerResult::default();
    loop {
        if stop.load(AtomicOrdering::Relaxed) {
            result.counters.stopped_early = true;
            break;
        }
        let job_idx = next_job.fetch_add(1, AtomicOrdering::Relaxed);
        if job_idx >= jobs.len() {
            break;
        }
        let job = &jobs[job_idx];
        debug_assert!(job.scan_start_word >= job.start_word);
        debug_assert!(job.scan_end_word <= job.end_word);
        let mut cursor = job.start_word;
        let mut prefix = Vec::with_capacity(job.k);
        let mut memo = HashMap::new();
        let keep_going = enumerate_compositions_range(
            job.k,
            job.total_a,
            config.max_a,
            &mut prefix,
            &mut cursor,
            job.scan_start_word,
            job.scan_end_word,
            &mut memo,
            &mut |word| {
                let scanned_before = scanned_words.fetch_add(1, AtomicOrdering::Relaxed);
                if config.max_words.map(|max| scanned_before >= max).unwrap_or(false) {
                    stop.store(true, AtomicOrdering::Relaxed);
                    result.counters.stopped_early = true;
                    return Ok(false);
                }
                scan_word(word, &mut result, &config);
                if config.progress_every > 0
                    && result.counters.words_scanned % config.progress_every == 0
                {
                    eprintln!(
                        "delta-lemma-progress worker={} words={} danger={} identity_failures={} families={}",
                        worker_id,
                        result.counters.words_scanned,
                        result.counters.nontrivial_normalized_residue_zero,
                        result.counters.identity_failures,
                        result.families.len()
                    );
                }
                Ok(true)
            },
        )
        .expect("enumerate compositions");
        if !keep_going && stop.load(AtomicOrdering::Relaxed) {
            result.counters.stopped_early = true;
            break;
        }
    }
    result
}

fn merge_family_stats(target: &mut FamilyStats, source: FamilyStats) {
    target.count += source.count;
    target.residue_zero += source.residue_zero;
    target.nontrivial_residue_zero += source.nontrivial_residue_zero;
    if let Some(value) = source.min_delta_q {
        target.min_delta_q = Some(
            target
                .min_delta_q
                .map_or(value, |existing| existing.min(value)),
        );
    }
    if let Some(value) = source.min_witness_prime {
        target.min_witness_prime = Some(
            target
                .min_witness_prime
                .map_or(value, |existing| existing.min(value)),
        );
    }
    if let Some(value) = source.min_witness_modulus {
        target.min_witness_modulus = Some(
            target
                .min_witness_modulus
                .map_or(value, |existing| existing.min(value)),
        );
    }
    if let Some(value) = source.min_delta_abs {
        target.min_delta_abs = Some(
            target
                .min_delta_abs
                .map_or(value, |existing| existing.min(value)),
        );
    }
    if let Some(value) = source.min_normalized_residue {
        target.min_normalized_residue = Some(
            target
                .min_normalized_residue
                .map_or(value, |existing| existing.min(value)),
        );
    }
    for (delta_q, count) in source.delta_q_counts {
        *target.delta_q_counts.entry(delta_q).or_insert(0) += count;
    }
    for (prime, count) in source.witness_prime_counts {
        *target.witness_prime_counts.entry(prime).or_insert(0) += count;
    }
    for (modulus, count) in source.witness_modulus_counts {
        *target.witness_modulus_counts.entry(modulus).or_insert(0) += count;
    }
    for example in source.examples {
        if target.examples.len() < 4 {
            target.examples.push(example);
        }
    }
}

fn merge_factor_class_stats(target: &mut FactorClassStats, source: FactorClassStats) {
    if target.d_factorization.is_empty() {
        target.d_factorization = source.d_factorization;
    }
    target.count += source.count;
    target.all_zero_prefix += source.all_zero_prefix;
    target.nonzero_prefix += source.nonzero_prefix;
    target.residue_zero += source.residue_zero;
    target.nontrivial_residue_zero += source.nontrivial_residue_zero;
    target.missing_witness_modulus += source.missing_witness_modulus;
    for (prime, count) in source.witness_prime_counts {
        *target.witness_prime_counts.entry(prime).or_insert(0) += count;
    }
    for (modulus, count) in source.witness_modulus_counts {
        *target.witness_modulus_counts.entry(modulus).or_insert(0) += count;
    }
    for example in source.examples {
        if target.examples.len() < 4 {
            target.examples.push(example);
        }
    }
}

fn run_scan(config: Arc<Config>) -> WorkerResult {
    let jobs = Arc::new(build_jobs(&config));
    let next_job = Arc::new(AtomicUsize::new(0));
    let scanned_words = Arc::new(AtomicU64::new(0));
    let stop = Arc::new(AtomicBool::new(false));
    let mut handles = Vec::new();
    for worker_id in 0..config.threads {
        let config = Arc::clone(&config);
        let jobs = Arc::clone(&jobs);
        let next_job = Arc::clone(&next_job);
        let scanned_words = Arc::clone(&scanned_words);
        let stop = Arc::clone(&stop);
        handles.push(thread::spawn(move || {
            run_worker(worker_id, config, jobs, next_job, scanned_words, stop)
        }));
    }

    let mut merged = WorkerResult::default();
    for handle in handles {
        let worker = handle.join().expect("worker join");
        merged.counters.add_assign(&worker.counters);
        merged.samples.extend(worker.samples);
        merged.danger_rows.extend(worker.danger_rows);
        for (key, stats) in worker.families {
            merge_family_stats(merged.families.entry(key).or_default(), stats);
        }
        for (key, stats) in worker.factor_classes {
            merge_factor_class_stats(merged.factor_classes.entry(key).or_default(), stats);
        }
    }
    merged.samples.sort_by(|lhs, rhs| {
        lhs.delta_q
            .cmp(&rhs.delta_q)
            .then_with(|| {
                lhs.normalized_delta_residue
                    .cmp(&rhs.normalized_delta_residue)
            })
            .then_with(|| lhs.k.cmp(&rhs.k))
            .then_with(|| word_string(&lhs.word).cmp(&word_string(&rhs.word)))
    });
    merged.samples.truncate(config.sample_limit);
    if config
        .max_words
        .map(|max_words| merged.counters.words_scanned >= max_words)
        .unwrap_or(false)
    {
        merged.counters.stopped_early = true;
    }
    merged
}

fn delta_q_counts_string(values: &BTreeMap<u128, u64>) -> String {
    values
        .iter()
        .take(16)
        .map(|(delta_q, count)| format!("{}:{}", delta_q, count))
        .collect::<Vec<_>>()
        .join(";")
}

fn write_certificates(path: PathBuf, rows: &[DeltaCertificate]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "word,A,k,B,D,D_factorization,delta_sign,delta_abs,delta_gcd,delta_q,witness_prime,witness_modulus,h,min_prefix_E,max_prefix_E,final_prefix_E,first_nonzero_prefix_index,first_nonzero_prefix_value,last_nonzero_prefix_index,last_nonzero_prefix_value,normalized_delta_residue,identity_residue,all_zero_prefix,deviation_word,prefix_E_word,normalized_prefix_H_word"
    )?;
    for row in rows {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            csv_escape(&word_string(&row.word)),
            row.a_sum,
            row.k,
            row.b,
            row.d,
            csv_escape(&row.d_factorization),
            row.delta_sign,
            row.delta_abs,
            row.delta_gcd,
            row.delta_q,
            row.witness_prime,
            row.witness_modulus,
            row.h,
            row.min_prefix_e,
            row.max_prefix_e,
            row.final_prefix_e,
            row.first_nonzero_prefix_index,
            row.first_nonzero_prefix_value,
            row.last_nonzero_prefix_index,
            row.last_nonzero_prefix_value,
            row.normalized_delta_residue,
            row.identity_residue,
            row.all_zero_prefix,
            csv_escape(&word_string(&row.deviation_word)),
            csv_escape(&word_string(&row.prefix_e_word)),
            csv_escape(&word_string(&row.normalized_prefix_h_word))
        )?;
    }
    Ok(())
}

fn write_factor_classes(
    path: PathBuf,
    classes: &BTreeMap<FactorClassKey, FactorClassStats>,
) -> std::io::Result<()> {
    let mut entries: Vec<(&FactorClassKey, &FactorClassStats)> = classes.iter().collect();
    entries.sort_by(|lhs, rhs| {
        rhs.1
            .missing_witness_modulus
            .cmp(&lhs.1.missing_witness_modulus)
            .then_with(|| {
                rhs.1
                    .nontrivial_residue_zero
                    .cmp(&lhs.1.nontrivial_residue_zero)
            })
            .then_with(|| lhs.0.k.cmp(&rhs.0.k))
            .then_with(|| lhs.0.a_sum.cmp(&rhs.0.a_sum))
            .then_with(|| lhs.0.d.cmp(&rhs.0.d))
    });
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "k,A,D,D_factorization,count,all_zero_prefix,nonzero_prefix,residue_zero,nontrivial_residue_zero,missing_witness_modulus,witness_prime_counts,witness_modulus_counts,examples"
    )?;
    for (key, stats) in entries {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{}",
            key.k,
            key.a_sum,
            key.d,
            csv_escape(&stats.d_factorization),
            stats.count,
            stats.all_zero_prefix,
            stats.nonzero_prefix,
            stats.residue_zero,
            stats.nontrivial_residue_zero,
            stats.missing_witness_modulus,
            csv_escape(&delta_q_counts_string(&stats.witness_prime_counts)),
            csv_escape(&delta_q_counts_string(&stats.witness_modulus_counts)),
            csv_escape(&stats.examples.join(" | "))
        )?;
    }
    Ok(())
}

fn write_families(
    path: PathBuf,
    families: &BTreeMap<FamilyKey, FamilyStats>,
) -> std::io::Result<()> {
    let mut entries: Vec<(&FamilyKey, &FamilyStats)> = families.iter().collect();
    entries.sort_by(|lhs, rhs| {
        rhs.1
            .nontrivial_residue_zero
            .cmp(&lhs.1.nontrivial_residue_zero)
            .then_with(|| {
                lhs.1
                    .min_delta_q
                    .unwrap_or(u128::MAX)
                    .cmp(&rhs.1.min_delta_q.unwrap_or(u128::MAX))
            })
            .then_with(|| rhs.1.count.cmp(&lhs.1.count))
            .then(Ordering::Equal)
    });
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "k,A,final_prefix_E,min_prefix_E,max_prefix_E,first_nonzero_prefix_index,first_nonzero_prefix_value,last_nonzero_prefix_index,last_nonzero_prefix_value,count,residue_zero,nontrivial_residue_zero,min_delta_q,min_witness_prime,min_witness_modulus,min_delta_abs,min_normalized_residue,delta_q_counts,witness_prime_counts,witness_modulus_counts,examples"
    )?;
    for (key, stats) in entries {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            key.k,
            key.a_sum,
            key.final_prefix_e,
            key.min_prefix_e,
            key.max_prefix_e,
            key.first_nonzero_prefix_index,
            key.first_nonzero_prefix_value,
            key.last_nonzero_prefix_index,
            key.last_nonzero_prefix_value,
            stats.count,
            stats.residue_zero,
            stats.nontrivial_residue_zero,
            stats.min_delta_q.unwrap_or(0),
            stats.min_witness_prime.unwrap_or(0),
            stats.min_witness_modulus.unwrap_or(0),
            stats.min_delta_abs.unwrap_or(0),
            stats.min_normalized_residue.unwrap_or(0),
            csv_escape(&delta_q_counts_string(&stats.delta_q_counts)),
            csv_escape(&delta_q_counts_string(&stats.witness_prime_counts)),
            csv_escape(&delta_q_counts_string(&stats.witness_modulus_counts)),
            csv_escape(&stats.examples.join(" | "))
        )?;
    }
    Ok(())
}

fn write_notes(path: PathBuf, result: &WorkerResult) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(file, "# Lock 1 Delta Lemma Miner")?;
    writeln!(file)?;
    writeln!(
        file,
        "This is the proof-obligation miner for the final Lock 1 loop obstruction."
    )?;
    writeln!(file)?;
    writeln!(file, "Identity checked modulo D for every retained row:")?;
    writeln!(file)?;
    writeln!(file, "```text")?;
    writeln!(file, "a_j = 2 + e_j")?;
    writeln!(file, "E_j = e_0 + ... + e_(j-1)")?;
    writeln!(file, "h = -min(0, E_0, ..., E_k)")?;
    writeln!(file, "Delta = B_w - D_w")?;
    writeln!(file, "D_w | B_w iff D_w | Delta")?;
    writeln!(file, "D_w | Delta iff D_w | 2^h Delta, since D_w is odd")?;
    writeln!(
        file,
        "2^h Delta = sum 3^(k-1-j)4^j(2^(E_j+h)-2^h) - 4^k(2^(E_k+h)-2^h)"
    )?;
    writeln!(file, "```")?;
    writeln!(file)?;
    writeln!(file, "Words scanned: {}", result.counters.words_scanned)?;
    writeln!(
        file,
        "Identity failures: {}",
        result.counters.identity_failures
    )?;
    writeln!(
        file,
        "All-zero prefix paths: {}",
        result.counters.all_zero_prefix_paths
    )?;
    writeln!(
        file,
        "Nonzero prefix paths: {}",
        result.counters.nonzero_prefix_paths
    )?;
    writeln!(
        file,
        "Nontrivial normalized residue zero rows: {}",
        result.counters.nontrivial_normalized_residue_zero
    )?;
    writeln!(
        file,
        "Factor-class witness rule groups: {}",
        result.factor_classes.len()
    )?;
    writeln!(file)?;
    writeln!(file, "Formal proof target:")?;
    writeln!(file)?;
    writeln!(
        file,
        "For every nonzero prefix path E, prove that at least one prime-power factor of D has nonzero normalized_delta_residue."
    )?;
    Ok(())
}

fn write_summary_json(
    path: PathBuf,
    result: &WorkerResult,
    config: &Config,
) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(file, "{{")?;
    writeln!(file, "  \"miner\": \"lock1_delta_lemma_miner\",")?;
    writeln!(file, "  \"max_k\": {},", config.max_k)?;
    writeln!(file, "  \"max_a\": {},", config.max_a)?;
    writeln!(file, "  \"min_k\": {},", config.min_k)?;
    writeln!(
        file,
        "  \"scope\": \"{}\",",
        if config.scope == Scope::All {
            "all"
        } else {
            "line"
        }
    )?;
    writeln!(file, "  \"line_window\": {},", config.line_window)?;
    writeln!(file, "  \"line_offset\": {},", config.line_offset)?;
    writeln!(file, "  \"threads\": {},", config.threads)?;
    writeln!(file, "  \"start_word\": {},", config.start_word)?;
    match config.end_word {
        Some(value) => writeln!(file, "  \"end_word\": {},", value)?,
        None => writeln!(file, "  \"end_word\": null,")?,
    }
    writeln!(
        file,
        "  \"words_scanned\": {},",
        result.counters.words_scanned
    )?;
    writeln!(
        file,
        "  \"D_le_zero_rejects\": {},",
        result.counters.d_le_zero_rejects
    )?;
    writeln!(
        file,
        "  \"overflow_rejects\": {},",
        result.counters.overflow_rejects
    )?;
    writeln!(
        file,
        "  \"identity_failures\": {},",
        result.counters.identity_failures
    )?;
    writeln!(
        file,
        "  \"all_zero_prefix_paths\": {},",
        result.counters.all_zero_prefix_paths
    )?;
    writeln!(
        file,
        "  \"nonzero_prefix_paths\": {},",
        result.counters.nonzero_prefix_paths
    )?;
    writeln!(
        file,
        "  \"normalized_residue_zero\": {},",
        result.counters.normalized_residue_zero
    )?;
    writeln!(
        file,
        "  \"nontrivial_normalized_residue_zero\": {},",
        result.counters.nontrivial_normalized_residue_zero
    )?;
    writeln!(file, "  \"family_groups\": {},", result.families.len())?;
    writeln!(
        file,
        "  \"factor_class_groups\": {},",
        result.factor_classes.len()
    )?;
    writeln!(
        file,
        "  \"claim_status_for_scanned_words\": \"{}\"",
        if result.counters.identity_failures == 0
            && result.counters.nontrivial_normalized_residue_zero == 0
        {
            "delta_identity_clean_no_nontrivial_zero_residue"
        } else {
            "attention_required"
        }
    )?;
    writeln!(file, "}}")?;
    Ok(())
}

fn main() {
    let config = Arc::new(parse_args());
    create_dir_all(&config.out_dir).expect("create out dir");
    let result = run_scan(Arc::clone(&config));

    write_certificates(
        config.out_dir.join("lock1_delta_samples.csv"),
        &result.samples,
    )
    .expect("write samples");
    write_certificates(
        config.out_dir.join("lock1_delta_danger_rows.csv"),
        &result.danger_rows,
    )
    .expect("write danger rows");
    write_families(
        config.out_dir.join("lock1_delta_families.csv"),
        &result.families,
    )
    .expect("write families");
    write_factor_classes(
        config.out_dir.join("lock1_factor_class_witness_rules.csv"),
        &result.factor_classes,
    )
    .expect("write factor classes");
    write_notes(config.out_dir.join("LOCK1_DELTA_LEMMA_NOTES.md"), &result).expect("write notes");
    write_summary_json(
        config.out_dir.join("lock1_delta_lemma_summary.json"),
        &result,
        &config,
    )
    .expect("write summary");

    println!("Lock 1 delta lemma miner");
    println!("words_scanned={}", result.counters.words_scanned);
    println!("D_le_zero_rejects={}", result.counters.d_le_zero_rejects);
    println!("identity_failures={}", result.counters.identity_failures);
    println!(
        "all_zero_prefix_paths={}",
        result.counters.all_zero_prefix_paths
    );
    println!(
        "nonzero_prefix_paths={}",
        result.counters.nonzero_prefix_paths
    );
    println!(
        "nontrivial_normalized_residue_zero={}",
        result.counters.nontrivial_normalized_residue_zero
    );
    println!("family_groups={}", result.families.len());
    println!("factor_class_groups={}", result.factor_classes.len());
    println!("wrote: {}", config.out_dir.display());
}
