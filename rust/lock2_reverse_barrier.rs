use std::cmp::{min, Ordering};
use std::collections::HashSet;
use std::env;
use std::fs::{create_dir_all, File};
use std::io::{BufWriter, Write};
use std::path::PathBuf;
use std::time::{Instant, SystemTime, UNIX_EPOCH};

#[derive(Clone, Debug, Eq, Hash, PartialEq)]
struct Big {
    limbs: Vec<u64>,
}

#[derive(Clone)]
struct Config {
    amax: usize,
    out_dir: PathBuf,
    stamp: String,
    include_equal: bool,
    target_num: u64,
    target_den: u64,
    top_n: usize,
    progress_every_a: usize,
    slow_pair_seconds: f64,
    residue_mod_power: usize,
    memo_exact_k: usize,
    failed_memo_limit: usize,
}

#[derive(Clone)]
struct Row {
    word: Vec<u16>,
    a_sum: usize,
    k: usize,
    b: Big,
    d: Big,
    rho: u64,
    score_den: Big,
    comparison: &'static str,
    margin: Big,
    verified: bool,
    verification_notes: String,
    image: Big,
    rho_bit_slack: i32,
    theta_candidate_odd_count: Big,
    count_1: usize,
    count_2: usize,
    count_ge3: usize,
    max_run_1: usize,
    max_run_2: usize,
    prefix5: String,
    suffix5: String,
    repeated_blocks: String,
    orbit_prefix: String,
    rho_mod_3: u64,
    rho_mod_5: u64,
    rho_mod_7: u64,
    rho_mod_11: u64,
    rho_mod_13: u64,
    extends_a54: bool,
    has_a54_prefix: bool,
    has_a54_suffix: bool,
}

struct Stats {
    ak_pairs: u64,
    rho_candidates: u128,
    b_candidates: u128,
    reconstructed_words: u128,
    memo_hits: u128,
    memo_misses: u128,
    memo_entries: usize,
    pruned_by_memo: u128,
    deepest_recursion: usize,
    largest_remaining_a_sum: usize,
    largest_remaining_b_bits: usize,
    zero_reconstruction_pairs: u64,
    slow_pairs: u64,
    pair_profiles: Vec<PairProfile>,
    hits: Vec<Row>,
    top_score: Vec<Row>,
    top_rho_slack: Vec<Row>,
    top_theta_candidates: Vec<Row>,
    top_margin_proximity: Vec<Row>,
    critical_failures: u64,
    runtime_seconds: f64,
}

#[derive(Clone, Debug, Eq, Hash, PartialEq)]
struct ReconstructState {
    a_sum: usize,
    k: usize,
    b: Big,
}

#[derive(Clone)]
struct PairProfile {
    a_sum: usize,
    k: usize,
    elapsed_seconds: f64,
    rho_candidates: u128,
    b_candidates: u128,
    reconstructed_words: u128,
    hits: usize,
    memo_hits: u128,
    memo_misses: u128,
    pruned_by_memo: u128,
    deepest_recursion: usize,
    largest_remaining_a_sum: usize,
    largest_remaining_b_bits: usize,
    zero_reconstruction_pair: bool,
    slow_pair: bool,
    failed_memo_entries: usize,
}

#[derive(Clone, Default)]
struct ReconstructMetrics {
    memo_hits: u128,
    memo_misses: u128,
    pruned_by_memo: u128,
    deepest_recursion: usize,
    largest_remaining_a_sum: usize,
    largest_remaining_b_bits: usize,
}

const A54_WORD: [u16; 34] = [
    1, 1, 1, 1, 1, 4, 1, 2, 1, 1, 2, 1, 1, 1, 2, 3, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 3, 1, 1, 1, 4, 2,
    2, 4,
];

fn main() {
    let config = parse_args();
    create_dir_all(&config.out_dir).expect("create out dir");
    let stats = scan(&config);
    write_outputs(&config, &stats);
    print_summary(&config, &stats);
}

fn parse_args() -> Config {
    let mut amax = None;
    let mut out_dir = PathBuf::from("data/runs");
    let mut stamp = None;
    let mut include_equal = true;
    let mut target_num = 48215861999407177u64;
    let mut target_den = 84244659018371145u64;
    let mut top_n = 100usize;
    let mut progress_every_a = 10usize;
    let mut slow_pair_seconds = 5.0f64;
    let mut residue_mod_power = 8usize;
    let mut memo_exact_k = 15usize;
    let mut failed_memo_limit = 1_000_000usize;

    let args: Vec<String> = env::args().collect();
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--Amax" => {
                i += 1;
                amax = Some(args[i].parse().expect("--Amax integer"));
            }
            "--out-dir" => {
                i += 1;
                out_dir = PathBuf::from(&args[i]);
            }
            "--stamp" => {
                i += 1;
                stamp = Some(args[i].clone());
            }
            "--strict" => include_equal = false,
            "--target-num" => {
                i += 1;
                target_num = args[i].parse().expect("--target-num integer");
            }
            "--target-den" => {
                i += 1;
                target_den = args[i].parse().expect("--target-den integer");
            }
            "--target" => {
                i += 1;
                let (n, d) = parse_target(&args[i]);
                target_num = n;
                target_den = d;
            }
            "--top-n" => {
                i += 1;
                top_n = args[i].parse().expect("--top-n integer");
            }
            "--progress-every-a" => {
                i += 1;
                progress_every_a = args[i].parse().expect("--progress-every-a integer");
            }
            "--slow-pair-seconds" => {
                i += 1;
                slow_pair_seconds = args[i].parse().expect("--slow-pair-seconds float");
            }
            "--residue-mod-power" => {
                i += 1;
                residue_mod_power = args[i].parse().expect("--residue-mod-power integer");
            }
            "--memo-exact-k" => {
                i += 1;
                memo_exact_k = args[i].parse().expect("--memo-exact-k integer");
            }
            "--failed-memo-limit" => {
                i += 1;
                failed_memo_limit = args[i].parse().expect("--failed-memo-limit integer");
            }
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

    Config {
        amax: amax.expect("--Amax is required"),
        out_dir,
        stamp,
        include_equal,
        target_num,
        target_den,
        top_n,
        progress_every_a,
        slow_pair_seconds,
        residue_mod_power,
        memo_exact_k,
        failed_memo_limit,
    }
}

fn parse_target(text: &str) -> (u64, u64) {
    if let Some((lhs, rhs)) = text.split_once('/') {
        return (
            lhs.parse().expect("target numerator"),
            rhs.parse().expect("target denominator"),
        );
    }
    if let Some((whole, frac)) = text.split_once('.') {
        let den = 10u64.pow(frac.len() as u32);
        let num = whole.parse::<u64>().expect("target whole") * den
            + frac.parse::<u64>().expect("target fraction");
        let g = gcd(num, den);
        return (num / g, den / g);
    }
    (text.parse().expect("target integer"), 1)
}

fn scan(config: &Config) -> Stats {
    let started = Instant::now();
    let powers2 = powers_big(2, config.amax + 2);
    let powers3 = powers_big(3, config.amax + 2);
    let max_prefix_sum = powers3
        .iter()
        .map(Big::bit_length_floor)
        .collect::<Vec<_>>();
    let (min_b, max_b) = precompute_b_bounds(config.amax, &powers2, &max_prefix_sum);
    let (exact_reachable_b, exact_reachable_entries) =
        precompute_exact_reachable_b(config.amax, config.memo_exact_k, &powers2, &max_prefix_sum);
    let mut failed_reconstruction_memo: HashSet<ReconstructState> = HashSet::new();
    let residue_filter = if config.residue_mod_power == 0 {
        None
    } else {
        let modulus = pow_u64(3, config.residue_mod_power);
        Some((
            modulus,
            precompute_reachable_residues(config.amax, modulus, &max_prefix_sum),
        ))
    };

    let mut stats = Stats {
        ak_pairs: 0,
        rho_candidates: 0,
        b_candidates: 0,
        reconstructed_words: 0,
        memo_hits: 0,
        memo_misses: 0,
        memo_entries: exact_reachable_entries,
        pruned_by_memo: 0,
        deepest_recursion: 0,
        largest_remaining_a_sum: 0,
        largest_remaining_b_bits: 0,
        zero_reconstruction_pairs: 0,
        slow_pairs: 0,
        pair_profiles: Vec::new(),
        hits: Vec::new(),
        top_score: Vec::new(),
        top_rho_slack: Vec::new(),
        top_theta_candidates: Vec::new(),
        top_margin_proximity: Vec::new(),
        critical_failures: 0,
        runtime_seconds: 0.0,
    };

    for a_sum in 1..=config.amax {
        for k in 1..=a_sum {
            let pair_started = Instant::now();
            let pair_rho_before = stats.rho_candidates;
            let pair_b_before = stats.b_candidates;
            let pair_reconstructed_before = stats.reconstructed_words;
            let pair_hits_before = stats.hits.len();
            let pair_memo_hits_before = stats.memo_hits;
            let pair_memo_misses_before = stats.memo_misses;
            let pair_pruned_before = stats.pruned_by_memo;
            let mut pair_deepest_recursion = 0usize;
            let mut pair_largest_remaining_a_sum = 0usize;
            let mut pair_largest_remaining_b_bits = 0usize;
            if powers2[a_sum] <= powers3[k] {
                continue;
            }
            if k > 1 && k - 1 > max_prefix_sum[k - 1] {
                continue;
            }
            stats.ak_pairs += 1;

            let d = powers2[a_sum].sub(&powers3[k]);
            let b_bound = powers3[k - 1].mul_small(k as u64);
            let numerator = b_bound.mul_small(config.target_den);
            let denominator = d.mul_small(config.target_num);
            let rho_max_big = numerator.div_big(&denominator);
            let Some(mut rho_max) = rho_max_big.to_u64() else {
                panic!("rho candidate range exceeded u64 at A={} k={}", a_sum, k);
            };
            if rho_max == 0 {
                continue;
            }
            let modulus = powers2[a_sum + 1].clone();
            if let Some(mod_minus_1) = modulus.sub_one().to_u64() {
                rho_max = min(rho_max, mod_minus_1);
            }

            for rho in (1..=rho_max).step_by(2) {
                stats.rho_candidates += 1;
                let threshold_b = d
                    .mul_small(config.target_num)
                    .mul_small(rho)
                    .div_ceil_small(config.target_den);

                let low = powers3[k].mul_small(rho).low_bits(a_sum + 1);
                let mut residue = powers2[a_sum].add(&modulus).sub(&low);
                if residue >= modulus {
                    residue = residue.sub(&modulus);
                }
                let mut b = if residue.is_zero() {
                    modulus.clone()
                } else {
                    residue
                };
                if b < threshold_b {
                    let diff = threshold_b.sub(&b);
                    let lifts = diff.div_ceil_big(&modulus);
                    b = b.add(&modulus.mul_big(&lifts));
                }
                while b <= b_bound {
                    stats.b_candidates += 1;
                    if let Some((residue_modulus, reachable_residues)) = &residue_filter {
                        if !reachable_residues[a_sum][k].contains(&b.mod_small(*residue_modulus)) {
                            b = b.add(&modulus);
                            continue;
                        }
                    }
                    let mut word_rev = Vec::new();
                    let mut metrics = ReconstructMetrics::default();
                    let _words_found = reverse_reconstruct(
                        a_sum,
                        k,
                        &b,
                        &powers2,
                        &max_prefix_sum,
                        &min_b,
                        &max_b,
                        &exact_reachable_b,
                        residue_filter.as_ref(),
                        &mut failed_reconstruction_memo,
                        config.failed_memo_limit,
                        &mut metrics,
                        &mut word_rev,
                        1,
                        &mut |word| {
                            stats.reconstructed_words += 1;
                            let row = make_row(config, word, a_sum, k, &b, &d, rho);
                            push_top_score(&mut stats.top_score, row.clone(), config.top_n);
                            push_top_rho_slack(&mut stats.top_rho_slack, row.clone(), config.top_n);
                            push_top_theta_candidates(
                                &mut stats.top_theta_candidates,
                                row.clone(),
                                config.top_n,
                            );
                            push_top_margin(
                                &mut stats.top_margin_proximity,
                                row.clone(),
                                config.top_n,
                            );
                            let cmp = compare_score_to_target(
                                &row.b,
                                &row.score_den,
                                config.target_num,
                                config.target_den,
                            );
                            let passes = if config.include_equal {
                                cmp != Ordering::Less
                            } else {
                                cmp == Ordering::Greater
                            };
                            if passes {
                                if !row.verified {
                                    stats.critical_failures += 1;
                                }
                                stats.hits.push(row);
                            }
                        },
                    );
                    stats.memo_hits += metrics.memo_hits;
                    stats.memo_misses += metrics.memo_misses;
                    stats.pruned_by_memo += metrics.pruned_by_memo;
                    stats.deepest_recursion =
                        stats.deepest_recursion.max(metrics.deepest_recursion);
                    stats.largest_remaining_a_sum = stats
                        .largest_remaining_a_sum
                        .max(metrics.largest_remaining_a_sum);
                    stats.largest_remaining_b_bits = stats
                        .largest_remaining_b_bits
                        .max(metrics.largest_remaining_b_bits);
                    pair_deepest_recursion = pair_deepest_recursion.max(metrics.deepest_recursion);
                    pair_largest_remaining_a_sum =
                        pair_largest_remaining_a_sum.max(metrics.largest_remaining_a_sum);
                    pair_largest_remaining_b_bits =
                        pair_largest_remaining_b_bits.max(metrics.largest_remaining_b_bits);
                    b = b.add(&modulus);
                }
            }
            let pair_elapsed = pair_started.elapsed().as_secs_f64();
            let pair_reconstructed_delta = stats.reconstructed_words - pair_reconstructed_before;
            let zero_reconstruction_pair =
                pair_reconstructed_delta == 0 && stats.b_candidates > pair_b_before;
            if zero_reconstruction_pair {
                stats.zero_reconstruction_pairs += 1;
            }
            let slow_pair =
                config.slow_pair_seconds > 0.0 && pair_elapsed >= config.slow_pair_seconds;
            if slow_pair {
                stats.slow_pairs += 1;
                eprintln!(
                    "[lock2-reverse-slow-pair] A={} k={} elapsed={:.1}s rho_candidates_delta={} b_candidates_delta={} reconstructed_delta={} hits_delta={} memo_hits_delta={} memo_misses_delta={} pruned_by_memo_delta={} deepest_recursion={} largest_remaining_A={} largest_remaining_B_bits={} memo_entries={} total_elapsed={:.1}s",
                    a_sum,
                    k,
                    pair_elapsed,
                    stats.rho_candidates - pair_rho_before,
                    stats.b_candidates - pair_b_before,
                    pair_reconstructed_delta,
                    stats.hits.len() - pair_hits_before,
                    stats.memo_hits - pair_memo_hits_before,
                    stats.memo_misses - pair_memo_misses_before,
                    stats.pruned_by_memo - pair_pruned_before,
                    pair_deepest_recursion,
                    pair_largest_remaining_a_sum,
                    pair_largest_remaining_b_bits,
                    exact_reachable_entries,
                    started.elapsed().as_secs_f64()
                );
            }
            stats.pair_profiles.push(PairProfile {
                a_sum,
                k,
                elapsed_seconds: pair_elapsed,
                rho_candidates: stats.rho_candidates - pair_rho_before,
                b_candidates: stats.b_candidates - pair_b_before,
                reconstructed_words: pair_reconstructed_delta,
                hits: stats.hits.len() - pair_hits_before,
                memo_hits: stats.memo_hits - pair_memo_hits_before,
                memo_misses: stats.memo_misses - pair_memo_misses_before,
                pruned_by_memo: stats.pruned_by_memo - pair_pruned_before,
                deepest_recursion: pair_deepest_recursion,
                largest_remaining_a_sum: pair_largest_remaining_a_sum,
                largest_remaining_b_bits: pair_largest_remaining_b_bits,
                zero_reconstruction_pair,
                slow_pair,
                failed_memo_entries: failed_reconstruction_memo.len(),
            });
        }
        if config.progress_every_a > 0
            && (a_sum == config.amax || a_sum % config.progress_every_a == 0)
        {
            let elapsed = started.elapsed().as_secs_f64();
            eprintln!(
                "[lock2-reverse] A={}/{} elapsed={:.1}s ak_pairs={} rho_candidates={} b_candidates={} reconstructed_words={} hits={} critical_failures={}",
                a_sum,
                config.amax,
                elapsed,
                stats.ak_pairs,
                stats.rho_candidates,
                stats.b_candidates,
                stats.reconstructed_words,
                stats.hits.len(),
                stats.critical_failures
            );
        }
    }

    sort_rows_by_score(&mut stats.hits);
    sort_rows_by_score(&mut stats.top_score);
    stats.top_rho_slack.sort_by(|a, b| {
        b.rho_bit_slack
            .cmp(&a.rho_bit_slack)
            .then_with(|| score_cmp(b, a))
    });
    stats.top_theta_candidates.sort_by(|a, b| {
        b.theta_candidate_odd_count
            .cmp(&a.theta_candidate_odd_count)
            .then_with(|| score_cmp(b, a))
    });
    stats
        .top_margin_proximity
        .sort_by(|a, b| a.margin.cmp(&b.margin).then_with(|| score_cmp(b, a)));
    stats.memo_entries = exact_reachable_entries + failed_reconstruction_memo.len();
    stats.runtime_seconds = started.elapsed().as_secs_f64();
    stats
}

fn reverse_reconstruct<F: FnMut(&[u16])>(
    a_sum: usize,
    k: usize,
    b: &Big,
    powers2: &[Big],
    max_prefix_sum: &[usize],
    min_b: &[Vec<Option<Big>>],
    max_b: &[Vec<Option<Big>>],
    exact_reachable_b: &[Vec<Option<HashSet<Big>>>],
    residue_filter: Option<&(u64, Vec<Vec<HashSet<u64>>>)>,
    failed_reconstruction_memo: &mut HashSet<ReconstructState>,
    failed_memo_limit: usize,
    metrics: &mut ReconstructMetrics,
    word_rev: &mut Vec<u16>,
    depth: usize,
    on_word: &mut F,
) -> u128 {
    metrics.deepest_recursion = metrics.deepest_recursion.max(depth);
    metrics.largest_remaining_a_sum = metrics.largest_remaining_a_sum.max(a_sum);
    metrics.largest_remaining_b_bits = metrics.largest_remaining_b_bits.max(b.bit_length());

    let state = ReconstructState {
        a_sum,
        k,
        b: b.clone(),
    };
    if failed_reconstruction_memo.contains(&state) {
        metrics.memo_hits += 1;
        metrics.pruned_by_memo += 1;
        return 0;
    }

    if !state_b_feasible(a_sum, k, b, min_b, max_b) {
        remember_failed(failed_reconstruction_memo, failed_memo_limit, state);
        return 0;
    }
    if let Some(reachable) = &exact_reachable_b[a_sum][k] {
        if reachable.contains(b) {
            metrics.memo_misses += 1;
        } else {
            metrics.memo_hits += 1;
            metrics.pruned_by_memo += 1;
            remember_failed(failed_reconstruction_memo, failed_memo_limit, state);
            return 0;
        }
    } else if let Some((residue_modulus, reachable_residues)) = residue_filter {
        if reachable_residues[a_sum][k].contains(&b.mod_small(*residue_modulus)) {
            metrics.memo_misses += 1;
        } else {
            metrics.memo_hits += 1;
            metrics.pruned_by_memo += 1;
            remember_failed(failed_reconstruction_memo, failed_memo_limit, state);
            return 0;
        }
    }

    if k == 1 {
        if *b == Big::one() && a_sum >= 1 {
            word_rev.push(a_sum as u16);
            let mut word = word_rev.clone();
            word.reverse();
            on_word(&word);
            word_rev.pop();
            return 1;
        }
        remember_failed(failed_reconstruction_memo, failed_memo_limit, state);
        return 0;
    }

    let min_prefix = k - 1;
    let max_prefix = min(a_sum - 1, max_prefix_sum[k - 1]);
    if min_prefix > max_prefix {
        remember_failed(failed_reconstruction_memo, failed_memo_limit, state);
        return 0;
    }

    let mut found = 0u128;
    for prefix_sum in min_prefix..=max_prefix {
        let term = &powers2[prefix_sum];
        if b < term {
            continue;
        }
        let rem = b.sub(term);
        if rem.mod_small(3) != 0 {
            continue;
        }
        let prev_b = rem.div_small(3);
        let last_a = a_sum - prefix_sum;
        word_rev.push(last_a as u16);
        found += reverse_reconstruct(
            prefix_sum,
            k - 1,
            &prev_b,
            powers2,
            max_prefix_sum,
            min_b,
            max_b,
            exact_reachable_b,
            residue_filter,
            failed_reconstruction_memo,
            failed_memo_limit,
            metrics,
            word_rev,
            depth + 1,
            on_word,
        );
        word_rev.pop();
    }

    if found == 0 {
        remember_failed(failed_reconstruction_memo, failed_memo_limit, state);
    }
    found
}

fn remember_failed(
    failed_reconstruction_memo: &mut HashSet<ReconstructState>,
    failed_memo_limit: usize,
    state: ReconstructState,
) {
    if failed_memo_limit == 0 || failed_reconstruction_memo.len() >= failed_memo_limit {
        return;
    }
    failed_reconstruction_memo.insert(state);
}

fn state_b_feasible(
    a_sum: usize,
    k: usize,
    b: &Big,
    min_b: &[Vec<Option<Big>>],
    max_b: &[Vec<Option<Big>>],
) -> bool {
    let Some(lo) = &min_b[a_sum][k] else {
        return false;
    };
    let Some(hi) = &max_b[a_sum][k] else {
        return false;
    };
    b >= lo && b <= hi
}

fn precompute_b_bounds(
    amax: usize,
    powers2: &[Big],
    max_prefix_sum: &[usize],
) -> (Vec<Vec<Option<Big>>>, Vec<Vec<Option<Big>>>) {
    let mut min_b = vec![vec![None; amax + 1]; amax + 1];
    let mut max_b = vec![vec![None; amax + 1]; amax + 1];

    for a in 1..=amax {
        min_b[a][1] = Some(Big::one());
        max_b[a][1] = Some(Big::one());
    }

    for k in 2..=amax {
        for a_sum in k..=amax {
            let max_prefix = min(a_sum - 1, max_prefix_sum[k - 1]);
            if k - 1 > max_prefix {
                continue;
            }
            let mut lo: Option<Big> = None;
            let mut hi: Option<Big> = None;
            for prefix_sum in k - 1..=max_prefix {
                let Some(prev_lo) = &min_b[prefix_sum][k - 1] else {
                    continue;
                };
                let Some(prev_hi) = &max_b[prefix_sum][k - 1] else {
                    continue;
                };
                let term = &powers2[prefix_sum];
                let cand_lo = prev_lo.mul_small(3).add(term);
                let cand_hi = prev_hi.mul_small(3).add(term);
                if lo.as_ref().map_or(true, |current| cand_lo < *current) {
                    lo = Some(cand_lo);
                }
                if hi.as_ref().map_or(true, |current| cand_hi > *current) {
                    hi = Some(cand_hi);
                }
            }
            min_b[a_sum][k] = lo;
            max_b[a_sum][k] = hi;
        }
    }

    (min_b, max_b)
}

fn precompute_exact_reachable_b(
    amax: usize,
    memo_exact_k: usize,
    powers2: &[Big],
    max_prefix_sum: &[usize],
) -> (Vec<Vec<Option<HashSet<Big>>>>, usize) {
    let memo_k = min(memo_exact_k, amax);
    let mut reachable = vec![vec![None; amax + 1]; amax + 1];
    if memo_k == 0 {
        return (reachable, 0);
    }

    let mut entries = 0usize;
    for a in 1..=amax {
        let mut set = HashSet::new();
        set.insert(Big::one());
        entries += set.len();
        reachable[a][1] = Some(set);
    }

    for k in 2..=memo_k {
        for a_sum in k..=amax {
            let max_prefix = min(a_sum - 1, max_prefix_sum[k - 1]);
            if k - 1 > max_prefix {
                continue;
            }
            let mut set = HashSet::new();
            for prefix_sum in k - 1..=max_prefix {
                let Some(prev_set) = &reachable[prefix_sum][k - 1] else {
                    continue;
                };
                let term = &powers2[prefix_sum];
                for prev_b in prev_set {
                    set.insert(prev_b.mul_small(3).add(term));
                }
            }
            if !set.is_empty() {
                entries += set.len();
                reachable[a_sum][k] = Some(set);
            }
        }
    }

    (reachable, entries)
}

fn pow_u64(base: u64, exp: usize) -> u64 {
    let mut value = 1u64;
    for _ in 0..exp {
        value = value.checked_mul(base).expect("residue modulus fits u64");
    }
    value
}

fn precompute_reachable_residues(
    amax: usize,
    residue_modulus: u64,
    max_prefix_sum: &[usize],
) -> Vec<Vec<HashSet<u64>>> {
    let mut pow2_mod = vec![0u64; amax + 1];
    pow2_mod[0] = 1 % residue_modulus;
    for i in 1..=amax {
        pow2_mod[i] = ((pow2_mod[i - 1] as u128 * 2) % residue_modulus as u128) as u64;
    }

    let mut reachable = vec![vec![HashSet::new(); amax + 1]; amax + 1];
    for a in 1..=amax {
        reachable[a][1].insert(1 % residue_modulus);
    }

    for k in 2..=amax {
        for a_sum in k..=amax {
            let max_prefix = min(a_sum - 1, max_prefix_sum[k - 1]);
            if k - 1 > max_prefix {
                continue;
            }
            let mut residues = HashSet::new();
            for prefix_sum in k - 1..=max_prefix {
                for &prev in &reachable[prefix_sum][k - 1] {
                    let next = (3u128 * prev as u128 + pow2_mod[prefix_sum] as u128)
                        % residue_modulus as u128;
                    residues.insert(next as u64);
                }
            }
            reachable[a_sum][k] = residues;
        }
    }

    reachable
}

fn make_row(
    config: &Config,
    word: &[u16],
    a_sum: usize,
    k: usize,
    b: &Big,
    d: &Big,
    rho: u64,
) -> Row {
    let score_den = d.mul_small(rho);
    let cmp = compare_score_to_target(b, &score_den, config.target_num, config.target_den);
    let comparison = match cmp {
        Ordering::Greater => "above",
        Ordering::Equal => "equal",
        Ordering::Less => "below",
    };
    let margin = d.mul_small(rho).sub(b);
    let verification = verify_word(word, a_sum, k, b, d, rho);
    let theta_candidate_odd_count = b.div_big(d).add_small(1).div_small(2);
    let (count_1, count_2, count_ge3) = exponent_counts(word);
    let prefix5 = word_to_string(&word[..min(5, word.len())]);
    let suffix5 = if word.len() <= 5 {
        word_to_string(word)
    } else {
        word_to_string(&word[word.len() - 5..])
    };

    Row {
        word: word.to_vec(),
        a_sum,
        k,
        b: b.clone(),
        d: d.clone(),
        rho,
        score_den,
        comparison,
        margin,
        verified: verification.verified,
        verification_notes: verification.notes,
        image: verification.image,
        rho_bit_slack: (a_sum as i32 + 1) - bit_length_u64(rho) as i32,
        theta_candidate_odd_count,
        count_1,
        count_2,
        count_ge3,
        max_run_1: max_run(word, |a| a == 1),
        max_run_2: max_run(word, |a| a == 2),
        prefix5,
        suffix5,
        repeated_blocks: repeated_blocks(word),
        orbit_prefix: verification.orbit_prefix,
        rho_mod_3: rho % 3,
        rho_mod_5: rho % 5,
        rho_mod_7: rho % 7,
        rho_mod_11: rho % 11,
        rho_mod_13: rho % 13,
        extends_a54: contains_subslice(word, &A54_WORD),
        has_a54_prefix: word.starts_with(&A54_WORD),
        has_a54_suffix: word.ends_with(&A54_WORD),
    }
}

struct Verification {
    verified: bool,
    notes: String,
    image: Big,
    orbit_prefix: String,
}

fn verify_word(word: &[u16], a_sum: usize, k: usize, b: &Big, d: &Big, rho: u64) -> Verification {
    if word.iter().all(|&a| a == 2) {
        return Verification {
            verified: true,
            notes: "trivial_all_twos_equality".to_string(),
            image: Big::from_u64(rho),
            orbit_prefix: word_to_string(&word[..min(20, word.len())]),
        };
    }

    let mut ok = true;
    let mut notes = Vec::new();
    let mut x = Big::from_u64(rho);
    let mut orbit = Vec::new();

    for &expected_a in word {
        let y = x.mul_small(3).add_small(1);
        let actual_a = y.trailing_zeros();
        orbit.push(actual_a as u16);
        if actual_a != expected_a as usize {
            ok = false;
            notes.push(format!(
                "rho_prefix_mismatch_expected_{}_got_{}",
                expected_a, actual_a
            ));
            x = y.shr_bits(actual_a);
            break;
        }
        x = y.shr_bits(actual_a);
    }

    if orbit.len() == word.len() && orbit != word {
        ok = false;
        notes.push("rho_does_not_follow_word".to_string());
    }
    if x.is_even() {
        ok = false;
        notes.push("image_not_odd".to_string());
    }
    if x >= Big::from_u64(rho) {
        ok = false;
        notes.push("image_not_below_rho".to_string());
    }
    if !margin_positive(d, b, rho) {
        ok = false;
        notes.push("margin_not_positive".to_string());
    }
    if !first_contractivity_final(word) {
        ok = false;
        notes.push("first_contractivity_index_not_final".to_string());
    }
    if word.len() != k || word.iter().map(|&a| a as usize).sum::<usize>() != a_sum {
        ok = false;
        notes.push("word_A_or_k_mismatch".to_string());
    }

    Verification {
        verified: ok,
        notes: if notes.is_empty() {
            "ok".to_string()
        } else {
            notes.join("|")
        },
        image: x,
        orbit_prefix: word_to_string(&orbit[..min(20, orbit.len())]),
    }
}

fn first_contractivity_final(word: &[u16]) -> bool {
    let mut a_sum = 0usize;
    let mut pow3 = Big::one();
    for (idx, &a) in word.iter().enumerate() {
        a_sum += a as usize;
        pow3 = pow3.mul_small(3);
        let pow2 = Big::pow2(a_sum);
        if idx + 1 < word.len() {
            if pow2 > pow3 {
                return false;
            }
        } else if pow2 <= pow3 {
            return false;
        }
    }
    true
}

fn margin_positive(d: &Big, b: &Big, rho: u64) -> bool {
    d.mul_small(rho) > *b
}

fn compare_score_to_target(b: &Big, score_den: &Big, target_num: u64, target_den: u64) -> Ordering {
    b.mul_small(target_den)
        .cmp(&score_den.mul_small(target_num))
}

fn score_cmp(a: &Row, b: &Row) -> Ordering {
    a.b.mul_big(&b.score_den).cmp(&b.b.mul_big(&a.score_den))
}

fn sort_rows_by_score(rows: &mut [Row]) {
    rows.sort_by(|a, b| score_cmp(b, a).then_with(|| a.a_sum.cmp(&b.a_sum)));
}

fn push_top_score(rows: &mut Vec<Row>, row: Row, top_n: usize) {
    push_top_by(rows, row, top_n, |candidate, existing| {
        score_cmp(candidate, existing)
    });
}

fn push_top_rho_slack(rows: &mut Vec<Row>, row: Row, top_n: usize) {
    push_top_by(rows, row, top_n, |candidate, existing| {
        candidate.rho_bit_slack.cmp(&existing.rho_bit_slack)
    });
}

fn push_top_theta_candidates(rows: &mut Vec<Row>, row: Row, top_n: usize) {
    push_top_by(rows, row, top_n, |candidate, existing| {
        candidate
            .theta_candidate_odd_count
            .cmp(&existing.theta_candidate_odd_count)
    });
}

fn push_top_margin(rows: &mut Vec<Row>, row: Row, top_n: usize) {
    push_top_by(rows, row, top_n, |candidate, existing| {
        existing.margin.cmp(&candidate.margin)
    });
}

fn push_top_by<F>(rows: &mut Vec<Row>, row: Row, top_n: usize, better: F)
where
    F: Fn(&Row, &Row) -> Ordering,
{
    if top_n == 0 {
        return;
    }
    if rows.len() < top_n {
        rows.push(row);
        return;
    }
    let mut worst_idx = 0usize;
    for idx in 1..rows.len() {
        if better(&rows[worst_idx], &rows[idx]) == Ordering::Greater {
            worst_idx = idx;
        }
    }
    if better(&row, &rows[worst_idx]) == Ordering::Greater {
        rows[worst_idx] = row;
    }
}

fn write_outputs(config: &Config, stats: &Stats) {
    let summary_path = config.out_dir.join(format!(
        "lock2_reverse_barrier_summary_Amax{}_{}.json",
        config.amax, config.stamp
    ));
    let hits_path = config.out_dir.join(format!(
        "lock2_reverse_barrier_hits_Amax{}_{}.csv",
        config.amax, config.stamp
    ));
    let top_path = config.out_dir.join(format!(
        "lock2_reverse_barrier_top_score_Amax{}_{}.csv",
        config.amax, config.stamp
    ));
    let slack_path = config.out_dir.join(format!(
        "lock2_reverse_barrier_top_rho_slack_Amax{}_{}.csv",
        config.amax, config.stamp
    ));
    let theta_path = config.out_dir.join(format!(
        "lock2_reverse_barrier_top_theta_candidates_Amax{}_{}.csv",
        config.amax, config.stamp
    ));
    let margin_path = config.out_dir.join(format!(
        "lock2_reverse_barrier_top_margin_proximity_Amax{}_{}.csv",
        config.amax, config.stamp
    ));
    let pair_profile_path = config.out_dir.join(format!(
        "lock2_reverse_barrier_pair_profile_Amax{}_{}.csv",
        config.amax, config.stamp
    ));
    let memo_stats_path = config.out_dir.join(format!(
        "lock2_reconstruction_memo_stats_Amax{}_{}.json",
        config.amax, config.stamp
    ));

    let new_top = stats
        .hits
        .iter()
        .find(|row| row.comparison == "above" && row.word != vec![2]);

    let mut summary = BufWriter::new(File::create(summary_path).expect("summary"));
    writeln!(summary, "{{").unwrap();
    writeln!(summary, "  \"Amax\": {},", config.amax).unwrap();
    writeln!(summary, "  \"target_num\": {},", config.target_num).unwrap();
    writeln!(summary, "  \"target_den\": {},", config.target_den).unwrap();
    writeln!(summary, "  \"include_equal\": {},", config.include_equal).unwrap();
    writeln!(
        summary,
        "  \"residue_mod_power\": {},",
        config.residue_mod_power
    )
    .unwrap();
    writeln!(summary, "  \"memo_exact_k\": {},", config.memo_exact_k).unwrap();
    writeln!(
        summary,
        "  \"failed_memo_limit\": {},",
        config.failed_memo_limit
    )
    .unwrap();
    writeln!(summary, "  \"ak_pairs\": {},", stats.ak_pairs).unwrap();
    writeln!(summary, "  \"rho_candidates\": {},", stats.rho_candidates).unwrap();
    writeln!(summary, "  \"b_candidates\": {},", stats.b_candidates).unwrap();
    writeln!(
        summary,
        "  \"reconstructed_words\": {},",
        stats.reconstructed_words
    )
    .unwrap();
    writeln!(summary, "  \"memo_hits\": {},", stats.memo_hits).unwrap();
    writeln!(summary, "  \"memo_misses\": {},", stats.memo_misses).unwrap();
    writeln!(summary, "  \"memo_entries\": {},", stats.memo_entries).unwrap();
    writeln!(summary, "  \"pruned_by_memo\": {},", stats.pruned_by_memo).unwrap();
    writeln!(
        summary,
        "  \"deepest_recursion\": {},",
        stats.deepest_recursion
    )
    .unwrap();
    writeln!(
        summary,
        "  \"largest_remaining_a_sum\": {},",
        stats.largest_remaining_a_sum
    )
    .unwrap();
    writeln!(
        summary,
        "  \"largest_remaining_b_bits\": {},",
        stats.largest_remaining_b_bits
    )
    .unwrap();
    writeln!(
        summary,
        "  \"zero_reconstruction_pairs\": {},",
        stats.zero_reconstruction_pairs
    )
    .unwrap();
    writeln!(summary, "  \"slow_pairs\": {},", stats.slow_pairs).unwrap();
    writeln!(summary, "  \"hit_count\": {},", stats.hits.len()).unwrap();
    writeln!(
        summary,
        "  \"critical_failures\": {},",
        stats.critical_failures
    )
    .unwrap();
    if let Some(row) = new_top {
        writeln!(
            summary,
            "  \"new_top_score_num\": \"{}\",",
            row.b.to_decimal()
        )
        .unwrap();
        writeln!(
            summary,
            "  \"new_top_score_den\": \"{}\",",
            row.score_den.to_decimal()
        )
        .unwrap();
    } else {
        writeln!(summary, "  \"new_top_score_num\": null,").unwrap();
        writeln!(summary, "  \"new_top_score_den\": null,").unwrap();
    }
    writeln!(summary, "  \"runtime_seconds\": {}", stats.runtime_seconds).unwrap();
    writeln!(summary, "}}").unwrap();

    write_rows(hits_path, &stats.hits);
    write_rows(top_path, &stats.top_score);
    write_rows(slack_path, &stats.top_rho_slack);
    write_rows(theta_path, &stats.top_theta_candidates);
    write_rows(margin_path, &stats.top_margin_proximity);
    write_pair_profiles(pair_profile_path, &stats.pair_profiles);
    write_memo_stats(memo_stats_path, config, stats);
}

fn write_pair_profiles(path: PathBuf, profiles: &[PairProfile]) {
    let mut file = BufWriter::new(File::create(path).expect("pair profile csv"));
    writeln!(
        file,
        "A,k,elapsed_seconds,rho_candidates,b_candidates,reconstructed_words,hits,memo_hits,memo_misses,pruned_by_memo,deepest_recursion,largest_remaining_A,largest_remaining_B_bits,zero_reconstruction_pair,slow_pair,failed_memo_entries"
    )
    .unwrap();
    for profile in profiles {
        writeln!(
            file,
            "{},{},{:.6},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            profile.a_sum,
            profile.k,
            profile.elapsed_seconds,
            profile.rho_candidates,
            profile.b_candidates,
            profile.reconstructed_words,
            profile.hits,
            profile.memo_hits,
            profile.memo_misses,
            profile.pruned_by_memo,
            profile.deepest_recursion,
            profile.largest_remaining_a_sum,
            profile.largest_remaining_b_bits,
            profile.zero_reconstruction_pair,
            profile.slow_pair,
            profile.failed_memo_entries
        )
        .unwrap();
    }
}

fn write_memo_stats(path: PathBuf, config: &Config, stats: &Stats) {
    let mut file = BufWriter::new(File::create(path).expect("memo stats json"));
    writeln!(file, "{{").unwrap();
    writeln!(file, "  \"Amax\": {},", config.amax).unwrap();
    writeln!(file, "  \"target_num\": {},", config.target_num).unwrap();
    writeln!(file, "  \"target_den\": {},", config.target_den).unwrap();
    writeln!(file, "  \"memo_exact_k\": {},", config.memo_exact_k).unwrap();
    writeln!(
        file,
        "  \"failed_memo_limit\": {},",
        config.failed_memo_limit
    )
    .unwrap();
    writeln!(
        file,
        "  \"residue_mod_power\": {},",
        config.residue_mod_power
    )
    .unwrap();
    writeln!(file, "  \"memo_hits\": {},", stats.memo_hits).unwrap();
    writeln!(file, "  \"memo_misses\": {},", stats.memo_misses).unwrap();
    writeln!(file, "  \"memo_entries\": {},", stats.memo_entries).unwrap();
    writeln!(file, "  \"pruned_by_memo\": {},", stats.pruned_by_memo).unwrap();
    writeln!(
        file,
        "  \"deepest_recursion\": {},",
        stats.deepest_recursion
    )
    .unwrap();
    writeln!(
        file,
        "  \"largest_remaining_a_sum\": {},",
        stats.largest_remaining_a_sum
    )
    .unwrap();
    writeln!(
        file,
        "  \"largest_remaining_b_bits\": {},",
        stats.largest_remaining_b_bits
    )
    .unwrap();
    writeln!(
        file,
        "  \"zero_reconstruction_pairs\": {},",
        stats.zero_reconstruction_pairs
    )
    .unwrap();
    writeln!(file, "  \"slow_pairs\": {},", stats.slow_pairs).unwrap();
    writeln!(
        file,
        "  \"pair_profile_rows\": {},",
        stats.pair_profiles.len()
    )
    .unwrap();
    writeln!(file, "  \"runtime_seconds\": {}", stats.runtime_seconds).unwrap();
    writeln!(file, "}}").unwrap();
}

fn write_rows(path: PathBuf, rows: &[Row]) {
    let mut file = BufWriter::new(File::create(path).expect("csv"));
    writeln!(
        file,
        "comparison,word,A,k,rho,score_num,score_den,score_float,B_w,D,margin,verified,verification_notes,image,rho_bit_slack,theta_candidate_odd_count,count_1,count_2,count_ge3,max_run_1,max_run_2,prefix5,suffix5,repeated_blocks,rho_mod_3,rho_mod_5,rho_mod_7,rho_mod_11,rho_mod_13,orbit_prefix,extends_a54,has_a54_prefix,has_a54_suffix"
    )
    .unwrap();
    for row in rows {
        writeln!(
            file,
            "{},\"{}\",{},{},{},{},{},{:.15},{},{},{},{},\"{}\",{},{},{},{},{},{},{},{},\"{}\",\"{}\",\"{}\",{},{},{},{},{},\"{}\",{},{},{}",
            row.comparison,
            word_to_string(&row.word),
            row.a_sum,
            row.k,
            row.rho,
            row.b.to_decimal(),
            row.score_den.to_decimal(),
            row.b.to_f64() / row.score_den.to_f64(),
            row.b.to_decimal(),
            row.d.to_decimal(),
            row.margin.to_decimal(),
            row.verified,
            row.verification_notes,
            row.image.to_decimal(),
            row.rho_bit_slack,
            row.theta_candidate_odd_count.to_decimal(),
            row.count_1,
            row.count_2,
            row.count_ge3,
            row.max_run_1,
            row.max_run_2,
            row.prefix5,
            row.suffix5,
            row.repeated_blocks,
            row.rho_mod_3,
            row.rho_mod_5,
            row.rho_mod_7,
            row.rho_mod_11,
            row.rho_mod_13,
            row.orbit_prefix,
            row.extends_a54,
            row.has_a54_prefix,
            row.has_a54_suffix
        )
        .unwrap();
    }
}

fn print_summary(config: &Config, stats: &Stats) {
    println!("Lock 2 reverse barrier scan");
    println!("Amax={}", config.amax);
    println!("target={}/{}", config.target_num, config.target_den);
    println!("residue_mod_power={}", config.residue_mod_power);
    println!("memo_exact_k={}", config.memo_exact_k);
    println!("failed_memo_limit={}", config.failed_memo_limit);
    println!("ak_pairs={}", stats.ak_pairs);
    println!("rho_candidates={}", stats.rho_candidates);
    println!("b_candidates={}", stats.b_candidates);
    println!("reconstructed_words={}", stats.reconstructed_words);
    println!("memo_hits={}", stats.memo_hits);
    println!("memo_misses={}", stats.memo_misses);
    println!("memo_entries={}", stats.memo_entries);
    println!("pruned_by_memo={}", stats.pruned_by_memo);
    println!("deepest_recursion={}", stats.deepest_recursion);
    println!("largest_remaining_a_sum={}", stats.largest_remaining_a_sum);
    println!(
        "largest_remaining_b_bits={}",
        stats.largest_remaining_b_bits
    );
    println!(
        "zero_reconstruction_pairs={}",
        stats.zero_reconstruction_pairs
    );
    println!("slow_pairs={}", stats.slow_pairs);
    println!("hit_count={}", stats.hits.len());
    println!("critical_failures={}", stats.critical_failures);
    println!("runtime_seconds={:.3}", stats.runtime_seconds);
    for row in stats.hits.iter().take(20) {
        println!(
            "hit comparison={} verified={} word=({}) A={} k={} rho={} score={}/{} {:.15}",
            row.comparison,
            row.verified,
            word_to_string(&row.word),
            row.a_sum,
            row.k,
            row.rho,
            row.b.to_decimal(),
            row.score_den.to_decimal(),
            row.b.to_f64() / row.score_den.to_f64()
        );
    }
}

impl Big {
    fn zero() -> Self {
        Self { limbs: Vec::new() }
    }

    fn one() -> Self {
        Self { limbs: vec![1] }
    }

    fn from_u64(value: u64) -> Self {
        if value == 0 {
            Self::zero()
        } else {
            Self { limbs: vec![value] }
        }
    }

    fn pow2(bits: usize) -> Self {
        let mut out = vec![0u64; bits / 64 + 1];
        out[bits / 64] = 1u64 << (bits % 64);
        Self { limbs: out }.normalized()
    }

    fn normalized(mut self) -> Self {
        while self.limbs.last() == Some(&0) {
            self.limbs.pop();
        }
        self
    }

    fn is_zero(&self) -> bool {
        self.limbs.is_empty()
    }

    fn is_even(&self) -> bool {
        self.limbs.first().copied().unwrap_or(0) & 1 == 0
    }

    fn bit_length(&self) -> usize {
        if let Some(&last) = self.limbs.last() {
            (self.limbs.len() - 1) * 64 + (64 - last.leading_zeros() as usize)
        } else {
            0
        }
    }

    fn bit_length_floor(&self) -> usize {
        self.bit_length().saturating_sub(1)
    }

    fn bit(&self, idx: usize) -> bool {
        let limb = idx / 64;
        if limb >= self.limbs.len() {
            false
        } else {
            (self.limbs[limb] >> (idx % 64)) & 1 == 1
        }
    }

    fn add(&self, other: &Self) -> Self {
        let len = self.limbs.len().max(other.limbs.len());
        let mut out = Vec::with_capacity(len + 1);
        let mut carry = 0u128;
        for i in 0..len {
            let a = self.limbs.get(i).copied().unwrap_or(0) as u128;
            let b = other.limbs.get(i).copied().unwrap_or(0) as u128;
            let sum = a + b + carry;
            out.push(sum as u64);
            carry = sum >> 64;
        }
        if carry > 0 {
            out.push(carry as u64);
        }
        Self { limbs: out }.normalized()
    }

    fn add_small(&self, small: u64) -> Self {
        self.add(&Self::from_u64(small))
    }

    fn sub(&self, other: &Self) -> Self {
        assert!(self >= other);
        let mut out = Vec::with_capacity(self.limbs.len());
        let mut borrow = 0i128;
        for i in 0..self.limbs.len() {
            let a = self.limbs[i] as i128;
            let b = other.limbs.get(i).copied().unwrap_or(0) as i128;
            let mut value = a - b - borrow;
            if value < 0 {
                value += 1i128 << 64;
                borrow = 1;
            } else {
                borrow = 0;
            }
            out.push(value as u64);
        }
        Self { limbs: out }.normalized()
    }

    fn sub_one(&self) -> Self {
        self.sub(&Self::one())
    }

    fn mul_small(&self, small: u64) -> Self {
        if self.is_zero() || small == 0 {
            return Self::zero();
        }
        let mut out = Vec::with_capacity(self.limbs.len() + 1);
        let mut carry = 0u128;
        for &limb in &self.limbs {
            let value = limb as u128 * small as u128 + carry;
            out.push(value as u64);
            carry = value >> 64;
        }
        if carry > 0 {
            out.push(carry as u64);
        }
        Self { limbs: out }.normalized()
    }

    fn mul_big(&self, other: &Self) -> Self {
        if self.is_zero() || other.is_zero() {
            return Self::zero();
        }
        let mut out = vec![0u64; self.limbs.len() + other.limbs.len()];
        for (i, &a) in self.limbs.iter().enumerate() {
            let mut carry = 0u128;
            for (j, &b) in other.limbs.iter().enumerate() {
                let idx = i + j;
                let value = out[idx] as u128 + a as u128 * b as u128 + carry;
                out[idx] = value as u64;
                carry = value >> 64;
            }
            let mut idx = i + other.limbs.len();
            while carry > 0 {
                let value = out[idx] as u128 + carry;
                out[idx] = value as u64;
                carry = value >> 64;
                idx += 1;
                if idx == out.len() && carry > 0 {
                    out.push(0);
                }
            }
        }
        Self { limbs: out }.normalized()
    }

    fn div_small(&self, divisor: u64) -> Self {
        assert!(divisor > 0);
        if self.is_zero() {
            return Self::zero();
        }
        let mut out = vec![0u64; self.limbs.len()];
        let mut rem = 0u128;
        for i in (0..self.limbs.len()).rev() {
            let value = (rem << 64) | self.limbs[i] as u128;
            out[i] = (value / divisor as u128) as u64;
            rem = value % divisor as u128;
        }
        Self { limbs: out }.normalized()
    }

    fn div_ceil_small(&self, divisor: u64) -> Self {
        let q = self.div_small(divisor);
        if self.mod_small(divisor) == 0 {
            q
        } else {
            q.add_small(1)
        }
    }

    fn mod_small(&self, divisor: u64) -> u64 {
        assert!(divisor > 0);
        let mut rem = 0u128;
        for &limb in self.limbs.iter().rev() {
            rem = ((rem << 64) + limb as u128) % divisor as u128;
        }
        rem as u64
    }

    fn div_big(&self, divisor: &Self) -> Self {
        assert!(!divisor.is_zero());
        if self < divisor {
            return Self::zero();
        }
        let mut q = Self::zero();
        let mut r = Self::zero();
        for bit in (0..self.bit_length()).rev() {
            r = r.shl1();
            if self.bit(bit) {
                r = r.add_small(1);
            }
            q = q.shl1();
            if r >= *divisor {
                r = r.sub(divisor);
                q = q.add_small(1);
            }
        }
        q
    }

    fn div_ceil_big(&self, divisor: &Self) -> Self {
        let q = self.div_big(divisor);
        if q.mul_big(divisor) == *self {
            q
        } else {
            q.add_small(1)
        }
    }

    fn shl1(&self) -> Self {
        let mut out = Vec::with_capacity(self.limbs.len() + 1);
        let mut carry = 0u64;
        for &limb in &self.limbs {
            out.push((limb << 1) | carry);
            carry = limb >> 63;
        }
        if carry > 0 {
            out.push(carry);
        }
        Self { limbs: out }.normalized()
    }

    fn shr_bits(&self, bits: usize) -> Self {
        let limb_shift = bits / 64;
        let bit_shift = bits % 64;
        if limb_shift >= self.limbs.len() {
            return Self::zero();
        }
        let mut out = Vec::with_capacity(self.limbs.len() - limb_shift);
        for i in limb_shift..self.limbs.len() {
            let mut value = self.limbs[i] >> bit_shift;
            if bit_shift > 0 && i + 1 < self.limbs.len() {
                value |= self.limbs[i + 1] << (64 - bit_shift);
            }
            out.push(value);
        }
        Self { limbs: out }.normalized()
    }

    fn trailing_zeros(&self) -> usize {
        for (idx, &limb) in self.limbs.iter().enumerate() {
            if limb != 0 {
                return idx * 64 + limb.trailing_zeros() as usize;
            }
        }
        0
    }

    fn low_bits(&self, bits: usize) -> Self {
        let limbs = bits.div_ceil(64);
        let mut out = self.limbs.iter().take(limbs).copied().collect::<Vec<_>>();
        if bits % 64 != 0 && !out.is_empty() {
            let mask = (1u64 << (bits % 64)) - 1;
            let last = out.len() - 1;
            out[last] &= mask;
        }
        Self { limbs: out }.normalized()
    }

    fn to_u64(&self) -> Option<u64> {
        if self.limbs.len() <= 1 {
            Some(self.limbs.first().copied().unwrap_or(0))
        } else {
            None
        }
    }

    fn to_decimal(&self) -> String {
        if self.is_zero() {
            return "0".to_string();
        }
        let mut n = self.clone();
        let mut parts = Vec::new();
        let base = 1_000_000_000u64;
        while !n.is_zero() {
            let rem = n.mod_small(base);
            n = n.div_small(base);
            parts.push(rem);
        }
        let mut out = parts.pop().unwrap().to_string();
        while let Some(part) = parts.pop() {
            out.push_str(&format!("{:09}", part));
        }
        out
    }

    fn to_f64(&self) -> f64 {
        let mut out = 0.0f64;
        for &limb in self.limbs.iter().rev() {
            out = out * 18446744073709551616.0 + limb as f64;
        }
        out
    }
}

impl Ord for Big {
    fn cmp(&self, other: &Self) -> Ordering {
        if self.limbs.len() != other.limbs.len() {
            return self.limbs.len().cmp(&other.limbs.len());
        }
        for i in (0..self.limbs.len()).rev() {
            if self.limbs[i] != other.limbs[i] {
                return self.limbs[i].cmp(&other.limbs[i]);
            }
        }
        Ordering::Equal
    }
}

impl PartialOrd for Big {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

fn powers_big(base: u64, len: usize) -> Vec<Big> {
    let mut out = vec![Big::one(); len];
    for i in 1..len {
        out[i] = out[i - 1].mul_small(base);
    }
    out
}

fn exponent_counts(word: &[u16]) -> (usize, usize, usize) {
    let mut ones = 0;
    let mut twos = 0;
    let mut ge3 = 0;
    for &a in word {
        if a == 1 {
            ones += 1;
        } else if a == 2 {
            twos += 1;
        } else {
            ge3 += 1;
        }
    }
    (ones, twos, ge3)
}

fn max_run<F: Fn(u16) -> bool>(word: &[u16], pred: F) -> usize {
    let mut best = 0usize;
    let mut current = 0usize;
    for &a in word {
        if pred(a) {
            current += 1;
            best = best.max(current);
        } else {
            current = 0;
        }
    }
    best
}

fn repeated_blocks(word: &[u16]) -> String {
    let mut blocks = Vec::new();
    for len in 3..=min(8, word.len() / 2) {
        for i in 0..=word.len() - 2 * len {
            let block = &word[i..i + len];
            for j in i + len..=word.len() - len {
                if block == &word[j..j + len] {
                    blocks.push(format!("{}@{}@{}", word_to_string(block), i, j));
                    if blocks.len() >= 8 {
                        return blocks.join(";");
                    }
                    break;
                }
            }
        }
    }
    blocks.join(";")
}

fn contains_subslice(word: &[u16], needle: &[u16]) -> bool {
    if needle.len() > word.len() {
        return false;
    }
    word.windows(needle.len()).any(|window| window == needle)
}

fn bit_length_u64(value: u64) -> usize {
    64 - value.leading_zeros() as usize
}

fn gcd(mut a: u64, mut b: u64) -> u64 {
    while b != 0 {
        let r = a % b;
        a = b;
        b = r;
    }
    a
}

fn word_to_string(word: &[u16]) -> String {
    word.iter()
        .map(|value| value.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
