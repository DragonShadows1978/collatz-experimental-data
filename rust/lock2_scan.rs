use std::cmp::{max, min};
use std::env;
use std::fs::{create_dir_all, File};
use std::io::{BufWriter, Write};
use std::path::PathBuf;
use std::sync::{
    atomic::{AtomicU64, Ordering},
    Arc, Mutex,
};
use std::thread;
use std::time::{Instant, SystemTime, UNIX_EPOCH};

#[derive(Clone)]
struct Row {
    word: String,
    k: usize,
    a_sum: usize,
    b: u128,
    rho: u128,
    theta_den: u128,
    theta_float: f64,
    margin: u128,
    threshold_gap_float: f64,
    relative_gap: f64,
    normalized_margin: f64,
    theta_candidate_odd_count: u128,
    rho_rank: u128,
    theta_over_rho: f64,
    candidate_to_rho_rank_ratio: f64,
    rho_bit_slack: i32,
    is_all_twos: bool,
    first_contractivity_index: usize,
    delta_from_all_twos: u64,
    count_ones: usize,
    count_twos: usize,
    count_ge3: usize,
    max_run_1: usize,
    max_run_2: usize,
    max_run_ge3: usize,
    primitive_period: usize,
    primitive_repetitions: usize,
}

#[derive(Clone)]
struct ByA {
    contractive: u64,
    first_contractivity: u64,
    min_rho: u128,
    min_rho_word: String,
    max_theta_candidate_count: u128,
    max_theta_candidate_word: String,
    max_theta_over_rho: f64,
    max_theta_over_rho_word: String,
    max_candidate_to_rho_rank_ratio: f64,
    max_candidate_to_rho_rank_word: String,
}

impl Default for ByA {
    fn default() -> Self {
        Self {
            contractive: 0,
            first_contractivity: 0,
            min_rho: 0,
            min_rho_word: String::new(),
            max_theta_candidate_count: 0,
            max_theta_candidate_word: String::new(),
            max_theta_over_rho: 0.0,
            max_theta_over_rho_word: String::new(),
            max_candidate_to_rho_rank_ratio: 0.0,
            max_candidate_to_rho_rank_word: String::new(),
        }
    }
}

#[derive(Clone)]
struct Config {
    amax: usize,
    top_n: usize,
    prediction_top_n: usize,
    out_dir: PathBuf,
    stamp: String,
    progress_every: u64,
    threads: usize,
    split_depth: usize,
    count_only: bool,
    total_expected_words: u128,
    predict_rho_slack_min: Option<i32>,
    predict_theta_candidates_min: Option<u128>,
    predict_theta_over_rho_min: Option<f64>,
}

struct Scanner {
    config: Config,
    powers2: Vec<u128>,
    powers3: Vec<u128>,
    max_solvent_sum: Vec<usize>,
    start_time: Instant,
    progress_counter: Option<Arc<AtomicU64>>,
    total_words: u64,
    contractive_words: u64,
    first_contractivity_words: u64,
    all_twos_zero_margins: u64,
    nontrivial_zero_margins: u64,
    negative_margins: u64,
    theta_buckets: Vec<(&'static str, u64)>,
    rho_small_counts: Vec<(&'static str, u128, u64)>,
    rho_slack_buckets: Vec<(&'static str, u64)>,
    by_a: Vec<ByA>,
    near_rows: Vec<Row>,
    prediction_rows: Vec<Row>,
    small_rho_rows: Vec<Row>,
    prediction_match_count: u64,
    min_nontrivial_margin: Option<Row>,
    min_nontrivial_relative_gap: Option<Row>,
    max_theta_candidate_row: Option<Row>,
}

#[derive(Clone)]
struct Task {
    prefix: Vec<u16>,
    prefix_sum: usize,
    prefix_b: u128,
}

fn main() {
    let config = parse_args();
    if config.amax >= 120 {
        panic!("u128 scanner is intended for Amax < 120");
    }
    if config.count_only {
        print_count_estimate(&config);
        return;
    }
    create_dir_all(&config.out_dir).expect("create out dir");
    let mut scanner = Scanner::new(config);
    if scanner.config.threads > 1 {
        scanner.scan_parallel();
    } else {
        scanner.scan();
    }
    scanner.write_outputs();
    scanner.print_summary();
}

fn parse_args() -> Config {
    let mut amax: Option<usize> = None;
    let mut top_n = 200usize;
    let mut prediction_top_n = 200usize;
    let mut out_dir = PathBuf::from("data/runs");
    let mut stamp: Option<String> = None;
    let mut progress_every = 10_000_000u64;
    let mut threads = 1usize;
    let mut split_depth = 5usize;
    let mut count_only = false;
    let mut predict_rho_slack_min = None;
    let mut predict_theta_candidates_min = None;
    let mut predict_theta_over_rho_min = None;

    let args: Vec<String> = env::args().collect();
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--Amax" => {
                i += 1;
                amax = Some(args[i].parse().expect("--Amax integer"));
            }
            "--top-n" => {
                i += 1;
                top_n = args[i].parse().expect("--top-n integer");
            }
            "--prediction-top-n" => {
                i += 1;
                prediction_top_n = args[i].parse().expect("--prediction-top-n integer");
            }
            "--out-dir" => {
                i += 1;
                out_dir = PathBuf::from(&args[i]);
            }
            "--stamp" => {
                i += 1;
                stamp = Some(args[i].clone());
            }
            "--progress-every" => {
                i += 1;
                progress_every = args[i].parse().expect("--progress-every integer");
            }
            "--threads" => {
                i += 1;
                threads = max(1, args[i].parse().expect("--threads integer"));
            }
            "--split-depth" => {
                i += 1;
                split_depth = args[i].parse().expect("--split-depth integer");
            }
            "--count-only" => {
                count_only = true;
            }
            "--predict-rho-slack-min" => {
                i += 1;
                predict_rho_slack_min = Some(args[i].parse().expect("rho slack integer"));
            }
            "--predict-theta-candidates-min" => {
                i += 1;
                predict_theta_candidates_min =
                    Some(args[i].parse().expect("theta candidates integer"));
            }
            "--predict-theta-over-rho-min" => {
                i += 1;
                predict_theta_over_rho_min = Some(args[i].parse().expect("theta/rho float"));
            }
            "--first-contractivity-only" => {}
            other => panic!("unknown arg: {}", other),
        }
        i += 1;
    }

    let stamp = stamp.unwrap_or_else(|| {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("time")
            .as_secs()
            .to_string()
    });

    let amax = amax.expect("--Amax is required");
    let total_expected_words = count_first_contractivity_words(amax);

    Config {
        amax,
        top_n,
        prediction_top_n,
        out_dir,
        stamp,
        progress_every,
        threads,
        split_depth,
        count_only,
        total_expected_words,
        predict_rho_slack_min,
        predict_theta_candidates_min,
        predict_theta_over_rho_min,
    }
}

fn print_count_estimate(config: &Config) {
    println!("Lock 2 first-contractivity count estimate");
    println!("Amax={}", config.amax);
    println!("expected_words={}", config.total_expected_words);
}

fn count_first_contractivity_words(amax: usize) -> u128 {
    let mut limits = vec![0usize; amax + 2];
    let mut power = 1u128;
    for (j, limit) in limits.iter_mut().enumerate().skip(1) {
        power *= 3;
        *limit = 127usize - power.leading_zeros() as usize;
        if j >= amax + 1 {
            break;
        }
    }

    let mut dp = vec![0u128; amax + 1];
    dp[0] = 1;
    let mut total = 0u128;

    for prefix_len in 0..amax {
        let final_len = prefix_len + 1;
        for (prefix_sum, count) in dp.iter().copied().enumerate() {
            if count == 0 {
                continue;
            }
            let min_final_sum = max(prefix_sum + 1, limits[final_len] + 1);
            if min_final_sum <= amax {
                total += count * (amax - min_final_sum + 1) as u128;
            }
        }

        let next_len = prefix_len + 1;
        if next_len >= amax {
            break;
        }
        let mut next = vec![0u128; amax + 1];
        for (prefix_sum, count) in dp.iter().copied().enumerate() {
            if count == 0 || prefix_sum + 1 >= amax {
                continue;
            }
            let max_a = min(
                amax - 1 - prefix_sum,
                limits[next_len].saturating_sub(prefix_sum),
            );
            for a in 1..=max_a {
                next[prefix_sum + a] += count;
            }
        }
        dp = next;
    }

    total
}

impl Scanner {
    fn new(config: Config) -> Self {
        let mut powers2 = vec![1u128; config.amax + 2];
        for i in 1..powers2.len() {
            powers2[i] = powers2[i - 1] << 1;
        }
        let mut powers3 = vec![1u128; config.amax + 2];
        for i in 1..powers3.len() {
            powers3[i] = powers3[i - 1] * 3;
        }
        let max_solvent_sum = powers3
            .iter()
            .map(|value| 127usize - value.leading_zeros() as usize)
            .collect::<Vec<_>>();

        Self {
            by_a: vec![ByA::default(); config.amax + 1],
            config,
            powers2,
            powers3,
            max_solvent_sum,
            start_time: Instant::now(),
            progress_counter: None,
            total_words: 0,
            contractive_words: 0,
            first_contractivity_words: 0,
            all_twos_zero_margins: 0,
            nontrivial_zero_margins: 0,
            negative_margins: 0,
            theta_buckets: vec![
                ("0", 0),
                ("1", 0),
                ("2", 0),
                ("3", 0),
                ("4", 0),
                ("5", 0),
                ("6-10", 0),
                ("11-100", 0),
                ("101-1000", 0),
                (">1000", 0),
            ],
            rho_small_counts: vec![
                ("rho_le_3", 3, 0),
                ("rho_le_5", 5, 0),
                ("rho_le_7", 7, 0),
                ("rho_le_15", 15, 0),
                ("rho_le_31", 31, 0),
                ("rho_le_63", 63, 0),
                ("rho_le_127", 127, 0),
                ("rho_le_255", 255, 0),
                ("rho_le_511", 511, 0),
                ("rho_le_1023", 1023, 0),
            ],
            rho_slack_buckets: vec![
                ("0", 0),
                ("1", 0),
                ("2", 0),
                ("3", 0),
                ("4", 0),
                ("5-8", 0),
                ("9-16", 0),
                (">16", 0),
            ],
            near_rows: Vec::new(),
            prediction_rows: Vec::new(),
            small_rho_rows: Vec::new(),
            prediction_match_count: 0,
            min_nontrivial_margin: None,
            min_nontrivial_relative_gap: None,
            max_theta_candidate_row: None,
        }
    }

    fn scan(&mut self) {
        let mut prefix = Vec::<u16>::new();
        self.recurse(&mut prefix, 0, 0);
        self.finish_sort();
    }

    fn scan_parallel(&mut self) {
        let split_depth = min(self.config.split_depth, self.config.amax);
        let mut tasks = Vec::<Task>::new();
        let mut prefix = Vec::<u16>::new();
        self.collect_tasks(&mut prefix, 0, 0, split_depth, &mut tasks);

        eprintln!(
            "[lock2-scan] parallel threads={} split_depth={} tasks={} shallow_rows={}",
            self.config.threads,
            split_depth,
            tasks.len(),
            self.total_words
        );

        if tasks.is_empty() {
            self.finish_sort();
            return;
        }

        let progress_counter = Arc::new(AtomicU64::new(self.total_words));
        let queue = Arc::new(Mutex::new(tasks));
        let mut handles = Vec::new();

        for _ in 0..self.config.threads {
            let queue = Arc::clone(&queue);
            let progress_counter = Arc::clone(&progress_counter);
            let config = self.config.clone();
            let start_time = self.start_time;
            handles.push(thread::spawn(move || {
                let mut worker = Scanner::new(config);
                worker.start_time = start_time;
                worker.progress_counter = Some(progress_counter);
                loop {
                    let task = {
                        let mut tasks = queue.lock().expect("task queue");
                        tasks.pop()
                    };
                    let Some(task) = task else {
                        break;
                    };
                    let mut prefix = task.prefix;
                    worker.recurse(&mut prefix, task.prefix_sum, task.prefix_b);
                }
                worker
            }));
        }

        for handle in handles {
            let worker = handle.join().expect("worker thread");
            self.merge_from(worker);
        }

        self.finish_sort();
    }

    fn finish_sort(&mut self) {
        self.near_rows
            .sort_by(|a, b| a.relative_gap.partial_cmp(&b.relative_gap).unwrap());
        self.prediction_rows
            .sort_by(|a, b| b.theta_over_rho.partial_cmp(&a.theta_over_rho).unwrap());
        self.small_rho_rows
            .sort_by(|a, b| (a.rho, a.a_sum, a.k).cmp(&(b.rho, b.a_sum, b.k)));
    }

    fn collect_tasks(
        &mut self,
        prefix: &mut Vec<u16>,
        prefix_sum: usize,
        prefix_b: u128,
        split_depth: usize,
        tasks: &mut Vec<Task>,
    ) {
        if prefix.len() >= split_depth {
            tasks.push(Task {
                prefix: prefix.clone(),
                prefix_sum,
                prefix_b,
            });
            return;
        }

        let prefix_len = prefix.len();
        let final_len = prefix_len + 1;
        if final_len <= self.config.amax {
            let min_final_a = max(prefix_sum + 1, self.max_solvent_sum[final_len] + 1);
            for final_a_sum in min_final_a..=self.config.amax {
                let final_a = final_a_sum - prefix_sum;
                let final_b = 3 * prefix_b + self.powers2[prefix_sum];
                prefix.push(final_a as u16);
                self.process_word(prefix, final_b);
                prefix.pop();
            }
        }

        let next_len = prefix_len + 1;
        if next_len >= self.config.amax || prefix_sum + 1 >= self.config.amax {
            return;
        }
        let max_a = min(
            self.config.amax - 1 - prefix_sum,
            self.max_solvent_sum[next_len].saturating_sub(prefix_sum),
        );
        for a in 1..=max_a {
            let next_b = 3 * prefix_b + self.powers2[prefix_sum];
            prefix.push(a as u16);
            self.collect_tasks(prefix, prefix_sum + a, next_b, split_depth, tasks);
            prefix.pop();
        }
    }

    fn recurse(&mut self, prefix: &mut Vec<u16>, prefix_sum: usize, prefix_b: u128) {
        let prefix_len = prefix.len();
        let final_len = prefix_len + 1;
        if final_len <= self.config.amax {
            let min_final_a = max(prefix_sum + 1, self.max_solvent_sum[final_len] + 1);
            for final_a_sum in min_final_a..=self.config.amax {
                let final_a = final_a_sum - prefix_sum;
                let final_b = 3 * prefix_b + self.powers2[prefix_sum];
                prefix.push(final_a as u16);
                self.process_word(prefix, final_b);
                prefix.pop();
            }
        }

        let next_len = prefix_len + 1;
        if next_len >= self.config.amax || prefix_sum + 1 >= self.config.amax {
            return;
        }
        let max_a = min(
            self.config.amax - 1 - prefix_sum,
            self.max_solvent_sum[next_len].saturating_sub(prefix_sum),
        );
        for a in 1..=max_a {
            let next_b = 3 * prefix_b + self.powers2[prefix_sum];
            prefix.push(a as u16);
            self.recurse(prefix, prefix_sum + a, next_b);
            prefix.pop();
        }
    }

    fn process_word(&mut self, word: &[u16], b: u128) {
        let row = make_row(word, b, &self.powers2, &self.powers3);
        self.total_words += 1;
        let progress_rows = if let Some(counter) = &self.progress_counter {
            counter.fetch_add(1, Ordering::Relaxed) + 1
        } else {
            self.total_words
        };
        self.maybe_log_progress(progress_rows, &row);
        self.contractive_words += 1;
        self.first_contractivity_words += 1;
        let by_a = &mut self.by_a[row.a_sum];
        by_a.contractive += 1;
        by_a.first_contractivity += 1;

        if row.margin == 0 {
            if row.is_all_twos {
                self.all_twos_zero_margins += 1;
            } else {
                self.nontrivial_zero_margins += 1;
            }
        }

        if !row.is_all_twos {
            if self
                .min_nontrivial_margin
                .as_ref()
                .map_or(true, |current| row.margin < current.margin)
            {
                self.min_nontrivial_margin = Some(row.clone());
            }
            if self
                .min_nontrivial_relative_gap
                .as_ref()
                .map_or(true, |current| row.relative_gap < current.relative_gap)
            {
                self.min_nontrivial_relative_gap = Some(row.clone());
            }
            consider_near(&mut self.near_rows, row.clone(), self.config.top_n);
        }

        count_theta_bucket(&mut self.theta_buckets, row.theta_candidate_odd_count);
        if self
            .max_theta_candidate_row
            .as_ref()
            .map_or(true, |current| {
                row.theta_candidate_odd_count > current.theta_candidate_odd_count
            })
        {
            self.max_theta_candidate_row = Some(row.clone());
        }
        count_rho_slack_bucket(&mut self.rho_slack_buckets, row.rho_bit_slack);
        for (_, limit, count) in self.rho_small_counts.iter_mut() {
            if row.rho <= *limit {
                *count += 1;
            }
        }
        if row.rho <= 1023 {
            self.small_rho_rows.push(row.clone());
        }

        if by_a.min_rho == 0 || row.rho < by_a.min_rho {
            by_a.min_rho = row.rho;
            by_a.min_rho_word = row.word.clone();
        }
        if row.theta_candidate_odd_count > by_a.max_theta_candidate_count {
            by_a.max_theta_candidate_count = row.theta_candidate_odd_count;
            by_a.max_theta_candidate_word = row.word.clone();
        }
        if row.theta_over_rho > by_a.max_theta_over_rho {
            by_a.max_theta_over_rho = row.theta_over_rho;
            by_a.max_theta_over_rho_word = row.word.clone();
        }
        if row.candidate_to_rho_rank_ratio > by_a.max_candidate_to_rho_rank_ratio {
            by_a.max_candidate_to_rho_rank_ratio = row.candidate_to_rho_rank_ratio;
            by_a.max_candidate_to_rho_rank_word = row.word.clone();
        }

        if self.prediction_matches(&row) {
            self.prediction_match_count += 1;
            consider_prediction(&mut self.prediction_rows, row, self.config.prediction_top_n);
        }
    }

    fn merge_from(&mut self, mut other: Scanner) {
        self.total_words += other.total_words;
        self.contractive_words += other.contractive_words;
        self.first_contractivity_words += other.first_contractivity_words;
        self.all_twos_zero_margins += other.all_twos_zero_margins;
        self.nontrivial_zero_margins += other.nontrivial_zero_margins;
        self.negative_margins += other.negative_margins;
        self.prediction_match_count += other.prediction_match_count;

        for (idx, (_, count)) in other.theta_buckets.iter().enumerate() {
            self.theta_buckets[idx].1 += count;
        }
        for (idx, (_, _, count)) in other.rho_small_counts.iter().enumerate() {
            self.rho_small_counts[idx].2 += count;
        }
        for (idx, (_, count)) in other.rho_slack_buckets.iter().enumerate() {
            self.rho_slack_buckets[idx].1 += count;
        }

        for (idx, row) in other.by_a.iter().enumerate() {
            let target = &mut self.by_a[idx];
            target.contractive += row.contractive;
            target.first_contractivity += row.first_contractivity;
            if row.min_rho != 0 && (target.min_rho == 0 || row.min_rho < target.min_rho) {
                target.min_rho = row.min_rho;
                target.min_rho_word = row.min_rho_word.clone();
            }
            if row.max_theta_candidate_count > target.max_theta_candidate_count {
                target.max_theta_candidate_count = row.max_theta_candidate_count;
                target.max_theta_candidate_word = row.max_theta_candidate_word.clone();
            }
            if row.max_theta_over_rho > target.max_theta_over_rho {
                target.max_theta_over_rho = row.max_theta_over_rho;
                target.max_theta_over_rho_word = row.max_theta_over_rho_word.clone();
            }
            if row.max_candidate_to_rho_rank_ratio > target.max_candidate_to_rho_rank_ratio {
                target.max_candidate_to_rho_rank_ratio = row.max_candidate_to_rho_rank_ratio;
                target.max_candidate_to_rho_rank_word = row.max_candidate_to_rho_rank_word.clone();
            }
        }

        for row in other.near_rows.drain(..) {
            consider_near(&mut self.near_rows, row, self.config.top_n);
        }
        for row in other.prediction_rows.drain(..) {
            consider_prediction(&mut self.prediction_rows, row, self.config.prediction_top_n);
        }
        self.small_rho_rows.append(&mut other.small_rho_rows);

        if let Some(row) = other.min_nontrivial_margin.take() {
            if self
                .min_nontrivial_margin
                .as_ref()
                .map_or(true, |current| row.margin < current.margin)
            {
                self.min_nontrivial_margin = Some(row);
            }
        }
        if let Some(row) = other.min_nontrivial_relative_gap.take() {
            if self
                .min_nontrivial_relative_gap
                .as_ref()
                .map_or(true, |current| row.relative_gap < current.relative_gap)
            {
                self.min_nontrivial_relative_gap = Some(row);
            }
        }
        if let Some(row) = other.max_theta_candidate_row.take() {
            if self
                .max_theta_candidate_row
                .as_ref()
                .map_or(true, |current| {
                    row.theta_candidate_odd_count > current.theta_candidate_odd_count
                })
            {
                self.max_theta_candidate_row = Some(row);
            }
        }
    }

    fn prediction_matches(&self, row: &Row) -> bool {
        let knobs_enabled = self.config.predict_rho_slack_min.is_some()
            || self.config.predict_theta_candidates_min.is_some()
            || self.config.predict_theta_over_rho_min.is_some();
        if !knobs_enabled {
            return false;
        }
        if let Some(limit) = self.config.predict_rho_slack_min {
            if row.rho_bit_slack < limit {
                return false;
            }
        }
        if let Some(limit) = self.config.predict_theta_candidates_min {
            if row.theta_candidate_odd_count < limit {
                return false;
            }
        }
        if let Some(limit) = self.config.predict_theta_over_rho_min {
            if row.theta_over_rho < limit {
                return false;
            }
        }
        true
    }

    fn maybe_log_progress(&self, progress_rows: u64, row: &Row) {
        if self.config.progress_every == 0 || progress_rows % self.config.progress_every != 0 {
            return;
        }
        let elapsed = self.start_time.elapsed().as_secs_f64();
        let rate = if elapsed > 0.0 {
            progress_rows as f64 / elapsed
        } else {
            0.0
        };
        let percent = if self.config.total_expected_words > 0 {
            progress_rows as f64 * 100.0 / self.config.total_expected_words as f64
        } else {
            0.0
        };
        let remaining = self
            .config
            .total_expected_words
            .saturating_sub(progress_rows as u128);
        let eta_seconds = if rate > 0.0 {
            remaining as f64 / rate
        } else {
            0.0
        };
        eprintln!(
            "[lock2-scan] rows={} total={} progress={:.3}% elapsed={:.1}s eta={:.1}s rate={:.0}/s current_A={} current_k={} current_rho={} current_margin={} current_theta_over_rho={:.12}",
            progress_rows,
            self.config.total_expected_words,
            percent,
            elapsed,
            eta_seconds,
            rate,
            row.a_sum,
            row.k,
            row.rho,
            row.margin,
            row.theta_over_rho
        );
    }

    fn path(&self, kind: &str, extension: &str) -> PathBuf {
        self.config.out_dir.join(format!(
            "lock2_{}_Amax{}_{}.{}",
            kind, self.config.amax, self.config.stamp, extension
        ))
    }

    fn write_outputs(&self) {
        write_summary(self.path("summary", "json"), self);
        write_rows(self.path("near_failures", "csv"), &self.near_rows, false);
        write_theta_buckets(self.path("theta_buckets", "csv"), &self.theta_buckets);
        write_rows(self.path("small_rho", "csv"), &self.small_rho_rows, true);
        write_by_a(self.path("by_A_threats", "csv"), &self.by_a);
        if !self.prediction_rows.is_empty() {
            write_rows(
                self.path("predictions", "csv"),
                &self.prediction_rows,
                false,
            );
        }
    }

    fn print_summary(&self) {
        println!("Lock 2 Rust first-contractivity scan");
        println!("Amax={}", self.config.amax);
        println!("expected_words={}", self.config.total_expected_words);
        println!("threads={}", self.config.threads);
        println!("split_depth={}", self.config.split_depth);
        println!(
            "elapsed_seconds={:.3}",
            self.start_time.elapsed().as_secs_f64()
        );
        println!("contractive_words={}", self.contractive_words);
        println!(
            "first_contractivity_words={}",
            self.first_contractivity_words
        );
        println!("all_twos_zero_margins={}", self.all_twos_zero_margins);
        println!("nontrivial_zero_margins={}", self.nontrivial_zero_margins);
        println!("negative_margins={}", self.negative_margins);
        println!(
            "lock2_holds_in_scan={}",
            self.negative_margins == 0 && self.nontrivial_zero_margins == 0
        );
        if let Some(row) = &self.min_nontrivial_relative_gap {
            println!(
                "worst_nontrivial_theta_over_rho word=({}) A={} k={} rho={} theta/rho={:.12} margin={}",
                row.word, row.a_sum, row.k, row.rho, row.theta_over_rho, row.margin
            );
        }
        if let Some(row) = &self.max_theta_candidate_row {
            println!(
                "max_theta_candidates={} word=({}) A={} k={} rho={}",
                row.theta_candidate_odd_count, row.word, row.a_sum, row.k, row.rho
            );
        }
        if self.config.predict_rho_slack_min.is_some()
            || self.config.predict_theta_candidates_min.is_some()
            || self.config.predict_theta_over_rho_min.is_some()
        {
            println!("prediction_match_count={}", self.prediction_match_count);
            for row in self.prediction_rows.iter().take(10) {
                println!(
                    "prediction word=({}) A={} k={} rho={} theta/rho={:.12} candidates={} slack={}",
                    row.word,
                    row.a_sum,
                    row.k,
                    row.rho,
                    row.theta_over_rho,
                    row.theta_candidate_odd_count,
                    row.rho_bit_slack
                );
            }
        }
    }
}

fn make_row(word: &[u16], b: u128, powers2: &[u128], powers3: &[u128]) -> Row {
    let k = word.len();
    let a_sum: usize = word.iter().map(|&a| a as usize).sum();
    let theta_den = powers2[a_sum] - powers3[k];
    let rho = rho_for_word(a_sum, k, b, powers2, powers3);
    let margin = theta_den * rho - b;
    let theta_float = b as f64 / theta_den as f64;
    let threshold_gap_float = margin as f64 / theta_den as f64;
    let relative_gap = threshold_gap_float / rho as f64;
    let normalized_margin = margin as f64 / powers2[a_sum] as f64;
    let theta_candidate_odd_count = ((b / theta_den) + 1) / 2;
    let rho_rank = (rho + 1) / 2;
    let theta_over_rho = theta_float / rho as f64;
    let candidate_to_rho_rank_ratio = if rho_rank == 0 {
        0.0
    } else {
        theta_candidate_odd_count as f64 / rho_rank as f64
    };

    let mut count_ones = 0usize;
    let mut count_twos = 0usize;
    let mut count_ge3 = 0usize;
    for &a in word {
        if a == 1 {
            count_ones += 1;
        } else if a == 2 {
            count_twos += 1;
        } else {
            count_ge3 += 1;
        }
    }
    let (primitive_period, primitive_repetitions) = primitive_period(word);

    Row {
        word: word_to_string(word),
        k,
        a_sum,
        b,
        rho,
        theta_den,
        theta_float,
        margin,
        threshold_gap_float,
        relative_gap,
        normalized_margin,
        theta_candidate_odd_count,
        rho_rank,
        theta_over_rho,
        candidate_to_rho_rank_ratio,
        rho_bit_slack: (a_sum as i32 + 1) - (128 - rho.leading_zeros() as i32),
        is_all_twos: word.iter().all(|&a| a == 2),
        first_contractivity_index: k,
        delta_from_all_twos: word.iter().map(|&a| (a as i32 - 2).abs() as u64).sum(),
        count_ones,
        count_twos,
        count_ge3,
        max_run_1: max_run(word, |a| a == 1),
        max_run_2: max_run(word, |a| a == 2),
        max_run_ge3: max_run(word, |a| a >= 3),
        primitive_period,
        primitive_repetitions,
    }
}

fn rho_for_word(a_sum: usize, k: usize, b: u128, powers2: &[u128], powers3: &[u128]) -> u128 {
    let bits = a_sum + 1;
    let modulus = powers2[bits];
    let mask = modulus - 1;
    let n = powers3[k] & mask;
    let inv = inverse_mod_power_two(n, bits);
    ((powers2[a_sum] + modulus - (b & mask)) * inv) & mask
}

fn inverse_mod_power_two(n: u128, bits: usize) -> u128 {
    let mask = (1u128 << bits) - 1;
    let mut inv = 1u128;
    let mut precision = 1usize;
    while precision < bits {
        inv = inv.wrapping_mul(2u128.wrapping_sub(n.wrapping_mul(inv))) & mask;
        precision *= 2;
    }
    inv & mask
}

fn max_run<F: Fn(u16) -> bool>(word: &[u16], pred: F) -> usize {
    let mut best = 0usize;
    let mut current = 0usize;
    for &a in word {
        if pred(a) {
            current += 1;
            best = max(best, current);
        } else {
            current = 0;
        }
    }
    best
}

fn primitive_period(word: &[u16]) -> (usize, usize) {
    for period in 1..=word.len() {
        if word.len() % period != 0 {
            continue;
        }
        let mut ok = true;
        for i in 0..word.len() {
            if word[i] != word[i % period] {
                ok = false;
                break;
            }
        }
        if ok {
            return (period, word.len() / period);
        }
    }
    (word.len(), 1)
}

fn consider_near(rows: &mut Vec<Row>, row: Row, top_n: usize) {
    if top_n == 0 {
        return;
    }
    if rows.len() < top_n {
        rows.push(row);
        return;
    }
    let mut worst_idx = 0usize;
    let mut worst_gap = rows[0].relative_gap;
    for (idx, existing) in rows.iter().enumerate().skip(1) {
        if existing.relative_gap > worst_gap {
            worst_idx = idx;
            worst_gap = existing.relative_gap;
        }
    }
    if row.relative_gap < worst_gap {
        rows[worst_idx] = row;
    }
}

fn consider_prediction(rows: &mut Vec<Row>, row: Row, top_n: usize) {
    if top_n == 0 {
        return;
    }
    if rows.len() < top_n {
        rows.push(row);
        return;
    }
    let mut worst_idx = 0usize;
    let mut worst_score = rows[0].theta_over_rho;
    for (idx, existing) in rows.iter().enumerate().skip(1) {
        if existing.theta_over_rho < worst_score {
            worst_idx = idx;
            worst_score = existing.theta_over_rho;
        }
    }
    if row.theta_over_rho > worst_score {
        rows[worst_idx] = row;
    }
}

fn count_theta_bucket(buckets: &mut [(&'static str, u64)], count: u128) {
    let label = if count <= 5 {
        match count {
            0 => "0",
            1 => "1",
            2 => "2",
            3 => "3",
            4 => "4",
            _ => "5",
        }
    } else if count <= 10 {
        "6-10"
    } else if count <= 100 {
        "11-100"
    } else if count <= 1000 {
        "101-1000"
    } else {
        ">1000"
    };
    for (bucket, value) in buckets {
        if *bucket == label {
            *value += 1;
            return;
        }
    }
}

fn count_rho_slack_bucket(buckets: &mut [(&'static str, u64)], slack: i32) {
    let label = if slack <= 4 {
        match slack {
            0 => "0",
            1 => "1",
            2 => "2",
            3 => "3",
            _ => "4",
        }
    } else if slack <= 8 {
        "5-8"
    } else if slack <= 16 {
        "9-16"
    } else {
        ">16"
    };
    for (bucket, value) in buckets {
        if *bucket == label {
            *value += 1;
            return;
        }
    }
}

fn write_summary(path: PathBuf, scanner: &Scanner) {
    let mut file = BufWriter::new(File::create(path).expect("summary file"));
    writeln!(file, "{{").unwrap();
    writeln!(file, "  \"Amax\": {},", scanner.config.amax).unwrap();
    writeln!(file, "  \"implementation\": \"rust-u128\",").unwrap();
    writeln!(file, "  \"first_contractivity_only\": true,").unwrap();
    writeln!(
        file,
        "  \"expected_words\": {},",
        scanner.config.total_expected_words
    )
    .unwrap();
    writeln!(file, "  \"threads\": {},", scanner.config.threads).unwrap();
    writeln!(file, "  \"split_depth\": {},", scanner.config.split_depth).unwrap();
    writeln!(
        file,
        "  \"elapsed_seconds\": {},",
        scanner.start_time.elapsed().as_secs_f64()
    )
    .unwrap();
    writeln!(
        file,
        "  \"contractive_words\": {},",
        scanner.contractive_words
    )
    .unwrap();
    writeln!(
        file,
        "  \"first_contractivity_words\": {},",
        scanner.first_contractivity_words
    )
    .unwrap();
    writeln!(
        file,
        "  \"all_twos_zero_margins\": {},",
        scanner.all_twos_zero_margins
    )
    .unwrap();
    writeln!(
        file,
        "  \"nontrivial_zero_margins\": {},",
        scanner.nontrivial_zero_margins
    )
    .unwrap();
    writeln!(
        file,
        "  \"negative_margins\": {},",
        scanner.negative_margins
    )
    .unwrap();
    writeln!(
        file,
        "  \"lock2_holds_in_scan\": {},",
        scanner.negative_margins == 0 && scanner.nontrivial_zero_margins == 0
    )
    .unwrap();
    if let Some(row) = &scanner.min_nontrivial_relative_gap {
        writeln!(
            file,
            "  \"min_nontrivial_relative_gap\": {{\"word\":\"{}\", \"A\":{}, \"k\":{}, \"rho\":{}, \"theta_over_rho\":{}, \"margin\":{}}},",
            row.word, row.a_sum, row.k, row.rho, row.theta_over_rho, row.margin
        )
        .unwrap();
    }
    if let Some(row) = &scanner.max_theta_candidate_row {
        writeln!(
            file,
            "  \"max_theta_candidate_odd_count\": {},",
            row.theta_candidate_odd_count
        )
        .unwrap();
        writeln!(
            file,
            "  \"max_theta_candidate_odd_count_row\": {{\"word\":\"{}\", \"A\":{}, \"k\":{}, \"rho\":{}}},",
            row.word, row.a_sum, row.k, row.rho
        )
        .unwrap();
    }
    writeln!(
        file,
        "  \"prediction_match_count\": {}",
        scanner.prediction_match_count
    )
    .unwrap();
    writeln!(file, "}}").unwrap();
}

fn write_rows(path: PathBuf, rows: &[Row], small_rho: bool) {
    let mut file = BufWriter::new(File::create(path).expect("row csv"));
    write_row_header(&mut file, small_rho);
    for row in rows {
        write_row(&mut file, row, small_rho);
    }
}

fn write_row_header(file: &mut BufWriter<File>, small_rho: bool) {
    write!(
        file,
        "word,k,A,B,rho,theta_num,theta_den,theta_float,margin,threshold_gap_float,relative_gap,normalized_margin,theta_candidate_odd_count,rho_rank,theta_over_rho,candidate_to_rho_rank_ratio,rho_bit_slack,is_all_twos,first_contractivity_index,delta_from_all_twos,count_ones,count_twos,count_ge3,max_run_1,max_run_2,max_run_ge3,primitive_period,primitive_repetitions"
    )
    .unwrap();
    if small_rho {
        write!(
            file,
            ",rho_orbit_prefix,rho_follows_word,congruence_valid,image_at_rho,image_at_rho_is_odd,image_at_rho_below_rho"
        )
        .unwrap();
    }
    writeln!(file).unwrap();
}

fn write_row(file: &mut BufWriter<File>, row: &Row, small_rho: bool) {
    write!(
        file,
        "\"{}\",{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
        row.word,
        row.k,
        row.a_sum,
        row.b,
        row.rho,
        row.b,
        row.theta_den,
        row.theta_float,
        row.margin,
        row.threshold_gap_float,
        row.relative_gap,
        row.normalized_margin,
        row.theta_candidate_odd_count,
        row.rho_rank,
        row.theta_over_rho,
        row.candidate_to_rho_rank_ratio,
        row.rho_bit_slack,
        row.is_all_twos,
        row.first_contractivity_index,
        row.delta_from_all_twos,
        row.count_ones,
        row.count_twos,
        row.count_ge3,
        row.max_run_1,
        row.max_run_2,
        row.max_run_ge3,
        row.primitive_period,
        row.primitive_repetitions
    )
    .unwrap();
    if small_rho {
        let word = parse_word(&row.word);
        let orbit = exponent_prefix(row.rho, row.k);
        let image_num = power3(row.k) * row.rho + row.b;
        let image_den = 1u128 << row.a_sum;
        let image = image_num / image_den;
        write!(
            file,
            ",\"{}\",{},{},{},{},{}",
            word_to_string(&orbit),
            orbit == word,
            ((power3(row.k) * row.rho + row.b - (1u128 << row.a_sum)) % (1u128 << (row.a_sum + 1)))
                == 0,
            image,
            image_num % image_den == 0 && image % 2 == 1,
            image_num % image_den == 0 && image < row.rho
        )
        .unwrap();
    }
    writeln!(file).unwrap();
}

fn write_theta_buckets(path: PathBuf, buckets: &[(&'static str, u64)]) {
    let mut file = BufWriter::new(File::create(path).expect("theta csv"));
    writeln!(file, "candidate_odd_count_bucket,words").unwrap();
    for (bucket, count) in buckets {
        if *count > 0 {
            writeln!(file, "{},{}", bucket, count).unwrap();
        }
    }
}

fn write_by_a(path: PathBuf, rows: &[ByA]) {
    let mut file = BufWriter::new(File::create(path).expect("by A csv"));
    writeln!(file, "A,contractive,first_contractivity,min_rho,min_rho_word,max_theta_candidate_count,max_theta_candidate_word,max_theta_over_rho,max_theta_over_rho_word,max_candidate_to_rho_rank_ratio,max_candidate_to_rho_rank_word").unwrap();
    for (a, row) in rows.iter().enumerate() {
        writeln!(
            file,
            "{},{},{},{},\"{}\",{},\"{}\",{},\"{}\",{},\"{}\"",
            a,
            row.contractive,
            row.first_contractivity,
            row.min_rho,
            row.min_rho_word,
            row.max_theta_candidate_count,
            row.max_theta_candidate_word,
            row.max_theta_over_rho,
            row.max_theta_over_rho_word,
            row.max_candidate_to_rho_rank_ratio,
            row.max_candidate_to_rho_rank_word
        )
        .unwrap();
    }
}

fn parse_word(s: &str) -> Vec<u16> {
    if s.is_empty() {
        return Vec::new();
    }
    s.split(',').map(|part| part.parse().unwrap()).collect()
}

fn word_to_string(word: &[u16]) -> String {
    word.iter()
        .map(|value| value.to_string())
        .collect::<Vec<_>>()
        .join(",")
}

fn exponent_prefix(mut x: u128, len: usize) -> Vec<u16> {
    let mut out = Vec::new();
    for _ in 0..len {
        let y = 3 * x + 1;
        let a = y.trailing_zeros() as u16;
        out.push(a);
        x = y >> a;
    }
    out
}

fn power3(k: usize) -> u128 {
    let mut out = 1u128;
    for _ in 0..k {
        out *= 3;
    }
    out
}
