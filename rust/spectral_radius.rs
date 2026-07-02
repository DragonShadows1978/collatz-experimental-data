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

struct Mat {
    n: usize,
    data: Vec<f64>,
}

impl Mat {
    fn zeros(n: usize) -> Self {
        Self { n, data: vec![0.0; n * n] }
    }

    fn identity(n: usize) -> Self {
        let mut m = Self::zeros(n);
        for i in 0..n {
            m.data[i * n + i] = 1.0;
        }
        m
    }

    fn add(&mut self, row: usize, col: usize, val: f64) {
        self.data[row * self.n + col] += val;
    }

    fn mul(&self, other: &Mat) -> Mat {
        let n = self.n;
        let mut result = Mat::zeros(n);
        for i in 0..n {
            for k in 0..n {
                let a_ik = self.data[i * n + k];
                if a_ik == 0.0 {
                    continue;
                }
                for j in 0..n {
                    result.data[i * n + j] += a_ik * other.data[k * n + j];
                }
            }
        }
        result
    }

    fn mat_vec(&self, v: &[f64]) -> Vec<f64> {
        let n = self.n;
        let mut result = vec![0.0; n];
        for i in 0..n {
            let row_start = i * n;
            let mut sum = 0.0;
            for j in 0..n {
                sum += self.data[row_start + j] * v[j];
            }
            result[i] = sum;
        }
        result
    }
}

fn build_step_matrix(c: i64, corridor: i64, modulus: u64, num_states: usize) -> Mat {
    let mut m = Mat::zeros(num_states);
    let mod_usize = modulus as usize;
    for d in 0..=corridor {
        for r in 0..modulus {
            if r == 1 { continue; }
            let src = d as usize * mod_usize + r as usize;
            let max_a = d + c;
            if max_a < 1 { continue; }
            let mut valid = Vec::new();
            for a in 1..=max_a {
                let d_next = d + c - a;
                if d_next < 0 || d_next > corridor { continue; }
                let r_next = next_residue(r, a, modulus);
                if r_next == 1 { continue; }
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

fn spectral_radius_power_iter(mat: &Mat, max_iter: usize, tol: f64) -> f64 {
    let n = mat.n;
    let mut v = vec![1.0 / (n as f64).sqrt(); n];
    let mut lambda = 0.0;
    for _iter in 0..max_iter {
        let w = mat.mat_vec(&v);
        let new_lambda = w.iter().map(|x| x * x).sum::<f64>().sqrt();
        if new_lambda < 1e-30 { return 0.0; }
        let scale = 1.0 / new_lambda;
        v = w.iter().map(|x| x * scale).collect();
        if (new_lambda - lambda).abs() < tol * new_lambda.max(1e-15) {
            return new_lambda;
        }
        lambda = new_lambda;
    }
    lambda
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let mut corridor: i64 = 10;
    let mut m_min: u32 = 1;
    let mut m_max: u32 = 8;
    let mut steps: usize = 53;
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--C" => { i += 1; corridor = args[i].parse().expect("--C"); }
            "--m-min" => { i += 1; m_min = args[i].parse().expect("--m-min"); }
            "--m-max" => { i += 1; m_max = args[i].parse().expect("--m-max"); }
            "--steps" => { i += 1; steps = args[i].parse().expect("--steps"); }
            other => panic!("unknown arg: {}", other),
        }
        i += 1;
    }

    let credits = sturmian_credits();
    eprintln!("spectral-radius C={} m={}..{} steps={}", corridor, m_min, m_max, steps);
    println!("m,C,states,spectral_radius,gap,steps,time_sec");

    for m in m_min..=m_max {
        let modulus = 3u64.pow(m);
        let num_states = (corridor as usize + 1) * modulus as usize;
        if num_states > 200000 {
            eprintln!("m={}: {} states — skipping", m, num_states);
            continue;
        }
        eprintln!("  m={}: {} states...", m, num_states);
        let started = Instant::now();

        let mut composed = Mat::identity(num_states);
        for step in 0..steps {
            let c = credits[step % 53];
            let step_m = build_step_matrix(c, corridor, modulus, num_states);
            composed = step_m.mul(&composed);
            if num_states > 1000 && (step + 1) % 10 == 0 {
                eprintln!("    step {}/{} ({:.0}s)", step + 1, steps, started.elapsed().as_secs_f64());
            }
        }

        let sr = spectral_radius_power_iter(&composed, 10000, 1e-12);
        let elapsed = started.elapsed().as_secs_f64();
        let gap = 1.0 - sr;
        println!("{},{},{},{:.12e},{:.12e},{},{:.1}", m, corridor, num_states, sr, gap, steps, elapsed);
        eprintln!("  m={}: ρ={:.10} gap={:.6e} {:.1}s {}", m, sr, gap, elapsed,
            if sr < 1.0 { "< 1 ✓" } else { "≥ 1 ✗" });
    }
}
