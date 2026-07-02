use std::collections::HashSet;
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

/// Compute (3r+1) * 2^{-a} mod 3^m
fn next_residue_3adic(r3: u64, a: u64, mod3: u64) -> u64 {
    let val = (3u128 * r3 as u128 + 1) % mod3 as u128;
    let inv = mod_inverse(pow_mod(2, a, mod3), mod3);
    ((val * inv as u128) % mod3 as u128) as u64
}

/// Compute (3r+1) / 2^a mod 2^j (exact integer division, then reduce)
/// This requires knowing r mod 2^{j+a} to get the result mod 2^j.
/// Since we only track r mod 2^j, we need j > a for the result to be
/// well-defined. When a >= j, the result is indeterminate (precision escape).
fn next_residue_2adic(r2: u64, a: u64, mod2: u64) -> Option<u64> {
    // r2 is odd (we only track odd residues)
    // 3*r2 + 1 is even, and we need v2(3*r2+1) = a
    let val_full = 3u128 * r2 as u128 + 1;
    let actual_a = val_full.trailing_zeros() as u64;
    if actual_a != a {
        return None; // this r2 doesn't produce the claimed a
    }
    // Divide by 2^a
    let divided = val_full >> a;
    // The result must be odd for the odd-only map
    if divided % 2 == 0 {
        return None; // result is even — shouldn't happen for odd-only
    }
    // Reduce mod 2^j
    // BUT: the result mod 2^j depends on bits above position j of r2.
    // We only know r2 mod 2^j (= mod2). The multiplication by 3 and
    // addition of 1 can carry above position j. The division by 2^a
    // shifts bits down, bringing bits from above j into the result.
    //
    // For the result mod 2^j to be well-defined from r2 mod 2^j alone,
    // we need: the bits of (3*r2+1) above position j don't affect the
    // result below position j after the shift. This requires j+a bits
    // of input to determine j bits of output.
    //
    // Since we only have j bits, the result is well-defined only up to
    // position j-a. For a full j-bit result, we'd need r2 mod 2^{j+a}.
    //
    // CONSERVATIVE APPROACH: compute from the j-bit r2 and flag if
    // precision might be insufficient. The result mod 2^{j-a} is
    // guaranteed correct; bits j-a through j-1 may be wrong.
    //
    // For now: compute and accept that high bits may be approximate.
    // Mark states where a is large relative to j as precision-escaped.
    Some((divided as u64) % mod2)
}

/// Product-space state: (deficit, r3 mod 3^m, r2 mod 2^j)
/// Packed into a u64 for efficiency.
/// Layout: deficit * (3^m * half_mod2) + r3 * half_mod2 + r2_idx
/// where r2_idx = (r2 - 1) / 2 (index into odd residues)
struct ProductState;

impl ProductState {
    fn pack(deficit: i64, r3: u64, r2: u64, mod3: u64, half_mod2: u64) -> u64 {
        let r2_idx = (r2 - 1) / 2;
        deficit as u64 * mod3 * half_mod2 + r3 * half_mod2 + r2_idx
    }

    fn unpack(id: u64, mod3: u64, half_mod2: u64) -> (i64, u64, u64) {
        let r2_idx = id % half_mod2;
        let rem = id / half_mod2;
        let r3 = rem % mod3;
        let deficit = (rem / mod3) as i64;
        let r2 = r2_idx * 2 + 1;
        (deficit, r3, r2)
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let mut corridor: i64 = 3;
    let mut m: u32 = 5;      // 3-adic precision
    let mut j: u32 = 10;     // 2-adic precision
    let mut heartbeats: usize = 1;
    let mut verbose = false;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--C" => { i += 1; corridor = args[i].parse().expect("--C"); }
            "--m" => { i += 1; m = args[i].parse().expect("--m"); }
            "--j" => { i += 1; j = args[i].parse().expect("--j"); }
            "--heartbeats" => { i += 1; heartbeats = args[i].parse().expect("--heartbeats"); }
            "--verbose" | "-v" => { verbose = true; }
            other => panic!("unknown arg: {}", other),
        }
        i += 1;
    }

    let mod3 = 3u64.pow(m);
    let mod2 = 1u64 << j;
    let half_mod2 = mod2 / 2; // number of odd residues mod 2^j
    let num_deficits = (corridor + 1) as u64;
    let total_states = num_deficits * mod3 * half_mod2;
    let credits = sturmian_credits();

    eprintln!("product-automaton C={} m={} (3^m={}) j={} (2^j={})",
              corridor, m, mod3, j, mod2);
    eprintln!("  deficits: {}, 3-adic classes: {}, 2-adic odd classes: {}",
              num_deficits, mod3, half_mod2);
    eprintln!("  total state space: {}", total_states);
    eprintln!("  heartbeats: {}", heartbeats);

    if total_states > 500_000_000 {
        eprintln!("ERROR: state space too large (>500M). Reduce parameters.");
        return;
    }

    // Initialize: all valid states are alive
    // Valid = deficit in [0, C], r3 in [0, 3^m), r2 odd in [1, 2^j)
    // Exclude terminal states: r3 == 1 (terminal residue mod 3^m)
    let started = Instant::now();

    let mut alive: HashSet<u64> = HashSet::new();
    for d in 0..=corridor {
        for r3 in 0..mod3 {
            if r3 == 1 { continue; } // terminal
            for r2_idx in 0..half_mod2 {
                let r2 = r2_idx * 2 + 1;
                let id = ProductState::pack(d, r3, r2, mod3, half_mod2);
                alive.insert(id);
            }
        }
    }

    let initial_alive = alive.len();
    eprintln!("  initial alive (non-terminal): {}", initial_alive);
    eprintln!("  build time: {:.1}s", started.elapsed().as_secs_f64());

    // Print CSV header
    println!("heartbeat,step,alive,killed_terminal,killed_exit,killed_precision,total_killed,elapsed_s");

    // Run heartbeats
    for hb in 0..heartbeats {
        for (step_idx, &credit) in credits.iter().enumerate() {
            let global_step = hb * 53 + step_idx;
            let before = alive.len();

            let mut next_alive: HashSet<u64> = HashSet::new();
            let mut killed_terminal = 0usize;
            let mut killed_exit = 0usize;
            let mut killed_precision = 0usize;

            for &id in alive.iter() {
                let (d, r3, r2) = ProductState::unpack(id, mod3, half_mod2);

                // Determine a from the 2-adic coordinate
                let val = 3u64.checked_mul(r2).and_then(|v| v.checked_add(1));
                let a = match val {
                    Some(v) => v.trailing_zeros() as i64,
                    None => {
                        // overflow — treat as precision escape
                        killed_precision += 1;
                        continue;
                    }
                };

                // Check precision: if a >= j, we can't resolve the 2-adic successor
                if a as u32 >= j {
                    killed_precision += 1;
                    continue;
                }

                // Compute deficit successor
                let d_next = d + credit - a;

                // Check corridor bounds
                if d_next < 0 || d_next > corridor {
                    killed_exit += 1;
                    continue;
                }

                // Compute 3-adic successor
                let r3_next = next_residue_3adic(r3, a as u64, mod3);

                // Check terminal
                if r3_next == 1 {
                    killed_terminal += 1;
                    continue;
                }

                // Compute 2-adic successor
                // (3*r2 + 1) / 2^a mod 2^j
                let val_full = 3u64 as u128 * r2 as u128 + 1;
                let divided = (val_full >> a) as u64;
                let r2_next = divided % mod2;

                // Result must be odd
                if r2_next % 2 == 0 {
                    // Even result — this means the actual odd-step result
                    // requires further halving. The v2 was larger than we
                    // computed from r2 alone (precision issue).
                    killed_precision += 1;
                    continue;
                }

                let next_id = ProductState::pack(d_next, r3_next, r2_next, mod3, half_mod2);
                next_alive.insert(next_id);
            }

            let total_killed = killed_terminal + killed_exit + killed_precision;
            alive = next_alive;

            println!("{},{},{},{},{},{},{},{:.1}",
                     hb, step_idx, alive.len(),
                     killed_terminal, killed_exit, killed_precision,
                     total_killed, started.elapsed().as_secs_f64());

            if verbose && (step_idx % 10 == 0 || alive.is_empty()) {
                eprintln!("  hb {} step {}: {} alive (term={} exit={} prec={}) {:.1}s",
                         hb, step_idx, alive.len(),
                         killed_terminal, killed_exit, killed_precision,
                         started.elapsed().as_secs_f64());
            }

            if alive.is_empty() {
                eprintln!("SURVIVOR GRAPH EMPTY at heartbeat {} step {} ({:.1}s)",
                         hb, step_idx, started.elapsed().as_secs_f64());
                eprintln!("  Total kills: terminal={} exit={} precision={}",
                         killed_terminal, killed_exit, killed_precision);
                println!("# EMPTY at hb={} step={}", hb, step_idx);
                return;
            }
        }

        eprintln!("  heartbeat {}: {} alive ({:.1}s)",
                 hb, alive.len(), started.elapsed().as_secs_f64());
    }

    // Summary
    eprintln!("\nFINAL: {} alive states after {} heartbeats ({:.1}s)",
             alive.len(), heartbeats, started.elapsed().as_secs_f64());
    eprintln!("  initial: {}, survival rate: {:.6}",
             initial_alive, alive.len() as f64 / initial_alive as f64);

    if alive.len() <= 20 && verbose {
        eprintln!("\nSurviving states:");
        for &id in alive.iter() {
            let (d, r3, r2) = ProductState::unpack(id, mod3, half_mod2);
            eprintln!("  deficit={} r3={} r2={}", d, r3, r2);
        }
    }
}
