use std::collections::HashSet;
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
    unbounded_parts: bool,
    min_k: usize,
    scope: Scope,
    line_window: usize,
    line_offset: i64,
    max_total_a: Option<usize>,
    out_dir: PathBuf,
}

#[derive(Clone, Copy, Eq)]
struct BarrierState {
    prefix_sum: usize,
    residue: u128,
    non_all2: bool,
}

impl PartialEq for BarrierState {
    fn eq(&self, other: &Self) -> bool {
        self.prefix_sum == other.prefix_sum
            && self.residue == other.residue
            && self.non_all2 == other.non_all2
    }
}

impl Hash for BarrierState {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.prefix_sum.hash(state);
        self.residue.hash(state);
        self.non_all2.hash(state);
    }
}

struct BarrierProof {
    k: usize,
    a_sum: usize,
    d: u128,
    max_barrier_states: usize,
    layer_counts: Vec<usize>,
    initial_blocked: bool,
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
    let mut unbounded_parts = false;
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
            "--unbounded-parts" => {
                unbounded_parts = true;
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
        unbounded_parts,
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

fn sub_mod(lhs: u128, rhs: u128, modulus: u128) -> u128 {
    if lhs >= rhs {
        lhs - rhs
    } else {
        modulus - (rhs - lhs)
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

fn inv3_mod(modulus: u128) -> Option<u128> {
    if modulus % 3 == 0 {
        return None;
    }
    // 3 * ((2m + 1) / 3) == 1 mod m when m == 1 mod 3.
    // 3 * ((m + 1) / 3) == 1 mod m when m == 2 mod 3.
    match modulus % 3 {
        1 => Some((modulus.checked_mul(2)? + 1) / 3),
        2 => Some((modulus + 1) / 3),
        _ => None,
    }
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
    let part_cap = if config.unbounded_parts {
        config
            .max_total_a
            .unwrap_or(k * config.max_a)
            .max(config.max_a)
    } else {
        config.max_a
    };
    match config.scope {
        Scope::All => {
            let max_total = config.max_total_a.unwrap_or(k * part_cap);
            (k..=max_total.min(k * part_cap)).collect()
        }
        Scope::Line => {
            let center = (k as f64 * ALPHA).floor() as i64 + config.line_offset;
            let low = center - config.line_window as i64;
            let high = center + config.line_window as i64;
            (low..=high)
                .filter(|value| *value >= k as i64 && *value <= (k * part_cap) as i64)
                .map(|value| value as usize)
                .collect()
        }
    }
}

fn can_finish(prefix_sum: usize, used_slots: usize, k: usize, a_sum: usize, max_a: usize) -> bool {
    if prefix_sum < used_slots {
        return false;
    }
    let remaining = k - used_slots;
    let min_total = prefix_sum + remaining;
    let max_total = prefix_sum + remaining * max_a;
    min_total <= a_sum && a_sum <= max_total
}

fn prove_barrier_class(k: usize, a_sum: usize, max_a: usize) -> Option<BarrierProof> {
    let two_a = 1u128.checked_shl(a_sum as u32)?;
    let three_k = checked_pow(3, k)?;
    if two_a <= three_k {
        return None;
    }
    let d = two_a - three_k;
    let inv3 = inv3_mod(d)?;
    let pow2 = pow2_table(a_sum, d);

    let mut barrier = HashSet::new();
    barrier.insert(BarrierState {
        prefix_sum: a_sum,
        residue: 0,
        non_all2: true,
    });

    let mut layer_counts = vec![0usize; k + 1];
    layer_counts[k] = barrier.len();
    let mut max_barrier_states = barrier.len();

    for position in (0..k).rev() {
        let mut previous = HashSet::new();
        for state in &barrier {
            let max_exp = max_a.min(state.prefix_sum);
            for exponent in 1..=max_exp {
                let previous_sum = state.prefix_sum - exponent;
                if !can_finish(previous_sum, position, k, a_sum, max_a) {
                    continue;
                }
                let residue_without_offset = sub_mod(state.residue, pow2[previous_sum], d);
                let previous_residue = mul_mod(residue_without_offset, inv3, d);
                if state.non_all2 {
                    previous.insert(BarrierState {
                        prefix_sum: previous_sum,
                        residue: previous_residue,
                        non_all2: true,
                    });
                    if exponent != 2 {
                        previous.insert(BarrierState {
                            prefix_sum: previous_sum,
                            residue: previous_residue,
                            non_all2: false,
                        });
                    }
                } else if exponent == 2 {
                    previous.insert(BarrierState {
                        prefix_sum: previous_sum,
                        residue: previous_residue,
                        non_all2: false,
                    });
                }
            }
        }
        layer_counts[position] = previous.len();
        max_barrier_states = max_barrier_states.max(previous.len());
        barrier = previous;
    }

    let initial = BarrierState {
        prefix_sum: 0,
        residue: 0,
        non_all2: false,
    };
    let initial_blocked = barrier.contains(&initial);
    let verdict = if initial_blocked {
        "failed_initial_inside_forbidden_preimage"
    } else {
        "barrier_proved_initial_outside_forbidden_preimage"
    };

    Some(BarrierProof {
        k,
        a_sum,
        d,
        max_barrier_states,
        layer_counts,
        initial_blocked,
        verdict,
    })
}

fn counts_string(counts: &[usize]) -> String {
    counts
        .iter()
        .map(|count| count.to_string())
        .collect::<Vec<_>>()
        .join(" ")
}

fn write_csv(path: PathBuf, rows: &[BarrierProof]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "k,A,D,max_barrier_states,initial_inside_forbidden_preimage,verdict,layer_counts"
    )?;
    for row in rows {
        writeln!(
            file,
            "{},{},{},{},{},{},\"{}\"",
            row.k,
            row.a_sum,
            row.d,
            row.max_barrier_states,
            row.initial_blocked,
            row.verdict,
            counts_string(&row.layer_counts)
        )?;
    }
    Ok(())
}

fn write_json(
    path: PathBuf,
    config: &Config,
    rows: &[BarrierProof],
    d_le_zero_skips: u64,
) -> std::io::Result<()> {
    let failed = rows.iter().filter(|row| row.initial_blocked).count();
    let max_barrier_states = rows
        .iter()
        .map(|row| row.max_barrier_states)
        .max()
        .unwrap_or(0);
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(file, "{{")?;
    writeln!(file, "  \"prover\": \"lock1_backward_barrier\",")?;
    writeln!(file, "  \"max_k\": {},", config.max_k)?;
    writeln!(file, "  \"max_a\": {},", config.max_a)?;
    writeln!(file, "  \"unbounded_parts\": {},", config.unbounded_parts)?;
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
    writeln!(file, "  \"failed_classes\": {},", failed)?;
    writeln!(file, "  \"max_barrier_states\": {},", max_barrier_states)?;
    writeln!(
        file,
        "  \"claim_status_for_scanned_classes\": \"{}\"",
        if failed == 0 {
            "barrier_proved_initial_outside_forbidden_preimage"
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
            let part_cap = if config.unbounded_parts {
                a_sum
            } else {
                config.max_a
            };
            match prove_barrier_class(k, a_sum, part_cap) {
                Some(row) => rows.push(row),
                None => d_le_zero_skips += 1,
            }
        }
    }

    write_csv(
        config.out_dir.join("lock1_backward_barrier_classes.csv"),
        &rows,
    )
    .expect("write csv");
    write_json(
        config.out_dir.join("lock1_backward_barrier_summary.json"),
        &config,
        &rows,
        d_le_zero_skips,
    )
    .expect("write json");

    let failed = rows.iter().filter(|row| row.initial_blocked).count();
    println!("Lock 1 backward barrier");
    println!("classes_proved={}", rows.len());
    println!("D_le_zero_skips={}", d_le_zero_skips);
    println!("failed_classes={}", failed);
    println!("wrote: {}", config.out_dir.display());
}
