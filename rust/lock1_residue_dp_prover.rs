use std::collections::HashMap;
use std::env;
use std::fs::{create_dir_all, File};
use std::hash::{Hash, Hasher};
use std::io::{BufWriter, Write};
use std::path::PathBuf;

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
    out_dir: PathBuf,
}

#[derive(Clone, Copy, Eq)]
struct State {
    prefix_sum: usize,
    residue: u128,
    non_all2: bool,
}

impl PartialEq for State {
    fn eq(&self, other: &Self) -> bool {
        self.prefix_sum == other.prefix_sum
            && self.residue == other.residue
            && self.non_all2 == other.non_all2
    }
}

impl Hash for State {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.prefix_sum.hash(state);
        self.residue.hash(state);
        self.non_all2.hash(state);
    }
}

struct ClassProof {
    k: usize,
    a_sum: usize,
    d: u128,
    words_covered: u128,
    final_states: usize,
    max_layer_states: usize,
    zero_all2_states: u128,
    zero_nontrivial_states: u128,
    verdict: &'static str,
}

fn parse_args() -> Config {
    let mut max_k = None;
    let mut max_a = None;
    let mut min_k = 1usize;
    let mut scope = Scope::Line;
    let mut line_window = 0usize;
    let mut line_offset = 1i64;
    let mut max_total_a = None;
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
        out_dir: out_dir.expect("--out-dir is required"),
    };
    if config.min_k == 0 || config.max_k == 0 || config.max_a == 0 {
        panic!("--min-k, --max-k, and --max-a must be positive");
    }
    if config.min_k > config.max_k {
        panic!("--min-k cannot exceed --max-k");
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

fn add_mod(lhs: u128, rhs: u128, modulus: u128) -> u128 {
    if modulus == 1 {
        return 0;
    }
    if lhs >= modulus - rhs {
        lhs - (modulus - rhs)
    } else {
        lhs + rhs
    }
}

fn mul_small_mod(value: u128, factor: u128, modulus: u128) -> u128 {
    if modulus == 1 {
        return 0;
    }
    let mut acc = 0u128;
    for _ in 0..factor {
        acc = add_mod(acc, value % modulus, modulus);
    }
    acc
}

fn pow2_table(max_exponent: usize, modulus: u128) -> Vec<u128> {
    let mut table = Vec::with_capacity(max_exponent + 1);
    let mut value = 1u128 % modulus;
    table.push(value);
    for _ in 0..max_exponent {
        value = add_mod(value, value, modulus);
        table.push(value);
    }
    table
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

fn count_words(k: usize, total: usize, max_part: usize) -> u128 {
    let mut dp = vec![vec![0u128; total + 1]; k + 1];
    dp[0][0] = 1;
    for used in 0..k {
        for sum in 0..=total {
            let current = dp[used][sum];
            if current == 0 {
                continue;
            }
            let max_exp = max_part.min(total - sum);
            for exponent in 1..=max_exp {
                dp[used + 1][sum + exponent] = dp[used + 1][sum + exponent].saturating_add(current);
            }
        }
    }
    dp[k][total]
}

fn prove_class(k: usize, a_sum: usize, max_part: usize) -> Option<ClassProof> {
    let two_a = 1u128.checked_shl(a_sum as u32)?;
    let three_k = checked_pow(3, k)?;
    if two_a <= three_k {
        return None;
    }
    let d = two_a - three_k;
    let pow2 = pow2_table(a_sum, d);
    let mut current: HashMap<State, u128> = HashMap::new();
    current.insert(
        State {
            prefix_sum: 0,
            residue: 0,
            non_all2: false,
        },
        1,
    );
    let mut max_layer_states = current.len();

    for position in 0..k {
        let remaining_slots = k - position - 1;
        let mut next: HashMap<State, u128> = HashMap::new();
        for (state, count) in current {
            let min_after = state.prefix_sum + 1 + remaining_slots;
            if min_after > a_sum {
                continue;
            }
            let max_exp_by_total = a_sum - state.prefix_sum - remaining_slots;
            let max_exp = max_part.min(max_exp_by_total);
            let min_exp = a_sum
                .saturating_sub(state.prefix_sum + remaining_slots * max_part)
                .max(1);
            if min_exp > max_exp {
                continue;
            }
            for exponent in min_exp..=max_exp {
                let new_prefix_sum = state.prefix_sum + exponent;
                let residue = add_mod(
                    mul_small_mod(state.residue, 3, d),
                    pow2[state.prefix_sum],
                    d,
                );
                let new_state = State {
                    prefix_sum: new_prefix_sum,
                    residue,
                    non_all2: state.non_all2 || exponent != 2,
                };
                *next.entry(new_state).or_insert(0) = next
                    .get(&new_state)
                    .copied()
                    .unwrap_or(0)
                    .saturating_add(count);
            }
        }
        max_layer_states = max_layer_states.max(next.len());
        current = next;
    }

    let mut zero_all2_states = 0u128;
    let mut zero_nontrivial_states = 0u128;
    for (state, count) in &current {
        if state.prefix_sum == a_sum && state.residue == 0 {
            if state.non_all2 {
                zero_nontrivial_states = zero_nontrivial_states.saturating_add(*count);
            } else {
                zero_all2_states = zero_all2_states.saturating_add(*count);
            }
        }
    }

    let verdict = if zero_nontrivial_states == 0 {
        "proved_no_nontrivial_zero_residue"
    } else {
        "failed_nontrivial_zero_residue_reachable"
    };

    Some(ClassProof {
        k,
        a_sum,
        d,
        words_covered: count_words(k, a_sum, max_part),
        final_states: current.len(),
        max_layer_states,
        zero_all2_states,
        zero_nontrivial_states,
        verdict,
    })
}

fn write_csv(path: PathBuf, rows: &[ClassProof]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "k,A,D,words_covered,final_states,max_layer_states,zero_all2_words,zero_nontrivial_words,verdict"
    )?;
    for row in rows {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{}",
            row.k,
            row.a_sum,
            row.d,
            row.words_covered,
            row.final_states,
            row.max_layer_states,
            row.zero_all2_states,
            row.zero_nontrivial_states,
            row.verdict
        )?;
    }
    Ok(())
}

fn write_json(
    path: PathBuf,
    config: &Config,
    rows: &[ClassProof],
    d_le_zero_skips: u64,
) -> std::io::Result<()> {
    let failed = rows
        .iter()
        .filter(|row| row.zero_nontrivial_states != 0)
        .count();
    let words_covered = rows
        .iter()
        .fold(0u128, |acc, row| acc.saturating_add(row.words_covered));
    let max_layer_states = rows
        .iter()
        .map(|row| row.max_layer_states)
        .max()
        .unwrap_or(0);
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(file, "{{")?;
    writeln!(file, "  \"prover\": \"lock1_residue_dp_prover\",")?;
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
    writeln!(file, "  \"classes_proved\": {},", rows.len())?;
    writeln!(file, "  \"D_le_zero_skips\": {},", d_le_zero_skips)?;
    writeln!(file, "  \"words_covered\": \"{}\",", words_covered)?;
    writeln!(file, "  \"failed_classes\": {},", failed)?;
    writeln!(file, "  \"max_layer_states\": {},", max_layer_states)?;
    writeln!(
        file,
        "  \"claim_status_for_scanned_classes\": \"{}\"",
        if failed == 0 {
            "dp_proved_no_nontrivial_zero_residue"
        } else {
            "attention_required"
        }
    )?;
    writeln!(file, "}}")?;
    Ok(())
}

fn main() {
    let config = parse_args();
    create_dir_all(&config.out_dir).expect("create out dir");

    let mut rows = Vec::new();
    let mut d_le_zero_skips = 0u64;
    for k in config.min_k..=config.max_k {
        for a_sum in total_a_values(&config, k) {
            match prove_class(k, a_sum, config.max_a) {
                Some(row) => rows.push(row),
                None => d_le_zero_skips += 1,
            }
        }
    }

    write_csv(config.out_dir.join("lock1_residue_dp_classes.csv"), &rows).expect("write csv");
    write_json(
        config.out_dir.join("lock1_residue_dp_summary.json"),
        &config,
        &rows,
        d_le_zero_skips,
    )
    .expect("write json");

    let failed = rows
        .iter()
        .filter(|row| row.zero_nontrivial_states != 0)
        .count();
    let words_covered = rows
        .iter()
        .fold(0u128, |acc, row| acc.saturating_add(row.words_covered));
    println!("Lock 1 residue DP prover");
    println!("classes_proved={}", rows.len());
    println!("D_le_zero_skips={}", d_le_zero_skips);
    println!("words_covered={}", words_covered);
    println!("failed_classes={}", failed);
    println!("wrote: {}", config.out_dir.display());
}
