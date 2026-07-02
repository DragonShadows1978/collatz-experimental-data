use std::cmp::Ordering;
use std::collections::HashMap;
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
    near_miss_limit: usize,
    progress_every: u64,
    threads: usize,
    job_chunk_words: u64,
    out_dir: PathBuf,
}

#[derive(Default)]
struct Counters {
    words_scanned: u64,
    d_le_zero_rejects: u64,
    divisibility_rejects: u64,
    non_positive_or_even_rejects: u64,
    exact_word_failures: u64,
    rotation_failures: u64,
    trivial_cycle_hits: u64,
    nontrivial_cycle_hits: u64,
    overflow_rejects: u64,
    stopped_early: bool,
}

impl Counters {
    fn add_assign(&mut self, other: &Self) {
        self.words_scanned += other.words_scanned;
        self.d_le_zero_rejects += other.d_le_zero_rejects;
        self.divisibility_rejects += other.divisibility_rejects;
        self.non_positive_or_even_rejects += other.non_positive_or_even_rejects;
        self.exact_word_failures += other.exact_word_failures;
        self.rotation_failures += other.rotation_failures;
        self.trivial_cycle_hits += other.trivial_cycle_hits;
        self.nontrivial_cycle_hits += other.nontrivial_cycle_hits;
        self.overflow_rejects += other.overflow_rejects;
        self.stopped_early |= other.stopped_early;
    }
}

struct WorkerResult {
    counters: Counters,
    near_misses: Vec<NearMiss>,
    candidate_rows: Vec<String>,
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
struct NearMiss {
    word: Vec<usize>,
    a_sum: usize,
    k: usize,
    b: u128,
    d: u128,
    gcd: u128,
    quotient: u128,
    remainder: u128,
    distance_num: u128,
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
    let mut near_miss_limit = 1000usize;
    let mut progress_every = 0u64;
    let mut threads = 1usize;
    let mut job_chunk_words = 250_000u64;
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
            "--near-miss-limit" => {
                i += 1;
                near_miss_limit = args[i].parse().expect("--near-miss-limit integer");
            }
            "--progress-every" => {
                i += 1;
                progress_every = args[i].parse().expect("--progress-every integer");
            }
            "--threads" => {
                i += 1;
                threads = args[i].parse().expect("--threads integer");
            }
            "--job-chunk-words" => {
                i += 1;
                job_chunk_words = args[i].parse().expect("--job-chunk-words integer");
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
        near_miss_limit,
        progress_every,
        threads,
        job_chunk_words,
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

fn v2(value: u128) -> usize {
    value.trailing_zeros() as usize
}

fn odd_step(value: u128) -> Option<(u128, usize)> {
    let lifted = value.checked_mul(3)?.checked_add(1)?;
    let exponent = v2(lifted);
    Some((lifted >> exponent, exponent))
}

fn word_string(word: &[usize]) -> String {
    word.iter()
        .map(|value| value.to_string())
        .collect::<Vec<_>>()
        .join(" ")
}

fn verify_word(value: u128, word: &[usize]) -> (bool, Vec<usize>, Vec<u128>, String) {
    let mut current = value;
    let mut observed = Vec::with_capacity(word.len());
    let mut orbit = Vec::with_capacity(word.len() + 1);
    orbit.push(value);
    for &expected in word {
        let Some((next, actual)) = odd_step(current) else {
            return (
                false,
                observed,
                orbit,
                "u128_overflow_during_forward_verify".to_string(),
            );
        };
        observed.push(actual);
        orbit.push(next);
        if actual != expected {
            return (
                false,
                observed,
                orbit,
                format!("valuation_mismatch_expected_{}_actual_{}", expected, actual),
            );
        }
        current = next;
    }
    if current != value {
        return (false, observed, orbit, "final_value_not_start".to_string());
    }
    (true, observed, orbit, "verified".to_string())
}

fn rotated_word(word: &[usize], offset: usize) -> Vec<usize> {
    word[offset..]
        .iter()
        .chain(word[..offset].iter())
        .copied()
        .collect()
}

fn verify_rotations(word: &[usize], orbit: &[u128]) -> (bool, String) {
    let cycle_values = &orbit[..orbit.len().saturating_sub(1)];
    for offset in 0..word.len() {
        let rotation = rotated_word(word, offset);
        let Some(data) = affine_data(&rotation) else {
            return (
                false,
                format!("rotation_overflow:{}", word_string(&rotation)),
            );
        };
        if data.two_a <= data.three_k {
            return (
                false,
                format!("rotation_D_le_zero:{}", word_string(&rotation)),
            );
        }
        let denominator = data.two_a - data.three_k;
        if data.b % denominator != 0 {
            return (
                false,
                format!("rotation_not_integral:{}", word_string(&rotation)),
            );
        }
        let x = data.b / denominator;
        if !cycle_values.contains(&x) {
            return (
                false,
                format!(
                    "rotation_value_not_in_cycle:{}:{}",
                    word_string(&rotation),
                    x
                ),
            );
        }
        let (ok, observed, _, reason) = verify_word(x, &rotation);
        if !ok {
            return (
                false,
                format!(
                    "rotation_exact_word_failure:{}:{}:{}",
                    word_string(&rotation),
                    word_string(&observed),
                    reason
                ),
            );
        }
    }
    (true, "rotations_verified".to_string())
}

fn csv_escape(value: &str) -> String {
    if value.contains(',') || value.contains('"') || value.contains('\n') {
        format!("\"{}\"", value.replace('"', "\"\""))
    } else {
        value.to_string()
    }
}

fn candidate_row_string(
    word: &[usize],
    data: &AffineData,
    denominator: u128,
    x: u128,
    status: &str,
    observed: &[usize],
    orbit: &[u128],
    notes: &str,
) -> String {
    let observed = word_string(observed);
    let orbit_values = orbit
        .iter()
        .map(|value| value.to_string())
        .collect::<Vec<_>>()
        .join(" ");
    format!(
        "{},{},{},{},{},{},{},{},{},{},{}",
        csv_escape(&word_string(word)),
        data.a_sum,
        data.k,
        data.b,
        denominator,
        x,
        x % 2 == 1,
        status,
        csv_escape(&observed),
        csv_escape(&orbit_values),
        csv_escape(notes)
    )
}

fn write_candidate_rows(path: PathBuf, rows: &[String]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "word,A,k,B,D,x,x_is_odd,status,observed_word,orbit_values,notes"
    )?;
    for row in rows {
        writeln!(file, "{}", row)?;
    }
    Ok(())
}

fn maybe_add_near_miss(
    near_misses: &mut Vec<NearMiss>,
    limit: usize,
    word: &[usize],
    data: &AffineData,
    denominator: u128,
) {
    if limit == 0 {
        return;
    }
    let remainder = data.b % denominator;
    let divisor = gcd(data.b, denominator);
    let distance_num = remainder.min(denominator - remainder);
    near_misses.push(NearMiss {
        word: word.to_vec(),
        a_sum: data.a_sum,
        k: data.k,
        b: data.b,
        d: denominator,
        gcd: divisor,
        quotient: denominator / divisor,
        remainder,
        distance_num,
    });
    near_misses.sort_by(|lhs, rhs| {
        lhs.quotient
            .cmp(&rhs.quotient)
            .then_with(|| {
                (lhs.distance_num * rhs.d)
                    .cmp(&(rhs.distance_num * lhs.d))
                    .then(Ordering::Equal)
            })
            .then_with(|| lhs.k.cmp(&rhs.k))
            .then_with(|| lhs.a_sum.cmp(&rhs.a_sum))
    });
    near_misses.truncate(limit);
}

fn scan_word(
    word: &[usize],
    counters: &mut Counters,
    candidate_rows: &mut Vec<String>,
    near_misses: &mut Vec<NearMiss>,
    near_miss_limit: usize,
) {
    counters.words_scanned += 1;
    let Some(data) = affine_data(word) else {
        counters.overflow_rejects += 1;
        return;
    };
    if data.two_a <= data.three_k {
        counters.d_le_zero_rejects += 1;
        return;
    }
    let denominator = data.two_a - data.three_k;
    if data.b % denominator != 0 {
        counters.divisibility_rejects += 1;
        maybe_add_near_miss(near_misses, near_miss_limit, word, &data, denominator);
        return;
    }

    let x = data.b / denominator;
    if x == 0 || x % 2 == 0 {
        counters.non_positive_or_even_rejects += 1;
        candidate_rows.push(candidate_row_string(
            word,
            &data,
            denominator,
            x,
            "non_positive_or_even",
            &[],
            &[],
            "",
        ));
        return;
    }

    let (ok, observed, orbit, reason) = verify_word(x, word);
    if !ok {
        counters.exact_word_failures += 1;
        candidate_rows.push(candidate_row_string(
            word,
            &data,
            denominator,
            x,
            "exact_word_failure",
            &observed,
            &orbit,
            &reason,
        ));
        return;
    }

    let (rotations_ok, rotation_notes) = verify_rotations(word, &orbit);
    if !rotations_ok {
        counters.rotation_failures += 1;
        candidate_rows.push(candidate_row_string(
            word,
            &data,
            denominator,
            x,
            "rotation_failure",
            &observed,
            &orbit,
            &rotation_notes,
        ));
        return;
    }

    let status = if x == 1 && word.iter().all(|&exponent| exponent == 2) {
        counters.trivial_cycle_hits += 1;
        "trivial_cycle"
    } else {
        counters.nontrivial_cycle_hits += 1;
        "nontrivial_cycle"
    };
    candidate_rows.push(candidate_row_string(
        word,
        &data,
        denominator,
        x,
        status,
        &observed,
        &orbit,
        &rotation_notes,
    ));
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

fn write_near_misses(path: PathBuf, near_misses: &[NearMiss]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "word,A,k,B,D,gcd(B,D),D/gcd(B,D),B mod D,approximate_x,distance_to_integer,distance_fraction"
    )?;
    for row in near_misses {
        let approximate_x = row.b as f64 / row.d as f64;
        let distance = row.distance_num as f64 / row.d as f64;
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{:.18},{:.18},{}/{}",
            csv_escape(&word_string(&row.word)),
            row.a_sum,
            row.k,
            row.b,
            row.d,
            row.gcd,
            row.quotient,
            row.remainder,
            approximate_x,
            distance,
            row.distance_num,
            row.d
        )?;
    }
    Ok(())
}

fn scope_name(scope: Scope) -> &'static str {
    match scope {
        Scope::All => "all",
        Scope::Line => "line",
    }
}

fn sort_near_misses(near_misses: &mut Vec<NearMiss>, limit: usize) {
    near_misses.sort_by(|lhs, rhs| {
        lhs.quotient
            .cmp(&rhs.quotient)
            .then_with(|| {
                (lhs.distance_num * rhs.d)
                    .cmp(&(rhs.distance_num * lhs.d))
                    .then(Ordering::Equal)
            })
            .then_with(|| lhs.k.cmp(&rhs.k))
            .then_with(|| lhs.a_sum.cmp(&rhs.a_sum))
    });
    near_misses.truncate(limit);
}

fn count_compositions(length: usize, total: usize, max_part: usize) -> u64 {
    let mut dp = vec![vec![0u64; total + 1]; length + 1];
    dp[0][0] = 1;
    for used in 0..length {
        for sum in 0..=total {
            let count = dp[used][sum];
            if count == 0 {
                continue;
            }
            for part in 1..=max_part {
                let next_sum = sum + part;
                if next_sum > total {
                    break;
                }
                dp[used + 1][next_sum] = dp[used + 1][next_sum].saturating_add(count);
            }
        }
    }
    dp[length][total]
}

fn count_compositions_memo(
    length: usize,
    total: usize,
    max_part: usize,
    memo: &mut HashMap<(usize, usize), u64>,
) -> u64 {
    if let Some(&value) = memo.get(&(length, total)) {
        return value;
    }
    let value = if length == 0 {
        u64::from(total == 0)
    } else if total < length || total > length.saturating_mul(max_part) {
        0
    } else if length == 1 {
        u64::from((1..=max_part).contains(&total))
    } else {
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
        count
    };
    memo.insert((length, total), value);
    value
}

fn build_jobs(config: &Config) -> Vec<Job> {
    let mut jobs = Vec::new();
    let mut next_start = 1u64;
    for k in config.min_k..=config.max_k {
        let (mut low, mut high) = match config.scope {
            Scope::Line => {
                let floor_line = (k as f64 * ALPHA).floor() as i64;
                let low = (floor_line + 1 + config.line_offset).max(k as i64) as usize;
                (low, low.saturating_add(config.line_window))
            }
            Scope::All => (k, k.saturating_mul(config.max_a)),
        };
        high = high.min(k.saturating_mul(config.max_a));
        if let Some(max_total_a) = config.max_total_a {
            high = high.min(max_total_a);
        }
        low = low.max(k);
        if low > high {
            continue;
        }
        for total_a in low..=high {
            let count = count_compositions(k, total_a, config.max_a);
            if count == 0 {
                continue;
            }
            let end_word = next_start.saturating_add(count).saturating_sub(1);
            let requested_start = config.start_word;
            let requested_end = config.end_word.unwrap_or(u64::MAX);
            let overlap_start = next_start.max(requested_start);
            let overlap_end = end_word.min(requested_end);
            if overlap_start <= overlap_end {
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
    let mut counters = Counters::default();
    let mut near_misses = Vec::new();
    let mut candidate_rows = Vec::new();
    loop {
        if stop.load(AtomicOrdering::Relaxed) {
            counters.stopped_early = true;
            break;
        }
        let job_idx = next_job.fetch_add(1, AtomicOrdering::Relaxed);
        let Some(job) = jobs.get(job_idx) else {
            break;
        };
        debug_assert!(job.scan_start_word >= job.start_word);
        debug_assert!(job.scan_end_word <= job.end_word);
        let mut cursor = job.start_word;
        let mut memo = HashMap::new();
        let mut prefix = Vec::with_capacity(job.k);
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
                    counters.stopped_early = true;
                    return Ok(false);
                }
                scan_word(
                    word,
                    &mut counters,
                    &mut candidate_rows,
                    &mut near_misses,
                    config.near_miss_limit,
                );
                let scanned = scanned_before + 1;
                if config.progress_every > 0 && scanned % config.progress_every == 0 {
                    eprintln!(
                        "lock1-scan-progress worker={} words={} local_words={} local_trivial={} local_nontrivial={} local_overflow={}",
                        worker_id,
                        scanned,
                        counters.words_scanned,
                        counters.trivial_cycle_hits,
                        counters.nontrivial_cycle_hits,
                        counters.overflow_rejects
                    );
                }
                Ok(true)
            },
        )
        .expect("enumerate compositions");
        if !keep_going {
            if stop.load(AtomicOrdering::Relaxed) {
                break;
            }
            continue;
        }
    }
    WorkerResult {
        counters,
        near_misses,
        candidate_rows,
    }
}

fn run_scan(config: &Config) -> WorkerResult {
    let jobs = Arc::new(build_jobs(config));
    let config = Arc::new(config.clone());
    let next_job = Arc::new(AtomicUsize::new(0));
    let scanned_words = Arc::new(AtomicU64::new(0));
    let stop = Arc::new(AtomicBool::new(false));
    let thread_count = config.threads.min(jobs.len().max(1));
    let mut handles = Vec::with_capacity(thread_count);

    for worker_id in 0..thread_count {
        let config = Arc::clone(&config);
        let jobs = Arc::clone(&jobs);
        let next_job = Arc::clone(&next_job);
        let scanned_words = Arc::clone(&scanned_words);
        let stop = Arc::clone(&stop);
        handles.push(thread::spawn(move || {
            run_worker(worker_id, config, jobs, next_job, scanned_words, stop)
        }));
    }

    let mut merged = WorkerResult {
        counters: Counters::default(),
        near_misses: Vec::new(),
        candidate_rows: Vec::new(),
    };
    for handle in handles {
        let worker = handle.join().expect("lock1 worker panicked");
        merged.counters.add_assign(&worker.counters);
        merged.near_misses.extend(worker.near_misses);
        merged.candidate_rows.extend(worker.candidate_rows);
    }
    if config
        .max_words
        .map(|max_words| merged.counters.words_scanned >= max_words)
        .unwrap_or(false)
    {
        merged.counters.stopped_early = true;
    }
    sort_near_misses(&mut merged.near_misses, config.near_miss_limit);
    merged
}

fn write_summary(path: PathBuf, config: &Config, counters: &Counters) -> std::io::Result<()> {
    let claim_status = if counters.nontrivial_cycle_hits == 0
        && counters.rotation_failures == 0
        && counters.exact_word_failures == 0
    {
        "passed"
    } else {
        "attention_required"
    };
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(file, "{{")?;
    writeln!(file, "  \"scanner\": \"lock1_cycle_scan\",")?;
    writeln!(file, "  \"scan_scope\": \"{}\",", scope_name(config.scope))?;
    writeln!(file, "  \"max_k\": {},", config.max_k)?;
    writeln!(file, "  \"max_a\": {},", config.max_a)?;
    writeln!(file, "  \"min_k\": {},", config.min_k)?;
    match config.scope {
        Scope::Line => {
            writeln!(file, "  \"line_window\": {},", config.line_window)?;
            writeln!(file, "  \"line_offset\": {},", config.line_offset)?;
        }
        Scope::All => {
            writeln!(file, "  \"line_window\": null,")?;
            writeln!(file, "  \"line_offset\": null,")?;
        }
    }
    match config.max_total_a {
        Some(max_total_a) => writeln!(file, "  \"max_total_a\": {},", max_total_a)?,
        None => writeln!(file, "  \"max_total_a\": null,")?,
    }
    match config.max_words {
        Some(max_words) => writeln!(file, "  \"max_words\": {},", max_words)?,
        None => writeln!(file, "  \"max_words\": null,")?,
    }
    writeln!(file, "  \"start_word\": {},", config.start_word)?;
    match config.end_word {
        Some(end_word) => writeln!(file, "  \"end_word\": {},", end_word)?,
        None => writeln!(file, "  \"end_word\": null,")?,
    }
    writeln!(file, "  \"threads\": {},", config.threads)?;
    writeln!(file, "  \"job_chunk_words\": {},", config.job_chunk_words)?;
    writeln!(file, "  \"words_scanned\": {},", counters.words_scanned)?;
    writeln!(
        file,
        "  \"D_le_zero_rejects\": {},",
        counters.d_le_zero_rejects
    )?;
    writeln!(
        file,
        "  \"divisibility_rejects\": {},",
        counters.divisibility_rejects
    )?;
    writeln!(
        file,
        "  \"non_positive_or_even_rejects\": {},",
        counters.non_positive_or_even_rejects
    )?;
    writeln!(
        file,
        "  \"exact_word_failures\": {},",
        counters.exact_word_failures
    )?;
    writeln!(
        file,
        "  \"rotation_failures\": {},",
        counters.rotation_failures
    )?;
    writeln!(
        file,
        "  \"trivial_cycle_hits\": {},",
        counters.trivial_cycle_hits
    )?;
    writeln!(
        file,
        "  \"nontrivial_cycle_hits\": {},",
        counters.nontrivial_cycle_hits
    )?;
    writeln!(
        file,
        "  \"overflow_rejects\": {},",
        counters.overflow_rejects
    )?;
    writeln!(file, "  \"stopped_early\": {},", counters.stopped_early)?;
    writeln!(
        file,
        "  \"claim_status_for_scanned_scope\": \"{}\",",
        claim_status
    )?;
    writeln!(
        file,
        "  \"semantics\": \"Enumerates exponent words, solves x=B/(2^A-3^k), then verifies exact odd-only valuation paths and all cyclic rotations. It does not enumerate starting numbers.\""
    )?;
    writeln!(file, "}}")?;
    Ok(())
}

fn main() {
    let config = parse_args();
    create_dir_all(&config.out_dir).expect("create output directory");

    let candidates_path = config.out_dir.join("cycle_candidates.csv");
    let near_misses_path = config.out_dir.join("cycle_near_misses.csv");
    let summary_path = config.out_dir.join("cycle_rejections_summary.json");

    let result = run_scan(&config);

    write_candidate_rows(candidates_path.clone(), &result.candidate_rows)
        .expect("write candidate rows");
    write_near_misses(near_misses_path.clone(), &result.near_misses).expect("write near misses");
    write_summary(summary_path.clone(), &config, &result.counters).expect("write summary");

    println!("Lock 1 cycle-word scanner");
    println!("scope={}", scope_name(config.scope));
    println!("max_k={}", config.max_k);
    println!("max_a={}", config.max_a);
    println!("threads={}", config.threads);
    println!("words_scanned={}", result.counters.words_scanned);
    println!("D_le_zero_rejects={}", result.counters.d_le_zero_rejects);
    println!(
        "divisibility_rejects={}",
        result.counters.divisibility_rejects
    );
    println!(
        "non_positive_or_even_rejects={}",
        result.counters.non_positive_or_even_rejects
    );
    println!(
        "exact_word_failures={}",
        result.counters.exact_word_failures
    );
    println!("rotation_failures={}", result.counters.rotation_failures);
    println!("trivial_cycle_hits={}", result.counters.trivial_cycle_hits);
    println!(
        "nontrivial_cycle_hits={}",
        result.counters.nontrivial_cycle_hits
    );
    println!("overflow_rejects={}", result.counters.overflow_rejects);
    println!("stopped_early={}", result.counters.stopped_early);
    println!("wrote candidates: {}", candidates_path.display());
    println!("wrote near misses: {}", near_misses_path.display());
    println!("wrote summary: {}", summary_path.display());
}
