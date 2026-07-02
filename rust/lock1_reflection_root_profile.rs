use std::collections::HashSet;
use std::env;
use std::fs::{create_dir_all, File};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::path::PathBuf;

#[derive(Clone)]
struct Config {
    input: PathBuf,
    out_dir: PathBuf,
    min_ratio: u128,
}

#[derive(Clone)]
struct KernelRow {
    k: usize,
    a_sum: usize,
    final_wall: u128,
    rotation_min_quotient: u128,
    word: Vec<usize>,
}

struct ProfileRow {
    k: usize,
    a_sum: usize,
    final_wall: u128,
    word: String,
    rotation_min_quotient: u128,
    z: u128,
    value_at_z: u128,
    value_at_z_inverse: u128,
    root_count: usize,
    reverse_root_count: usize,
    reciprocal_root_count: usize,
    common_reverse_roots: usize,
    common_reciprocal_roots: usize,
    inverse_closed_roots: usize,
    gcd_reciprocal_degree: isize,
    gcd_reverse_degree: isize,
    reverse_inverse_match: bool,
    reciprocal_inverse_match: bool,
    dihedral_self_reflective: bool,
    roots: Vec<u128>,
    reverse_roots: Vec<u128>,
}

fn parse_args() -> Config {
    let mut input = None;
    let mut out_dir = None;
    let mut min_ratio = 3u128;
    let args: Vec<String> = env::args().collect();
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--input" => {
                i += 1;
                input = Some(PathBuf::from(&args[i]));
            }
            "--out-dir" => {
                i += 1;
                out_dir = Some(PathBuf::from(&args[i]));
            }
            "--min-ratio" => {
                i += 1;
                min_ratio = args[i].parse().expect("--min-ratio integer");
            }
            other => panic!("unknown arg: {}", other),
        }
        i += 1;
    }
    Config {
        input: input.expect("--input is required"),
        out_dir: out_dir.expect("--out-dir is required"),
        min_ratio,
    }
}

fn parse_word(raw: &str) -> Vec<usize> {
    raw.trim_matches('"')
        .split_whitespace()
        .map(|part| part.parse().expect("word exponent"))
        .collect()
}

fn parse_kernel_line(line: &str) -> Option<KernelRow> {
    let (prefix, word_raw) = line.rsplit_once(",\"")?;
    let cols = prefix.split(',').collect::<Vec<_>>();
    if cols.len() != 10 {
        return None;
    }
    Some(KernelRow {
        k: cols[0].parse().ok()?,
        a_sum: cols[1].parse().ok()?,
        final_wall: cols[5].parse().ok()?,
        rotation_min_quotient: cols[9].parse().ok()?,
        word: parse_word(word_raw),
    })
}

fn read_kernel(path: &PathBuf) -> Vec<KernelRow> {
    let file = File::open(path).expect("open input csv");
    let reader = BufReader::new(file);
    reader
        .lines()
        .skip(1)
        .filter_map(|line| parse_kernel_line(&line.expect("read line")))
        .collect()
}

fn egcd(a: i128, b: i128) -> (i128, i128, i128) {
    if b == 0 {
        (a, 1, 0)
    } else {
        let (g, x, y) = egcd(b, a % b);
        (g, y, x - (a / b) * y)
    }
}

fn inv_mod(value: u128, modulus: u128) -> Option<u128> {
    let (g, x, _) = egcd(value as i128, modulus as i128);
    if g != 1 {
        return None;
    }
    let m = modulus as i128;
    Some(((x % m + m) % m) as u128)
}

fn pow_mod(mut base: u128, mut exp: usize, modulus: u128) -> u128 {
    let mut acc = 1u128 % modulus;
    base %= modulus;
    while exp > 0 {
        if exp & 1 == 1 {
            acc = (acc * base) % modulus;
        }
        exp >>= 1;
        if exp > 0 {
            base = (base * base) % modulus;
        }
    }
    acc
}

fn normalized_coeffs(word: &[usize], modulus: u128) -> Vec<u128> {
    let inv2 = inv_mod(2, modulus).expect("2 invertible");
    let mut coeffs = Vec::with_capacity(word.len());
    let mut prefix_sum = 0isize;
    for (index, exponent) in word.iter().enumerate() {
        let delta = prefix_sum - (2 * index) as isize;
        let coeff = if delta >= 0 {
            pow_mod(2, delta as usize, modulus)
        } else {
            pow_mod(inv2, (-delta) as usize, modulus)
        };
        coeffs.push(coeff);
        prefix_sum += *exponent as isize;
    }
    coeffs
}

fn eval_poly(coeffs: &[u128], x: u128, modulus: u128) -> u128 {
    let mut acc = 0u128;
    for coeff in coeffs.iter().rev() {
        acc = (acc * x + *coeff) % modulus;
    }
    acc
}

fn trim_poly(poly: &mut Vec<u128>) {
    while poly.last().copied() == Some(0) {
        poly.pop();
    }
}

fn poly_degree(poly: &[u128]) -> isize {
    for index in (0..poly.len()).rev() {
        if poly[index] != 0 {
            return index as isize;
        }
    }
    -1
}

fn poly_rem(mut lhs: Vec<u128>, rhs: &[u128], modulus: u128) -> Vec<u128> {
    let rhs_degree = poly_degree(rhs);
    if rhs_degree < 0 {
        panic!("division by zero polynomial");
    }
    let rhs_lead = rhs[rhs_degree as usize];
    let rhs_lead_inv = inv_mod(rhs_lead, modulus).expect("invert leading coefficient");
    while poly_degree(&lhs) >= rhs_degree {
        let lhs_degree = poly_degree(&lhs) as usize;
        let shift = lhs_degree - rhs_degree as usize;
        let scale = (lhs[lhs_degree] * rhs_lead_inv) % modulus;
        for (index, coeff) in rhs.iter().enumerate().take(rhs_degree as usize + 1) {
            let target = index + shift;
            let subtrahend = (scale * *coeff) % modulus;
            lhs[target] = (lhs[target] + modulus - subtrahend) % modulus;
        }
        trim_poly(&mut lhs);
    }
    lhs
}

fn poly_gcd_degree(lhs: &[u128], rhs: &[u128], modulus: u128) -> isize {
    let mut a = lhs.to_vec();
    let mut b = rhs.to_vec();
    trim_poly(&mut a);
    trim_poly(&mut b);
    while poly_degree(&b) >= 0 {
        let rem = poly_rem(a, &b, modulus);
        a = b;
        b = rem;
    }
    poly_degree(&a)
}

fn find_roots(coeffs: &[u128], modulus: u128) -> Vec<u128> {
    let mut found = Vec::new();
    for x in 0..modulus {
        if eval_poly(coeffs, x, modulus) == 0 {
            found.push(x);
        }
    }
    found
}

fn rotations(word: &[usize]) -> Vec<Vec<usize>> {
    (0..word.len())
        .map(|offset| {
            (0..word.len())
                .map(|index| word[(offset + index) % word.len()])
                .collect()
        })
        .collect()
}

fn canonical_rotation_vec(word: &[usize]) -> Vec<usize> {
    rotations(word).into_iter().min().unwrap_or_default()
}

fn dihedral_self_reflective(word: &[usize]) -> bool {
    let canonical = canonical_rotation_vec(word);
    let mut reversed = word.to_vec();
    reversed.reverse();
    canonical_rotation_vec(&reversed) == canonical
}

fn set(values: &[u128]) -> HashSet<u128> {
    values.iter().copied().collect()
}

fn inverse_image(values: &[u128], modulus: u128) -> Option<HashSet<u128>> {
    let mut image = HashSet::new();
    for value in values {
        image.insert(inv_mod(*value, modulus)?);
    }
    Some(image)
}

fn profile(row: &KernelRow, min_ratio: u128) -> Option<ProfileRow> {
    let q = row.final_wall;
    if row.rotation_min_quotient < min_ratio * q {
        return None;
    }
    let coeffs = normalized_coeffs(&row.word, q);
    let mut reversed = row.word.clone();
    reversed.reverse();
    let reverse_coeffs = normalized_coeffs(&reversed, q);
    let reciprocal_coeffs = coeffs.iter().rev().copied().collect::<Vec<_>>();
    let roots = find_roots(&coeffs, q);
    let reverse_roots = find_roots(&reverse_coeffs, q);
    let reciprocal_roots = find_roots(&reciprocal_coeffs, q);
    let root_set = set(&roots);
    let reverse_set = set(&reverse_roots);
    let reciprocal_set = set(&reciprocal_roots);
    let inverse_set = inverse_image(&roots, q).unwrap_or_default();
    let reverse_inverse_match = reverse_set == inverse_set;
    let reciprocal_inverse_match = reciprocal_set == inverse_set;
    let inverse_closed_roots = roots
        .iter()
        .filter(|root| {
            inv_mod(**root, q)
                .map(|inv| root_set.contains(&inv))
                .unwrap_or(false)
        })
        .count();
    let z = (4 * inv_mod(3, q).expect("3 invertible")) % q;
    let z_inverse = inv_mod(z, q).expect("z invertible");
    Some(ProfileRow {
        k: row.k,
        a_sum: row.a_sum,
        final_wall: q,
        word: row
            .word
            .iter()
            .map(|value| value.to_string())
            .collect::<Vec<_>>()
            .join(" "),
        rotation_min_quotient: row.rotation_min_quotient,
        z,
        value_at_z: eval_poly(&coeffs, z, q),
        value_at_z_inverse: eval_poly(&coeffs, z_inverse, q),
        root_count: roots.len(),
        reverse_root_count: reverse_roots.len(),
        reciprocal_root_count: reciprocal_roots.len(),
        common_reverse_roots: root_set.intersection(&reverse_set).count(),
        common_reciprocal_roots: root_set.intersection(&reciprocal_set).count(),
        inverse_closed_roots,
        gcd_reciprocal_degree: poly_gcd_degree(&coeffs, &reciprocal_coeffs, q),
        gcd_reverse_degree: poly_gcd_degree(&coeffs, &reverse_coeffs, q),
        reverse_inverse_match,
        reciprocal_inverse_match,
        dihedral_self_reflective: dihedral_self_reflective(&row.word),
        roots,
        reverse_roots,
    })
}

fn root_string(values: &[u128]) -> String {
    values
        .iter()
        .map(|value| value.to_string())
        .collect::<Vec<_>>()
        .join(";")
}

fn write_profiles(path: PathBuf, rows: &[ProfileRow]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "k,A,final_wall,rotation_min_quotient,z,value_at_z,value_at_z_inverse,root_count,reverse_root_count,reciprocal_root_count,common_reverse_roots,common_reciprocal_roots,inverse_closed_roots,gcd_reciprocal_degree,gcd_reverse_degree,reverse_inverse_match,reciprocal_inverse_match,dihedral_self_reflective,roots,reverse_roots,word"
    )?;
    for row in rows {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},\"{}\",\"{}\",\"{}\"",
            row.k,
            row.a_sum,
            row.final_wall,
            row.rotation_min_quotient,
            row.z,
            row.value_at_z,
            row.value_at_z_inverse,
            row.root_count,
            row.reverse_root_count,
            row.reciprocal_root_count,
            row.common_reverse_roots,
            row.common_reciprocal_roots,
            row.inverse_closed_roots,
            row.gcd_reciprocal_degree,
            row.gcd_reverse_degree,
            row.reverse_inverse_match,
            row.reciprocal_inverse_match,
            row.dihedral_self_reflective,
            root_string(&row.roots),
            root_string(&row.reverse_roots),
            row.word
        )?;
    }
    Ok(())
}

fn write_summary(path: PathBuf, input_rows: usize, rows: &[ProfileRow]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    let nonzero_roots = rows.iter().filter(|row| row.root_count != 0).count();
    let reverse_inverse_matches = rows.iter().filter(|row| row.reverse_inverse_match).count();
    let reciprocal_inverse_matches = rows
        .iter()
        .filter(|row| row.reciprocal_inverse_match)
        .count();
    let dihedral_self_reflective = rows
        .iter()
        .filter(|row| row.dihedral_self_reflective)
        .count();
    let z_roots = rows.iter().filter(|row| row.value_at_z == 0).count();
    let z_inverse_roots = rows
        .iter()
        .filter(|row| row.value_at_z_inverse == 0)
        .count();
    let reciprocal_gcd_hits = rows
        .iter()
        .filter(|row| row.gcd_reciprocal_degree > 0)
        .count();
    let reverse_gcd_hits = rows.iter().filter(|row| row.gcd_reverse_degree > 0).count();
    writeln!(file, "{{")?;
    writeln!(file, "  \"miner\": \"lock1_reflection_root_profile\",")?;
    writeln!(file, "  \"input_kernel_rows\": {},", input_rows)?;
    writeln!(file, "  \"min_value_survivor_rows\": {},", rows.len())?;
    writeln!(file, "  \"rows_with_roots\": {},", nonzero_roots)?;
    writeln!(file, "  \"z_root_rows\": {},", z_roots)?;
    writeln!(file, "  \"z_inverse_root_rows\": {},", z_inverse_roots)?;
    writeln!(
        file,
        "  \"reverse_inverse_match_rows\": {},",
        reverse_inverse_matches
    )?;
    writeln!(
        file,
        "  \"reciprocal_inverse_match_rows\": {},",
        reciprocal_inverse_matches
    )?;
    writeln!(
        file,
        "  \"reciprocal_gcd_positive_rows\": {},",
        reciprocal_gcd_hits
    )?;
    writeln!(
        file,
        "  \"reverse_gcd_positive_rows\": {},",
        reverse_gcd_hits
    )?;
    writeln!(
        file,
        "  \"dihedral_self_reflective_rows\": {}",
        dihedral_self_reflective
    )?;
    writeln!(file, "}}")?;
    Ok(())
}

fn main() {
    let config = parse_args();
    create_dir_all(&config.out_dir).expect("create out dir");
    let rows = read_kernel(&config.input);
    let profiles = rows
        .iter()
        .filter_map(|row| profile(row, config.min_ratio))
        .collect::<Vec<_>>();
    write_profiles(
        config.out_dir.join("lock1_reflection_root_profiles.csv"),
        &profiles,
    )
    .expect("write profiles");
    write_summary(
        config.out_dir.join("lock1_reflection_root_summary.json"),
        rows.len(),
        &profiles,
    )
    .expect("write summary");
    println!("Lock 1 reflection root profile");
    println!("input_kernel_rows={}", rows.len());
    println!("min_value_survivor_rows={}", profiles.len());
    println!("wrote: {}", config.out_dir.display());
}
