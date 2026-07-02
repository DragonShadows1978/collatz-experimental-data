use std::collections::HashMap;
use std::env;
use std::time::Instant;

const ALPHA: f64 = 1.5849625007211563;

fn sturmian_credits() -> Vec<i64> {
    (0..53)
        .map(|n| {
            let c = ((n + 1) as f64 * ALPHA).floor() - (n as f64 * ALPHA).floor();
            c as i64
        })
        .collect()
}

fn pow_mod(mut base: u64, mut exp: u64, modulus: u64) -> u64 {
    if modulus == 1 {
        return 0;
    }
    let mut result = 1u64;
    base %= modulus;
    while exp > 0 {
        if exp & 1 == 1 {
            result = ((result as u128 * base as u128) % modulus as u128) as u64;
        }
        base = ((base as u128 * base as u128) % modulus as u128) as u64;
        exp >>= 1;
    }
    result
}

fn mod_inverse(value: u64, modulus: u64) -> u64 {
    let mut t = 0i128;
    let mut new_t = 1i128;
    let mut r = modulus as i128;
    let mut new_r = value as i128;
    while new_r != 0 {
        let q = r / new_r;
        let tmp_t = t;
        t = new_t;
        new_t = tmp_t - q * new_t;
        let tmp_r = r;
        r = new_r;
        new_r = tmp_r - q * new_r;
    }
    if t < 0 {
        t += modulus as i128;
    }
    t as u64
}

fn next_residue(r: u64, a: i64, modulus: u64) -> u64 {
    let val = (3u128 * r as u128 + 1) % modulus as u128;
    let inv = mod_inverse(pow_mod(2, a as u64, modulus), modulus);
    ((val * inv as u128) % modulus as u128) as u64
}

/// Sparse matrix in CSR-like format: vec of (col, val) per row
struct SparseMat {
    n: usize,
    rows: Vec<Vec<(usize, f64)>>,
}

impl SparseMat {
    fn new(n: usize) -> Self {
        Self {
            n,
            rows: vec![Vec::new(); n],
        }
    }

    fn add(&mut self, row: usize, col: usize, val: f64) {
        for entry in self.rows[row].iter_mut() {
            if entry.0 == col {
                entry.1 += val;
                return;
            }
        }
        self.rows[row].push((col, val));
    }

    fn mat_vec(&self, v: &[f64]) -> Vec<f64> {
        let mut result = vec![0.0; self.n];
        for (i, row) in self.rows.iter().enumerate() {
            let mut sum = 0.0;
            for &(col, val) in row {
                sum += val * v[col];
            }
            result[i] = sum;
        }
        result
    }

    fn transpose_mat_vec(&self, v: &[f64]) -> Vec<f64> {
        let mut result = vec![0.0; self.n];
        for (i, row) in self.rows.iter().enumerate() {
            for &(col, val) in row {
                result[col] += val * v[i];
            }
        }
        result
    }

    fn nnz(&self) -> usize {
        self.rows.iter().map(|r| r.len()).sum()
    }
}

fn build_step_sparse(c: i64, corridor: i64, modulus: u64, num_states: usize) -> SparseMat {
    let mut m = SparseMat::new(num_states);
    let mod_usize = modulus as usize;
    for d in 0..=corridor {
        for r in 0..modulus {
            if r == 1 {
                continue;
            }
            let src = d as usize * mod_usize + r as usize;
            let max_a = d + c;
            if max_a < 1 {
                continue;
            }
            let mut valid = Vec::new();
            for a in 1..=max_a {
                let d_next = d + c - a;
                if d_next < 0 || d_next > corridor {
                    continue;
                }
                let r_next = next_residue(r, a, modulus);
                if r_next == 1 {
                    continue;
                }
                valid.push(d_next as usize * mod_usize + r_next as usize);
            }
            let total = max_a as f64;
            for dst in valid {
                m.add(dst, src, 1.0 / total);
            }
        }
    }
    m
}

/// Compose sparse matrices by applying them sequentially to basis vectors
/// Result is stored as a sparse matrix (only keeping nonzero entries)
fn compose_sparse(steps: &[SparseMat], n: usize, tol: f64) -> SparseMat {
    let mut composed = SparseMat::new(n);
    let num_steps = steps.len();

    for col in 0..n {
        // Start with basis vector e_col
        let mut v = vec![0.0; n];
        v[col] = 1.0;

        // Apply each step matrix
        for step in steps.iter() {
            v = step.mat_vec(&v);
        }

        // Store nonzero results
        for (row, &val) in v.iter().enumerate() {
            if val.abs() > tol {
                composed.add(row, col, val);
            }
        }

        if n > 5000 && (col + 1) % 5000 == 0 {
            eprintln!("    composed {}/{} columns", col + 1, n);
        }
    }
    composed
}

/// Power iteration for spectral radius
fn spectral_radius_power_iter(mat: &SparseMat, max_iter: usize, tol: f64) -> f64 {
    let n = mat.n;
    let mut v = vec![1.0 / (n as f64).sqrt(); n];
    let mut lambda = 0.0;

    for _iter in 0..max_iter {
        let w = mat.mat_vec(&v);
        let new_lambda = w.iter().map(|x| x * x).sum::<f64>().sqrt();
        if new_lambda < 1e-30 {
            return 0.0;
        }
        let scale = 1.0 / new_lambda;
        v = w.iter().map(|x| x * scale).collect();
        if (new_lambda - lambda).abs() < tol * new_lambda.max(1e-15) {
            return new_lambda;
        }
        lambda = new_lambda;
    }
    lambda
}

/// Alternative: compute spectral radius without full composition
/// Apply the 53 step matrices sequentially to a vector, repeat
fn spectral_radius_iterative(
    steps: &[SparseMat],
    n: usize,
    heartbeats: usize,
    tol: f64,
) -> f64 {
    let mut v = vec![1.0 / (n as f64).sqrt(); n];
    let mut lambda = 0.0;

    for hb in 0..heartbeats {
        // Apply one full heartbeat (all step matrices)
        for step in steps.iter() {
            v = step.mat_vec(&v);
        }

        let new_lambda = v.iter().map(|x| x * x).sum::<f64>().sqrt();
        if new_lambda < 1e-30 {
            return 0.0;
        }
        let scale = 1.0 / new_lambda;
        v.iter_mut().for_each(|x| *x *= scale);

        if hb > 0 && (new_lambda - lambda).abs() < tol * lambda.max(1e-15) {
            eprintln!(
                "    converged at heartbeat {} (λ={:.12e})",
                hb + 1,
                new_lambda
            );
            return new_lambda;
        }
        lambda = new_lambda;

        if (hb + 1) % 100 == 0 {
            eprintln!(
                "    heartbeat {}: λ={:.12e}",
                hb + 1,
                new_lambda
            );
        }
    }
    lambda
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let mut corridor: i64 = 10;
    let mut m_min: u32 = 1;
    let mut m_max: u32 = 12;
    let mut mode = "iterative".to_string();
    let mut heartbeats: usize = 2000;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--C" => {
                i += 1;
                corridor = args[i].parse().expect("--C");
            }
            "--m-min" => {
                i += 1;
                m_min = args[i].parse().expect("--m-min");
            }
            "--m-max" => {
                i += 1;
                m_max = args[i].parse().expect("--m-max");
            }
            "--mode" => {
                i += 1;
                mode = args[i].clone();
            }
            "--heartbeats" => {
                i += 1;
                heartbeats = args[i].parse().expect("--heartbeats");
            }
            other => panic!("unknown arg: {}", other),
        }
        i += 1;
    }

    let credits = sturmian_credits();
    eprintln!(
        "spectral-radius-sparse C={} m={}..{} mode={} heartbeats={}",
        corridor, m_min, m_max, mode, heartbeats
    );

    println!("m,C,states,nnz_per_step,spectral_radius,gap,mode,time_sec");

    for m in m_min..=m_max {
        let modulus = 3u64.pow(m);
        let num_states = (corridor as usize + 1) * modulus as usize;

        eprintln!("  m={}: {} states, building step matrices...", m, num_states);
        let started = Instant::now();

        // Build all 53 step matrices as sparse
        let step_matrices: Vec<SparseMat> = credits
            .iter()
            .map(|&c| build_step_sparse(c, corridor, modulus, num_states))
            .collect();

        let avg_nnz: usize = step_matrices.iter().map(|s| s.nnz()).sum::<usize>() / 53;
        let density = avg_nnz as f64 / (num_states * num_states) as f64;
        eprintln!(
            "    avg nnz/step: {} ({:.4}% dense), build: {:.1}s",
            avg_nnz,
            density * 100.0,
            started.elapsed().as_secs_f64()
        );

        let sr = if mode == "compose" {
            // Full composition then power iteration
            eprintln!("    composing {} steps...", step_matrices.len());
            let composed = compose_sparse(&step_matrices, num_states, 1e-15);
            eprintln!(
                "    composed nnz: {}, computing spectral radius...",
                composed.nnz()
            );
            spectral_radius_power_iter(&composed, 10000, 1e-12)
        } else {
            // Iterative: apply heartbeats directly (no full composition)
            eprintln!("    running {} heartbeats...", heartbeats);
            spectral_radius_iterative(&step_matrices, num_states, heartbeats, 1e-12)
        };

        let elapsed = started.elapsed().as_secs_f64();
        let gap = 1.0 - sr;

        println!(
            "{},{},{},{},{:.12e},{:.12e},{},{:.1}",
            m, corridor, num_states, avg_nnz, sr, gap, mode, elapsed
        );

        eprintln!(
            "  m={}: ρ={:.10} gap={:.6e} {:.1}s {}",
            m,
            sr,
            gap,
            elapsed,
            if sr < 1.0 { "< 1 ✓" } else { "≥ 1 ✗" }
        );
    }
}
