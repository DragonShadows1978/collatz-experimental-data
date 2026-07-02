use std::collections::BTreeMap;
use std::env;
use std::fs::{create_dir_all, File};
use std::io::{BufWriter, Write};
use std::path::PathBuf;

#[derive(Clone)]
struct Config {
    k: usize,
    a_sum: usize,
    out_dir: PathBuf,
}

fn parse_args() -> Config {
    let mut k = None;
    let mut a_sum = None;
    let mut out_dir = None;
    let args: Vec<String> = env::args().collect();
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--k" => {
                i += 1;
                k = Some(args[i].parse().expect("--k integer"));
            }
            "--a" | "--A" => {
                i += 1;
                a_sum = Some(args[i].parse().expect("--a integer"));
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
        k: k.expect("--k is required"),
        a_sum: a_sum.expect("--a is required"),
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

fn minimal_period(word: &[usize]) -> usize {
    for period in 1..=word.len() {
        if word.len() % period != 0 {
            continue;
        }
        let mut ok = true;
        for i in period..word.len() {
            if word[i] != word[i % period] {
                ok = false;
                break;
            }
        }
        if ok {
            return period;
        }
    }
    word.len()
}

fn canonical_rotation(word: &[usize]) -> String {
    let mut best: Option<Vec<usize>> = None;
    for offset in 0..word.len() {
        let rotated = (0..word.len())
            .map(|index| word[(offset + index) % word.len()])
            .collect::<Vec<_>>();
        if best.as_ref().map(|value| rotated < *value).unwrap_or(true) {
            best = Some(rotated);
        }
    }
    word_string(&best.unwrap_or_default())
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

fn write_summary(
    path: PathBuf,
    config: &Config,
    d: u128,
    factors: &[(u128, u128)],
    candidates: usize,
    period_counts: &BTreeMap<usize, usize>,
    rotation_counts: &BTreeMap<String, usize>,
    zero_final_residue: usize,
) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    let period_text = period_counts
        .iter()
        .map(|(period, count)| format!("{}:{}", period, count))
        .collect::<Vec<_>>()
        .join(";");
    let mut rotation_rows = rotation_counts
        .iter()
        .map(|(rotation, count)| (*count, rotation.clone()))
        .collect::<Vec<_>>();
    rotation_rows.sort_by(|lhs, rhs| rhs.0.cmp(&lhs.0).then(lhs.1.cmp(&rhs.1)));
    let top_rotations = rotation_rows
        .iter()
        .take(10)
        .map(|(count, rotation)| format!("{}:{}", rotation, count))
        .collect::<Vec<_>>()
        .join(";");
    writeln!(file, "{{")?;
    writeln!(file, "  \"miner\": \"lock1_cascade_survivor_dump\",")?;
    writeln!(file, "  \"k\": {},", config.k)?;
    writeln!(file, "  \"A\": {},", config.a_sum)?;
    writeln!(file, "  \"D\": \"{}\",", d)?;
    writeln!(
        file,
        "  \"D_factorization\": \"{}\",",
        factor_string(factors)
    )?;
    writeln!(file, "  \"pre_final_candidates\": {},", candidates)?;
    writeln!(file, "  \"zero_final_residue\": {},", zero_final_residue)?;
    writeln!(file, "  \"period_counts\": \"{}\",", period_text)?;
    writeln!(file, "  \"rotation_classes\": {},", rotation_counts.len())?;
    writeln!(file, "  \"top_rotation_classes\": \"{}\"", top_rotations)?;
    writeln!(file, "}}")?;
    Ok(())
}

fn main() {
    let config = parse_args();
    create_dir_all(&config.out_dir).expect("create out dir");
    let two_a = 1u128
        .checked_shl(config.a_sum as u32)
        .expect("A too large for u128 shift");
    let three_k = checked_pow(3, config.k).expect("3^k overflow");
    if two_a <= three_k {
        panic!("class is not contractive: 2^A <= 3^k");
    }
    let d = two_a - three_k;
    let factors = prime_power_factors(d);
    if factors.is_empty() {
        panic!("D has no odd prime-power factors");
    }
    let final_wall = factors.last().unwrap().1;
    let prefix_walls = factors
        .iter()
        .take(factors.len().saturating_sub(1))
        .map(|(_, power)| *power)
        .collect::<Vec<_>>();
    let pow2 = pow2_table(config.a_sum, d);

    let mut candidates = Vec::new();
    let mut period_counts = BTreeMap::new();
    let mut rotation_counts = BTreeMap::new();
    let mut zero_final_residue = 0usize;
    let mut prefix = Vec::new();
    enumerate_words(config.k, config.a_sum, &mut prefix, &mut |word| {
        if word.iter().all(|value| *value == 2) {
            return;
        }
        let residue = residue_for_word(word, d, &pow2);
        if prefix_walls.iter().any(|wall| residue % *wall != 0) {
            return;
        }
        let final_residue = residue % final_wall;
        if final_residue == 0 {
            zero_final_residue += 1;
        }
        let period = minimal_period(word);
        *period_counts.entry(period).or_insert(0) += 1;
        let rotation = canonical_rotation(word);
        *rotation_counts.entry(rotation.clone()).or_insert(0) += 1;
        candidates.push((
            final_residue,
            final_residue.min(final_wall - final_residue),
            period,
            signature(word),
            rotation,
            word_string(word),
        ));
    });
    candidates.sort_by(|lhs, rhs| lhs.1.cmp(&rhs.1).then(lhs.0.cmp(&rhs.0)));

    let mut file =
        BufWriter::new(File::create(config.out_dir.join("lock1_pre_final_survivors.csv")).unwrap());
    writeln!(
        file,
        "k,A,D,D_factorization,final_wall,final_residue,final_distance,minimal_period,signature,rotation_class,word"
    )
    .unwrap();
    for (final_residue, final_distance, period, sig, rotation, word) in &candidates {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},\"{}\",\"{}\",\"{}\"",
            config.k,
            config.a_sum,
            d,
            factor_string(&factors),
            final_wall,
            final_residue,
            final_distance,
            period,
            sig,
            rotation,
            word
        )
        .unwrap();
    }

    write_summary(
        config
            .out_dir
            .join("lock1_pre_final_survivors_summary.json"),
        &config,
        d,
        &factors,
        candidates.len(),
        &period_counts,
        &rotation_counts,
        zero_final_residue,
    )
    .expect("write summary");

    println!("Lock 1 cascade survivor dump");
    println!("k={} A={} D={}", config.k, config.a_sum, d);
    println!("D_factorization={}", factor_string(&factors));
    println!("pre_final_candidates={}", candidates.len());
    println!("zero_final_residue={}", zero_final_residue);
    println!("wrote: {}", config.out_dir.display());
}
