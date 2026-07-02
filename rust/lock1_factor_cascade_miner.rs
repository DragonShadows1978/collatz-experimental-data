use std::collections::{BTreeMap, BinaryHeap};
use std::env;
use std::fs::{create_dir_all, File};
use std::io::{BufWriter, Write};
use std::path::PathBuf;

#[derive(Clone)]
struct Config {
    max_k: usize,
    max_total_a: usize,
    example_limit: usize,
    out_dir: PathBuf,
}

#[derive(Clone)]
struct FactorLayer {
    factor_index: usize,
    prime: u128,
    prime_power: u128,
    space_words: u128,
    blocked_words: u128,
    survivor_words: u128,
    closest_nonzero_distance: Option<u128>,
    closest_nonzero_residue: Option<u128>,
    closest_nonzero_word: String,
    survivor_signatures: BTreeMap<String, u128>,
    survivor_examples: Vec<String>,
}

#[derive(Clone)]
struct ClassCascade {
    k: usize,
    a_sum: usize,
    d: u128,
    factorization: String,
    non_all2_words: u128,
    zero_residue_words: u128,
    final_survivor_words: u128,
    layers: Vec<FactorLayer>,
}

fn parse_args() -> Config {
    let mut max_k = None;
    let mut max_total_a = None;
    let mut example_limit = 5usize;
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
            "--example-limit" => {
                i += 1;
                example_limit = args[i].parse().expect("--example-limit integer");
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
        example_limit,
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

fn signature(word: &[usize]) -> String {
    let mut prefix_dev = 0i64;
    let mut min_dev = 0i64;
    let mut max_dev = 0i64;
    for &part in word {
        prefix_dev += part as i64 - 2;
        min_dev = min_dev.min(prefix_dev);
        max_dev = max_dev.max(prefix_dev);
    }
    format!("final={},min={},max={}", prefix_dev, min_dev, max_dev)
}

fn top_signatures(values: &BTreeMap<String, u128>, limit: usize) -> String {
    let mut heap = BinaryHeap::new();
    for (key, count) in values {
        heap.push((*count, key.clone()));
    }
    let mut parts = Vec::new();
    for _ in 0..limit {
        let Some((count, key)) = heap.pop() else {
            break;
        };
        parts.push(format!("{}:{}", key, count));
    }
    parts.join(";")
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

fn residue_for_word(word: &[usize], d: u128, pow2: &[u128]) -> u128 {
    let mut prefix_sum = 0usize;
    let mut residue = 0u128;
    for &exponent in word {
        residue = add_mod(mul_mod(residue, 3, d), pow2[prefix_sum], d);
        prefix_sum += exponent;
    }
    residue
}

fn mine_class(k: usize, a_sum: usize, example_limit: usize) -> Option<ClassCascade> {
    let two_a = 1u128.checked_shl(a_sum as u32)?;
    let three_k = checked_pow(3, k)?;
    if two_a <= three_k {
        return None;
    }
    let d = two_a - three_k;
    let factors = prime_power_factors(d);
    let pow2 = pow2_table(a_sum, d);
    let mut layers = factors
        .iter()
        .enumerate()
        .map(|(index, (prime, prime_power))| FactorLayer {
            factor_index: index + 1,
            prime: *prime,
            prime_power: *prime_power,
            space_words: 0,
            blocked_words: 0,
            survivor_words: 0,
            closest_nonzero_distance: None,
            closest_nonzero_residue: None,
            closest_nonzero_word: String::new(),
            survivor_signatures: BTreeMap::new(),
            survivor_examples: Vec::new(),
        })
        .collect::<Vec<_>>();

    let mut non_all2_words = 0u128;
    let mut zero_residue_words = 0u128;
    let mut prefix = Vec::new();
    enumerate_words(k, a_sum, &mut prefix, &mut |word| {
        if word.iter().all(|value| *value == 2) {
            return;
        }
        non_all2_words += 1;
        let residue = residue_for_word(word, d, &pow2);
        if residue == 0 {
            zero_residue_words += 1;
        }
        let mut alive = true;
        for layer in &mut layers {
            if !alive {
                break;
            }
            layer.space_words += 1;
            let wall_residue = residue % layer.prime_power;
            if wall_residue == 0 {
                layer.survivor_words += 1;
                let sig = signature(word);
                *layer.survivor_signatures.entry(sig).or_insert(0) += 1;
                if layer.survivor_examples.len() < example_limit {
                    layer.survivor_examples.push(word_string(word));
                }
            } else {
                let distance = wall_residue.min(layer.prime_power - wall_residue);
                if layer.closest_nonzero_distance.is_none()
                    || Some(distance) < layer.closest_nonzero_distance
                {
                    layer.closest_nonzero_distance = Some(distance);
                    layer.closest_nonzero_residue = Some(wall_residue);
                    layer.closest_nonzero_word = word_string(word);
                }
                layer.blocked_words += 1;
                alive = false;
            }
        }
    });

    let final_survivor_words = layers
        .last()
        .map(|layer| layer.survivor_words)
        .unwrap_or(non_all2_words);
    Some(ClassCascade {
        k,
        a_sum,
        d,
        factorization: factor_string(&factors),
        non_all2_words,
        zero_residue_words,
        final_survivor_words,
        layers,
    })
}

fn write_csv(path: PathBuf, rows: &[ClassCascade]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "k,A,D,D_factorization,non_all2_words,zero_residue_words,factor_index,prime,prime_power,space_words,blocked_words,survivor_words,closest_nonzero_distance,closest_nonzero_residue,closest_nonzero_word,top_survivor_signatures,survivor_examples"
    )?;
    for row in rows {
        for layer in &row.layers {
            writeln!(
                file,
                "{},{},{},{},{},{},{},{},{},{},{},{},{},{},\"{}\",\"{}\",\"{}\"",
                row.k,
                row.a_sum,
                row.d,
                row.factorization,
                row.non_all2_words,
                row.zero_residue_words,
                layer.factor_index,
                layer.prime,
                layer.prime_power,
                layer.space_words,
                layer.blocked_words,
                layer.survivor_words,
                layer
                    .closest_nonzero_distance
                    .map(|value| value.to_string())
                    .unwrap_or_default(),
                layer
                    .closest_nonzero_residue
                    .map(|value| value.to_string())
                    .unwrap_or_default(),
                layer.closest_nonzero_word,
                top_signatures(&layer.survivor_signatures, 5),
                layer.survivor_examples.join(";")
            )?;
        }
    }
    Ok(())
}

fn write_summary(path: PathBuf, config: &Config, rows: &[ClassCascade]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    let zero_residue_classes = rows
        .iter()
        .filter(|row| row.zero_residue_words != 0)
        .count();
    let max_final_survivors = rows
        .iter()
        .map(|row| row.final_survivor_words)
        .max()
        .unwrap_or(0);
    let total_layers = rows.iter().map(|row| row.layers.len()).sum::<usize>();
    writeln!(file, "{{")?;
    writeln!(file, "  \"miner\": \"lock1_factor_cascade_miner\",")?;
    writeln!(file, "  \"max_k\": {},", config.max_k)?;
    writeln!(file, "  \"max_total_a\": {},", config.max_total_a)?;
    writeln!(file, "  \"classes\": {},", rows.len())?;
    writeln!(file, "  \"factor_layers\": {},", total_layers)?;
    writeln!(
        file,
        "  \"zero_residue_classes\": {},",
        zero_residue_classes
    )?;
    writeln!(
        file,
        "  \"max_final_survivor_words\": \"{}\"",
        max_final_survivors
    )?;
    writeln!(file, "}}")?;
    Ok(())
}

fn main() {
    let config = parse_args();
    create_dir_all(&config.out_dir).expect("create out dir");
    let mut rows = Vec::new();
    for k in 1..=config.max_k {
        for a_sum in k..=config.max_total_a {
            if let Some(row) = mine_class(k, a_sum, config.example_limit) {
                rows.push(row);
            }
        }
    }
    write_csv(config.out_dir.join("lock1_factor_cascade.csv"), &rows).expect("write csv");
    write_summary(
        config.out_dir.join("lock1_factor_cascade_summary.json"),
        &config,
        &rows,
    )
    .expect("write summary");

    let zero_residue_classes = rows
        .iter()
        .filter(|row| row.zero_residue_words != 0)
        .count();
    println!("Lock 1 factor cascade miner");
    println!("classes={}", rows.len());
    println!("zero_residue_classes={}", zero_residue_classes);
    println!("wrote: {}", config.out_dir.display());
}
