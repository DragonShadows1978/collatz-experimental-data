use std::collections::{BTreeMap, HashSet};
use std::env;
use std::fs::{create_dir_all, File};
use std::hash::{Hash, Hasher};
use std::io::{BufWriter, Write};
use std::path::PathBuf;

#[derive(Clone)]
struct Config {
    max_k: usize,
    max_total_a: usize,
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

struct ShapeRow {
    k: usize,
    a_sum: usize,
    d: u128,
    layer: usize,
    states: usize,
    false_states: usize,
    true_states: usize,
    prefix_sums: usize,
    residues: usize,
    min_prefix_sum: usize,
    max_prefix_sum: usize,
    has_initial_false: bool,
    has_initial_true: bool,
    false_prefix_counts: String,
    true_prefix_counts: String,
}

fn parse_args() -> Config {
    let mut max_k = None;
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
    Config {
        max_k: max_k.expect("--max-k is required"),
        max_total_a: max_total_a.expect("--max-total-a is required"),
        out_dir: out_dir.expect("--out-dir is required"),
    }
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

fn can_finish(prefix_sum: usize, used_slots: usize, k: usize, a_sum: usize) -> bool {
    if prefix_sum < used_slots {
        return false;
    }
    let remaining = k - used_slots;
    prefix_sum + remaining <= a_sum
}

fn counts_string(values: &BTreeMap<usize, usize>) -> String {
    values
        .iter()
        .map(|(key, count)| format!("{}:{}", key, count))
        .collect::<Vec<_>>()
        .join(";")
}

fn layer_shape(k: usize, a_sum: usize, d: u128, layer: usize, states: &HashSet<State>) -> ShapeRow {
    let mut false_prefix = BTreeMap::new();
    let mut true_prefix = BTreeMap::new();
    let mut prefixes = HashSet::new();
    let mut residues = HashSet::new();
    let mut min_prefix = usize::MAX;
    let mut max_prefix = 0usize;
    let mut false_states = 0usize;
    let mut true_states = 0usize;
    for state in states {
        prefixes.insert(state.prefix_sum);
        residues.insert(state.residue);
        min_prefix = min_prefix.min(state.prefix_sum);
        max_prefix = max_prefix.max(state.prefix_sum);
        if state.non_all2 {
            true_states += 1;
            *true_prefix.entry(state.prefix_sum).or_insert(0) += 1;
        } else {
            false_states += 1;
            *false_prefix.entry(state.prefix_sum).or_insert(0) += 1;
        }
    }
    ShapeRow {
        k,
        a_sum,
        d,
        layer,
        states: states.len(),
        false_states,
        true_states,
        prefix_sums: prefixes.len(),
        residues: residues.len(),
        min_prefix_sum: if states.is_empty() { 0 } else { min_prefix },
        max_prefix_sum: max_prefix,
        has_initial_false: states.contains(&State {
            prefix_sum: 0,
            residue: 0,
            non_all2: false,
        }),
        has_initial_true: states.contains(&State {
            prefix_sum: 0,
            residue: 0,
            non_all2: true,
        }),
        false_prefix_counts: counts_string(&false_prefix),
        true_prefix_counts: counts_string(&true_prefix),
    }
}

fn mine_class(k: usize, a_sum: usize) -> Option<Vec<ShapeRow>> {
    let two_a = 1u128.checked_shl(a_sum as u32)?;
    let three_k = checked_pow(3, k)?;
    if two_a <= three_k {
        return None;
    }
    let d = two_a - three_k;
    let inv3 = inv3_mod(d)?;
    let pow2 = pow2_table(a_sum, d);
    let mut rows = Vec::new();
    let mut barrier = HashSet::new();
    barrier.insert(State {
        prefix_sum: a_sum,
        residue: 0,
        non_all2: true,
    });
    rows.push(layer_shape(k, a_sum, d, k, &barrier));
    for position in (0..k).rev() {
        let mut previous = HashSet::new();
        for state in &barrier {
            for exponent in 1..=state.prefix_sum {
                let previous_sum = state.prefix_sum - exponent;
                if !can_finish(previous_sum, position, k, a_sum) {
                    continue;
                }
                let residue_without_offset = sub_mod(state.residue, pow2[previous_sum], d);
                let previous_residue = mul_mod(residue_without_offset, inv3, d);
                if state.non_all2 {
                    previous.insert(State {
                        prefix_sum: previous_sum,
                        residue: previous_residue,
                        non_all2: true,
                    });
                    if exponent != 2 {
                        previous.insert(State {
                            prefix_sum: previous_sum,
                            residue: previous_residue,
                            non_all2: false,
                        });
                    }
                } else if exponent == 2 {
                    previous.insert(State {
                        prefix_sum: previous_sum,
                        residue: previous_residue,
                        non_all2: false,
                    });
                }
            }
        }
        rows.push(layer_shape(k, a_sum, d, position, &previous));
        barrier = previous;
    }
    rows.sort_by(|lhs, rhs| lhs.layer.cmp(&rhs.layer));
    Some(rows)
}

fn write_rows(path: PathBuf, rows: &[ShapeRow]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "k,A,D,layer,states,false_states,true_states,prefix_sums,residues,min_prefix_sum,max_prefix_sum,has_initial_false,has_initial_true,false_prefix_counts,true_prefix_counts"
    )?;
    for row in rows {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{},\"{}\",\"{}\"",
            row.k,
            row.a_sum,
            row.d,
            row.layer,
            row.states,
            row.false_states,
            row.true_states,
            row.prefix_sums,
            row.residues,
            row.min_prefix_sum,
            row.max_prefix_sum,
            row.has_initial_false,
            row.has_initial_true,
            row.false_prefix_counts,
            row.true_prefix_counts
        )?;
    }
    Ok(())
}

fn main() {
    let config = parse_args();
    create_dir_all(&config.out_dir).expect("create out dir");
    let mut rows = Vec::new();
    let mut classes = 0usize;
    let mut failed_initial = 0usize;
    for k in 1..=config.max_k {
        for a_sum in k..=config.max_total_a {
            if let Some(mut class_rows) = mine_class(k, a_sum) {
                classes += 1;
                if class_rows
                    .iter()
                    .any(|row| row.layer == 0 && row.has_initial_false)
                {
                    failed_initial += 1;
                }
                rows.append(&mut class_rows);
            }
        }
    }
    write_rows(config.out_dir.join("lock1_barrier_shapes.csv"), &rows).expect("write rows");
    let mut summary = BufWriter::new(
        File::create(config.out_dir.join("lock1_barrier_shape_summary.json")).unwrap(),
    );
    writeln!(summary, "{{").unwrap();
    writeln!(summary, "  \"miner\": \"lock1_barrier_shape_miner\",").unwrap();
    writeln!(summary, "  \"max_k\": {},", config.max_k).unwrap();
    writeln!(summary, "  \"max_total_a\": {},", config.max_total_a).unwrap();
    writeln!(summary, "  \"classes\": {},", classes).unwrap();
    writeln!(summary, "  \"failed_initial_classes\": {}", failed_initial).unwrap();
    writeln!(summary, "}}").unwrap();
    println!("Lock 1 barrier shape miner");
    println!("classes={}", classes);
    println!("failed_initial_classes={}", failed_initial);
    println!("wrote: {}", config.out_dir.display());
}
