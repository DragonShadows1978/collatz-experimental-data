use std::collections::BTreeMap;
use std::env;
use std::fs::{create_dir_all, File};
use std::io::{BufWriter, Write};
use std::path::PathBuf;

#[derive(Clone)]
struct Config {
    max_k: usize,
    max_total_a: usize,
    out_dir: PathBuf,
}

#[derive(Default)]
struct FactorWitnessStats {
    rows: u64,
    words: u128,
    zero_residue_words: u128,
    witness_counts: BTreeMap<u128, u128>,
    witness_modulus_counts: BTreeMap<u128, u128>,
    example: String,
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

fn prime_power_factors(mut value: u128) -> Vec<(u128, u128)> {
    let mut factors = Vec::new();
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

fn factor_string(factors: &[(u128, u128)]) -> String {
    factors
        .iter()
        .map(|(prime, power)| format!("{}:{}", prime, power))
        .collect::<Vec<_>>()
        .join(";")
}

fn word_string(word: &[usize]) -> String {
    word.iter()
        .map(|value| value.to_string())
        .collect::<Vec<_>>()
        .join(" ")
}

fn counts_string(values: &BTreeMap<u128, u128>) -> String {
    values
        .iter()
        .map(|(key, count)| format!("{}:{}", key, count))
        .collect::<Vec<_>>()
        .join(";")
}

fn enumerate_words(
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
        enumerate_words(slots - 1, total - part, prefix, callback);
        prefix.pop();
    }
}

fn witness_for_word(word: &[usize], d: u128, factors: &[(u128, u128)]) -> (u128, u128, u128) {
    let pow2 = pow2_table(word.iter().sum(), d);
    let mut prefix_sum = 0usize;
    let mut residue = 0u128;
    for &exponent in word {
        residue = add_mod(mul_mod(residue, 3, d), pow2[prefix_sum], d);
        prefix_sum += exponent;
    }
    if residue == 0 {
        return (0, 0, 0);
    }
    for &(prime, power) in factors {
        if residue % power != 0 {
            return (prime, power, residue);
        }
    }
    (0, 0, residue)
}

fn mine_class(
    k: usize,
    a_sum: usize,
    stats: &mut BTreeMap<(usize, usize, u128), FactorWitnessStats>,
) {
    let Some(two_a) = 1u128.checked_shl(a_sum as u32) else {
        return;
    };
    let Some(three_k) = checked_pow(3, k) else {
        return;
    };
    if two_a <= three_k {
        return;
    }
    let d = two_a - three_k;
    let factors = prime_power_factors(d);
    let key = (k, a_sum, d);
    let mut prefix = Vec::new();
    enumerate_words(k, a_sum, &mut prefix, &mut |word| {
        if word.iter().all(|value| *value == 2) {
            return;
        }
        let (prime, power, residue) = witness_for_word(word, d, &factors);
        let entry = stats.entry(key).or_default();
        entry.rows += 1;
        entry.words += 1;
        if residue == 0 {
            entry.zero_residue_words += 1;
        }
        *entry.witness_counts.entry(prime).or_insert(0) += 1;
        *entry.witness_modulus_counts.entry(power).or_insert(0) += 1;
        if entry.example.is_empty() {
            entry.example = word_string(word);
        }
    });
}

fn write_csv(
    path: PathBuf,
    stats: &BTreeMap<(usize, usize, u128), FactorWitnessStats>,
) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "k,A,D,D_factorization,non_all2_words,zero_residue_words,witness_prime_counts,witness_modulus_counts,example"
    )?;
    for ((k, a_sum, d), row) in stats {
        let factors = prime_power_factors(*d);
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},\"{}\"",
            k,
            a_sum,
            d,
            factor_string(&factors),
            row.words,
            row.zero_residue_words,
            counts_string(&row.witness_counts),
            counts_string(&row.witness_modulus_counts),
            row.example
        )?;
    }
    Ok(())
}

fn main() {
    let config = parse_args();
    create_dir_all(&config.out_dir).expect("create out dir");
    let mut stats = BTreeMap::new();
    for k in 1..=config.max_k {
        for a_sum in k..=config.max_total_a {
            mine_class(k, a_sum, &mut stats);
        }
    }
    let zero_classes = stats
        .values()
        .filter(|row| row.zero_residue_words != 0)
        .count();
    write_csv(config.out_dir.join("lock1_barrier_witnesses.csv"), &stats).expect("write csv");
    let mut summary = BufWriter::new(
        File::create(config.out_dir.join("lock1_barrier_witness_summary.json")).unwrap(),
    );
    writeln!(summary, "{{").unwrap();
    writeln!(summary, "  \"miner\": \"lock1_barrier_witness_miner\",").unwrap();
    writeln!(summary, "  \"max_k\": {},", config.max_k).unwrap();
    writeln!(summary, "  \"max_total_a\": {},", config.max_total_a).unwrap();
    writeln!(summary, "  \"classes\": {},", stats.len()).unwrap();
    writeln!(summary, "  \"zero_residue_classes\": {}", zero_classes).unwrap();
    writeln!(summary, "}}").unwrap();
    println!("Lock 1 barrier witness miner");
    println!("classes={}", stats.len());
    println!("zero_residue_classes={}", zero_classes);
    println!("wrote: {}", config.out_dir.display());
}
