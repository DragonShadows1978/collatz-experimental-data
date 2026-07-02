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

struct ClassRow {
    k: usize,
    a_sum: usize,
    d: u128,
    factorization: String,
    prefix_modulus: u128,
    final_wall: u128,
    primitive_necklaces: u128,
    pre_final_necklaces: u128,
    final_hits: u128,
    rotation_window_proved: u128,
    rotation_window_unresolved: u128,
    max_rotation_min_quotient: Option<u128>,
    quotient_min: Option<u128>,
    quotient_max: Option<u128>,
    quotient_windows: u128,
    closest_final_distance: Option<u128>,
    closest_final_residue: Option<u128>,
    closest_word: String,
    kernel_rows: Vec<KernelRow>,
}

struct KernelRow {
    k: usize,
    a_sum: usize,
    d: u128,
    factorization: String,
    prefix_modulus: u128,
    final_wall: u128,
    quotient: u128,
    final_residue: u128,
    final_distance: u128,
    rotation_min_quotient: u128,
    word: String,
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

fn canonical_rotation_vec(word: &[usize]) -> Vec<usize> {
    let mut best: Option<Vec<usize>> = None;
    for offset in 0..word.len() {
        let rotated = (0..word.len())
            .map(|index| word[(offset + index) % word.len()])
            .collect::<Vec<_>>();
        if best.as_ref().map(|value| rotated < *value).unwrap_or(true) {
            best = Some(rotated);
        }
    }
    best.unwrap_or_default()
}

fn rotations(word: &[usize]) -> Vec<Vec<usize>> {
    (0..word.len())
        .map(|offset| {
            (0..word.len())
                .map(|index| word[(offset + index) % word.len()])
                .collect::<Vec<_>>()
        })
        .collect()
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

fn offset_for_word(word: &[usize]) -> Option<u128> {
    let mut prefix_sum = 0usize;
    let mut offset = 0u128;
    for &exponent in word {
        let shifted = 1u128.checked_shl(prefix_sum as u32)?;
        offset = offset.checked_mul(3)?.checked_add(shifted)?;
        prefix_sum += exponent;
    }
    Some(offset)
}

fn mine_class(k: usize, a_sum: usize) -> Option<ClassRow> {
    let two_a = 1u128.checked_shl(a_sum as u32)?;
    let three_k = checked_pow(3, k)?;
    if two_a <= three_k {
        return None;
    }
    let d = two_a - three_k;
    let factors = prime_power_factors(d);
    let final_wall = factors.last()?.1;
    let prefix_modulus = d / final_wall;
    let mut row = ClassRow {
        k,
        a_sum,
        d,
        factorization: factor_string(&factors),
        prefix_modulus,
        final_wall,
        primitive_necklaces: 0,
        pre_final_necklaces: 0,
        final_hits: 0,
        rotation_window_proved: 0,
        rotation_window_unresolved: 0,
        max_rotation_min_quotient: None,
        quotient_min: None,
        quotient_max: None,
        quotient_windows: 0,
        closest_final_distance: None,
        closest_final_residue: None,
        closest_word: String::new(),
        kernel_rows: Vec::new(),
    };
    let mut prefix = Vec::new();
    enumerate_words(k, a_sum, &mut prefix, &mut |word| {
        if word.iter().all(|value| *value == 2) || minimal_period(word) != word.len() {
            return;
        }
        let canonical = canonical_rotation_vec(word);
        if canonical.as_slice() != word {
            return;
        }
        row.primitive_necklaces += 1;
        let Some(offset) = offset_for_word(word) else {
            return;
        };
        if offset % prefix_modulus != 0 {
            return;
        }
        row.pre_final_necklaces += 1;
        let quotient = offset / prefix_modulus;
        row.quotient_min = Some(
            row.quotient_min
                .map(|value| value.min(quotient))
                .unwrap_or(quotient),
        );
        row.quotient_max = Some(
            row.quotient_max
                .map(|value| value.max(quotient))
                .unwrap_or(quotient),
        );
        let residue = quotient % final_wall;
        if residue == 0 {
            row.final_hits += 1;
        }
        let rotation_min = rotations(word)
            .iter()
            .filter_map(|rotation| {
                let offset = offset_for_word(rotation)?;
                if offset % prefix_modulus == 0 {
                    Some(offset / prefix_modulus)
                } else {
                    None
                }
            })
            .min();
        if let Some(rotation_min) = rotation_min {
            row.max_rotation_min_quotient = Some(
                row.max_rotation_min_quotient
                    .map(|value| value.max(rotation_min))
                    .unwrap_or(rotation_min),
            );
            if rotation_min > 0 && rotation_min < final_wall {
                row.rotation_window_proved += 1;
            } else {
                row.rotation_window_unresolved += 1;
                row.kernel_rows.push(KernelRow {
                    k,
                    a_sum,
                    d,
                    factorization: row.factorization.clone(),
                    prefix_modulus,
                    final_wall,
                    quotient,
                    final_residue: residue,
                    final_distance: residue.min(final_wall - residue),
                    rotation_min_quotient: rotation_min,
                    word: word_string(word),
                });
            }
        } else {
            row.rotation_window_unresolved += 1;
            row.kernel_rows.push(KernelRow {
                k,
                a_sum,
                d,
                factorization: row.factorization.clone(),
                prefix_modulus,
                final_wall,
                quotient,
                final_residue: residue,
                final_distance: residue.min(final_wall - residue),
                rotation_min_quotient: 0,
                word: word_string(word),
            });
        }
        let distance = residue.min(final_wall - residue);
        if row.closest_final_distance.is_none() || Some(distance) < row.closest_final_distance {
            row.closest_final_distance = Some(distance);
            row.closest_final_residue = Some(residue);
            row.closest_word = word_string(word);
        }
    });
    if let (Some(minimum), Some(maximum)) = (row.quotient_min, row.quotient_max) {
        row.quotient_windows = maximum / final_wall - minimum / final_wall + 1;
    }
    Some(row)
}

fn write_csv(path: PathBuf, rows: &[ClassRow]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "k,A,D,D_factorization,prefix_modulus,final_wall,primitive_necklaces,pre_final_necklaces,final_hits,rotation_window_proved,rotation_window_unresolved,max_rotation_min_quotient,quotient_min,quotient_max,quotient_windows,closest_final_distance,closest_final_residue,closest_word"
    )?;
    for row in rows {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},\"{}\"",
            row.k,
            row.a_sum,
            row.d,
            row.factorization,
            row.prefix_modulus,
            row.final_wall,
            row.primitive_necklaces,
            row.pre_final_necklaces,
            row.final_hits,
            row.rotation_window_proved,
            row.rotation_window_unresolved,
            row.max_rotation_min_quotient
                .map(|value| value.to_string())
                .unwrap_or_default(),
            row.quotient_min
                .map(|value| value.to_string())
                .unwrap_or_default(),
            row.quotient_max
                .map(|value| value.to_string())
                .unwrap_or_default(),
            row.quotient_windows,
            row.closest_final_distance
                .map(|value| value.to_string())
                .unwrap_or_default(),
            row.closest_final_residue
                .map(|value| value.to_string())
                .unwrap_or_default(),
            row.closest_word
        )?;
    }
    Ok(())
}

fn write_kernel_csv(path: PathBuf, rows: &[ClassRow]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "k,A,D,D_factorization,prefix_modulus,final_wall,quotient,final_residue,final_distance,rotation_min_quotient,word"
    )?;
    for row in rows {
        for kernel in &row.kernel_rows {
            writeln!(
                file,
                "{},{},{},{},{},{},{},{},{},{},\"{}\"",
                kernel.k,
                kernel.a_sum,
                kernel.d,
                kernel.factorization,
                kernel.prefix_modulus,
                kernel.final_wall,
                kernel.quotient,
                kernel.final_residue,
                kernel.final_distance,
                kernel.rotation_min_quotient,
                kernel.word
            )?;
        }
    }
    Ok(())
}

fn write_summary(path: PathBuf, config: &Config, rows: &[ClassRow]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    let pre_final_classes = rows
        .iter()
        .filter(|row| row.pre_final_necklaces != 0)
        .count();
    let final_hit_classes = rows.iter().filter(|row| row.final_hits != 0).count();
    let rotation_window_unresolved_classes = rows
        .iter()
        .filter(|row| row.rotation_window_unresolved != 0)
        .count();
    let rotation_window_proved_necklaces = rows.iter().fold(0u128, |acc, row| {
        acc.saturating_add(row.rotation_window_proved)
    });
    let rotation_window_unresolved_necklaces = rows.iter().fold(0u128, |acc, row| {
        acc.saturating_add(row.rotation_window_unresolved)
    });
    let max_pre_final = rows
        .iter()
        .map(|row| row.pre_final_necklaces)
        .max()
        .unwrap_or(0);
    let max_windows = rows
        .iter()
        .map(|row| row.quotient_windows)
        .max()
        .unwrap_or(0);
    writeln!(file, "{{")?;
    writeln!(file, "  \"miner\": \"lock1_final_wall_quotient_miner\",")?;
    writeln!(file, "  \"max_k\": {},", config.max_k)?;
    writeln!(file, "  \"max_total_a\": {},", config.max_total_a)?;
    writeln!(file, "  \"classes\": {},", rows.len())?;
    writeln!(file, "  \"pre_final_classes\": {},", pre_final_classes)?;
    writeln!(file, "  \"final_hit_classes\": {},", final_hit_classes)?;
    writeln!(
        file,
        "  \"rotation_window_unresolved_classes\": {},",
        rotation_window_unresolved_classes
    )?;
    writeln!(
        file,
        "  \"rotation_window_proved_necklaces\": \"{}\",",
        rotation_window_proved_necklaces
    )?;
    writeln!(
        file,
        "  \"rotation_window_unresolved_necklaces\": \"{}\",",
        rotation_window_unresolved_necklaces
    )?;
    writeln!(
        file,
        "  \"max_pre_final_necklaces\": \"{}\",",
        max_pre_final
    )?;
    writeln!(file, "  \"max_quotient_windows\": \"{}\"", max_windows)?;
    writeln!(file, "}}")?;
    Ok(())
}

fn main() {
    let config = parse_args();
    create_dir_all(&config.out_dir).expect("create out dir");
    let mut rows = Vec::new();
    for k in 1..=config.max_k {
        for a_sum in k..=config.max_total_a {
            if let Some(row) = mine_class(k, a_sum) {
                rows.push(row);
            }
        }
    }
    write_csv(config.out_dir.join("lock1_final_wall_quotients.csv"), &rows).expect("write csv");
    write_kernel_csv(
        config
            .out_dir
            .join("lock1_rotation_window_unresolved_kernel.csv"),
        &rows,
    )
    .expect("write kernel csv");
    write_summary(
        config
            .out_dir
            .join("lock1_final_wall_quotient_summary.json"),
        &config,
        &rows,
    )
    .expect("write summary");
    let final_hit_classes = rows.iter().filter(|row| row.final_hits != 0).count();
    println!("Lock 1 final wall quotient miner");
    println!("classes={}", rows.len());
    println!("final_hit_classes={}", final_hit_classes);
    println!("wrote: {}", config.out_dir.display());
}
