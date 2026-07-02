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
    max_words: Option<u64>,
    start_word: u64,
    end_word: Option<u64>,
    threads: usize,
    job_chunk_words: u64,
    sample_limit: usize,
    exact_family_limit: usize,
    progress_every: u64,
    out_dir: PathBuf,
}

#[derive(Default, Clone)]
struct Counters {
    words_scanned: u64,
    overflow_rejects: u64,
    d_le_zero_rejects: u64,
    obstruction_rows: u64,
    q_equals_1_rows: u64,
    rho_equals_0_rows: u64,
    trivial_all2_closures: u64,
    nontrivial_closure_candidates: u64,
    exact_family_rows_skipped: u64,
    stopped_early: bool,
}

impl Counters {
    fn add_assign(&mut self, other: &Self) {
        self.words_scanned += other.words_scanned;
        self.overflow_rejects += other.overflow_rejects;
        self.d_le_zero_rejects += other.d_le_zero_rejects;
        self.obstruction_rows += other.obstruction_rows;
        self.q_equals_1_rows += other.q_equals_1_rows;
        self.rho_equals_0_rows += other.rho_equals_0_rows;
        self.trivial_all2_closures += other.trivial_all2_closures;
        self.nontrivial_closure_candidates += other.nontrivial_closure_candidates;
        self.exact_family_rows_skipped += other.exact_family_rows_skipped;
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
struct ObstructionRow {
    word: Vec<usize>,
    a_sum: usize,
    k: usize,
    b: u128,
    d: u128,
    gcd: u128,
    q: u128,
    rho: u128,
    phase_distance: u128,
    remainder: u128,
    delta_sign: i8,
    delta_abs: u128,
    delta_gcd: u128,
    delta_q: u128,
    final_deviation: i64,
    first_nonzero_deviation_index: isize,
    first_nonzero_deviation_value: i64,
    last_nonzero_deviation_index: isize,
    last_nonzero_deviation_value: i64,
    max_abs_partial_deviation: i64,
    max_abs_prefix_deviation_before_terms: i64,
    positive_deviations: usize,
    negative_deviations: usize,
    zero_deviations: usize,
    deviation_word: Vec<i64>,
    prefix_deviation_before_terms: Vec<i64>,
    delta_term_sign_word: Vec<i64>,
    partial_deviation_word: Vec<i64>,
    sturmian_carry_word: Vec<i64>,
    sturmian_deviation_word: Vec<i64>,
    partial_sturmian_deviation_word: Vec<i64>,
    sturmian_gap: i64,
    primitive_word: Vec<usize>,
    primitive_reps: usize,
    canonical_rotation: Vec<usize>,
}

#[derive(Clone, Eq, PartialEq, Ord, PartialOrd)]
struct CoarseKey {
    k: usize,
    a_sum: usize,
    final_deviation: i64,
    first_nonzero_deviation_index: isize,
    first_nonzero_deviation_value: i64,
    last_nonzero_deviation_index: isize,
    last_nonzero_deviation_value: i64,
    max_abs_partial_deviation: i64,
    max_abs_prefix_deviation_before_terms: i64,
    positive_deviations: usize,
    negative_deviations: usize,
    zero_deviations: usize,
    sturmian_gap: i64,
}

#[derive(Default, Clone)]
struct GroupStats {
    count: u64,
    q_equals_1: u64,
    rho_equals_0: u64,
    trivial_all2: u64,
    nontrivial_closure: u64,
    min_q: Option<u128>,
    min_delta_q: Option<u128>,
    min_delta_abs: Option<u128>,
    min_phase_distance: Option<u128>,
    q_counts: BTreeMap<u128, u64>,
    delta_q_counts: BTreeMap<u128, u64>,
    examples: Vec<String>,
}

impl GroupStats {
    fn add_row(&mut self, row: &ObstructionRow) {
        self.count += 1;
        self.q_equals_1 += u64::from(row.q == 1);
        self.rho_equals_0 += u64::from(row.rho == 0);
        let all2 = is_all_twos(&row.word);
        self.trivial_all2 += u64::from(row.q == 1 && all2);
        self.nontrivial_closure += u64::from(row.q == 1 && !all2);
        self.min_q = Some(self.min_q.map_or(row.q, |value| value.min(row.q)));
        self.min_delta_q = Some(
            self.min_delta_q
                .map_or(row.delta_q, |value| value.min(row.delta_q)),
        );
        self.min_delta_abs = Some(
            self.min_delta_abs
                .map_or(row.delta_abs, |value| value.min(row.delta_abs)),
        );
        self.min_phase_distance = Some(
            self.min_phase_distance
                .map_or(row.phase_distance, |value| value.min(row.phase_distance)),
        );
        *self.q_counts.entry(row.q).or_insert(0) += 1;
        *self.delta_q_counts.entry(row.delta_q).or_insert(0) += 1;
        if self.examples.len() < 4 {
            self.examples.push(word_string(&row.word));
        }
    }
}

#[derive(Default)]
struct WorkerResult {
    counters: Counters,
    samples: Vec<ObstructionRow>,
    closure_rows: Vec<ObstructionRow>,
    coarse_groups: BTreeMap<CoarseKey, GroupStats>,
    exact_deviation_groups: BTreeMap<String, GroupStats>,
}

fn parse_args() -> Config {
    let mut max_k = None;
    let mut max_a = None;
    let mut min_k = 1usize;
    let mut scope = Scope::Line;
    let mut line_window = 0usize;
    let mut line_offset = 0i64;
    let mut max_total_a = None;
    let mut max_words = None;
    let mut start_word = 1u64;
    let mut end_word = None;
    let mut threads = 1usize;
    let mut job_chunk_words = 250_000u64;
    let mut sample_limit = 0usize;
    let mut exact_family_limit = 0usize;
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
            "--max-words" => {
                i += 1;
                max_words = Some(args[i].parse().expect("--max-words integer"));
            }
            "--start-word" => {
                i += 1;
                start_word = args[i].parse().expect("--start-word integer");
            }
            "--end-word" => {
                i += 1;
                end_word = Some(args[i].parse().expect("--end-word integer"));
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
            "--exact-family-limit" => {
                i += 1;
                exact_family_limit = args[i].parse().expect("--exact-family-limit integer");
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
        max_words,
        start_word,
        end_word,
        threads,
        job_chunk_words,
        sample_limit,
        exact_family_limit,
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
        let two_prefix = if a_sum < 128 {
            1u128 << a_sum
        } else {
            return None;
        };
        b = b.checked_mul(3)?.checked_add(two_prefix)?;
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

fn is_all_twos(word: &[usize]) -> bool {
    word.iter().all(|&value| value == 2)
}

fn rotate(word: &[usize], offset: usize) -> Vec<usize> {
    word[offset..]
        .iter()
        .chain(word[..offset].iter())
        .copied()
        .collect()
}

fn canonical_rotation(word: &[usize]) -> Vec<usize> {
    if word.is_empty() {
        return Vec::new();
    }
    let mut best = word.to_vec();
    for offset in 1..word.len() {
        let candidate = rotate(word, offset);
        if candidate < best {
            best = candidate;
        }
    }
    best
}

fn primitive_block(word: &[usize]) -> (Vec<usize>, usize) {
    for period in 1..=word.len() {
        if word.len() % period != 0 {
            continue;
        }
        let primitive = &word[..period];
        if word.chunks(period).all(|chunk| chunk == primitive) {
            return (primitive.to_vec(), word.len() / period);
        }
    }
    (word.to_vec(), 1)
}

#[allow(clippy::type_complexity)]
fn deviation_data(
    word: &[usize],
) -> (
    Vec<i64>,
    Vec<i64>,
    Vec<i64>,
    Vec<i64>,
    i64,
    isize,
    i64,
    isize,
    i64,
    i64,
    i64,
    usize,
    usize,
    usize,
) {
    let mut deviations = Vec::with_capacity(word.len());
    let mut prefix_before_terms = Vec::with_capacity(word.len());
    let mut delta_term_signs = Vec::with_capacity(word.len());
    let mut partial = Vec::with_capacity(word.len());
    let mut running = 0i64;
    let mut max_abs = 0i64;
    let mut max_abs_prefix_before_terms = 0i64;
    let mut positive = 0usize;
    let mut negative = 0usize;
    let mut zero = 0usize;
    let mut first_nonzero_index = -1isize;
    let mut first_nonzero_value = 0i64;
    let mut last_nonzero_index = -1isize;
    let mut last_nonzero_value = 0i64;
    for (idx, &exponent) in word.iter().enumerate() {
        prefix_before_terms.push(running);
        delta_term_signs.push(running.signum());
        max_abs_prefix_before_terms = max_abs_prefix_before_terms.max(running.abs());
        let value = exponent as i64 - 2;
        deviations.push(value);
        if value != 0 {
            if first_nonzero_index < 0 {
                first_nonzero_index = idx as isize;
                first_nonzero_value = value;
            }
            last_nonzero_index = idx as isize;
            last_nonzero_value = value;
        }
        running += value;
        partial.push(running);
        max_abs = max_abs.max(running.abs());
        positive += usize::from(value > 0);
        negative += usize::from(value < 0);
        zero += usize::from(value == 0);
    }
    (
        deviations,
        prefix_before_terms,
        delta_term_signs,
        partial,
        running,
        first_nonzero_index,
        first_nonzero_value,
        last_nonzero_index,
        last_nonzero_value,
        max_abs,
        max_abs_prefix_before_terms,
        positive,
        negative,
        zero,
    )
}

fn sturmian_data(word: &[usize]) -> (Vec<i64>, Vec<i64>, Vec<i64>, i64) {
    let mut carry = Vec::with_capacity(word.len());
    let mut deviations = Vec::with_capacity(word.len());
    let mut partial = Vec::with_capacity(word.len());
    let mut running = 0i64;
    for (idx, &exponent) in word.iter().enumerate() {
        let before = ((idx as f64) * ALPHA).floor() as i64;
        let after = (((idx + 1) as f64) * ALPHA).floor() as i64;
        let step = after - before;
        let deviation = exponent as i64 - step;
        running += deviation;
        carry.push(step);
        deviations.push(deviation);
        partial.push(running);
    }
    let sturmian_gap =
        word.iter().sum::<usize>() as i64 - ((word.len() as f64) * ALPHA).floor() as i64;
    (carry, deviations, partial, sturmian_gap)
}

fn make_obstruction_row(word: &[usize], data: &AffineData, d: u128) -> ObstructionRow {
    let divisor = gcd(data.b, d);
    let q = d / divisor;
    let remainder = data.b % d;
    let rho = (data.b / divisor) % q;
    let phase_distance = rho.min(q - rho);
    let delta_sign = match data.b.cmp(&d) {
        Ordering::Greater => 1,
        Ordering::Equal => 0,
        Ordering::Less => -1,
    };
    let delta_abs = if data.b >= d { data.b - d } else { d - data.b };
    let delta_gcd = gcd(delta_abs, d);
    let delta_q = d / delta_gcd;
    let (
        deviation_word,
        prefix_deviation_before_terms,
        delta_term_sign_word,
        partial_deviation_word,
        final_deviation,
        first_nonzero_deviation_index,
        first_nonzero_deviation_value,
        last_nonzero_deviation_index,
        last_nonzero_deviation_value,
        max_abs_partial_deviation,
        max_abs_prefix_deviation_before_terms,
        positive_deviations,
        negative_deviations,
        zero_deviations,
    ) = deviation_data(word);
    let (
        sturmian_carry_word,
        sturmian_deviation_word,
        partial_sturmian_deviation_word,
        sturmian_gap,
    ) = sturmian_data(word);
    let (primitive_word, primitive_reps) = primitive_block(word);
    let canonical_rotation = canonical_rotation(&primitive_word);
    ObstructionRow {
        word: word.to_vec(),
        a_sum: data.a_sum,
        k: data.k,
        b: data.b,
        d,
        gcd: divisor,
        q,
        rho,
        phase_distance,
        remainder,
        delta_sign,
        delta_abs,
        delta_gcd,
        delta_q,
        final_deviation,
        first_nonzero_deviation_index,
        first_nonzero_deviation_value,
        last_nonzero_deviation_index,
        last_nonzero_deviation_value,
        max_abs_partial_deviation,
        max_abs_prefix_deviation_before_terms,
        positive_deviations,
        negative_deviations,
        zero_deviations,
        deviation_word,
        prefix_deviation_before_terms,
        delta_term_sign_word,
        partial_deviation_word,
        sturmian_carry_word,
        sturmian_deviation_word,
        partial_sturmian_deviation_word,
        sturmian_gap,
        primitive_word,
        primitive_reps,
        canonical_rotation,
    }
}

fn coarse_key(row: &ObstructionRow) -> CoarseKey {
    CoarseKey {
        k: row.k,
        a_sum: row.a_sum,
        final_deviation: row.final_deviation,
        first_nonzero_deviation_index: row.first_nonzero_deviation_index,
        first_nonzero_deviation_value: row.first_nonzero_deviation_value,
        last_nonzero_deviation_index: row.last_nonzero_deviation_index,
        last_nonzero_deviation_value: row.last_nonzero_deviation_value,
        max_abs_partial_deviation: row.max_abs_partial_deviation,
        max_abs_prefix_deviation_before_terms: row.max_abs_prefix_deviation_before_terms,
        positive_deviations: row.positive_deviations,
        negative_deviations: row.negative_deviations,
        zero_deviations: row.zero_deviations,
        sturmian_gap: row.sturmian_gap,
    }
}

fn exact_deviation_key(row: &ObstructionRow) -> String {
    format!(
        "dev=[{}];prefix_before=[{}];partial=[{}];term_sign=[{}];sturm=[{}]",
        word_string(&row.deviation_word),
        word_string(&row.prefix_deviation_before_terms),
        word_string(&row.partial_deviation_word),
        word_string(&row.delta_term_sign_word),
        word_string(&row.sturmian_carry_word)
    )
}

fn add_sample(samples: &mut Vec<ObstructionRow>, limit: usize, row: &ObstructionRow) {
    if limit == 0 {
        return;
    }
    samples.push(row.clone());
    samples.sort_by(|lhs, rhs| {
        lhs.q
            .cmp(&rhs.q)
            .then_with(|| lhs.phase_distance.cmp(&rhs.phase_distance))
            .then_with(|| lhs.k.cmp(&rhs.k))
            .then_with(|| lhs.a_sum.cmp(&rhs.a_sum))
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
    let row = make_obstruction_row(word, &data, d);
    result.counters.obstruction_rows += 1;
    result.counters.q_equals_1_rows += u64::from(row.q == 1);
    result.counters.rho_equals_0_rows += u64::from(row.rho == 0);
    result.counters.trivial_all2_closures += u64::from(row.q == 1 && is_all_twos(word));
    result.counters.nontrivial_closure_candidates += u64::from(row.q == 1 && !is_all_twos(word));

    result
        .coarse_groups
        .entry(coarse_key(&row))
        .or_default()
        .add_row(&row);

    if config.exact_family_limit > 0 {
        let exact_key = exact_deviation_key(&row);
        if result.exact_deviation_groups.contains_key(&exact_key)
            || result.exact_deviation_groups.len() < config.exact_family_limit
        {
            result
                .exact_deviation_groups
                .entry(exact_key)
                .or_default()
                .add_row(&row);
        } else {
            result.counters.exact_family_rows_skipped += 1;
        }
    }

    if row.q == 1 || row.rho == 0 {
        result.closure_rows.push(row.clone());
    }
    add_sample(&mut result.samples, config.sample_limit, &row);
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
            let requested_start = config.start_word;
            let requested_end = config.end_word.unwrap_or(u64::MAX);
            if end_word >= requested_start && next_start <= requested_end {
                let overlap_start = next_start.max(requested_start);
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
                        "lock1-obstruction-progress worker={} words={} q1={} nontrivial_q1={} exact_family_groups={}",
                        worker_id,
                        result.counters.words_scanned,
                        result.counters.q_equals_1_rows,
                        result.counters.nontrivial_closure_candidates,
                        result.exact_deviation_groups.len()
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

fn merge_group_maps(
    target: &mut BTreeMap<CoarseKey, GroupStats>,
    source: BTreeMap<CoarseKey, GroupStats>,
) {
    for (key, stats) in source {
        merge_group_stats(target.entry(key).or_default(), stats);
    }
}

fn merge_exact_maps(
    target: &mut BTreeMap<String, GroupStats>,
    source: BTreeMap<String, GroupStats>,
    counters: &mut Counters,
    exact_family_limit: usize,
) {
    for (key, stats) in source {
        if target.contains_key(&key) || target.len() < exact_family_limit {
            merge_group_stats(target.entry(key).or_default(), stats);
        } else {
            counters.exact_family_rows_skipped += stats.count;
        }
    }
}

fn merge_group_stats(target: &mut GroupStats, source: GroupStats) {
    target.count += source.count;
    target.q_equals_1 += source.q_equals_1;
    target.rho_equals_0 += source.rho_equals_0;
    target.trivial_all2 += source.trivial_all2;
    target.nontrivial_closure += source.nontrivial_closure;
    if let Some(value) = source.min_q {
        target.min_q = Some(target.min_q.map_or(value, |existing| existing.min(value)));
    }
    if let Some(value) = source.min_delta_q {
        target.min_delta_q = Some(
            target
                .min_delta_q
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
    if let Some(value) = source.min_phase_distance {
        target.min_phase_distance = Some(
            target
                .min_phase_distance
                .map_or(value, |existing| existing.min(value)),
        );
    }
    for (q, count) in source.q_counts {
        *target.q_counts.entry(q).or_insert(0) += count;
    }
    for (q, count) in source.delta_q_counts {
        *target.delta_q_counts.entry(q).or_insert(0) += count;
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
        merged.closure_rows.extend(worker.closure_rows);
        merge_group_maps(&mut merged.coarse_groups, worker.coarse_groups);
        merge_exact_maps(
            &mut merged.exact_deviation_groups,
            worker.exact_deviation_groups,
            &mut merged.counters,
            config.exact_family_limit,
        );
    }
    if config
        .max_words
        .map(|max_words| merged.counters.words_scanned >= max_words)
        .unwrap_or(false)
    {
        merged.counters.stopped_early = true;
    }
    merged.samples.sort_by(|lhs, rhs| {
        lhs.q
            .cmp(&rhs.q)
            .then_with(|| lhs.phase_distance.cmp(&rhs.phase_distance))
            .then_with(|| lhs.k.cmp(&rhs.k))
            .then_with(|| lhs.a_sum.cmp(&rhs.a_sum))
            .then_with(|| word_string(&lhs.word).cmp(&word_string(&rhs.word)))
    });
    merged.samples.truncate(config.sample_limit);
    merged
}

fn q_counts_string(values: &BTreeMap<u128, u64>) -> String {
    values
        .iter()
        .take(16)
        .map(|(q, count)| format!("{}:{}", q, count))
        .collect::<Vec<_>>()
        .join(";")
}

fn write_rows(path: PathBuf, rows: &[ObstructionRow]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "word,A,k,B,D,gcd,q,rho,phase_distance,remainder,delta_sign,delta_abs,delta_gcd,delta_q,final_deviation,first_nonzero_deviation_index,first_nonzero_deviation_value,last_nonzero_deviation_index,last_nonzero_deviation_value,max_abs_partial_deviation,max_abs_prefix_deviation_before_terms,positive_deviations,negative_deviations,zero_deviations,deviation_word,prefix_deviation_before_terms,delta_term_sign_word,partial_deviation_word,sturmian_carry_word,sturmian_deviation_word,partial_sturmian_deviation_word,sturmian_gap,primitive_word,primitive_reps,canonical_rotation"
    )?;
    for row in rows {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            csv_escape(&word_string(&row.word)),
            row.a_sum,
            row.k,
            row.b,
            row.d,
            row.gcd,
            row.q,
            row.rho,
            row.phase_distance,
            row.remainder,
            row.delta_sign,
            row.delta_abs,
            row.delta_gcd,
            row.delta_q,
            row.final_deviation,
            row.first_nonzero_deviation_index,
            row.first_nonzero_deviation_value,
            row.last_nonzero_deviation_index,
            row.last_nonzero_deviation_value,
            row.max_abs_partial_deviation,
            row.max_abs_prefix_deviation_before_terms,
            row.positive_deviations,
            row.negative_deviations,
            row.zero_deviations,
            csv_escape(&word_string(&row.deviation_word)),
            csv_escape(&word_string(&row.prefix_deviation_before_terms)),
            csv_escape(&word_string(&row.delta_term_sign_word)),
            csv_escape(&word_string(&row.partial_deviation_word)),
            csv_escape(&word_string(&row.sturmian_carry_word)),
            csv_escape(&word_string(&row.sturmian_deviation_word)),
            csv_escape(&word_string(&row.partial_sturmian_deviation_word)),
            row.sturmian_gap,
            csv_escape(&word_string(&row.primitive_word)),
            row.primitive_reps,
            csv_escape(&word_string(&row.canonical_rotation))
        )?;
    }
    Ok(())
}

fn write_coarse_groups(
    path: PathBuf,
    groups: &BTreeMap<CoarseKey, GroupStats>,
) -> std::io::Result<()> {
    let mut entries: Vec<(&CoarseKey, &GroupStats)> = groups.iter().collect();
    entries.sort_by(|lhs, rhs| {
        rhs.1
            .nontrivial_closure
            .cmp(&lhs.1.nontrivial_closure)
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
        "k,A,final_deviation,first_nonzero_deviation_index,first_nonzero_deviation_value,last_nonzero_deviation_index,last_nonzero_deviation_value,max_abs_partial_deviation,max_abs_prefix_deviation_before_terms,positive_deviations,negative_deviations,zero_deviations,sturmian_gap,count,q_equals_1,rho_equals_0,trivial_all2,nontrivial_closure,min_q,min_delta_q,min_delta_abs,min_phase_distance,q_counts,delta_q_counts,examples"
    )?;
    for (key, stats) in entries {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            key.k,
            key.a_sum,
            key.final_deviation,
            key.first_nonzero_deviation_index,
            key.first_nonzero_deviation_value,
            key.last_nonzero_deviation_index,
            key.last_nonzero_deviation_value,
            key.max_abs_partial_deviation,
            key.max_abs_prefix_deviation_before_terms,
            key.positive_deviations,
            key.negative_deviations,
            key.zero_deviations,
            key.sturmian_gap,
            stats.count,
            stats.q_equals_1,
            stats.rho_equals_0,
            stats.trivial_all2,
            stats.nontrivial_closure,
            stats.min_q.unwrap_or(0),
            stats.min_delta_q.unwrap_or(0),
            stats.min_delta_abs.unwrap_or(0),
            stats.min_phase_distance.unwrap_or(0),
            csv_escape(&q_counts_string(&stats.q_counts)),
            csv_escape(&q_counts_string(&stats.delta_q_counts)),
            csv_escape(&stats.examples.join(" | "))
        )?;
    }
    Ok(())
}

fn write_exact_groups(path: PathBuf, groups: &BTreeMap<String, GroupStats>) -> std::io::Result<()> {
    let mut entries: Vec<(&String, &GroupStats)> = groups.iter().collect();
    entries.sort_by(|lhs, rhs| {
        rhs.1
            .nontrivial_closure
            .cmp(&lhs.1.nontrivial_closure)
            .then_with(|| {
                lhs.1
                    .min_delta_q
                    .unwrap_or(u128::MAX)
                    .cmp(&rhs.1.min_delta_q.unwrap_or(u128::MAX))
            })
            .then_with(|| rhs.1.count.cmp(&lhs.1.count))
            .then_with(|| lhs.0.cmp(rhs.0))
    });
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "exact_deviation_family,count,q_equals_1,rho_equals_0,trivial_all2,nontrivial_closure,min_q,min_delta_q,min_delta_abs,min_phase_distance,q_counts,delta_q_counts,examples"
    )?;
    for (key, stats) in entries {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{}",
            csv_escape(key),
            stats.count,
            stats.q_equals_1,
            stats.rho_equals_0,
            stats.trivial_all2,
            stats.nontrivial_closure,
            stats.min_q.unwrap_or(0),
            stats.min_delta_q.unwrap_or(0),
            stats.min_delta_abs.unwrap_or(0),
            stats.min_phase_distance.unwrap_or(0),
            csv_escape(&q_counts_string(&stats.q_counts)),
            csv_escape(&q_counts_string(&stats.delta_q_counts)),
            csv_escape(&stats.examples.join(" | "))
        )?;
    }
    Ok(())
}

fn write_notes(path: PathBuf, result: &WorkerResult) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(file, "# Lock 1 Obstruction Scanner Notes")?;
    writeln!(file)?;
    writeln!(file, "This scanner is aimed at the algebraic loop obstruction, not at forward-number enumeration.")?;
    writeln!(file)?;
    writeln!(file, "For each exponent word `w`:")?;
    writeln!(file)?;
    writeln!(file, "```text")?;
    writeln!(file, "F_w(x) = (3^k x + B_w) / 2^A")?;
    writeln!(file, "D = 2^A - 3^k")?;
    writeln!(file, "g = gcd(B_w, D)")?;
    writeln!(file, "q = D / g")?;
    writeln!(file, "rho = (B_w / g) mod q")?;
    writeln!(file, "nontrivial loop closure requires q = 1")?;
    writeln!(file, "```")?;
    writeln!(file)?;
    writeln!(file, "Rows scanned: {}", result.counters.words_scanned)?;
    writeln!(
        file,
        "Obstruction rows with D > 0: {}",
        result.counters.obstruction_rows
    )?;
    writeln!(file, "Rows with q=1: {}", result.counters.q_equals_1_rows)?;
    writeln!(
        file,
        "Trivial all-2 closures: {}",
        result.counters.trivial_all2_closures
    )?;
    writeln!(
        file,
        "Nontrivial closure candidates: {}",
        result.counters.nontrivial_closure_candidates
    )?;
    writeln!(file)?;
    writeln!(file, "How to use this output:")?;
    writeln!(file)?;
    writeln!(file, "1. `lock1_closure_rows.csv` is the danger file. For a clean run it should contain only all-2 words.")?;
    writeln!(file, "2. `lock1_exact_deviation_families.csv` groups the obstruction by deviation from the all-2 heartbeat.")?;
    writeln!(file, "3. `lock1_coarse_obstruction_families.csv` tells which deviation envelopes get closest to q=1.")?;
    writeln!(
        file,
        "4. The proof target is now exact: show every nonzero deviation family forces q>1."
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
    writeln!(file, "  \"scanner\": \"lock1_obstruction_scan\",")?;
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
    match config.max_words {
        Some(value) => writeln!(file, "  \"max_words\": {},", value)?,
        None => writeln!(file, "  \"max_words\": null,")?,
    }
    writeln!(
        file,
        "  \"words_scanned\": {},",
        result.counters.words_scanned
    )?;
    writeln!(
        file,
        "  \"overflow_rejects\": {},",
        result.counters.overflow_rejects
    )?;
    writeln!(
        file,
        "  \"D_le_zero_rejects\": {},",
        result.counters.d_le_zero_rejects
    )?;
    writeln!(
        file,
        "  \"obstruction_rows\": {},",
        result.counters.obstruction_rows
    )?;
    writeln!(
        file,
        "  \"q_equals_1_rows\": {},",
        result.counters.q_equals_1_rows
    )?;
    writeln!(
        file,
        "  \"rho_equals_0_rows\": {},",
        result.counters.rho_equals_0_rows
    )?;
    writeln!(
        file,
        "  \"trivial_all2_closures\": {},",
        result.counters.trivial_all2_closures
    )?;
    writeln!(
        file,
        "  \"nontrivial_closure_candidates\": {},",
        result.counters.nontrivial_closure_candidates
    )?;
    writeln!(
        file,
        "  \"exact_family_groups\": {},",
        result.exact_deviation_groups.len()
    )?;
    writeln!(
        file,
        "  \"exact_family_rows_skipped\": {},",
        result.counters.exact_family_rows_skipped
    )?;
    writeln!(
        file,
        "  \"coarse_family_groups\": {},",
        result.coarse_groups.len()
    )?;
    writeln!(
        file,
        "  \"stopped_early\": {},",
        result.counters.stopped_early
    )?;
    writeln!(
        file,
        "  \"claim_status_for_scanned_words\": \"{}\"",
        if result.counters.nontrivial_closure_candidates == 0 {
            "no_nontrivial_q_equals_1_seen"
        } else {
            "nontrivial_closure_candidate_requires_audit"
        }
    )?;
    writeln!(file, "}}")?;
    Ok(())
}

fn main() {
    let config = Arc::new(parse_args());
    create_dir_all(&config.out_dir).expect("create out dir");
    let result = run_scan(Arc::clone(&config));

    write_rows(
        config.out_dir.join("lock1_obstruction_samples.csv"),
        &result.samples,
    )
    .expect("write samples");
    write_rows(
        config.out_dir.join("lock1_closure_rows.csv"),
        &result.closure_rows,
    )
    .expect("write closure rows");
    write_coarse_groups(
        config.out_dir.join("lock1_coarse_obstruction_families.csv"),
        &result.coarse_groups,
    )
    .expect("write coarse groups");
    write_exact_groups(
        config.out_dir.join("lock1_exact_deviation_families.csv"),
        &result.exact_deviation_groups,
    )
    .expect("write exact groups");
    write_notes(
        config.out_dir.join("LOCK1_OBSTRUCTION_SCAN_NOTES.md"),
        &result,
    )
    .expect("write notes");
    write_summary_json(
        config.out_dir.join("lock1_obstruction_summary.json"),
        &result,
        &config,
    )
    .expect("write summary");

    println!("Lock 1 obstruction scanner");
    println!("words_scanned={}", result.counters.words_scanned);
    println!("D_le_zero_rejects={}", result.counters.d_le_zero_rejects);
    println!("obstruction_rows={}", result.counters.obstruction_rows);
    println!("q_equals_1_rows={}", result.counters.q_equals_1_rows);
    println!(
        "nontrivial_closure_candidates={}",
        result.counters.nontrivial_closure_candidates
    );
    println!(
        "exact_family_groups={}",
        result.exact_deviation_groups.len()
    );
    println!("coarse_family_groups={}", result.coarse_groups.len());
    println!("wrote: {}", config.out_dir.display());
}
