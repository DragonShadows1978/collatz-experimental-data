use std::collections::{BTreeMap, BTreeSet};
use std::env;
use std::fs::{create_dir_all, read_to_string, File};
use std::io::{BufWriter, Write};
use std::path::PathBuf;

#[derive(Clone)]
struct Config {
    inputs: Vec<PathBuf>,
    candidate_inputs: Vec<PathBuf>,
    out_dir: PathBuf,
}

#[derive(Clone)]
struct NearMissRow {
    source: String,
    word: Vec<usize>,
    a_sum: usize,
    k: usize,
    b: u128,
    d: u128,
    gcd: u128,
    q: u128,
    remainder: u128,
    rho: u128,
    phase_distance: u128,
    primitive: Vec<usize>,
    primitive_reps: usize,
    canonical_rotation: Vec<usize>,
    rotation_offset: usize,
    sturmian_gap: i64,
}

#[derive(Default)]
struct CandidateCounts {
    trivial: u64,
    nontrivial: u64,
    exact_failures: u64,
    rotation_failures: u64,
    other: u64,
}

#[derive(Default)]
struct GroupSummary {
    count: usize,
    min_k: usize,
    max_k: usize,
    min_a: usize,
    max_a: usize,
    sources: BTreeSet<String>,
    q_values: BTreeSet<u128>,
    rho_counts: BTreeMap<u128, usize>,
    distance_counts: BTreeMap<u128, usize>,
    reps: BTreeSet<usize>,
    sturmian_gaps: BTreeSet<i64>,
    examples: Vec<String>,
}

fn parse_args() -> Config {
    let mut inputs = Vec::new();
    let mut candidate_inputs = Vec::new();
    let mut out_dir = None;
    let args: Vec<String> = env::args().collect();
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--input" => {
                i += 1;
                inputs.push(PathBuf::from(&args[i]));
            }
            "--candidate-input" => {
                i += 1;
                candidate_inputs.push(PathBuf::from(&args[i]));
            }
            "--out-dir" => {
                i += 1;
                out_dir = Some(PathBuf::from(&args[i]));
            }
            other => panic!("unknown arg: {}", other),
        }
        i += 1;
    }
    if inputs.is_empty() {
        panic!("at least one --input near-miss CSV is required");
    }
    Config {
        inputs,
        candidate_inputs,
        out_dir: out_dir.expect("--out-dir is required"),
    }
}

fn gcd(mut lhs: u128, mut rhs: u128) -> u128 {
    while rhs != 0 {
        let next = lhs % rhs;
        lhs = rhs;
        rhs = next;
    }
    lhs
}

fn word_string(word: &[usize]) -> String {
    word.iter()
        .map(|value| value.to_string())
        .collect::<Vec<_>>()
        .join(" ")
}

fn parse_word(value: &str) -> Vec<usize> {
    if value.trim().is_empty() {
        return Vec::new();
    }
    value
        .split_whitespace()
        .map(|part| part.parse().expect("word exponent integer"))
        .collect()
}

fn primitive_block(word: &[usize]) -> (Vec<usize>, usize) {
    for period in 1..=word.len() {
        if word.len() % period != 0 {
            continue;
        }
        let primitive = &word[..period];
        if word.chunks(period).all(|chunk| chunk == primitive) {
            return (primitive.to_vec(), word.len() / period);
        }
    }
    (word.to_vec(), 1)
}

fn rotate(word: &[usize], offset: usize) -> Vec<usize> {
    word[offset..]
        .iter()
        .chain(word[..offset].iter())
        .copied()
        .collect()
}

fn canonical_rotation(word: &[usize]) -> (Vec<usize>, usize) {
    let mut best = word.to_vec();
    let mut best_offset = 0usize;
    for offset in 1..word.len() {
        let candidate = rotate(word, offset);
        if candidate < best {
            best = candidate;
            best_offset = offset;
        }
    }
    (best, best_offset)
}

fn sturmian_gap(k: usize, a_sum: usize) -> i64 {
    const ALPHA: f64 = 1.584_962_500_721_156_3;
    a_sum as i64 - (k as f64 * ALPHA).floor() as i64
}

fn csv_escape(value: &str) -> String {
    if value.contains(',') || value.contains('"') || value.contains('\n') {
        format!("\"{}\"", value.replace('"', "\"\""))
    } else {
        value.to_string()
    }
}

fn parse_near_miss_file(path: &PathBuf) -> Vec<NearMissRow> {
    let text = read_to_string(path).expect("read near-miss CSV");
    let source = path.display().to_string();
    let mut rows = Vec::new();
    for (line_idx, line) in text.lines().enumerate() {
        if line_idx == 0 || line.trim().is_empty() {
            continue;
        }
        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() != 11 {
            panic!(
                "unexpected near-miss CSV field count {} in {} line {}",
                fields.len(),
                source,
                line_idx + 1
            );
        }
        let word = parse_word(fields[0]);
        let a_sum = fields[1].parse().expect("A integer");
        let k = fields[2].parse().expect("k integer");
        let b = fields[3].parse().expect("B integer");
        let d = fields[4].parse().expect("D integer");
        let gcd_value: u128 = fields[5].parse().expect("gcd integer");
        let q: u128 = fields[6].parse().expect("D/gcd integer");
        let remainder: u128 = fields[7].parse().expect("remainder integer");
        let checked_gcd = gcd(b, d);
        if checked_gcd != gcd_value || d / checked_gcd != q {
            panic!(
                "near-miss gcd/q mismatch in {} line {}",
                source,
                line_idx + 1
            );
        }
        let rho = (remainder / gcd_value) % q;
        let phase_distance = rho.min(q - rho);
        let (primitive, primitive_reps) = primitive_block(&word);
        let (canonical_rotation, rotation_offset) = canonical_rotation(&primitive);
        rows.push(NearMissRow {
            source: source.clone(),
            word,
            a_sum,
            k,
            b,
            d,
            gcd: gcd_value,
            q,
            remainder,
            rho,
            phase_distance,
            primitive,
            primitive_reps,
            canonical_rotation,
            rotation_offset,
            sturmian_gap: sturmian_gap(k, a_sum),
        });
    }
    rows
}

fn parse_candidate_counts(paths: &[PathBuf]) -> CandidateCounts {
    let mut counts = CandidateCounts::default();
    for path in paths {
        let text = read_to_string(path).expect("read candidate CSV");
        for (line_idx, line) in text.lines().enumerate() {
            if line_idx == 0 || line.trim().is_empty() {
                continue;
            }
            let fields: Vec<&str> = line.split(',').collect();
            if fields.len() < 8 {
                counts.other += 1;
                continue;
            }
            match fields[7] {
                "trivial_cycle" => counts.trivial += 1,
                "nontrivial_cycle" => counts.nontrivial += 1,
                "exact_word_failure" => counts.exact_failures += 1,
                "rotation_failure" => counts.rotation_failures += 1,
                _ => counts.other += 1,
            }
        }
    }
    counts
}

fn add_group_row(summary: &mut GroupSummary, row: &NearMissRow) {
    if summary.count == 0 {
        summary.min_k = row.k;
        summary.max_k = row.k;
        summary.min_a = row.a_sum;
        summary.max_a = row.a_sum;
    } else {
        summary.min_k = summary.min_k.min(row.k);
        summary.max_k = summary.max_k.max(row.k);
        summary.min_a = summary.min_a.min(row.a_sum);
        summary.max_a = summary.max_a.max(row.a_sum);
    }
    summary.count += 1;
    summary.sources.insert(row.source.clone());
    summary.q_values.insert(row.q);
    *summary.rho_counts.entry(row.rho).or_insert(0) += 1;
    *summary
        .distance_counts
        .entry(row.phase_distance)
        .or_insert(0) += 1;
    summary.reps.insert(row.primitive_reps);
    summary.sturmian_gaps.insert(row.sturmian_gap);
    if summary.examples.len() < 5 {
        summary.examples.push(word_string(&row.word));
    }
}

fn u128_set_string(values: &BTreeSet<u128>) -> String {
    values
        .iter()
        .map(|value| value.to_string())
        .collect::<Vec<_>>()
        .join(" ")
}

fn usize_set_string(values: &BTreeSet<usize>) -> String {
    values
        .iter()
        .map(|value| value.to_string())
        .collect::<Vec<_>>()
        .join(" ")
}

fn i64_set_string(values: &BTreeSet<i64>) -> String {
    values
        .iter()
        .map(|value| value.to_string())
        .collect::<Vec<_>>()
        .join(" ")
}

fn map_string(values: &BTreeMap<u128, usize>) -> String {
    values
        .iter()
        .map(|(key, value)| format!("{}:{}", key, value))
        .collect::<Vec<_>>()
        .join(";")
}

fn write_q_phase_summary(path: PathBuf, rows: &[NearMissRow]) -> std::io::Result<()> {
    let mut groups: BTreeMap<u128, GroupSummary> = BTreeMap::new();
    for row in rows {
        add_group_row(groups.entry(row.q).or_default(), row);
    }
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "q,count,min_k,max_k,min_A,max_A,rho_counts,phase_distance_counts,sturmian_gaps,example_words"
    )?;
    for (q, summary) in groups {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{}",
            q,
            summary.count,
            summary.min_k,
            summary.max_k,
            summary.min_a,
            summary.max_a,
            csv_escape(&map_string(&summary.rho_counts)),
            csv_escape(&map_string(&summary.distance_counts)),
            csv_escape(&i64_set_string(&summary.sturmian_gaps)),
            csv_escape(&summary.examples.join(" | "))
        )?;
    }
    Ok(())
}

fn write_primitive_summary(path: PathBuf, rows: &[NearMissRow]) -> std::io::Result<()> {
    let mut groups: BTreeMap<String, GroupSummary> = BTreeMap::new();
    for row in rows {
        let key = word_string(&row.primitive);
        add_group_row(groups.entry(key).or_default(), row);
    }
    let mut entries: Vec<(String, GroupSummary)> = groups.into_iter().collect();
    entries.sort_by(|lhs, rhs| {
        rhs.1
            .count
            .cmp(&lhs.1.count)
            .then_with(|| lhs.0.cmp(&rhs.0))
    });
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "primitive_word,count,min_k,max_k,min_A,max_A,q_values,rho_counts,phase_distance_counts,repetitions,sturmian_gaps,examples"
    )?;
    for (primitive, summary) in entries {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{}",
            csv_escape(&primitive),
            summary.count,
            summary.min_k,
            summary.max_k,
            summary.min_a,
            summary.max_a,
            csv_escape(&u128_set_string(&summary.q_values)),
            csv_escape(&map_string(&summary.rho_counts)),
            csv_escape(&map_string(&summary.distance_counts)),
            csv_escape(&usize_set_string(&summary.reps)),
            csv_escape(&i64_set_string(&summary.sturmian_gaps)),
            csv_escape(&summary.examples.join(" | "))
        )?;
    }
    Ok(())
}

fn write_rotation_summary(path: PathBuf, rows: &[NearMissRow]) -> std::io::Result<()> {
    let mut groups: BTreeMap<String, GroupSummary> = BTreeMap::new();
    for row in rows {
        let key = word_string(&row.canonical_rotation);
        add_group_row(groups.entry(key).or_default(), row);
    }
    let mut entries: Vec<(String, GroupSummary)> = groups.into_iter().collect();
    entries.sort_by(|lhs, rhs| {
        rhs.1
            .count
            .cmp(&lhs.1.count)
            .then_with(|| lhs.0.cmp(&rhs.0))
    });
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "canonical_rotation,count,min_k,max_k,min_A,max_A,q_values,rho_counts,phase_distance_counts,repetitions,sturmian_gaps,examples"
    )?;
    for (rotation, summary) in entries {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{}",
            csv_escape(&rotation),
            summary.count,
            summary.min_k,
            summary.max_k,
            summary.min_a,
            summary.max_a,
            csv_escape(&u128_set_string(&summary.q_values)),
            csv_escape(&map_string(&summary.rho_counts)),
            csv_escape(&map_string(&summary.distance_counts)),
            csv_escape(&usize_set_string(&summary.reps)),
            csv_escape(&i64_set_string(&summary.sturmian_gaps)),
            csv_escape(&summary.examples.join(" | "))
        )?;
    }
    Ok(())
}

fn write_row_enriched(path: PathBuf, rows: &[NearMissRow]) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "source,word,A,k,B,D,gcd,q,rho,phase_distance,remainder,primitive_word,primitive_reps,canonical_rotation,rotation_offset,sturmian_gap"
    )?;
    for row in rows {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            csv_escape(&row.source),
            csv_escape(&word_string(&row.word)),
            row.a_sum,
            row.k,
            row.b,
            row.d,
            row.gcd,
            row.q,
            row.rho,
            row.phase_distance,
            row.remainder,
            csv_escape(&word_string(&row.primitive)),
            row.primitive_reps,
            csv_escape(&word_string(&row.canonical_rotation)),
            row.rotation_offset,
            row.sturmian_gap
        )?;
    }
    Ok(())
}

fn write_theorem_notes(
    path: PathBuf,
    rows: &[NearMissRow],
    candidate_counts: &CandidateCounts,
) -> std::io::Result<()> {
    let mut q_counts: BTreeMap<u128, usize> = BTreeMap::new();
    let mut zero_phase = 0usize;
    let mut q_one = 0usize;
    for row in rows {
        *q_counts.entry(row.q).or_insert(0) += 1;
        zero_phase += usize::from(row.rho == 0);
        q_one += usize::from(row.q == 1);
    }
    let mut q_entries: Vec<(u128, usize)> = q_counts.into_iter().collect();
    q_entries.sort_by(|lhs, rhs| rhs.1.cmp(&lhs.1).then_with(|| lhs.0.cmp(&rhs.0)));
    let top_q = q_entries
        .iter()
        .take(12)
        .map(|(q, count)| format!("{} ({})", q, count))
        .collect::<Vec<_>>()
        .join(", ");

    let mut file = BufWriter::new(File::create(path)?);
    writeln!(file, "# Lock 1 Proof-Miner Notes")?;
    writeln!(file)?;
    writeln!(file, "Rows analyzed: {}", rows.len())?;
    writeln!(
        file,
        "Candidate trivial cycles: {}",
        candidate_counts.trivial
    )?;
    writeln!(
        file,
        "Candidate nontrivial cycles: {}",
        candidate_counts.nontrivial
    )?;
    writeln!(
        file,
        "Candidate exact-word failures: {}",
        candidate_counts.exact_failures
    )?;
    writeln!(
        file,
        "Candidate rotation failures: {}",
        candidate_counts.rotation_failures
    )?;
    writeln!(file)?;
    writeln!(file, "Observed obstruction variables:")?;
    writeln!(file)?;
    writeln!(file, "```text")?;
    writeln!(file, "D = 2^A - 3^k")?;
    writeln!(file, "g = gcd(B_w, D)")?;
    writeln!(file, "q = D / g")?;
    writeln!(file, "rho = (B_w / g) mod q")?;
    writeln!(file, "loop requires q = 1, equivalently rho = 0 mod q")?;
    writeln!(file, "```")?;
    writeln!(file)?;
    writeln!(file, "Near-miss rows with q=1: {}", q_one)?;
    writeln!(file, "Near-miss rows with rho=0: {}", zero_phase)?;
    writeln!(file, "Most common q values: {}", top_q)?;
    writeln!(file)?;
    writeln!(file, "Proof target suggested by mined data:")?;
    writeln!(file)?;
    writeln!(
        file,
        "For every non-all-2 exponent word with D > 0, prove q(w) = D/gcd(B_w,D) > 1."
    )?;
    writeln!(
        file,
        "Equivalently, prove the reduced phase rho(w) never vanishes. The output CSVs group the phase by primitive block and rotation class."
    )?;
    Ok(())
}

fn write_summary_json(
    path: PathBuf,
    rows: &[NearMissRow],
    candidate_counts: &CandidateCounts,
    config: &Config,
) -> std::io::Result<()> {
    let min_q = rows.iter().map(|row| row.q).min().unwrap_or(0);
    let max_q = rows.iter().map(|row| row.q).max().unwrap_or(0);
    let q_one = rows.iter().filter(|row| row.q == 1).count();
    let zero_phase = rows.iter().filter(|row| row.rho == 0).count();
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(file, "{{")?;
    writeln!(file, "  \"miner\": \"lock1_proof_miner\",")?;
    writeln!(file, "  \"input_files\": [")?;
    for (idx, input) in config.inputs.iter().enumerate() {
        let comma = if idx + 1 == config.inputs.len() {
            ""
        } else {
            ","
        };
        writeln!(file, "    \"{}\"{}", input.display(), comma)?;
    }
    writeln!(file, "  ],")?;
    writeln!(file, "  \"near_miss_rows\": {},", rows.len())?;
    writeln!(file, "  \"min_q\": {},", min_q)?;
    writeln!(file, "  \"max_q\": {},", max_q)?;
    writeln!(file, "  \"q_equals_1_rows\": {},", q_one)?;
    writeln!(file, "  \"rho_equals_0_rows\": {},", zero_phase)?;
    writeln!(
        file,
        "  \"candidate_trivial_cycles\": {},",
        candidate_counts.trivial
    )?;
    writeln!(
        file,
        "  \"candidate_nontrivial_cycles\": {},",
        candidate_counts.nontrivial
    )?;
    writeln!(
        file,
        "  \"candidate_exact_word_failures\": {},",
        candidate_counts.exact_failures
    )?;
    writeln!(
        file,
        "  \"candidate_rotation_failures\": {},",
        candidate_counts.rotation_failures
    )?;
    writeln!(
        file,
        "  \"claim_status_for_mined_rows\": \"{}\"",
        if q_one == 0 && zero_phase == 0 && candidate_counts.nontrivial == 0 {
            "no_reduced_closure_phase_seen"
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
    for input in &config.inputs {
        rows.extend(parse_near_miss_file(input));
    }
    let candidate_counts = parse_candidate_counts(&config.candidate_inputs);

    write_row_enriched(config.out_dir.join("lock1_near_miss_enriched.csv"), &rows)
        .expect("write enriched rows");
    write_q_phase_summary(config.out_dir.join("lock1_q_phase_summary.csv"), &rows)
        .expect("write q phase summary");
    write_primitive_summary(
        config.out_dir.join("lock1_primitive_family_summary.csv"),
        &rows,
    )
    .expect("write primitive summary");
    write_rotation_summary(
        config.out_dir.join("lock1_rotation_class_summary.csv"),
        &rows,
    )
    .expect("write rotation summary");
    write_theorem_notes(
        config.out_dir.join("LOCK1_PROOF_MINER_NOTES.md"),
        &rows,
        &candidate_counts,
    )
    .expect("write theorem notes");
    write_summary_json(
        config.out_dir.join("lock1_proof_miner_summary.json"),
        &rows,
        &candidate_counts,
        &config,
    )
    .expect("write summary json");

    println!("Lock 1 proof miner");
    println!("near_miss_rows={}", rows.len());
    println!(
        "candidate_nontrivial_cycles={}",
        candidate_counts.nontrivial
    );
    println!(
        "q_equals_1_rows={}",
        rows.iter().filter(|row| row.q == 1).count()
    );
    println!(
        "rho_equals_0_rows={}",
        rows.iter().filter(|row| row.rho == 0).count()
    );
    println!("wrote: {}", config.out_dir.display());
}
