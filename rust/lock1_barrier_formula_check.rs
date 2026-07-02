use std::collections::HashSet;
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

#[derive(Default)]
struct CheckRow {
    k: usize,
    a_sum: usize,
    d: u128,
    layer: usize,
    recursive_states: usize,
    formula_states: usize,
    missing_from_formula: usize,
    extra_in_formula: usize,
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

fn pow_mod(mut base: u128, mut exponent: usize, modulus: u128) -> u128 {
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

fn recursive_layers(k: usize, a_sum: usize, d: u128) -> Vec<HashSet<State>> {
    let inv3 = inv3_mod(d).expect("D is coprime to 3");
    let pow2 = pow2_table(a_sum, d);
    let mut layers = vec![HashSet::new(); k + 1];
    layers[k].insert(State {
        prefix_sum: a_sum,
        residue: 0,
        non_all2: true,
    });
    for position in (0..k).rev() {
        let mut previous = HashSet::new();
        for state in &layers[position + 1] {
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
        layers[position] = previous;
    }
    layers
}

fn enumerate_suffixes(
    slots: usize,
    total: usize,
    prefix: &mut Vec<usize>,
    callback: &mut impl FnMut(&[usize]),
) {
    if slots == 0 {
        if total == 0 {
            callback(prefix);
        }
        return;
    }
    if total < slots {
        return;
    }
    let max_part = total - (slots - 1);
    for part in 1..=max_part {
        prefix.push(part);
        enumerate_suffixes(slots - 1, total - part, prefix, callback);
        prefix.pop();
    }
}

fn suffix_offset_mod(word: &[usize], modulus: u128) -> u128 {
    let mut prefix_sum = 0usize;
    let mut offset = 0u128;
    let pow2 = pow2_table(word.iter().sum(), modulus);
    for &exponent in word {
        offset = add_mod(mul_mod(offset, 3, modulus), pow2[prefix_sum], modulus);
        prefix_sum += exponent;
    }
    offset
}

fn formula_layer(k: usize, a_sum: usize, d: u128, layer: usize) -> HashSet<State> {
    let suffix_slots = k - layer;
    let inv_3n = pow_mod(inv3_mod(d).expect("D is coprime to 3"), suffix_slots, d);
    let pow2 = pow2_table(a_sum, d);
    let mut states = HashSet::new();
    let min_prefix_sum = layer;
    let max_prefix_sum = a_sum - suffix_slots;
    for prefix_sum in min_prefix_sum..=max_prefix_sum {
        let suffix_total = a_sum - prefix_sum;
        let mut suffix = Vec::new();
        enumerate_suffixes(suffix_slots, suffix_total, &mut suffix, &mut |word| {
            let suffix_offset = suffix_offset_mod(word, d);
            let scaled_offset = mul_mod(pow2[prefix_sum], suffix_offset, d);
            let residue = if scaled_offset == 0 {
                0
            } else {
                d - mul_mod(inv_3n, scaled_offset, d)
            };
            let suffix_non_all2 = word.iter().any(|value| *value != 2);
            if suffix_non_all2 {
                states.insert(State {
                    prefix_sum,
                    residue,
                    non_all2: false,
                });
                states.insert(State {
                    prefix_sum,
                    residue,
                    non_all2: true,
                });
            } else {
                states.insert(State {
                    prefix_sum,
                    residue,
                    non_all2: true,
                });
            }
        });
    }
    states
}

fn check_class(k: usize, a_sum: usize) -> Option<Vec<CheckRow>> {
    let two_a = 1u128.checked_shl(a_sum as u32)?;
    let three_k = checked_pow(3, k)?;
    if two_a <= three_k {
        return None;
    }
    let d = two_a - three_k;
    let recursive = recursive_layers(k, a_sum, d);
    let mut rows = Vec::new();
    for (layer, recursive_states) in recursive.iter().enumerate() {
        let formula_states = formula_layer(k, a_sum, d, layer);
        let missing = recursive_states.difference(&formula_states).count();
        let extra = formula_states.difference(recursive_states).count();
        rows.push(CheckRow {
            k,
            a_sum,
            d,
            layer,
            recursive_states: recursive_states.len(),
            formula_states: formula_states.len(),
            missing_from_formula: missing,
            extra_in_formula: extra,
        });
    }
    Some(rows)
}

fn write_rows(path: PathBuf, rows: &[CheckRow]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "k,A,D,layer,recursive_states,formula_states,missing_from_formula,extra_in_formula"
    )?;
    for row in rows {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{}",
            row.k,
            row.a_sum,
            row.d,
            row.layer,
            row.recursive_states,
            row.formula_states,
            row.missing_from_formula,
            row.extra_in_formula
        )?;
    }
    Ok(())
}

fn main() {
    let config = parse_args();
    create_dir_all(&config.out_dir).expect("create out dir");
    let mut rows = Vec::new();
    let mut classes = 0usize;
    for k in 1..=config.max_k {
        for a_sum in k..=config.max_total_a {
            if let Some(mut class_rows) = check_class(k, a_sum) {
                classes += 1;
                rows.append(&mut class_rows);
            }
        }
    }
    let mismatched_layers = rows
        .iter()
        .filter(|row| row.missing_from_formula != 0 || row.extra_in_formula != 0)
        .count();
    write_rows(
        config.out_dir.join("lock1_barrier_formula_check.csv"),
        &rows,
    )
    .expect("write rows");
    let mut summary = BufWriter::new(
        File::create(
            config
                .out_dir
                .join("lock1_barrier_formula_check_summary.json"),
        )
        .unwrap(),
    );
    writeln!(summary, "{{").unwrap();
    writeln!(summary, "  \"checker\": \"lock1_barrier_formula_check\",").unwrap();
    writeln!(summary, "  \"max_k\": {},", config.max_k).unwrap();
    writeln!(summary, "  \"max_total_a\": {},", config.max_total_a).unwrap();
    writeln!(summary, "  \"classes\": {},", classes).unwrap();
    writeln!(summary, "  \"layers\": {},", rows.len()).unwrap();
    writeln!(summary, "  \"mismatched_layers\": {}", mismatched_layers).unwrap();
    writeln!(summary, "}}").unwrap();
    println!("Lock 1 barrier formula check");
    println!("classes={}", classes);
    println!("layers={}", rows.len());
    println!("mismatched_layers={}", mismatched_layers);
    println!("wrote: {}", config.out_dir.display());
}
