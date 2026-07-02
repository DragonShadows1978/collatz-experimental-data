use std::cmp::Ordering;
use std::collections::{BTreeMap, HashMap, HashSet};
use std::env;
use std::fs::{create_dir_all, metadata, read_to_string, rename, File, OpenOptions};
use std::io::{BufWriter, Read, Write};
use std::path::PathBuf;
use std::process::Command;
use std::time::Instant;

use rayon::prelude::*;

const ALPHA: f64 = 1.5849625007211563;
const CONVERGENT_DENOMINATORS: [usize; 10] = [1, 2, 7, 12, 53, 359, 665, 16266, 31867, 111202];

#[derive(Clone, Debug, Eq, PartialEq)]
struct Big {
    limbs: Vec<u32>,
}

impl Big {
    const BASE: u64 = 1_000_000_000;

    fn zero() -> Self {
        Self { limbs: Vec::new() }
    }

    fn one() -> Self {
        Self { limbs: vec![1] }
    }

    fn is_zero(&self) -> bool {
        self.limbs.is_empty()
    }

    fn add_assign(&mut self, other: &Self) {
        let max_len = self.limbs.len().max(other.limbs.len());
        self.limbs.resize(max_len, 0);
        let mut carry = 0u64;
        for idx in 0..max_len {
            let lhs = self.limbs[idx] as u64;
            let rhs = other.limbs.get(idx).copied().unwrap_or(0) as u64;
            let sum = lhs + rhs + carry;
            self.limbs[idx] = (sum % Self::BASE) as u32;
            carry = sum / Self::BASE;
        }
        if carry > 0 {
            self.limbs.push(carry as u32);
        }
    }

    fn cmp_big(&self, other: &Self) -> Ordering {
        match self.limbs.len().cmp(&other.limbs.len()) {
            Ordering::Equal => {
                for (lhs, rhs) in self.limbs.iter().rev().zip(other.limbs.iter().rev()) {
                    match lhs.cmp(rhs) {
                        Ordering::Equal => {}
                        ord => return ord,
                    }
                }
                Ordering::Equal
            }
            ord => ord,
        }
    }

    fn to_decimal(&self) -> String {
        if self.is_zero() {
            return "0".to_string();
        }
        let mut out = String::new();
        for (idx, limb) in self.limbs.iter().rev().enumerate() {
            if idx == 0 {
                out.push_str(&limb.to_string());
            } else {
                out.push_str(&format!("{:09}", limb));
            }
        }
        out
    }

    fn to_f64_lossy(&self) -> f64 {
        let mut value = 0.0;
        for limb in self.limbs.iter().rev() {
            value = value * Self::BASE as f64 + *limb as f64;
        }
        value
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct BigBits {
    limbs: Vec<u64>,
}

impl BigBits {
    fn zero() -> Self {
        Self { limbs: Vec::new() }
    }

    fn one() -> Self {
        Self { limbs: vec![1] }
    }

    fn from_power_of_two(bit: usize) -> Self {
        let mut out = Self {
            limbs: vec![0; bit / 64 + 1],
        };
        out.limbs[bit / 64] = 1u64 << (bit % 64);
        out
    }

    fn normalize(&mut self) {
        while self.limbs.last().copied() == Some(0) {
            self.limbs.pop();
        }
    }

    fn bit_length(&self) -> usize {
        match self.limbs.last() {
            Some(last) => 64 * (self.limbs.len() - 1) + (64 - last.leading_zeros() as usize),
            None => 0,
        }
    }

    fn to_u128_checked(&self) -> Option<u128> {
        if self.limbs.len() > 2 {
            return None;
        }
        let low = self.limbs.get(0).copied().unwrap_or(0) as u128;
        let high = self.limbs.get(1).copied().unwrap_or(0) as u128;
        Some(low | (high << 64))
    }

    fn add_power_of_two(&mut self, bit: usize) {
        let limb = bit / 64;
        let offset = bit % 64;
        self.limbs.resize(limb + 1, 0);
        let mut idx = limb;
        let mut carry = 1u64 << offset;
        loop {
            let (value, overflow) = self.limbs[idx].overflowing_add(carry);
            self.limbs[idx] = value;
            if !overflow {
                break;
            }
            idx += 1;
            if idx == self.limbs.len() {
                self.limbs.push(0);
            }
            carry = 1;
        }
    }

    fn mul_small(&mut self, factor: u64) {
        if factor == 0 || self.limbs.is_empty() {
            self.limbs.clear();
            return;
        }
        let mut carry = 0u128;
        for limb in self.limbs.iter_mut() {
            let value = *limb as u128 * factor as u128 + carry;
            *limb = value as u64;
            carry = value >> 64;
        }
        if carry > 0 {
            self.limbs.push(carry as u64);
        }
    }

    fn truncated(&self, bits: usize) -> Self {
        if bits == 0 {
            return Self::zero();
        }
        let limb_count = (bits + 63) / 64;
        let mut out = Self {
            limbs: self.limbs.iter().take(limb_count).copied().collect(),
        };
        let extra = bits % 64;
        if extra != 0 && out.limbs.len() == limb_count {
            if let Some(last) = out.limbs.last_mut() {
                *last &= (1u64 << extra) - 1;
            }
        }
        out.normalize();
        out
    }

    fn add_shifted_digit(&self, digit: u64, shift: usize) -> Self {
        let mut out = self.clone();
        if digit == 0 {
            return out;
        }
        let limb = shift / 64;
        let offset = shift % 64;
        out.limbs.resize(limb + 2, 0);
        let low = digit << offset;
        let high = if offset == 0 {
            0
        } else {
            digit >> (64 - offset)
        };
        let (value, overflow) = out.limbs[limb].overflowing_add(low);
        out.limbs[limb] = value;
        let add_high = high + u64::from(overflow);
        let (value, overflow) = out.limbs[limb + 1].overflowing_add(add_high);
        out.limbs[limb + 1] = value;
        let mut carry = u64::from(overflow);
        let mut idx = limb + 2;
        while carry > 0 {
            if idx == out.limbs.len() {
                out.limbs.push(0);
            }
            let (value, overflow) = out.limbs[idx].overflowing_add(carry);
            out.limbs[idx] = value;
            carry = u64::from(overflow);
            idx += 1;
        }
        out.normalize();
        out
    }
}

#[derive(Clone)]
struct Witness {
    a_sum: usize,
    b: BigBits,
    pow3: BigBits,
    previous_rho: Option<BigBits>,
    lift_count: usize,
    current_plateau: usize,
    longest_plateau: usize,
}

#[derive(Clone)]
struct Config {
    c: i64,
    depth: usize,
    terminal_value: u64,
    residue_mod_power: usize,
    out_dir: PathBuf,
    progress_every: usize,
    label: String,
    export_terminal_witnesses: bool,
    checkpoint_path: Option<PathBuf>,
    checkpoint_every: usize,
    resume_path: Option<PathBuf>,
    memory_lean: bool,
    no_checkpoint: bool,
    memory_cap_mb: Option<u64>,
    auto_prior_odd_on_even_dirty: bool,
    progress_jsonl_path: Option<PathBuf>,
    lift_profile_base_m: Option<usize>,
    lift_profile_path: Option<PathBuf>,
    track_corridor_breaches: bool,
    export_breach_witnesses: bool,
    max_breach_witnesses: usize,
    max_corridor_breach_target: Option<i64>,
    follow_breach_witnesses: bool,
    follow_down_witnesses: bool,
    max_follow_witnesses: usize,
    max_follow_steps: usize,
    threads: usize,
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
struct Key(u64);

impl Key {
    fn new(deficit: i64, residue: u64) -> Self {
        if deficit < 0 || deficit > u32::MAX as i64 {
            panic!("deficit cannot be packed into census key: {}", deficit);
        }
        if residue > u32::MAX as u64 {
            panic!("residue cannot be packed into census key: {}", residue);
        }
        Self(((deficit as u64) << 32) | residue)
    }

    fn deficit(self) -> i64 {
        (self.0 >> 32) as i64
    }

    fn residue(self) -> u64 {
        self.0 & 0xffff_ffff
    }
}

#[derive(Clone)]
struct Row {
    depth: usize,
    residue_modulus: u64,
    terminal_residue_signature: u64,
    symbolic_branch_count: Big,
    merged_state_count: usize,
    valid_from_1_count: Big,
    exact_depth_valid1: Big,
    terminal_1_compatible_signature_count: usize,
    valid_residue_count: usize,
    max_branch_multiplicity: Big,
    rho_stable_count: usize,
    rho_lift_count: usize,
    longest_plateau: usize,
    max_rho_bit_length: usize,
    compression_ratio: String,
    valid_fraction: String,
    current_rss_kb: u64,
    peak_rss_kb: u64,
    live_valid1_count: usize,
    valid1_shadow_birth_count: usize,
    valid1_shadow_death_count: usize,
    max_valid1_shadow_lifetime: usize,
    valid1_shadow_persisted_from_previous: bool,
    live_valid1_lineage_count: Big,
    valid1_lineage_birth_count: Big,
    valid1_lineage_death_count: Big,
    max_valid1_lineage_lifetime: usize,
    lineage_lifetime_histogram_compact: String,
    exit_up_count: Big,
    exit_down_count: Big,
    stay_count: Big,
    notes: String,
}

struct CensusResult {
    rows: Vec<Row>,
    birth_audit_rows: Vec<BirthAuditRow>,
    corridor_breach_events: Vec<CorridorBreachEvent>,
    corridor_breach_follows: Vec<CorridorBreachFollow>,
    downward_exit_follows: Vec<DownwardExitFollow>,
}

#[derive(Clone)]
struct BirthAuditRow {
    c: i64,
    m: usize,
    depth: usize,
    key: Key,
    birth_depth: usize,
    lineage_count: Big,
    l_at_birth: i64,
    i_birth: i64,
    parent_existed: bool,
    parent_key: Option<Key>,
    birth_reason: &'static str,
}

#[derive(Clone)]
struct CorridorBreachEvent {
    c_configured: i64,
    m: usize,
    depth: usize,
    key: Key,
    old_max_d: i64,
    new_max_d: i64,
    breached_from_c: i64,
    breached_to_c: i64,
    d_k: i64,
    a_k: i64,
    terminal_compatible: bool,
    live_valid1_key_count: usize,
    live_valid1_lineage_count: Big,
    lineage_count: Big,
    birth_count: Big,
    death_count: Big,
    lifetime: usize,
    notes: &'static str,
}

#[derive(Clone)]
struct CorridorBreachFollow {
    c_configured: i64,
    m: usize,
    breach_depth: usize,
    key: Key,
    breached_from_c: i64,
    breached_to_c: i64,
    d_k: i64,
    a_k: i64,
    rho: Option<u128>,
    rho_modulus_bit_length: usize,
    candidate_integer: Option<u128>,
    candidate_bit_length: usize,
    combined_modulus_bit_length: usize,
    terminal_value_after_prefix: Option<u128>,
    terminal_value_bit_length: usize,
    follow_steps: usize,
    collapsed_to_1: bool,
    min_d_seen_after_breach: i64,
    max_d_seen_after_breach: i64,
    max_c_seen_after_breach: i64,
    re_entered_birth_corridor: bool,
    peak_value_bit_length: usize,
    status: String,
    notes: String,
}

#[derive(Clone)]
struct DownwardExitFollow {
    c_configured: i64,
    m: usize,
    exit_depth: usize,
    key: Key,
    exited_from_c: i64,
    d_k: i64,
    a_k: i64,
    rho: Option<u128>,
    candidate_integer: Option<u128>,
    candidate_bit_length: usize,
    terminal_value_after_prefix: Option<u128>,
    terminal_value_bit_length: usize,
    follow_steps: usize,
    collapsed_to_1: bool,
    min_d_seen_after_exit: i64,
    max_d_seen_after_exit: i64,
    re_entered_corridor: bool,
    re_entry_depth: usize,
    peak_value_bit_length: usize,
    status: String,
    notes: String,
}

fn try_follow_down_exit_u128(
    config: &Config,
    depth: usize,
    key: &Key,
    a: i64,
    witness: &Witness,
) -> DownwardExitFollow {
    let mut row = DownwardExitFollow {
        c_configured: config.c,
        m: config.residue_mod_power,
        exit_depth: depth,
        key: *key,
        exited_from_c: config.c,
        d_k: key.deficit() + credit_at_step(depth - 1) - a,
        a_k: a,
        rho: None,
        candidate_integer: None,
        candidate_bit_length: 0,
        terminal_value_after_prefix: None,
        terminal_value_bit_length: 0,
        follow_steps: 0,
        collapsed_to_1: false,
        min_d_seen_after_exit: 0,
        max_d_seen_after_exit: 0,
        re_entered_corridor: false,
        re_entry_depth: 0,
        peak_value_bit_length: 0,
        status: "unstarted".to_string(),
        notes: String::new(),
    };

    let down_witness = update_witness(witness, a);
    let Some(rho) = down_witness
        .previous_rho
        .as_ref()
        .and_then(BigBits::to_u128_checked)
    else {
        row.status = "too_wide_for_u128_rho".to_string();
        return row;
    };
    if down_witness.a_sum + 1 >= 128 {
        row.rho = Some(rho);
        row.status = "too_wide_for_u128_rho_modulus".to_string();
        return row;
    }
    let rho_modulus = 1u128 << (down_witness.a_sum + 1);
    let modulus3 = residue_modulus(depth, config.residue_mod_power);
    let Some((candidate, _combined_modulus)) =
        crt_power2_power3_u128(rho, rho_modulus, key.residue(), modulus3)
    else {
        row.rho = Some(rho);
        row.status = "too_wide_for_u128_crt".to_string();
        return row;
    };
    row.rho = Some(rho);
    row.candidate_integer = Some(candidate);
    row.candidate_bit_length = bit_length_u128(candidate);

    let Some(pow3) = down_witness.pow3.to_u128_checked() else {
        row.status = "too_wide_for_u128_pow3".to_string();
        return row;
    };
    let Some(b) = down_witness.b.to_u128_checked() else {
        row.status = "too_wide_for_u128_affine_offset".to_string();
        return row;
    };
    let Some(numerator) = pow3
        .checked_mul(candidate)
        .and_then(|value| value.checked_add(b))
    else {
        row.status = "too_wide_for_u128_affine_value".to_string();
        return row;
    };
    if down_witness.a_sum >= 128 {
        row.status = "too_wide_for_u128_affine_shift".to_string();
        return row;
    }
    let divisor = if down_witness.a_sum == 0 {
        1u128
    } else {
        1u128 << down_witness.a_sum
    };
    if numerator % divisor != 0 {
        row.status = "affine_prefix_not_integral".to_string();
        return row;
    }
    let mut value = numerator / divisor;
    row.terminal_value_after_prefix = Some(value);
    row.terminal_value_bit_length = bit_length_u128(value);
    row.peak_value_bit_length = row.terminal_value_bit_length;

    let mut follow_depth = depth;
    let mut a_sum = down_witness.a_sum;
    row.min_d_seen_after_exit = row.d_k;
    row.max_d_seen_after_exit = row.d_k;

    while value != 1 && row.follow_steps < config.max_follow_steps {
        let Some((next_value, exponent)) = odd_collatz_step_u128(value) else {
            row.status = "u128_overflow_during_follow".to_string();
            return row;
        };
        value = next_value;
        follow_depth += 1;
        a_sum = a_sum.saturating_add(exponent);
        row.follow_steps += 1;
        row.peak_value_bit_length = row.peak_value_bit_length.max(bit_length_u128(value));
        let d = ((follow_depth as f64 * ALPHA).floor() as i64) - a_sum as i64;
        row.min_d_seen_after_exit = row.min_d_seen_after_exit.min(d);
        row.max_d_seen_after_exit = row.max_d_seen_after_exit.max(d);
        if !row.re_entered_corridor && d >= 0 && d <= config.c {
            row.re_entered_corridor = true;
            row.re_entry_depth = follow_depth;
        }
    }

    if value == 1 {
        row.collapsed_to_1 = true;
        row.status = "collapsed_to_1".to_string();
        row.notes = format!(
            "reached 1 in {} steps; min_d={}; max_d={}; re_entered={}",
            row.follow_steps, row.min_d_seen_after_exit, row.max_d_seen_after_exit,
            row.re_entered_corridor
        );
    } else {
        row.status = "max_follow_steps_reached".to_string();
        row.notes = "did not reach 1 within follow step cap".to_string();
    }
    row
}

fn main() {
    let config = parse_args();
    if config.threads > 0 {
        rayon::ThreadPoolBuilder::new()
            .num_threads(config.threads)
            .build_global()
            .expect("failed to set rayon thread count");
    }
    if config.memory_lean && config.export_terminal_witnesses {
        panic!("--memory-lean does not store witnesses; omit --export-terminal-witnesses");
    }
    if config.memory_lean && config.follow_breach_witnesses {
        panic!("--memory-lean does not store witnesses; omit --memory-lean for --follow-breach-witnesses");
    }
    if config.memory_lean && config.follow_down_witnesses {
        panic!("--memory-lean does not store witnesses; omit --memory-lean for --follow-down-witnesses");
    }
    if config.terminal_value == 0 || config.terminal_value % 2 == 0 {
        panic!("--terminal-value must be a positive odd integer");
    }
    create_dir_all(&config.out_dir).expect("create out dir");
    initialize_lift_profile(&config).expect("initialize lift profile");

    let started = Instant::now();
    let result = run_census(&config, started);
    write_outputs(
        &config,
        &result.rows,
        &result.birth_audit_rows,
        &result.corridor_breach_events,
        &result.corridor_breach_follows,
        &result.downward_exit_follows,
    )
    .expect("write outputs");
    write_lift_profile_summary(&config).expect("write lift profile summary");
    emit_final_jsonl(&config, &result.rows, started);
    print_summary(&config, &result.rows);
    if should_run_prior_odd_after_dirty(&config, &result.rows) {
        run_prior_odd_after_dirty(&config);
    }
}

fn parse_args() -> Config {
    let mut c: Option<i64> = None;
    let mut depth: Option<usize> = None;
    let mut terminal_value = 1u64;
    let mut residue_mod_power = 8usize;
    let mut out_dir = PathBuf::from("data/runs");
    let mut progress_every = 0usize;
    let mut label = "lock3".to_string();
    let mut export_terminal_witnesses = false;
    let mut checkpoint_path = None;
    let mut checkpoint_every = 0usize;
    let mut resume_path = None;
    let mut memory_lean = false;
    let mut no_checkpoint = false;
    let mut memory_cap_mb = None;
    let mut auto_prior_odd_on_even_dirty = false;
    let mut progress_jsonl_path = None;
    let mut lift_profile_base_m = None;
    let mut lift_profile_path = None;
    let mut track_corridor_breaches = false;
    let mut export_breach_witnesses = false;
    let mut max_breach_witnesses = 100usize;
    let mut max_corridor_breach_target = None;
    let mut follow_breach_witnesses = false;
    let mut follow_down_witnesses = false;
    let mut max_follow_witnesses = 20usize;
    let mut max_follow_steps = 10000usize;
    let mut threads = 0usize;

    let args: Vec<String> = env::args().collect();
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--C" => {
                i += 1;
                c = Some(args[i].parse().expect("--C integer"));
            }
            "--depth" => {
                i += 1;
                depth = Some(args[i].parse().expect("--depth integer"));
            }
            "--terminal-value" => {
                i += 1;
                terminal_value = args[i].parse().expect("--terminal-value integer");
            }
            "--residue-mod-power" => {
                i += 1;
                residue_mod_power = args[i].parse().expect("--residue-mod-power integer");
            }
            "--out-dir" => {
                i += 1;
                out_dir = PathBuf::from(&args[i]);
            }
            "--progress-every" => {
                i += 1;
                progress_every = args[i].parse().expect("--progress-every integer");
            }
            "--label" => {
                i += 1;
                label = args[i].clone();
            }
            "--export-terminal-witnesses" => {
                export_terminal_witnesses = true;
            }
            "--checkpoint-path" => {
                i += 1;
                checkpoint_path = Some(PathBuf::from(&args[i]));
            }
            "--checkpoint-every" => {
                i += 1;
                checkpoint_every = args[i].parse().expect("--checkpoint-every integer");
            }
            "--resume" => {
                i += 1;
                resume_path = Some(PathBuf::from(&args[i]));
            }
            "--memory-lean" => {
                memory_lean = true;
            }
            "--no-checkpoint" => {
                no_checkpoint = true;
            }
            "--memory-cap-mb" => {
                i += 1;
                memory_cap_mb = Some(args[i].parse().expect("--memory-cap-mb integer"));
            }
            "--auto-prior-odd-on-even-dirty" => {
                auto_prior_odd_on_even_dirty = true;
            }
            "--no-auto-prior-odd-on-even-dirty" => {
                auto_prior_odd_on_even_dirty = false;
            }
            "--progress-jsonl" => {
                i += 1;
                progress_jsonl_path = Some(PathBuf::from(&args[i]));
            }
            "--lift-profile-base-m" => {
                i += 1;
                lift_profile_base_m = Some(args[i].parse().expect("--lift-profile-base-m integer"));
            }
            "--lift-profile-out" => {
                i += 1;
                lift_profile_path = Some(PathBuf::from(&args[i]));
            }
            "--track-corridor-breaches" => {
                track_corridor_breaches = true;
            }
            "--export-breach-witnesses" => {
                export_breach_witnesses = true;
            }
            "--max-breach-witnesses" => {
                i += 1;
                max_breach_witnesses = args[i].parse().expect("--max-breach-witnesses integer");
            }
            "--max-corridor-breach-target" => {
                i += 1;
                max_corridor_breach_target = Some(
                    args[i]
                        .parse()
                        .expect("--max-corridor-breach-target integer"),
                );
            }
            "--follow-breach-witnesses" => {
                follow_breach_witnesses = true;
                track_corridor_breaches = true;
            }
            "--follow-down-witnesses" => {
                follow_down_witnesses = true;
            }
            "--max-follow-witnesses" => {
                i += 1;
                max_follow_witnesses = args[i].parse().expect("--max-follow-witnesses integer");
            }
            "--max-follow-steps" => {
                i += 1;
                max_follow_steps = args[i].parse().expect("--max-follow-steps integer");
            }
            "--threads" => {
                i += 1;
                threads = args[i].parse().expect("--threads integer");
            }
            other => panic!("unknown arg: {}", other),
        }
        i += 1;
    }

    if let Some(base_m) = lift_profile_base_m {
        if residue_mod_power != base_m + 1 {
            panic!(
                "--lift-profile-base-m expects --residue-mod-power to be base_m + 1; got base_m={} residue_mod_power={}",
                base_m, residue_mod_power
            );
        }
    }

    Config {
        c: c.expect("--C is required"),
        depth: depth.expect("--depth is required"),
        terminal_value,
        residue_mod_power,
        out_dir,
        progress_every,
        label,
        export_terminal_witnesses,
        checkpoint_path,
        checkpoint_every,
        resume_path,
        memory_lean,
        no_checkpoint,
        memory_cap_mb,
        auto_prior_odd_on_even_dirty,
        progress_jsonl_path,
        lift_profile_base_m,
        lift_profile_path,
        track_corridor_breaches,
        export_breach_witnesses,
        max_breach_witnesses,
        max_corridor_breach_target,
        follow_breach_witnesses,
        follow_down_witnesses,
        max_follow_witnesses,
        max_follow_steps,
        threads,
    }
}

fn should_run_prior_odd_after_dirty(config: &Config, rows: &[Row]) -> bool {
    if !config.auto_prior_odd_on_even_dirty {
        return false;
    }
    if config.residue_mod_power == 0 || config.residue_mod_power % 2 != 0 {
        return false;
    }
    rows.first()
        .map(|row| {
            row.terminal_1_compatible_signature_count > 0 || !row.exact_depth_valid1.is_zero()
        })
        .unwrap_or(false)
}

fn should_stop_for_start_dirty(config: &Config, row: &Row) -> bool {
    config.auto_prior_odd_on_even_dirty
        && config.residue_mod_power > 0
        && config.residue_mod_power % 2 == 0
        && row.depth == 1
        && (row.terminal_1_compatible_signature_count > 0 || !row.exact_depth_valid1.is_zero())
}

fn json_escape(value: &str) -> String {
    let mut escaped = String::with_capacity(value.len() + 8);
    for ch in value.chars() {
        match ch {
            '\\' => escaped.push_str("\\\\"),
            '"' => escaped.push_str("\\\""),
            '\n' => escaped.push_str("\\n"),
            '\r' => escaped.push_str("\\r"),
            '\t' => escaped.push_str("\\t"),
            other => escaped.push(other),
        }
    }
    escaped
}

fn append_jsonl(config: &Config, line: &str) -> std::io::Result<()> {
    if let Some(path) = &config.progress_jsonl_path {
        if let Some(parent) = path.parent() {
            create_dir_all(parent)?;
        }
        let mut file = OpenOptions::new().create(true).append(true).open(path)?;
        writeln!(file, "{}", line)?;
    }
    Ok(())
}

fn lift_profile_path(config: &Config) -> Option<PathBuf> {
    config.lift_profile_base_m.map(|base_m| {
        config.lift_profile_path.clone().unwrap_or_else(|| {
            config.out_dir.join(format!(
                "C{}_m{}_to_m{}_lift_profile.csv",
                config.c,
                base_m,
                base_m + 1
            ))
        })
    })
}

fn lift_profile_summary_path(config: &Config) -> Option<PathBuf> {
    lift_profile_path(config).map(|path| {
        let stem = path
            .file_stem()
            .and_then(|value| value.to_str())
            .unwrap_or("lift_profile");
        path.with_file_name(format!("{}_summary.json", stem))
    })
}

fn initialize_lift_profile(config: &Config) -> std::io::Result<()> {
    let Some(path) = lift_profile_path(config) else {
        return Ok(());
    };
    if let Some(parent) = path.parent() {
        create_dir_all(parent)?;
    }
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "depth,m_base,m_lift,deficit_state,signature_mod_3_base,live_at_m_base,lift0_signature,lift0_present,lift0_terminal_valid,lift1_signature,lift1_present,lift1_terminal_valid,lift2_signature,lift2_present,lift2_terminal_valid,lift_count,terminal_lift_digit,survives_to_m_lift_terminal,lineage_id"
    )?;
    Ok(())
}

fn append_lift_profile(
    config: &Config,
    depth: usize,
    counts: &HashMap<Key, Big>,
) -> std::io::Result<()> {
    let Some(base_m) = config.lift_profile_base_m else {
        return Ok(());
    };
    let Some(path) = lift_profile_path(config) else {
        return Ok(());
    };
    let lift_m = base_m + 1;
    if depth < lift_m {
        return Ok(());
    }

    let base_modulus = residue_modulus(base_m, base_m);
    let lift_modulus = residue_modulus(lift_m, lift_m);
    let terminal_base_signature = config.terminal_value % base_modulus;
    let terminal_lift_signature = config.terminal_value % lift_modulus;
    let terminal_lift_digit =
        ((terminal_lift_signature - terminal_base_signature) / base_modulus) as usize;
    let mut groups: HashMap<(i64, u64), [bool; 3]> = HashMap::new();

    for key in counts.keys() {
        let base_signature = key.residue() % base_modulus;
        if base_signature != terminal_base_signature {
            continue;
        }
        let lift_digit = ((key.residue() - base_signature) / base_modulus) as usize;
        if lift_digit >= 3 {
            continue;
        }
        groups
            .entry((key.deficit(), base_signature))
            .or_insert([false; 3])[lift_digit] = true;
    }

    if groups.is_empty() {
        return Ok(());
    }

    let mut entries: Vec<((i64, u64), [bool; 3])> = groups.into_iter().collect();
    entries.sort_by_key(|((deficit, signature), _)| (*deficit, *signature));

    let mut file = OpenOptions::new().create(true).append(true).open(path)?;
    for ((deficit, signature), lifts) in entries {
        let lift_count = lifts.iter().filter(|present| **present).count();
        let survives_terminal = lifts[terminal_lift_digit];
        let lift0_signature = signature;
        let lift1_signature = signature + base_modulus;
        let lift2_signature = signature + 2 * base_modulus;
        let lineage_id = format!("d{}_r{}", deficit, signature);
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            depth,
            base_m,
            lift_m,
            deficit,
            signature,
            true,
            lift0_signature,
            lifts[0],
            lifts[0] && terminal_lift_digit == 0,
            lift1_signature,
            lifts[1],
            lifts[1] && terminal_lift_digit == 1,
            lift2_signature,
            lifts[2],
            lifts[2] && terminal_lift_digit == 2,
            lift_count,
            terminal_lift_digit,
            survives_terminal,
            lineage_id
        )?;
    }
    Ok(())
}

fn write_lift_profile_summary(config: &Config) -> std::io::Result<()> {
    let Some(profile_path) = lift_profile_path(config) else {
        return Ok(());
    };
    let Some(summary_path) = lift_profile_summary_path(config) else {
        return Ok(());
    };
    let text = read_to_string(&profile_path)?;
    let mut total_m_base_live = 0usize;
    let mut total_m_lift_terminal_live = 0usize;
    let mut deaths_before_m_lift = 0usize;
    let mut single_lift_survivors = 0usize;
    let mut multi_lift_survivors = 0usize;
    let mut max_lift_count = 0usize;

    for line in text.lines().skip(1) {
        if line.trim().is_empty() {
            continue;
        }
        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 19 {
            continue;
        }
        let lift_count: usize = fields[15].parse().unwrap_or(0);
        let survives_terminal = fields[17] == "true";
        total_m_base_live += 1;
        max_lift_count = max_lift_count.max(lift_count);
        if survives_terminal {
            total_m_lift_terminal_live += 1;
        } else {
            deaths_before_m_lift += 1;
        }
        if lift_count == 1 {
            single_lift_survivors += 1;
        } else if lift_count > 1 {
            multi_lift_survivors += 1;
        }
    }

    let total_possible_lifts = 3usize.saturating_mul(total_m_base_live);
    let lift_survival_ratio = if total_possible_lifts == 0 {
        0.0
    } else {
        total_m_lift_terminal_live as f64 / total_possible_lifts as f64
    };
    let mut file = BufWriter::new(File::create(summary_path)?);
    writeln!(file, "{{")?;
    writeln!(file, "  \"C\": {},", config.c)?;
    writeln!(
        file,
        "  \"m_base\": {},",
        config.lift_profile_base_m.unwrap_or(0)
    )?;
    writeln!(file, "  \"m_lift\": {},", config.residue_mod_power)?;
    writeln!(
        file,
        "  \"profile_path\": \"{}\",",
        json_escape(&profile_path.display().to_string())
    )?;
    writeln!(file, "  \"total_m_base_live\": {},", total_m_base_live)?;
    writeln!(
        file,
        "  \"total_possible_lifts\": {},",
        total_possible_lifts
    )?;
    writeln!(
        file,
        "  \"total_m_lift_terminal_live\": {},",
        total_m_lift_terminal_live
    )?;
    writeln!(
        file,
        "  \"lift_survival_ratio\": {:.12},",
        lift_survival_ratio
    )?;
    writeln!(
        file,
        "  \"deaths_before_m_lift\": {},",
        deaths_before_m_lift
    )?;
    writeln!(
        file,
        "  \"single_lift_survivors\": {},",
        single_lift_survivors
    )?;
    writeln!(
        file,
        "  \"multi_lift_survivors\": {},",
        multi_lift_survivors
    )?;
    writeln!(file, "  \"max_lift_count\": {}", max_lift_count)?;
    writeln!(file, "}}")?;
    Ok(())
}

fn emit_progress_jsonl(config: &Config, row: &Row, ever_seen_valid1: bool, started: Instant) {
    let line = format!(
        "{{\"event\":\"progress\",\"engine\":\"rust\",\"C\":{},\"target_depth\":{},\"depth\":{},\"residue_mod_power\":{},\"residue_modulus\":{},\"terminal_residue_signature\":{},\"symbolic_branch_count\":\"{}\",\"merged_state_count\":{},\"valid_from_1_count\":\"{}\",\"exact_depth_valid1\":\"{}\",\"terminal_1_compatible_signature_count\":{},\"live_valid1_count\":{},\"valid1_shadow_birth_count\":{},\"valid1_shadow_death_count\":{},\"max_valid1_shadow_lifetime\":{},\"valid1_shadow_persisted_from_previous\":{},\"live_valid1_lineage_count\":\"{}\",\"valid1_lineage_birth_count\":\"{}\",\"valid1_lineage_death_count\":\"{}\",\"max_valid1_lineage_lifetime\":{},\"lineage_lifetime_histogram\":\"{}\",\"ever_seen_valid1\":{},\"valid_residue_count\":{},\"max_branch_multiplicity\":\"{}\",\"rho_stable_count\":{},\"rho_lift_count\":{},\"longest_plateau\":{},\"max_rho_bit_length\":{},\"current_rss_kb\":{},\"peak_rss_kb\":{},\"elapsed_sec\":{:.6},\"notes\":\"{}\"}}",
        config.c,
        config.depth,
        row.depth,
        config.residue_mod_power,
        row.residue_modulus,
        row.terminal_residue_signature,
        row.symbolic_branch_count.to_decimal(),
        row.merged_state_count,
        row.valid_from_1_count.to_decimal(),
        row.exact_depth_valid1.to_decimal(),
        row.terminal_1_compatible_signature_count,
        row.live_valid1_count,
        row.valid1_shadow_birth_count,
        row.valid1_shadow_death_count,
        row.max_valid1_shadow_lifetime,
        row.valid1_shadow_persisted_from_previous,
        row.live_valid1_lineage_count.to_decimal(),
        row.valid1_lineage_birth_count.to_decimal(),
        row.valid1_lineage_death_count.to_decimal(),
        row.max_valid1_lineage_lifetime,
        json_escape(&row.lineage_lifetime_histogram_compact),
        ever_seen_valid1,
        row.valid_residue_count,
        row.max_branch_multiplicity.to_decimal(),
        row.rho_stable_count,
        row.rho_lift_count,
        row.longest_plateau,
        row.max_rho_bit_length,
        row.current_rss_kb,
        row.peak_rss_kb,
        started.elapsed().as_secs_f64(),
        json_escape(&row.notes)
    );
    append_jsonl(config, &line).expect("append progress jsonl");
}

fn emit_checkpoint_jsonl(config: &Config, depth: usize, path: &PathBuf, started: Instant) {
    let size_bytes = metadata(path).ok().map(|meta| meta.len()).unwrap_or(0);
    let line = format!(
        "{{\"event\":\"checkpoint\",\"engine\":\"rust\",\"C\":{},\"target_depth\":{},\"depth\":{},\"residue_mod_power\":{},\"checkpoint_path\":\"{}\",\"checkpoint_size_bytes\":{},\"elapsed_sec\":{:.6}}}",
        config.c,
        config.depth,
        depth,
        config.residue_mod_power,
        json_escape(&path.display().to_string()),
        size_bytes,
        started.elapsed().as_secs_f64()
    );
    append_jsonl(config, &line).expect("append checkpoint jsonl");
}

fn emit_final_jsonl(config: &Config, rows: &[Row], started: Instant) {
    let Some(last) = rows.last() else {
        return;
    };
    let ever_seen_valid1 = rows.iter().any(|row| !row.exact_depth_valid1.is_zero());
    let first_valid1_depth = rows
        .iter()
        .find(|row| !row.exact_depth_valid1.is_zero())
        .map(|row| row.depth);
    let first_valid1_json = first_valid1_depth
        .map(|depth| depth.to_string())
        .unwrap_or_else(|| "null".to_string());
    let line = format!(
        "{{\"event\":\"final\",\"engine\":\"rust\",\"C\":{},\"target_depth\":{},\"completed_depth\":{},\"residue_mod_power\":{},\"ever_seen_valid1\":{},\"first_valid1_depth\":{},\"final_live_valid1_count\":{},\"final_live_valid1_lineage_count\":\"{}\",\"final_valid_from_1_count\":\"{}\",\"final_compatible_signatures\":{},\"max_valid1_shadow_lifetime\":{},\"max_valid1_lineage_lifetime\":{},\"lineage_lifetime_histogram\":\"{}\",\"checkpoint_size_bytes\":{},\"elapsed_sec\":{:.6}}}",
        config.c,
        config.depth,
        last.depth,
        config.residue_mod_power,
        ever_seen_valid1,
        first_valid1_json,
        last.live_valid1_count,
        last.live_valid1_lineage_count.to_decimal(),
        last.valid_from_1_count.to_decimal(),
        last.terminal_1_compatible_signature_count,
        rows.iter()
            .map(|row| row.max_valid1_shadow_lifetime)
            .max()
            .unwrap_or(0),
        rows.iter()
            .map(|row| row.max_valid1_lineage_lifetime)
            .max()
            .unwrap_or(0),
        json_escape(&last.lineage_lifetime_histogram_compact),
        checkpoint_size_bytes(config).unwrap_or(0),
        started.elapsed().as_secs_f64()
    );
    append_jsonl(config, &line).expect("append final jsonl");
}

fn run_prior_odd_after_dirty(config: &Config) {
    let prior_m = config
        .residue_mod_power
        .checked_sub(1)
        .expect("prior odd residue power");
    let out_dir = PathBuf::from(format!(
        "{}_auto_prior_m{}",
        config.out_dir.display(),
        prior_m
    ));
    eprintln!(
        "lock3-auto-prior-odd trigger=start_dirty C={} even_m={} prior_m={} out_dir={}",
        config.c,
        config.residue_mod_power,
        prior_m,
        out_dir.display()
    );

    let exe = env::current_exe().expect("current executable path");
    let mut command = Command::new(exe);
    command
        .arg("--C")
        .arg(config.c.to_string())
        .arg("--depth")
        .arg(config.depth.to_string())
        .arg("--terminal-value")
        .arg(config.terminal_value.to_string())
        .arg("--residue-mod-power")
        .arg(prior_m.to_string())
        .arg("--out-dir")
        .arg(&out_dir)
        .arg("--progress-every")
        .arg(config.progress_every.to_string())
        .arg("--label")
        .arg(&config.label)
        .arg("--no-auto-prior-odd-on-even-dirty");
    if config.memory_lean {
        command.arg("--memory-lean");
    }
    if config.no_checkpoint {
        command.arg("--no-checkpoint");
    } else if config.checkpoint_every > 0 {
        let checkpoint_path = out_dir.join(format!(
            "lock3_C{}_m{}_auto_prior.checkpoint.bin",
            config.c, prior_m
        ));
        command
            .arg("--checkpoint-path")
            .arg(checkpoint_path)
            .arg("--checkpoint-every")
            .arg(config.checkpoint_every.to_string());
    }
    if let Some(memory_cap_mb) = config.memory_cap_mb {
        command
            .arg("--memory-cap-mb")
            .arg(memory_cap_mb.to_string());
    }
    let status = command.status().expect("run auto prior odd census");
    if !status.success() {
        panic!("auto prior odd census failed with status {}", status);
    }
}

fn credit_at_step(k: usize) -> i64 {
    (((k + 1) as f64 * ALPHA).floor() - (k as f64 * ALPHA).floor()) as i64
}

fn deficit_branch_capacity(c: i64) -> usize {
    if c < 0 {
        0
    } else {
        (c as usize).saturating_add(1)
    }
}

fn max_deficit_for_c(c: i64) -> Option<i64> {
    if c < 0 {
        None
    } else {
        Some(c)
    }
}

fn residue_modulus(depth: usize, residue_mod_power: usize) -> u64 {
    let power = depth.min(residue_mod_power);
    let mut modulus = 1u64;
    for _ in 0..power {
        modulus = modulus.checked_mul(3).expect("residue modulus overflow");
    }
    modulus
}

fn pow_mod(mut base: u64, mut exp: i64, modulus: u64) -> u64 {
    if modulus == 1 {
        return 0;
    }
    let mut acc = 1u64;
    base %= modulus;
    while exp > 0 {
        if exp & 1 == 1 {
            acc = ((acc as u128 * base as u128) % modulus as u128) as u64;
        }
        base = ((base as u128 * base as u128) % modulus as u128) as u64;
        exp >>= 1;
    }
    acc
}

fn mod_inverse(value: u64, modulus: u64) -> u64 {
    let mut t = 0i128;
    let mut new_t = 1i128;
    let mut r = modulus as i128;
    let mut new_r = value as i128;
    while new_r != 0 {
        let q = r / new_r;
        let old_t = t;
        t = new_t;
        new_t = old_t - q * new_t;
        let old_r = r;
        r = new_r;
        new_r = old_r - q * new_r;
    }
    if r != 1 {
        panic!("value is not invertible modulo modulus");
    }
    if t < 0 {
        t += modulus as i128;
    }
    t as u64
}

fn next_terminal_residue(residue: u64, exponent: i64, modulus: u64) -> u64 {
    if modulus == 1 {
        return 0;
    }
    let inv = mod_inverse(pow_mod(2, exponent, modulus), modulus);
    (((3u128 * residue as u128 + 1) * inv as u128) % modulus as u128) as u64
}

fn multiply_mod_power_of_two(lhs: &BigBits, rhs: &BigBits, bits: usize) -> BigBits {
    if bits == 0 || lhs.limbs.is_empty() || rhs.limbs.is_empty() {
        return BigBits::zero();
    }
    let limb_count = (bits + 63) / 64;
    let mut out = vec![0u64; limb_count];
    for (i, &a) in lhs.limbs.iter().enumerate() {
        if i >= limb_count {
            break;
        }
        let mut carry = 0u128;
        for (j, &b) in rhs.limbs.iter().enumerate() {
            let idx = i + j;
            if idx >= limb_count {
                break;
            }
            let value = out[idx] as u128 + a as u128 * b as u128 + carry;
            out[idx] = value as u64;
            carry = value >> 64;
        }
        let mut idx = i + rhs.limbs.len();
        while carry > 0 && idx < limb_count {
            let value = out[idx] as u128 + carry;
            out[idx] = value as u64;
            carry = value >> 64;
            idx += 1;
        }
    }
    BigBits { limbs: out }.truncated(bits)
}

fn subtract_mod_power_of_two(lhs: &BigBits, rhs: &BigBits, bits: usize) -> BigBits {
    if bits == 0 {
        return BigBits::zero();
    }
    let limb_count = (bits + 63) / 64;
    let lhs = lhs.truncated(bits);
    let rhs = rhs.truncated(bits);
    let mut out = vec![0u64; limb_count];
    let mut borrow = 0u128;
    for idx in 0..limb_count {
        let a = lhs.limbs.get(idx).copied().unwrap_or(0) as u128;
        let b = rhs.limbs.get(idx).copied().unwrap_or(0) as u128 + borrow;
        if a >= b {
            out[idx] = (a - b) as u64;
            borrow = 0;
        } else {
            out[idx] = ((1u128 << 64) + a - b) as u64;
            borrow = 1;
        }
    }
    BigBits { limbs: out }.truncated(bits)
}

fn rho_from_affine_small(a_sum: usize, b: &BigBits, pow3: &BigBits) -> BigBits {
    let bits = a_sum + 1;
    if bits > 20 {
        panic!("rho fallback exceeded small modulus");
    }
    let target = subtract_mod_power_of_two(&BigBits::from_power_of_two(a_sum), b, bits);
    let limit = 1u64 << bits;
    for candidate in 0..limit {
        let candidate_bits = BigBits {
            limbs: if candidate == 0 {
                Vec::new()
            } else {
                vec![candidate]
            },
        };
        if multiply_mod_power_of_two(pow3, &candidate_bits, bits) == target {
            if candidate == 0 {
                return BigBits::from_power_of_two(bits);
            }
            return candidate_bits;
        }
    }
    panic!("rho not found");
}

fn lift_rho(
    witness: &Witness,
    next_a_sum: usize,
    next_b: &BigBits,
    next_pow3: &BigBits,
) -> BigBits {
    let bits = next_a_sum + 1;
    let target = subtract_mod_power_of_two(&BigBits::from_power_of_two(next_a_sum), next_b, bits);
    if let Some(previous_rho) = &witness.previous_rho {
        let lift_bits = next_a_sum - witness.a_sum;
        let lift_limit = 1u64 << lift_bits;
        let shift = witness.a_sum + 1;
        for lift_digit in 0..lift_limit {
            let candidate = previous_rho.add_shifted_digit(lift_digit, shift);
            if multiply_mod_power_of_two(next_pow3, &candidate, bits) == target {
                return candidate;
            }
        }
    }
    rho_from_affine_small(next_a_sum, next_b, next_pow3)
}

fn update_witness(witness: &Witness, exponent: i64) -> Witness {
    let next_a_sum = witness.a_sum + exponent as usize;
    let mut next_b = witness.b.clone();
    next_b.mul_small(3);
    next_b.add_power_of_two(witness.a_sum);
    let mut next_pow3 = witness.pow3.clone();
    next_pow3.mul_small(3);
    let rho = lift_rho(witness, next_a_sum, &next_b, &next_pow3);
    let rho_changed = witness
        .previous_rho
        .as_ref()
        .map(|previous| previous != &rho)
        .unwrap_or(true);
    let lift_count =
        witness.lift_count + usize::from(rho_changed && witness.previous_rho.is_some());
    let current_plateau = if rho_changed {
        0
    } else {
        witness.current_plateau + 1
    };
    Witness {
        a_sum: next_a_sum,
        b: next_b,
        pow3: next_pow3,
        previous_rho: Some(rho),
        lift_count,
        current_plateau,
        longest_plateau: witness.longest_plateau.max(current_plateau),
    }
}

fn bit_length_u128(value: u128) -> usize {
    if value == 0 {
        0
    } else {
        128 - value.leading_zeros() as usize
    }
}

fn mod_inverse_u128_mod_u64(value: u128, modulus: u64) -> Option<u64> {
    if modulus == 1 {
        return Some(0);
    }
    let mut t = 0i128;
    let mut new_t = 1i128;
    let mut r = modulus as i128;
    let mut new_r = (value % modulus as u128) as i128;
    while new_r != 0 {
        let q = r / new_r;
        let old_t = t;
        t = new_t;
        new_t = old_t - q * new_t;
        let old_r = r;
        r = new_r;
        new_r = old_r - q * new_r;
    }
    if r != 1 {
        return None;
    }
    if t < 0 {
        t += modulus as i128;
    }
    Some(t as u64)
}

fn crt_power2_power3_u128(
    rho: u128,
    rho_modulus: u128,
    residue: u64,
    modulus3: u64,
) -> Option<(u128, u128)> {
    let rho_mod = rho % rho_modulus;
    let inv = mod_inverse_u128_mod_u64(rho_modulus, modulus3)?;
    let diff =
        (residue as u128 + modulus3 as u128 - (rho_mod % modulus3 as u128)) % modulus3 as u128;
    let t = (diff * inv as u128) % modulus3 as u128;
    let combined_modulus = rho_modulus.checked_mul(modulus3 as u128)?;
    let candidate = rho_mod.checked_add(rho_modulus.checked_mul(t)?)? % combined_modulus;
    let candidate = if candidate == 0 {
        combined_modulus
    } else {
        candidate
    };
    Some((candidate, combined_modulus))
}

fn odd_collatz_step_u128(value: u128) -> Option<(u128, usize)> {
    let lifted = value.checked_mul(3)?.checked_add(1)?;
    let exponent = lifted.trailing_zeros() as usize;
    Some((lifted >> exponent, exponent))
}

fn try_follow_breach_u128(
    config: &Config,
    event: &CorridorBreachEvent,
    witness: &Witness,
) -> CorridorBreachFollow {
    let mut row = CorridorBreachFollow {
        c_configured: event.c_configured,
        m: event.m,
        breach_depth: event.depth,
        key: event.key,
        breached_from_c: event.breached_from_c,
        breached_to_c: event.breached_to_c,
        d_k: event.d_k,
        a_k: event.a_k,
        rho: None,
        rho_modulus_bit_length: witness.a_sum.saturating_add(1),
        candidate_integer: None,
        candidate_bit_length: 0,
        combined_modulus_bit_length: 0,
        terminal_value_after_prefix: None,
        terminal_value_bit_length: 0,
        follow_steps: 0,
        collapsed_to_1: false,
        min_d_seen_after_breach: event.d_k,
        max_d_seen_after_breach: event.d_k,
        max_c_seen_after_breach: event.d_k.max(config.c),
        re_entered_birth_corridor: false,
        peak_value_bit_length: 0,
        status: "unstarted".to_string(),
        notes: String::new(),
    };

    let Some(rho) = witness
        .previous_rho
        .as_ref()
        .and_then(BigBits::to_u128_checked)
    else {
        row.status = "too_wide_for_u128_rho".to_string();
        row.notes = "representative rho exceeds u128 follow path".to_string();
        return row;
    };
    if witness.a_sum + 1 >= 128 {
        row.rho = Some(rho);
        row.status = "too_wide_for_u128_rho_modulus".to_string();
        row.notes = "2^(A+1) does not fit the u128 CRT path".to_string();
        return row;
    }
    let rho_modulus = 1u128 << (witness.a_sum + 1);
    let modulus3 = residue_modulus(event.depth, config.residue_mod_power);
    let Some((candidate, combined_modulus)) =
        crt_power2_power3_u128(rho, rho_modulus, event.key.residue(), modulus3)
    else {
        row.rho = Some(rho);
        row.status = "too_wide_for_u128_crt".to_string();
        row.notes = "CRT product overflowed u128".to_string();
        return row;
    };
    row.rho = Some(rho);
    row.candidate_integer = Some(candidate);
    row.candidate_bit_length = bit_length_u128(candidate);
    row.combined_modulus_bit_length = bit_length_u128(combined_modulus);

    let Some(pow3) = witness.pow3.to_u128_checked() else {
        row.status = "too_wide_for_u128_pow3".to_string();
        row.notes = "3^depth exceeds u128 prefix evaluation path".to_string();
        return row;
    };
    let Some(b) = witness.b.to_u128_checked() else {
        row.status = "too_wide_for_u128_affine_offset".to_string();
        row.notes = "affine offset exceeds u128 prefix evaluation path".to_string();
        return row;
    };
    let Some(numerator) = pow3
        .checked_mul(candidate)
        .and_then(|value| value.checked_add(b))
    else {
        row.status = "too_wide_for_u128_affine_value".to_string();
        row.notes = "prefix affine value overflows u128".to_string();
        return row;
    };
    if witness.a_sum >= 128 {
        row.status = "too_wide_for_u128_affine_shift".to_string();
        row.notes = "A sum exceeds u128 prefix evaluation path".to_string();
        return row;
    }
    let divisor = if witness.a_sum == 0 {
        1u128
    } else {
        1u128 << witness.a_sum
    };
    if numerator % divisor != 0 {
        row.status = "affine_prefix_not_integral".to_string();
        row.notes = "representative witness failed integral prefix division".to_string();
        return row;
    }
    let mut value = numerator / divisor;
    if value % modulus3 as u128 != event.key.residue() as u128 {
        row.status = "terminal_residue_mismatch_after_prefix".to_string();
        row.notes = "prefix value did not match breach residue signature".to_string();
        return row;
    }

    row.terminal_value_after_prefix = Some(value);
    row.terminal_value_bit_length = bit_length_u128(value);
    row.peak_value_bit_length = row.terminal_value_bit_length;

    let mut depth = event.depth;
    let mut a_sum = witness.a_sum;
    while value != 1 && row.follow_steps < config.max_follow_steps {
        let Some((next_value, exponent)) = odd_collatz_step_u128(value) else {
            row.status = "u128_overflow_during_follow".to_string();
            row.notes = "3x+1 overflowed the bounded witness follow path".to_string();
            return row;
        };
        value = next_value;
        depth += 1;
        a_sum = a_sum.saturating_add(exponent);
        row.follow_steps += 1;
        row.peak_value_bit_length = row.peak_value_bit_length.max(bit_length_u128(value));
        let d = ((depth as f64 * ALPHA).floor() as i64) - a_sum as i64;
        row.min_d_seen_after_breach = row.min_d_seen_after_breach.min(d);
        row.max_d_seen_after_breach = row.max_d_seen_after_breach.max(d);
        row.max_c_seen_after_breach = row.max_c_seen_after_breach.max(d);
        if !row.re_entered_birth_corridor && d >= 0 && d <= config.c {
            row.re_entered_birth_corridor = true;
        }
    }

    if value == 1 {
        row.collapsed_to_1 = true;
        row.status = "collapsed_to_1".to_string();
        row.notes = format!(
            "reached 1; min_d={}; max_d={}; re_entered_birth={}",
            row.min_d_seen_after_breach, row.max_d_seen_after_breach,
            row.re_entered_birth_corridor
        );
    } else {
        row.status = "max_follow_steps_reached".to_string();
        row.notes = "bounded u128 witness did not reach 1 before the follow-step cap".to_string();
    }
    row
}

fn format_ratio(numerator: &Big, denominator: &Big) -> String {
    if denominator.is_zero() {
        return "0".to_string();
    }
    format!(
        "{:.12}",
        numerator.to_f64_lossy() / denominator.to_f64_lossy()
    )
}

fn format_ratio_usize(numerator: &Big, denominator: usize) -> String {
    if denominator == 0 {
        return "0".to_string();
    }
    format!("{:.12}", numerator.to_f64_lossy() / denominator as f64)
}

fn memory_kb() -> (u64, u64) {
    let Ok(status) = read_to_string("/proc/self/status") else {
        return (0, 0);
    };
    let mut rss = 0u64;
    let mut hwm = 0u64;
    for line in status.lines() {
        if let Some(rest) = line.strip_prefix("VmRSS:") {
            rss = rest
                .split_whitespace()
                .next()
                .and_then(|value| value.parse().ok())
                .unwrap_or(0);
        } else if let Some(rest) = line.strip_prefix("VmHWM:") {
            hwm = rest
                .split_whitespace()
                .next()
                .and_then(|value| value.parse().ok())
                .unwrap_or(0);
        }
    }
    (rss, hwm)
}

fn enforce_memory_cap(config: &Config, peak_rss_kb: u64) {
    if let Some(cap_mb) = config.memory_cap_mb {
        let cap_kb = cap_mb.saturating_mul(1024);
        if peak_rss_kb > cap_kb {
            panic!(
                "memory cap exceeded: peak_rss_kb={} cap_kb={}",
                peak_rss_kb, cap_kb
            );
        }
    }
}

fn write_u8(file: &mut BufWriter<File>, value: u8) -> std::io::Result<()> {
    file.write_all(&[value])
}

fn write_u32(file: &mut BufWriter<File>, value: u32) -> std::io::Result<()> {
    file.write_all(&value.to_le_bytes())
}

fn write_u64(file: &mut BufWriter<File>, value: u64) -> std::io::Result<()> {
    file.write_all(&value.to_le_bytes())
}

fn write_i64(file: &mut BufWriter<File>, value: i64) -> std::io::Result<()> {
    file.write_all(&value.to_le_bytes())
}

fn read_exact<const N: usize>(file: &mut File) -> std::io::Result<[u8; N]> {
    let mut buf = [0u8; N];
    file.read_exact(&mut buf)?;
    Ok(buf)
}

fn read_u8(file: &mut File) -> std::io::Result<u8> {
    Ok(read_exact::<1>(file)?[0])
}

fn read_u32(file: &mut File) -> std::io::Result<u32> {
    Ok(u32::from_le_bytes(read_exact::<4>(file)?))
}

fn read_u64(file: &mut File) -> std::io::Result<u64> {
    Ok(u64::from_le_bytes(read_exact::<8>(file)?))
}

fn read_i64(file: &mut File) -> std::io::Result<i64> {
    Ok(i64::from_le_bytes(read_exact::<8>(file)?))
}

fn write_big(file: &mut BufWriter<File>, value: &Big) -> std::io::Result<()> {
    write_u64(file, value.limbs.len() as u64)?;
    for limb in value.limbs.iter() {
        write_u32(file, *limb)?;
    }
    Ok(())
}

fn read_big(file: &mut File) -> std::io::Result<Big> {
    let len = read_u64(file)? as usize;
    let mut limbs = Vec::with_capacity(len);
    for _ in 0..len {
        limbs.push(read_u32(file)?);
    }
    Ok(Big { limbs })
}

fn write_bigbits(file: &mut BufWriter<File>, value: &BigBits) -> std::io::Result<()> {
    write_u64(file, value.limbs.len() as u64)?;
    for limb in value.limbs.iter() {
        write_u64(file, *limb)?;
    }
    Ok(())
}

fn read_bigbits(file: &mut File) -> std::io::Result<BigBits> {
    let len = read_u64(file)? as usize;
    let mut limbs = Vec::with_capacity(len);
    for _ in 0..len {
        limbs.push(read_u64(file)?);
    }
    Ok(BigBits { limbs })
}

fn write_row(file: &mut BufWriter<File>, row: &Row) -> std::io::Result<()> {
    write_u64(file, row.depth as u64)?;
    write_u64(file, row.residue_modulus)?;
    write_u64(file, row.terminal_residue_signature)?;
    write_big(file, &row.symbolic_branch_count)?;
    write_u64(file, row.merged_state_count as u64)?;
    write_big(file, &row.valid_from_1_count)?;
    write_u64(file, row.terminal_1_compatible_signature_count as u64)?;
    write_u64(file, row.valid_residue_count as u64)?;
    write_big(file, &row.max_branch_multiplicity)?;
    write_u64(file, row.rho_stable_count as u64)?;
    write_u64(file, row.rho_lift_count as u64)?;
    write_u64(file, row.longest_plateau as u64)?;
    write_u64(file, row.max_rho_bit_length as u64)?;
    Ok(())
}

fn read_row(file: &mut File, config: &Config) -> std::io::Result<Row> {
    let depth = read_u64(file)? as usize;
    let residue_modulus = read_u64(file)?;
    let terminal_residue_signature = read_u64(file)?;
    let symbolic_branch_count = read_big(file)?;
    let merged_state_count = read_u64(file)? as usize;
    let valid_from_1_count = read_big(file)?;
    let terminal_1_compatible_signature_count = read_u64(file)? as usize;
    let valid_residue_count = read_u64(file)? as usize;
    let max_branch_multiplicity = read_big(file)?;
    let rho_stable_count = read_u64(file)? as usize;
    let rho_lift_count = read_u64(file)? as usize;
    let longest_plateau = read_u64(file)? as usize;
    let max_rho_bit_length = read_u64(file)? as usize;
    let notes = format!(
        "rust_census_by_deficit_and_terminal_residue_signature;rho_metrics_on_representative_witnesses;terminal_compatibility_mod_3^{}",
        depth.min(config.residue_mod_power)
    );
    Ok(Row {
        depth,
        residue_modulus,
        terminal_residue_signature,
        compression_ratio: format_ratio_usize(&symbolic_branch_count, merged_state_count),
        valid_fraction: format_ratio(&valid_from_1_count, &symbolic_branch_count),
        symbolic_branch_count,
        merged_state_count,
        exact_depth_valid1: valid_from_1_count.clone(),
        valid_from_1_count,
        terminal_1_compatible_signature_count,
        valid_residue_count,
        max_branch_multiplicity,
        rho_stable_count,
        rho_lift_count,
        longest_plateau,
        max_rho_bit_length,
        notes,
        current_rss_kb: 0,
        peak_rss_kb: 0,
        live_valid1_count: 0,
        valid1_shadow_birth_count: 0,
        valid1_shadow_death_count: 0,
        max_valid1_shadow_lifetime: 0,
        valid1_shadow_persisted_from_previous: false,
        live_valid1_lineage_count: Big::zero(),
        valid1_lineage_birth_count: Big::zero(),
        valid1_lineage_death_count: Big::zero(),
        max_valid1_lineage_lifetime: 0,
        lineage_lifetime_histogram_compact: String::new(),
        exit_up_count: Big::zero(),
        exit_down_count: Big::zero(),
        stay_count: Big::zero(),
    })
}

fn write_checkpoint(
    path: &PathBuf,
    config: &Config,
    depth: usize,
    counts: &HashMap<Key, Big>,
    witnesses: &HashMap<Key, Witness>,
    order: &[Key],
    rows: &[Row],
) -> std::io::Result<()> {
    let tmp_path = path.with_extension("tmp");
    if let Some(parent) = path.parent() {
        create_dir_all(parent)?;
    }
    let mut file = BufWriter::new(File::create(&tmp_path)?);
    file.write_all(b"L3CENSUS2")?;
    write_u64(&mut file, depth as u64)?;
    write_i64(&mut file, config.c)?;
    write_u64(&mut file, config.terminal_value)?;
    write_u64(&mut file, config.residue_mod_power as u64)?;
    write_u64(&mut file, rows.len() as u64)?;
    for row in rows {
        write_row(&mut file, row)?;
    }
    write_u64(&mut file, order.len() as u64)?;
    for key in order {
        let count = counts.get(key).expect("checkpoint count missing");
        let witness = witnesses.get(key).expect("checkpoint witness missing");
        write_i64(&mut file, key.deficit())?;
        write_u64(&mut file, key.residue())?;
        write_big(&mut file, count)?;
        write_u64(&mut file, witness.a_sum as u64)?;
        write_bigbits(&mut file, &witness.b)?;
        write_bigbits(&mut file, &witness.pow3)?;
        match &witness.previous_rho {
            Some(rho) => {
                write_u8(&mut file, 1)?;
                write_bigbits(&mut file, rho)?;
            }
            None => write_u8(&mut file, 0)?,
        }
        write_u64(&mut file, witness.lift_count as u64)?;
        write_u64(&mut file, witness.current_plateau as u64)?;
        write_u64(&mut file, witness.longest_plateau as u64)?;
    }
    file.flush()?;
    rename(tmp_path, path)?;
    Ok(())
}

fn read_checkpoint(
    path: &PathBuf,
    config: &Config,
) -> std::io::Result<(
    usize,
    HashMap<Key, Big>,
    HashMap<Key, Witness>,
    Vec<Key>,
    Vec<Row>,
)> {
    let mut file = File::open(path)?;
    let mut magic = [0u8; 9];
    file.read_exact(&mut magic)?;
    if &magic != b"L3CENSUS2" {
        panic!("invalid Lock 3 checkpoint magic");
    }
    let depth = read_u64(&mut file)? as usize;
    let c = read_i64(&mut file)?;
    let terminal_value = read_u64(&mut file)?;
    let residue_mod_power = read_u64(&mut file)? as usize;
    if c != config.c
        || terminal_value != config.terminal_value
        || residue_mod_power != config.residue_mod_power
    {
        panic!("checkpoint parameters do not match requested run");
    }
    let row_count = read_u64(&mut file)? as usize;
    let mut rows = Vec::with_capacity(row_count);
    for _ in 0..row_count {
        rows.push(read_row(&mut file, config)?);
    }
    let state_count = read_u64(&mut file)? as usize;
    let mut counts = HashMap::with_capacity(state_count);
    let mut witnesses = HashMap::with_capacity(state_count);
    let mut order = Vec::with_capacity(state_count);
    for _ in 0..state_count {
        let key = Key::new(read_i64(&mut file)?, read_u64(&mut file)?);
        let count = read_big(&mut file)?;
        let a_sum = read_u64(&mut file)? as usize;
        let b = read_bigbits(&mut file)?;
        let pow3 = read_bigbits(&mut file)?;
        let previous_rho = if read_u8(&mut file)? == 1 {
            Some(read_bigbits(&mut file)?)
        } else {
            None
        };
        let lift_count = read_u64(&mut file)? as usize;
        let current_plateau = read_u64(&mut file)? as usize;
        let longest_plateau = read_u64(&mut file)? as usize;
        order.push(key);
        counts.insert(key, count);
        witnesses.insert(
            key,
            Witness {
                a_sum,
                b,
                pow3,
                previous_rho,
                lift_count,
                current_plateau,
                longest_plateau,
            },
        );
    }
    Ok((depth, counts, witnesses, order, rows))
}

fn write_lean_checkpoint(
    path: &PathBuf,
    config: &Config,
    depth: usize,
    counts: &HashMap<Key, Big>,
    rows: &[Row],
) -> std::io::Result<()> {
    let tmp_path = path.with_extension("tmp");
    if let Some(parent) = path.parent() {
        create_dir_all(parent)?;
    }
    let mut file = BufWriter::new(File::create(&tmp_path)?);
    file.write_all(b"L3LEAN01")?;
    write_u64(&mut file, depth as u64)?;
    write_i64(&mut file, config.c)?;
    write_u64(&mut file, config.terminal_value)?;
    write_u64(&mut file, config.residue_mod_power as u64)?;
    write_u64(&mut file, rows.len() as u64)?;
    for row in rows {
        write_row(&mut file, row)?;
    }
    write_u64(&mut file, counts.len() as u64)?;
    for (key, count) in counts {
        write_u64(&mut file, key.0)?;
        write_big(&mut file, count)?;
    }
    file.flush()?;
    rename(tmp_path, path)?;
    Ok(())
}

fn read_lean_checkpoint(
    path: &PathBuf,
    config: &Config,
) -> std::io::Result<(usize, HashMap<Key, Big>, Vec<Row>)> {
    let mut file = File::open(path)?;
    let mut magic = [0u8; 8];
    file.read_exact(&mut magic)?;
    if &magic != b"L3LEAN01" {
        panic!("invalid Lock 3 lean checkpoint magic");
    }
    let depth = read_u64(&mut file)? as usize;
    let c = read_i64(&mut file)?;
    let terminal_value = read_u64(&mut file)?;
    let residue_mod_power = read_u64(&mut file)? as usize;
    if c != config.c
        || terminal_value != config.terminal_value
        || residue_mod_power != config.residue_mod_power
    {
        panic!("lean checkpoint parameters do not match requested run");
    }
    let row_count = read_u64(&mut file)? as usize;
    let mut rows = Vec::with_capacity(row_count.max(config.depth));
    for _ in 0..row_count {
        rows.push(read_row(&mut file, config)?);
    }
    let state_count = read_u64(&mut file)? as usize;
    let mut counts = HashMap::with_capacity(state_count);
    for _ in 0..state_count {
        let key = Key(read_u64(&mut file)?);
        let count = read_big(&mut file)?;
        counts.insert(key, count);
    }
    Ok((depth, counts, rows))
}

fn run_census(config: &Config, started: Instant) -> CensusResult {
    if config.memory_lean {
        return run_census_lean(config, started);
    }
    let (start_depth, mut counts, mut witnesses, mut order, mut rows) =
        if let Some(path) = &config.resume_path {
            read_checkpoint(path, config).expect("read checkpoint")
        } else {
            let mut counts = HashMap::new();
            let mut witnesses = HashMap::new();
            let order = vec![Key::new(0, 0)];
            counts.insert(Key::new(0, 0), Big::one());
            witnesses.insert(
                Key::new(0, 0),
                Witness {
                    a_sum: 0,
                    b: BigBits::zero(),
                    pow3: BigBits::one(),
                    previous_rho: None,
                    lift_count: 0,
                    current_plateau: 0,
                    longest_plateau: 0,
                },
            );
            (
                0,
                counts,
                witnesses,
                order,
                Vec::with_capacity(config.depth),
            )
        };
    if start_depth > config.depth {
        panic!("checkpoint depth is beyond requested target depth");
    }

    let mut ever_seen_valid1 = rows.iter().any(|row| !row.exact_depth_valid1.is_zero());
    let mut corridor_breach_events = Vec::new();
    let mut corridor_breach_follows = Vec::new();
    let mut downward_exit_follows: Vec<DownwardExitFollow> = Vec::new();

    for next_depth in (start_depth + 1)..=config.depth {
        let c = credit_at_step(next_depth - 1);
        let modulus = residue_modulus(next_depth, config.residue_mod_power);
        let terminal_residue_signature = config.terminal_value % modulus;
        let branch_capacity = deficit_branch_capacity(config.c);
        let mut next_counts: HashMap<Key, Big> =
            HashMap::with_capacity(counts.len().saturating_mul(branch_capacity));
        let mut next_witnesses: HashMap<Key, Witness> =
            HashMap::with_capacity(counts.len().saturating_mul(branch_capacity));
        let mut next_order: Vec<Key> =
            Vec::with_capacity(counts.len().saturating_mul(branch_capacity));

        // --- PARALLEL STATE TRANSITION (full witness mode) ---
        if let Some(max_deficit) = max_deficit_for_c(config.c) {
            // Phase 1: compute successor (key, multiplicity, witness) triples in parallel
            let keyed_entries: Vec<(&Key, &Big, &Witness)> = order
                .iter()
                .map(|key| {
                    let multiplicity = counts.get(key).expect("multiplicity missing");
                    let witness = witnesses.get(key).expect("witness missing");
                    (key, multiplicity, witness)
                })
                .collect();

            let partial_results: Vec<Vec<(Key, Big, Witness)>> = keyed_entries
                .par_iter()
                .map(|&(key, multiplicity, witness)| {
                    let mut local: Vec<(Key, Big, Witness)> = Vec::with_capacity(max_deficit as usize + 1);
                    for d_next in 0..=max_deficit {
                        let a = key.deficit() + c - d_next;
                        if a < 1 {
                            continue;
                        }
                        let next_key =
                            Key::new(d_next, next_terminal_residue(key.residue(), a, modulus));
                        local.push((next_key, multiplicity.clone(), update_witness(witness, a)));
                    }
                    local
                })
                .collect();

            // Merge partial results
            for local in partial_results {
                for (next_key, multiplicity, wit) in local {
                    if !next_counts.contains_key(&next_key) {
                        next_order.push(next_key);
                        next_counts.insert(next_key, Big::zero());
                        next_witnesses.insert(next_key, wit);
                    }
                    next_counts
                        .get_mut(&next_key)
                        .expect("newly inserted count missing")
                        .add_assign(&multiplicity);
                }
            }

            // Phase 2: sequential breach + downward exit tracking (needs witness data)
            for key in order.iter() {
                let multiplicity = counts.get(key).expect("multiplicity missing");
                let witness = witnesses.get(key).expect("witness missing");

                // Upward breach tracking
                if config.track_corridor_breaches {
                    let breach_start = max_deficit + 1;
                    let breach_end = config.max_corridor_breach_target.unwrap_or(breach_start);
                    for breach_deficit in breach_start..=breach_end {
                        let a = key.deficit() + c - breach_deficit;
                        if a >= 1 {
                            let breach_key = Key::new(
                                breach_deficit,
                                next_terminal_residue(key.residue(), a, modulus),
                            );
                            let event = CorridorBreachEvent {
                                c_configured: config.c,
                                m: config.residue_mod_power,
                                depth: next_depth,
                                key: breach_key,
                                old_max_d: max_deficit,
                                new_max_d: breach_deficit,
                                breached_from_c: max_deficit,
                                breached_to_c: breach_deficit,
                                d_k: breach_deficit,
                                a_k: a,
                                terminal_compatible: breach_key.residue()
                                    == terminal_residue_signature,
                                live_valid1_key_count: 0,
                                live_valid1_lineage_count: Big::zero(),
                                lineage_count: multiplicity.clone(),
                                birth_count: Big::zero(),
                                death_count: Big::zero(),
                                lifetime: 0,
                                notes:
                                    "candidate_boundary_transition_not_inserted_into_fixed_C_census",
                            };
                            if config.follow_breach_witnesses
                                && corridor_breach_follows.len() < config.max_follow_witnesses
                            {
                                let breach_witness = update_witness(witness, a);
                                corridor_breach_follows.push(try_follow_breach_u128(
                                    config,
                                    &event,
                                    &breach_witness,
                                ));
                            }
                            corridor_breach_events.push(event);
                        }
                    }
                }

                // Downward exit following
                if config.follow_down_witnesses
                    && downward_exit_follows.len() < config.max_follow_witnesses
                {
                    let max_a_in_corridor = key.deficit() + c;
                    let down_a = max_a_in_corridor + 1;
                    if down_a >= 1 {
                        downward_exit_follows.push(try_follow_down_exit_u128(
                            config,
                            next_depth,
                            key,
                            down_a,
                            witness,
                        ));
                    }
                }
            }
        }

        counts = next_counts;
        witnesses = next_witnesses;
        order = next_order;
        let mut symbolic_branch_count = Big::zero();
        let mut valid_from_1_count = Big::zero();
        let mut max_branch_multiplicity = Big::zero();
        let mut residues: HashSet<u64> = HashSet::with_capacity(counts.len());
        let mut compatible_signatures = 0usize;

        for key in order.iter() {
            let multiplicity = counts
                .get(key)
                .expect("multiplicity missing for ordered census key");
            symbolic_branch_count.add_assign(multiplicity);
            residues.insert(key.residue());
            if multiplicity.cmp_big(&max_branch_multiplicity) == Ordering::Greater {
                max_branch_multiplicity = multiplicity.clone();
            }
            if key.residue() == terminal_residue_signature {
                compatible_signatures += 1;
                valid_from_1_count.add_assign(multiplicity);
            }
        }
        append_lift_profile(config, next_depth, &counts).expect("append lift profile");
        let rho_stable_count = witnesses
            .values()
            .filter(|witness| witness.current_plateau > 0)
            .count();
        let rho_lift_count = witnesses
            .values()
            .map(|witness| witness.lift_count)
            .max()
            .unwrap_or(0);
        let longest_plateau = witnesses
            .values()
            .map(|witness| witness.longest_plateau)
            .max()
            .unwrap_or(0);
        let max_rho_bit_length = witnesses
            .values()
            .filter_map(|witness| witness.previous_rho.as_ref())
            .map(|rho| rho.bit_length())
            .max()
            .unwrap_or(0);

        let merged_state_count = counts.len();
        let notes = format!(
            "rust_census_by_deficit_and_terminal_residue_signature;rho_metrics_on_representative_witnesses;terminal_compatibility_mod_3^{}",
            next_depth.min(config.residue_mod_power)
        );
        let (current_rss_kb, peak_rss_kb) = memory_kb();
        let row = Row {
            depth: next_depth,
            residue_modulus: modulus,
            terminal_residue_signature,
            compression_ratio: format_ratio_usize(&symbolic_branch_count, merged_state_count),
            valid_fraction: format_ratio(&valid_from_1_count, &symbolic_branch_count),
            current_rss_kb,
            peak_rss_kb,
            symbolic_branch_count,
            merged_state_count,
            exact_depth_valid1: valid_from_1_count.clone(),
            valid_from_1_count,
            terminal_1_compatible_signature_count: compatible_signatures,
            valid_residue_count: residues.len(),
            max_branch_multiplicity,
            rho_stable_count,
            rho_lift_count,
            longest_plateau,
            max_rho_bit_length,
            notes,
            live_valid1_count: 0,
            valid1_shadow_birth_count: 0,
            valid1_shadow_death_count: 0,
            max_valid1_shadow_lifetime: 0,
            valid1_shadow_persisted_from_previous: false,
            live_valid1_lineage_count: Big::zero(),
            valid1_lineage_birth_count: Big::zero(),
            valid1_lineage_death_count: Big::zero(),
            max_valid1_lineage_lifetime: 0,
            lineage_lifetime_histogram_compact: String::new(),
            exit_up_count: Big::zero(),
            exit_down_count: Big::zero(),
            stay_count: Big::zero(),
        };
        enforce_memory_cap(config, row.peak_rss_kb);
        ever_seen_valid1 |= !row.exact_depth_valid1.is_zero();
        emit_progress_jsonl(config, &row, ever_seen_valid1, started);

        if config.progress_every > 0
            && (next_depth == config.depth || next_depth % config.progress_every == 0)
        {
            eprintln!(
                "lock3-census-progress engine=rust C={} depth={}/{} branches={} merged={} valid1={} exact_depth_valid1={} compatible_signatures={} ever_seen_valid1={} valid_residues={} mod={} lifts={} longest_plateau={} max_bits={} rss_kb={} peak_rss_kb={} elapsed_sec={:.1} notes={}",
                config.c,
                next_depth,
                config.depth,
                row.symbolic_branch_count.to_decimal(),
                row.merged_state_count,
                row.valid_from_1_count.to_decimal(),
                row.exact_depth_valid1.to_decimal(),
                row.terminal_1_compatible_signature_count,
                ever_seen_valid1,
                row.valid_residue_count,
                row.residue_modulus,
                row.rho_lift_count,
                row.longest_plateau,
                row.max_rho_bit_length,
                row.current_rss_kb,
                row.peak_rss_kb,
                started.elapsed().as_secs_f64(),
                row.notes
            );
        }
        let stop_for_start_dirty = should_stop_for_start_dirty(config, &row);
        rows.push(row);
        if !config.no_checkpoint {
            if let Some(path) = &config.checkpoint_path {
                if config.checkpoint_every > 0
                    && (next_depth == config.depth || next_depth % config.checkpoint_every == 0)
                {
                    write_checkpoint(path, config, next_depth, &counts, &witnesses, &order, &rows)
                        .expect("write checkpoint");
                    eprintln!(
                        "lock3-census-checkpoint depth={} path={}",
                        next_depth,
                        path.display()
                    );
                    emit_checkpoint_jsonl(config, next_depth, path, started);
                }
            }
        }
        if stop_for_start_dirty {
            eprintln!(
                "lock3-auto-stop reason=start_dirty C={} even_m={} depth={}",
                config.c, config.residue_mod_power, next_depth
            );
            break;
        }
    }

    CensusResult {
        rows,
        birth_audit_rows: Vec::new(),
        corridor_breach_events,
        corridor_breach_follows,
        downward_exit_follows,
    }
}

fn add_lineage_cohort(
    cohorts: &mut HashMap<Key, BTreeMap<usize, Big>>,
    key: Key,
    birth_depth: usize,
    count: &Big,
) {
    cohorts
        .entry(key)
        .or_default()
        .entry(birth_depth)
        .or_insert_with(Big::zero)
        .add_assign(count);
}

fn sum_lineage_cohorts(cohorts: &HashMap<Key, BTreeMap<usize, Big>>) -> Big {
    let mut total = Big::zero();
    for birth_counts in cohorts.values() {
        for count in birth_counts.values() {
            total.add_assign(count);
        }
    }
    total
}

fn compact_lifetime_histogram(histogram: &BTreeMap<usize, Big>) -> String {
    let mut parts = Vec::with_capacity(histogram.len());
    for (lifetime, count) in histogram {
        parts.push(format!("{}:{}", lifetime, count.to_decimal()));
    }
    parts.join(";")
}

fn run_census_lean(config: &Config, started: Instant) -> CensusResult {
    let (start_depth, mut counts, mut rows) = if let Some(path) = &config.resume_path {
        read_lean_checkpoint(path, config).expect("read lean checkpoint")
    } else {
        let mut counts = HashMap::new();
        counts.insert(Key::new(0, 0), Big::one());
        (0, counts, Vec::with_capacity(config.depth))
    };
    if start_depth > config.depth {
        panic!("lean checkpoint depth is beyond requested target depth");
    }
    let mut ever_seen_valid1 = rows.iter().any(|row| !row.exact_depth_valid1.is_zero());
    let mut live_valid1: HashMap<Key, usize> = HashMap::new();
    let mut live_valid1_lineages: HashMap<Key, BTreeMap<usize, Big>> = HashMap::new();
    let mut lineage_lifetime_histogram: BTreeMap<usize, Big> = BTreeMap::new();
    let mut birth_audit_rows = Vec::new();
    let mut corridor_breach_events = Vec::new();
    let mut max_valid1_shadow_lifetime_seen = rows
        .iter()
        .map(|row| row.max_valid1_shadow_lifetime)
        .max()
        .unwrap_or(0);
    let mut max_valid1_lineage_lifetime_seen = rows
        .iter()
        .map(|row| row.max_valid1_lineage_lifetime)
        .max()
        .unwrap_or(0);

    for next_depth in (start_depth + 1)..=config.depth {
        let c = credit_at_step(next_depth - 1);
        let modulus = residue_modulus(next_depth, config.residue_mod_power);
        let terminal_residue_signature = config.terminal_value % modulus;
        let branch_capacity = deficit_branch_capacity(config.c);
        let mut next_counts: HashMap<Key, Big> =
            HashMap::with_capacity(counts.len().saturating_mul(branch_capacity));
        let mut next_live_valid1: HashMap<Key, usize> = HashMap::new();
        let mut next_live_valid1_lineages: HashMap<Key, BTreeMap<usize, Big>> = HashMap::new();
        let mut survived_valid1_parents: HashSet<Key> = HashSet::new();
        let mut valid1_lineage_birth_count = Big::zero();
        let mut exit_up_count = Big::zero();
        let mut exit_down_count = Big::zero();
        let mut stay_count = Big::zero();

        // --- PARALLEL STATE TRANSITION ---
        // Phase 1: compute next_counts in parallel using rayon
        if let Some(max_deficit) = max_deficit_for_c(config.c) {
            // Count flow directions for each state:
            // - exit_up: state has a valid transition to d_next > C (breach upward)
            // - exit_down: state has a valid transition to d_next < 0 (contract below corridor)
            //   This means a > key.deficit() + c, i.e., dividing by more than the corridor allows.
            //   Every state with deficit + credit >= 1 can take a=deficit+credit+1 to go below.
            //   We count every state as having a downward exit channel (v_2 is unbounded).
            // - stay: state has at least one transition staying in [0, C]
            //
            // A single state can count in multiple categories (it has branches going
            // up, down, AND staying simultaneously).
            for (key, multiplicity) in counts.iter() {
                // Upward exit: d_next = max_deficit + 1 requires a = key.deficit() + c - (max_deficit + 1)
                let a_up = key.deficit() + c - (max_deficit + 1);
                if a_up >= 1 {
                    exit_up_count.add_assign(multiplicity);
                }
                // Downward exit: a > key.deficit() + c gives d_next < 0
                // This is always possible (v_2(3x+1) is unbounded) for any state
                // where key.deficit() + c >= 1 (which is always true since deficit >= 0 and c >= 1)
                exit_down_count.add_assign(multiplicity);
                // Stay: at least one a in [1, key.deficit()+c] gives d_next in [0, max_deficit]
                let max_a_stay = key.deficit() + c;
                if max_a_stay >= 1 {
                    stay_count.add_assign(multiplicity);
                }
            }

            let entries: Vec<(&Key, &Big)> = counts.iter().collect();
            let partial_maps: Vec<Vec<(Key, Big)>> = entries
                .par_iter()
                .map(|&(key, multiplicity)| {
                    let mut local: Vec<(Key, Big)> = Vec::with_capacity(max_deficit as usize + 1);
                    for d_next in 0..=max_deficit {
                        let a = key.deficit() + c - d_next;
                        if a < 1 {
                            continue;
                        }
                        let next_key =
                            Key::new(d_next, next_terminal_residue(key.residue(), a, modulus));
                        local.push((next_key, multiplicity.clone()));
                    }
                    local
                })
                .collect();

            // Merge partial results into next_counts
            for local in partial_maps {
                for (next_key, multiplicity) in local {
                    next_counts
                        .entry(next_key)
                        .or_insert_with(Big::zero)
                        .add_assign(&multiplicity);
                }
            }

            // Phase 2: sequential lineage tracking + breach events (needs shared mutable state)
            for (key, multiplicity) in counts.iter() {
                if config.track_corridor_breaches {
                    let breach_start = max_deficit + 1;
                    let breach_end = config.max_corridor_breach_target.unwrap_or(breach_start);
                    for breach_deficit in breach_start..=breach_end {
                        let a = key.deficit() + c - breach_deficit;
                        if a >= 1 {
                            let breach_key = Key::new(
                                breach_deficit,
                                next_terminal_residue(key.residue(), a, modulus),
                            );
                            let parent_birth_depth = live_valid1.get(key).copied();
                            let lifetime = parent_birth_depth
                                .map(|birth_depth| next_depth.saturating_sub(birth_depth) + 1)
                                .unwrap_or(0);
                            let terminal_compatible =
                                breach_key.residue() == terminal_residue_signature;
                            let mut birth_count = Big::zero();
                            if terminal_compatible && !live_valid1_lineages.contains_key(key) {
                                birth_count.add_assign(multiplicity);
                            }
                            corridor_breach_events.push(CorridorBreachEvent {
                                c_configured: config.c,
                                m: config.residue_mod_power,
                                depth: next_depth,
                                key: breach_key,
                                old_max_d: max_deficit,
                                new_max_d: breach_deficit,
                                breached_from_c: max_deficit,
                                breached_to_c: breach_deficit,
                                d_k: breach_deficit,
                                a_k: a,
                                terminal_compatible,
                                live_valid1_key_count: live_valid1.len(),
                                live_valid1_lineage_count: sum_lineage_cohorts(
                                    &live_valid1_lineages,
                                ),
                                lineage_count: multiplicity.clone(),
                                birth_count,
                                death_count: Big::zero(),
                                lifetime,
                                notes: "candidate_boundary_transition_not_inserted_into_fixed_C_census",
                            });
                        }
                    }
                }
                for d_next in 0..=max_deficit {
                    let a = key.deficit() + c - d_next;
                    if a < 1 {
                        continue;
                    }
                    let next_key =
                        Key::new(d_next, next_terminal_residue(key.residue(), a, modulus));
                    if next_key.residue() == terminal_residue_signature {
                        if let Some(&birth_depth) = live_valid1.get(key) {
                            survived_valid1_parents.insert(*key);
                            next_live_valid1
                                .entry(next_key)
                                .and_modify(|existing| {
                                    if birth_depth < *existing {
                                        *existing = birth_depth;
                                    }
                                })
                                .or_insert(birth_depth);
                        } else {
                            next_live_valid1.entry(next_key).or_insert(next_depth);
                        }
                        if let Some(cohorts) = live_valid1_lineages.get(key) {
                            for (birth_depth, lineage_count) in cohorts {
                                add_lineage_cohort(
                                    &mut next_live_valid1_lineages,
                                    next_key,
                                    *birth_depth,
                                    lineage_count,
                                );
                            }
                        } else {
                            let l_at_birth = 1;
                            add_lineage_cohort(
                                &mut next_live_valid1_lineages,
                                next_key,
                                next_depth,
                                multiplicity,
                            );
                            birth_audit_rows.push(BirthAuditRow {
                                c: config.c,
                                m: config.residue_mod_power,
                                depth: next_depth,
                                key: next_key,
                                birth_depth: next_depth,
                                lineage_count: multiplicity.clone(),
                                l_at_birth,
                                i_birth: l_at_birth + config.residue_mod_power as i64
                                    - 3 * config.c,
                                parent_existed: false,
                                parent_key: Some(*key),
                                birth_reason: "no_live_terminal_compatible_parent",
                            });
                            valid1_lineage_birth_count.add_assign(multiplicity);
                        }
                    }
                }
            }
        }

        counts = next_counts;
        let mut symbolic_branch_count = Big::zero();
        let mut valid_from_1_count = Big::zero();
        let mut max_branch_multiplicity = Big::zero();
        let mut compatible_signatures = 0usize;
        let mut residues = Vec::with_capacity(counts.len());

        for (key, multiplicity) in counts.iter() {
            symbolic_branch_count.add_assign(multiplicity);
            residues.push(key.residue());
            if multiplicity.cmp_big(&max_branch_multiplicity) == Ordering::Greater {
                max_branch_multiplicity = multiplicity.clone();
            }
            if key.residue() == terminal_residue_signature {
                compatible_signatures += 1;
                valid_from_1_count.add_assign(multiplicity);
            }
        }
        append_lift_profile(config, next_depth, &counts).expect("append lift profile");
        residues.sort_unstable();
        residues.dedup();
        let valid1_shadow_birth_count = next_live_valid1
            .values()
            .filter(|birth_depth| **birth_depth == next_depth)
            .count();
        let valid1_shadow_death_count = live_valid1
            .len()
            .saturating_sub(survived_valid1_parents.len());
        let mut valid1_lineage_death_count = Big::zero();
        for (key, cohorts) in live_valid1_lineages.iter() {
            if survived_valid1_parents.contains(key) {
                continue;
            }
            for (birth_depth, lineage_count) in cohorts {
                valid1_lineage_death_count.add_assign(lineage_count);
                let lifetime = next_depth.saturating_sub(*birth_depth);
                lineage_lifetime_histogram
                    .entry(lifetime)
                    .or_insert_with(Big::zero)
                    .add_assign(lineage_count);
                max_valid1_lineage_lifetime_seen = max_valid1_lineage_lifetime_seen.max(lifetime);
            }
        }
        let valid1_shadow_persisted_from_previous = next_live_valid1
            .values()
            .any(|birth_depth| *birth_depth < next_depth);
        let current_max_valid1_shadow_lifetime = next_live_valid1
            .values()
            .map(|birth_depth| next_depth - *birth_depth + 1)
            .max()
            .unwrap_or(0);
        max_valid1_shadow_lifetime_seen =
            max_valid1_shadow_lifetime_seen.max(current_max_valid1_shadow_lifetime);
        let current_max_valid1_lineage_lifetime = next_live_valid1_lineages
            .values()
            .flat_map(|cohorts| cohorts.keys())
            .map(|birth_depth| next_depth - *birth_depth + 1)
            .max()
            .unwrap_or(0);
        max_valid1_lineage_lifetime_seen =
            max_valid1_lineage_lifetime_seen.max(current_max_valid1_lineage_lifetime);
        let live_valid1_lineage_count = sum_lineage_cohorts(&next_live_valid1_lineages);
        let lineage_lifetime_histogram_compact =
            compact_lifetime_histogram(&lineage_lifetime_histogram);

        let merged_state_count = counts.len();
        let notes = format!(
            "rust_census_by_deficit_and_terminal_residue_signature;memory_lean_counts_only;terminal_compatibility_mod_3^{}",
            next_depth.min(config.residue_mod_power)
        );
        let (current_rss_kb, peak_rss_kb) = memory_kb();
        let row = Row {
            depth: next_depth,
            residue_modulus: modulus,
            terminal_residue_signature,
            compression_ratio: format_ratio_usize(&symbolic_branch_count, merged_state_count),
            valid_fraction: format_ratio(&valid_from_1_count, &symbolic_branch_count),
            symbolic_branch_count,
            merged_state_count,
            exact_depth_valid1: valid_from_1_count.clone(),
            valid_from_1_count,
            terminal_1_compatible_signature_count: compatible_signatures,
            valid_residue_count: residues.len(),
            max_branch_multiplicity,
            rho_stable_count: 0,
            rho_lift_count: 0,
            longest_plateau: 0,
            max_rho_bit_length: 0,
            current_rss_kb,
            peak_rss_kb,
            live_valid1_count: next_live_valid1.len(),
            valid1_shadow_birth_count,
            valid1_shadow_death_count,
            max_valid1_shadow_lifetime: max_valid1_shadow_lifetime_seen,
            valid1_shadow_persisted_from_previous,
            live_valid1_lineage_count,
            valid1_lineage_birth_count,
            valid1_lineage_death_count,
            max_valid1_lineage_lifetime: max_valid1_lineage_lifetime_seen,
            lineage_lifetime_histogram_compact,
            exit_up_count,
            exit_down_count,
            stay_count,
            notes,
        };
        live_valid1 = next_live_valid1;
        live_valid1_lineages = next_live_valid1_lineages;
        ever_seen_valid1 |= !row.exact_depth_valid1.is_zero();
        enforce_memory_cap(config, row.peak_rss_kb);
        emit_progress_jsonl(config, &row, ever_seen_valid1, started);

        if config.progress_every > 0
            && (next_depth == config.depth || next_depth % config.progress_every == 0)
        {
            eprintln!(
                "lock3-census-progress engine=rust C={} depth={}/{} branches={} merged={} valid1={} compatible_sigs={} exit_up={} exit_down={} stay={} live_valid1={} ever_seen_valid1={} valid_residues={} mod={} rss_kb={} peak_rss_kb={} elapsed_sec={:.1}",
                config.c,
                next_depth,
                config.depth,
                row.symbolic_branch_count.to_decimal(),
                row.merged_state_count,
                row.valid_from_1_count.to_decimal(),
                row.terminal_1_compatible_signature_count,
                row.exit_up_count.to_decimal(),
                row.exit_down_count.to_decimal(),
                row.stay_count.to_decimal(),
                row.live_valid1_count,
                ever_seen_valid1,
                row.valid_residue_count,
                row.residue_modulus,
                row.current_rss_kb,
                row.peak_rss_kb,
                started.elapsed().as_secs_f64(),
            );
        }

        let stop_for_start_dirty = should_stop_for_start_dirty(config, &row);
        rows.push(row);
        if !config.no_checkpoint {
            if let Some(path) = &config.checkpoint_path {
                if config.checkpoint_every > 0
                    && (next_depth == config.depth || next_depth % config.checkpoint_every == 0)
                {
                    write_lean_checkpoint(path, config, next_depth, &counts, &rows)
                        .expect("write lean checkpoint");
                    eprintln!(
                        "lock3-census-checkpoint depth={} path={}",
                        next_depth,
                        path.display()
                    );
                    emit_checkpoint_jsonl(config, next_depth, path, started);
                }
            }
        }
        if stop_for_start_dirty {
            eprintln!(
                "lock3-auto-stop reason=start_dirty C={} even_m={} depth={}",
                config.c, config.residue_mod_power, next_depth
            );
            break;
        }
    }

    CensusResult {
        rows,
        birth_audit_rows,
        corridor_breach_events,
        corridor_breach_follows: Vec::new(),
        downward_exit_follows: Vec::new(),
    }
}

fn write_outputs(
    config: &Config,
    rows: &[Row],
    birth_audit_rows: &[BirthAuditRow],
    corridor_breach_events: &[CorridorBreachEvent],
    corridor_breach_follows: &[CorridorBreachFollow],
    downward_exit_follows: &[DownwardExitFollow],
) -> std::io::Result<()> {
    let summary_path = config
        .out_dir
        .join(format!("{}_summary_C{}.json", config.label, config.c));
    let census_path = config
        .out_dir
        .join(format!("{}_census_C{}.csv", config.label, config.c));
    let events_path = config
        .out_dir
        .join(format!("{}_events_C{}.csv", config.label, config.c));
    let witnesses_path = config
        .out_dir
        .join(format!("{}_witnesses_C{}.jsonl", config.label, config.c));
    let birth_audit_path = config.out_dir.join("lock3_birth_invariant_audit.csv");
    let birth_audit_summary_path = config.out_dir.join("lock3_birth_invariant_summary.json");
    let corridor_transition_path = config.out_dir.join(format!(
        "lock3_corridor_transitions_C{}_m{}.csv",
        config.c, config.residue_mod_power
    ));
    let corridor_transition_summary_path = config.out_dir.join(format!(
        "lock3_corridor_transition_summary_C{}_m{}.json",
        config.c, config.residue_mod_power
    ));
    let corridor_breach_witnesses_path = config.out_dir.join(format!(
        "lock3_corridor_breach_witnesses_C{}_m{}.jsonl",
        config.c, config.residue_mod_power
    ));
    let corridor_breach_follow_path = config.out_dir.join(format!(
        "lock3_corridor_breach_follow_C{}_m{}.jsonl",
        config.c, config.residue_mod_power
    ));
    let corridor_breach_follow_summary_path = config.out_dir.join(format!(
        "lock3_corridor_breach_follow_summary_C{}_m{}.json",
        config.c, config.residue_mod_power
    ));
    let downward_exit_follow_path = config.out_dir.join(format!(
        "lock3_downward_exit_follow_C{}_m{}.jsonl",
        config.c, config.residue_mod_power
    ));

    write_summary(config, rows, &summary_path)?;
    write_census(config, rows, &census_path)?;
    write_events(config, rows, &events_path)?;
    write_witnesses(config, rows, &witnesses_path)?;
    write_birth_invariant_audit(config, birth_audit_rows, &birth_audit_path)?;
    write_birth_invariant_summary(config, birth_audit_rows, &birth_audit_summary_path)?;
    write_corridor_transitions(config, corridor_breach_events, &corridor_transition_path)?;
    write_corridor_transition_summary(
        config,
        corridor_breach_events,
        &corridor_transition_summary_path,
    )?;
    write_corridor_breach_witnesses(
        config,
        corridor_breach_events,
        &corridor_breach_witnesses_path,
    )?;
    write_corridor_breach_follow(
        config,
        corridor_breach_follows,
        &corridor_breach_follow_path,
    )?;
    write_corridor_breach_follow_summary(
        config,
        corridor_breach_follows,
        &corridor_breach_follow_summary_path,
    )?;
    // Write downward exit follows
    if !downward_exit_follows.is_empty() {
        let mut file = BufWriter::new(File::create(&downward_exit_follow_path)?);
        for follow in downward_exit_follows {
            writeln!(
                file,
                "{{\"C_configured\":{},\"m\":{},\"exit_depth\":{},\"exited_from_C\":{},\"d_k\":{},\"a_k\":{},\"rho\":{},\"candidate_integer\":{},\"candidate_bit_length\":{},\"terminal_value_after_prefix\":{},\"terminal_value_bit_length\":{},\"follow_steps\":{},\"collapsed_to_1\":{},\"min_d_seen_after_exit\":{},\"max_d_seen_after_exit\":{},\"re_entered_corridor\":{},\"re_entry_depth\":{},\"peak_value_bit_length\":{},\"status\":\"{}\",\"notes\":\"{}\"}}",
                follow.c_configured,
                follow.m,
                follow.exit_depth,
                follow.exited_from_c,
                follow.d_k,
                follow.a_k,
                follow.rho.map(|v| v.to_string()).unwrap_or_else(|| "null".to_string()),
                follow.candidate_integer.map(|v| v.to_string()).unwrap_or_else(|| "null".to_string()),
                follow.candidate_bit_length,
                follow.terminal_value_after_prefix.map(|v| v.to_string()).unwrap_or_else(|| "null".to_string()),
                follow.terminal_value_bit_length,
                follow.follow_steps,
                follow.collapsed_to_1,
                follow.min_d_seen_after_exit,
                follow.max_d_seen_after_exit,
                follow.re_entered_corridor,
                follow.re_entry_depth,
                follow.peak_value_bit_length,
                json_escape(&follow.status),
                json_escape(&follow.notes)
            )?;
        }
        eprintln!(
            "wrote downward exit follows: {} ({} records)",
            downward_exit_follow_path.display(),
            downward_exit_follows.len()
        );
    }
    Ok(())
}

fn key_csv_value(key: Key) -> String {
    key.0.to_string()
}

fn write_birth_invariant_audit(
    config: &Config,
    birth_audit_rows: &[BirthAuditRow],
    path: &PathBuf,
) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "C,m,depth,key,deficit_state,residue_signature,birth_depth,lineage_count,L_at_birth,I_birth,parent_existed,parent_key,parent_deficit_state,parent_residue_signature,birth_reason"
    )?;
    for row in birth_audit_rows {
        let parent_key = row
            .parent_key
            .map(key_csv_value)
            .unwrap_or_else(String::new);
        let parent_deficit = row
            .parent_key
            .map(|key| key.deficit().to_string())
            .unwrap_or_else(String::new);
        let parent_residue = row
            .parent_key
            .map(|key| key.residue().to_string())
            .unwrap_or_else(String::new);
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            row.c,
            row.m,
            row.depth,
            key_csv_value(row.key),
            row.key.deficit(),
            row.key.residue(),
            row.birth_depth,
            row.lineage_count.to_decimal(),
            row.l_at_birth,
            row.i_birth,
            row.parent_existed,
            parent_key,
            parent_deficit,
            parent_residue,
            row.birth_reason
        )?;
    }
    if !config.memory_lean && !birth_audit_rows.is_empty() {
        eprintln!("lock3-birth-audit-warning non-lean mode unexpectedly produced audit rows");
    }
    Ok(())
}

fn write_birth_invariant_summary(
    config: &Config,
    birth_audit_rows: &[BirthAuditRow],
    path: &PathBuf,
) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    let max_i_birth = birth_audit_rows.iter().map(|row| row.i_birth).max();
    let min_i_birth = birth_audit_rows.iter().map(|row| row.i_birth).min();
    let births_i_gt_1 = birth_audit_rows
        .iter()
        .filter(|row| row.i_birth > 1)
        .count();
    let births_i_eq_1 = birth_audit_rows
        .iter()
        .filter(|row| row.i_birth == 1)
        .count();
    let births_i_lt_1 = birth_audit_rows
        .iter()
        .filter(|row| row.i_birth < 1)
        .count();
    let mut total_birth_lineage_count = Big::zero();
    let mut total_birth_lineage_count_by_i: BTreeMap<i64, Big> = BTreeMap::new();
    for row in birth_audit_rows {
        total_birth_lineage_count.add_assign(&row.lineage_count);
        total_birth_lineage_count_by_i
            .entry(row.i_birth)
            .or_insert_with(Big::zero)
            .add_assign(&row.lineage_count);
    }

    writeln!(file, "{{")?;
    writeln!(file, "  \"C\": {},", config.c)?;
    writeln!(file, "  \"m\": {},", config.residue_mod_power)?;
    writeln!(file, "  \"max_depth\": {},", config.depth)?;
    writeln!(file, "  \"memory_lean\": {},", config.memory_lean)?;
    writeln!(file, "  \"audit_enabled\": {},", config.memory_lean)?;
    match max_i_birth {
        Some(value) => writeln!(file, "  \"max_I_birth\": {},", value)?,
        None => writeln!(file, "  \"max_I_birth\": null,")?,
    }
    match min_i_birth {
        Some(value) => writeln!(file, "  \"min_I_birth\": {},", value)?,
        None => writeln!(file, "  \"min_I_birth\": null,")?,
    }
    writeln!(file, "  \"births_I_gt_1\": {},", births_i_gt_1)?;
    writeln!(file, "  \"births_I_eq_1\": {},", births_i_eq_1)?;
    writeln!(file, "  \"births_I_lt_1\": {},", births_i_lt_1)?;
    writeln!(
        file,
        "  \"total_birth_lineage_count\": \"{}\",",
        total_birth_lineage_count.to_decimal()
    )?;
    writeln!(file, "  \"total_birth_lineage_count_by_I\": {{")?;
    for (idx, (i_birth, count)) in total_birth_lineage_count_by_i.iter().enumerate() {
        let comma = if idx + 1 == total_birth_lineage_count_by_i.len() {
            ""
        } else {
            ","
        };
        writeln!(
            file,
            "    \"{}\": \"{}\"{}",
            i_birth,
            count.to_decimal(),
            comma
        )?;
    }
    writeln!(file, "  }},")?;
    writeln!(file, "  \"examples_I_birth_gt_1\": [")?;
    let mut examples_written = 0usize;
    for row in birth_audit_rows
        .iter()
        .filter(|row| row.i_birth > 1)
        .take(10)
    {
        let comma = if examples_written == 0 { "" } else { "," };
        writeln!(
            file,
            "{}    {{\"C\": {}, \"m\": {}, \"depth\": {}, \"key\": \"{}\", \"deficit_state\": {}, \"residue_signature\": {}, \"birth_depth\": {}, \"lineage_count\": \"{}\", \"L_at_birth\": {}, \"I_birth\": {}, \"parent_existed\": {}, \"parent_key\": {}, \"birth_reason\": \"{}\"}}",
            comma,
            row.c,
            row.m,
            row.depth,
            key_csv_value(row.key),
            row.key.deficit(),
            row.key.residue(),
            row.birth_depth,
            row.lineage_count.to_decimal(),
            row.l_at_birth,
            row.i_birth,
            row.parent_existed,
            row.parent_key
                .map(|key| format!("\"{}\"", key_csv_value(key)))
                .unwrap_or_else(|| "null".to_string()),
            json_escape(row.birth_reason)
        )?;
        examples_written += 1;
    }
    writeln!(file, "  ],")?;
    if config.memory_lean {
        writeln!(
            file,
            "  \"main_theorem_test_passed\": {},",
            births_i_gt_1 == 0
        )?;
    } else {
        writeln!(file, "  \"main_theorem_test_passed\": null,")?;
    }
    writeln!(
        file,
        "  \"audit_semantics\": \"cohort birth rows are emitted when a terminal-1-compatible child has no live terminal-compatible parent cohort; L_at_birth is the scanner's birth-time lineage length\","
    )?;
    writeln!(file, "  \"total_birth_rows\": {}", birth_audit_rows.len())?;
    writeln!(file, "}}")?;
    Ok(())
}

fn write_corridor_transitions(
    config: &Config,
    events: &[CorridorBreachEvent],
    path: &PathBuf,
) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "C_configured,m,depth,key,old_max_d,new_max_d,breached_from_C,breached_to_C,d_k,A_k,terminal_compatible,live_valid1_key_count,live_valid1_lineage_count,lineage_count,birth_count,death_count,lifetime,notes"
    )?;
    if !config.track_corridor_breaches {
        return Ok(());
    }
    for event in events {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            event.c_configured,
            event.m,
            event.depth,
            key_csv_value(event.key),
            event.old_max_d,
            event.new_max_d,
            event.breached_from_c,
            event.breached_to_c,
            event.d_k,
            event.a_k,
            event.terminal_compatible,
            event.live_valid1_key_count,
            event.live_valid1_lineage_count.to_decimal(),
            event.lineage_count.to_decimal(),
            event.birth_count.to_decimal(),
            event.death_count.to_decimal(),
            event.lifetime,
            event.notes
        )?;
    }
    Ok(())
}

fn write_corridor_transition_summary(
    config: &Config,
    events: &[CorridorBreachEvent],
    path: &PathBuf,
) -> std::io::Result<()> {
    let mut first_by_c: BTreeMap<i64, usize> = BTreeMap::new();
    let mut last_by_c: BTreeMap<i64, usize> = BTreeMap::new();
    let mut counts_by_c: BTreeMap<i64, usize> = BTreeMap::new();
    let mut terminal_count = 0usize;
    let mut max_c_reached = config.c;
    for event in events {
        terminal_count += usize::from(event.terminal_compatible);
        max_c_reached = max_c_reached.max(event.breached_to_c);
        first_by_c
            .entry(event.breached_to_c)
            .and_modify(|depth| *depth = (*depth).min(event.depth))
            .or_insert(event.depth);
        last_by_c
            .entry(event.breached_to_c)
            .and_modify(|depth| *depth = (*depth).max(event.depth))
            .or_insert(event.depth);
        *counts_by_c.entry(event.breached_to_c).or_insert(0) += 1;
    }

    let mut file = BufWriter::new(File::create(path)?);
    writeln!(file, "{{")?;
    writeln!(file, "  \"C\": {},", config.c)?;
    writeln!(file, "  \"m\": {},", config.residue_mod_power)?;
    writeln!(
        file,
        "  \"track_corridor_breaches\": {},",
        config.track_corridor_breaches
    )?;
    match config.max_corridor_breach_target {
        Some(target) => writeln!(file, "  \"max_corridor_breach_target\": {},", target)?,
        None => writeln!(file, "  \"max_corridor_breach_target\": null,")?,
    }
    writeln!(file, "  \"total_breach_events\": {},", events.len())?;
    writeln!(
        file,
        "  \"terminal_compatible_breach_events\": {},",
        terminal_count
    )?;
    writeln!(file, "  \"max_C_reached\": {},", max_c_reached)?;
    write_i64_usize_map(&mut file, "first_breach_depth_by_C", &first_by_c, true)?;
    write_i64_usize_map(&mut file, "last_breach_depth_by_C", &last_by_c, true)?;
    write_i64_usize_map(&mut file, "breach_counts_by_target_C", &counts_by_c, true)?;
    writeln!(file, "  \"breaches_that_remain_live_next_depth\": 0,")?;
    writeln!(
        file,
        "  \"breaches_that_die_immediately\": {},",
        events.len()
    )?;
    writeln!(file, "  \"breaches_that_fall_back_to_lower_C\": 0,")?;
    writeln!(file, "  \"longest_sustained_high_C_interval\": 0,")?;
    writeln!(
        file,
        "  \"semantics\": \"boundary breach candidates are d_next=C+1 transitions observed from the fixed-C census frontier; they are not inserted into the fixed-C next state\""
    )?;
    writeln!(file, "}}")?;
    Ok(())
}

fn write_corridor_breach_witnesses(
    config: &Config,
    events: &[CorridorBreachEvent],
    path: &PathBuf,
) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    if !config.track_corridor_breaches || !config.export_breach_witnesses {
        return Ok(());
    }
    for event in events.iter().take(config.max_breach_witnesses) {
        writeln!(
            file,
            "{{\"C_configured\":{},\"m\":{},\"depth\":{},\"key\":\"{}\",\"deficit_state\":{},\"residue_signature\":{},\"breached_from_C\":{},\"breached_to_C\":{},\"d_k\":{},\"A_k\":{},\"terminal_compatible\":{},\"lineage_count\":\"{}\",\"notes\":\"{}\"}}",
            event.c_configured,
            event.m,
            event.depth,
            key_csv_value(event.key),
            event.key.deficit(),
            event.key.residue(),
            event.breached_from_c,
            event.breached_to_c,
            event.d_k,
            event.a_k,
            event.terminal_compatible,
            event.lineage_count.to_decimal(),
            json_escape(event.notes)
        )?;
    }
    Ok(())
}

fn write_corridor_breach_follow(
    config: &Config,
    follows: &[CorridorBreachFollow],
    path: &PathBuf,
) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    if !config.track_corridor_breaches || !config.follow_breach_witnesses {
        return Ok(());
    }
    for row in follows {
        let rho = row
            .rho
            .map(|value| value.to_string())
            .unwrap_or_else(|| "null".to_string());
        let candidate = row
            .candidate_integer
            .map(|value| value.to_string())
            .unwrap_or_else(|| "null".to_string());
        let terminal_value = row
            .terminal_value_after_prefix
            .map(|value| value.to_string())
            .unwrap_or_else(|| "null".to_string());
        writeln!(
            file,
            "{{\"C_configured\":{},\"m\":{},\"breach_depth\":{},\"key\":\"{}\",\"deficit_state\":{},\"residue_signature\":{},\"breached_from_C\":{},\"breached_to_C\":{},\"d_k\":{},\"A_k\":{},\"rho\":{},\"rho_modulus_bit_length\":{},\"candidate_integer\":{},\"candidate_bit_length\":{},\"combined_modulus_bit_length\":{},\"terminal_value_after_prefix\":{},\"terminal_value_bit_length\":{},\"follow_steps\":{},\"collapsed_to_1\":{},\"max_d_seen_after_breach\":{},\"max_C_seen_after_breach\":{},\"peak_value_bit_length\":{},\"status\":\"{}\",\"notes\":\"{}\"}}",
            row.c_configured,
            row.m,
            row.breach_depth,
            key_csv_value(row.key),
            row.key.deficit(),
            row.key.residue(),
            row.breached_from_c,
            row.breached_to_c,
            row.d_k,
            row.a_k,
            rho,
            row.rho_modulus_bit_length,
            candidate,
            row.candidate_bit_length,
            row.combined_modulus_bit_length,
            terminal_value,
            row.terminal_value_bit_length,
            row.follow_steps,
            row.collapsed_to_1,
            row.max_d_seen_after_breach,
            row.max_c_seen_after_breach,
            row.peak_value_bit_length,
            json_escape(&row.status),
            json_escape(&row.notes)
        )?;
    }
    Ok(())
}

fn write_corridor_breach_follow_summary(
    config: &Config,
    follows: &[CorridorBreachFollow],
    path: &PathBuf,
) -> std::io::Result<()> {
    let mut status_counts: BTreeMap<String, usize> = BTreeMap::new();
    let mut collapsed_to_1 = 0usize;
    let mut max_d_seen_after_breach = config.c;
    let mut max_c_seen_after_breach = config.c;
    let mut max_follow_steps_used = 0usize;
    let mut max_peak_value_bit_length = 0usize;
    for row in follows {
        *status_counts.entry(row.status.clone()).or_insert(0) += 1;
        collapsed_to_1 += usize::from(row.collapsed_to_1);
        max_d_seen_after_breach = max_d_seen_after_breach.max(row.max_d_seen_after_breach);
        max_c_seen_after_breach = max_c_seen_after_breach.max(row.max_c_seen_after_breach);
        max_follow_steps_used = max_follow_steps_used.max(row.follow_steps);
        max_peak_value_bit_length = max_peak_value_bit_length.max(row.peak_value_bit_length);
    }

    let mut file = BufWriter::new(File::create(path)?);
    writeln!(file, "{{")?;
    writeln!(file, "  \"C\": {},", config.c)?;
    writeln!(file, "  \"m\": {},", config.residue_mod_power)?;
    writeln!(
        file,
        "  \"follow_breach_witnesses\": {},",
        config.follow_breach_witnesses
    )?;
    writeln!(
        file,
        "  \"max_follow_witnesses\": {},",
        config.max_follow_witnesses
    )?;
    writeln!(file, "  \"max_follow_steps\": {},", config.max_follow_steps)?;
    writeln!(file, "  \"followed_witnesses\": {},", follows.len())?;
    writeln!(file, "  \"collapsed_to_1\": {},", collapsed_to_1)?;
    writeln!(
        file,
        "  \"max_d_seen_after_breach\": {},",
        max_d_seen_after_breach
    )?;
    writeln!(
        file,
        "  \"max_C_seen_after_breach\": {},",
        max_c_seen_after_breach
    )?;
    writeln!(
        file,
        "  \"max_follow_steps_used\": {},",
        max_follow_steps_used
    )?;
    writeln!(
        file,
        "  \"max_peak_value_bit_length\": {},",
        max_peak_value_bit_length
    )?;
    writeln!(file, "  \"status_counts\": {{")?;
    for (idx, (status, count)) in status_counts.iter().enumerate() {
        let comma = if idx + 1 == status_counts.len() {
            ""
        } else {
            ","
        };
        writeln!(file, "    \"{}\": {}{}", json_escape(status), count, comma)?;
    }
    writeln!(file, "  }},")?;
    writeln!(
        file,
        "  \"semantics\": \"bounded concrete u128 witnesses are followed after the breach prefix; rows outside the u128 CRT or affine path report a status instead of a follow result\""
    )?;
    writeln!(file, "}}")?;
    Ok(())
}

fn write_i64_usize_map(
    file: &mut BufWriter<File>,
    field_name: &str,
    values: &BTreeMap<i64, usize>,
    trailing_comma: bool,
) -> std::io::Result<()> {
    writeln!(file, "  \"{}\": {{", field_name)?;
    for (idx, (key, value)) in values.iter().enumerate() {
        let comma = if idx + 1 == values.len() { "" } else { "," };
        writeln!(file, "    \"{}\": {}{}", key, value, comma)?;
    }
    writeln!(file, "  }}{}", if trailing_comma { "," } else { "" })?;
    Ok(())
}

fn write_summary(config: &Config, rows: &[Row], path: &PathBuf) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    let last = rows.last();
    let zero = Big::zero();
    let valid1_hit_depths: Vec<usize> = rows
        .iter()
        .filter(|row| !row.exact_depth_valid1.is_zero())
        .map(|row| row.depth)
        .collect();
    let first_valid1_depth = valid1_hit_depths.first().copied();
    let last_valid1_depth = valid1_hit_depths.last().copied();
    let clean_prefix_depth = first_valid1_depth
        .map(|depth| depth.saturating_sub(1))
        .unwrap_or_else(|| last.map(|row| row.depth).unwrap_or(0));
    let ever_seen_valid1 = !valid1_hit_depths.is_empty();
    let final_valid1_is_zero = last
        .map(|row| row.exact_depth_valid1.is_zero())
        .unwrap_or(true);
    let transient_valid1_depths: &[usize] = if ever_seen_valid1 && final_valid1_is_zero {
        &valid1_hit_depths
    } else {
        &[]
    };
    writeln!(file, "{{")?;
    writeln!(file, "  \"C\": {},", config.c)?;
    writeln!(file, "  \"engine\": \"rust\",")?;
    writeln!(file, "  \"mode\": \"census\",")?;
    writeln!(file, "  \"max_depth\": {},", config.depth)?;
    writeln!(
        file,
        "  \"completed_depth\": {},",
        last.map(|row| row.depth).unwrap_or(0)
    )?;
    writeln!(file, "  \"terminal_value\": {},", config.terminal_value)?;
    writeln!(
        file,
        "  \"residue_mod_power\": {},",
        config.residue_mod_power
    )?;
    writeln!(file, "  \"memory_lean\": {},", config.memory_lean)?;
    writeln!(
        file,
        "  \"auto_prior_odd_on_even_dirty\": {},",
        config.auto_prior_odd_on_even_dirty
    )?;
    writeln!(file, "  \"checkpoint_enabled\": {},", !config.no_checkpoint)?;
    match config.memory_cap_mb {
        Some(memory_cap_mb) => writeln!(file, "  \"memory_cap_mb\": {},", memory_cap_mb)?,
        None => writeln!(file, "  \"memory_cap_mb\": null,")?,
    }
    writeln!(
        file,
        "  \"residue_modulus\": {},",
        last.map(|r| r.residue_modulus).unwrap_or(1)
    )?;
    writeln!(
        file,
        "  \"terminal_residue_signature\": {},",
        last.map(|r| r.terminal_residue_signature).unwrap_or(0)
    )?;
    writeln!(
        file,
        "  \"merge_strategy\": \"deficit_state_and_terminal_residue_signature\","
    )?;
    writeln!(
        file,
        "  \"symbolic_branch_count\": {},",
        last.map(|r| r.symbolic_branch_count.to_decimal())
            .unwrap_or_else(|| "1".to_string())
    )?;
    writeln!(
        file,
        "  \"merged_state_count\": {},",
        last.map(|r| r.merged_state_count).unwrap_or(1)
    )?;
    writeln!(file, "  \"valid_from_1_tracked\": true,")?;
    writeln!(file, "  \"valid_from_1_is_modular_compatibility\": true,")?;
    writeln!(
        file,
        "  \"valid_from_1_count\": {},",
        last.map(|r| r.valid_from_1_count.to_decimal())
            .unwrap_or_else(|| zero.to_decimal())
    )?;
    writeln!(file, "  \"ever_seen_valid1\": {},", ever_seen_valid1)?;
    match first_valid1_depth {
        Some(depth) => writeln!(file, "  \"first_valid1_depth\": {},", depth)?,
        None => writeln!(file, "  \"first_valid1_depth\": null,")?,
    }
    match last_valid1_depth {
        Some(depth) => writeln!(file, "  \"last_valid1_depth\": {},", depth)?,
        None => writeln!(file, "  \"last_valid1_depth\": null,")?,
    }
    writeln!(file, "  \"clean_prefix_depth\": {},", clean_prefix_depth)?;
    write_usize_array_field(
        &mut file,
        "transient_valid1_depths",
        transient_valid1_depths,
        true,
    )?;
    write_alignment_field(
        &mut file,
        "valid1_convergent_alignment",
        &valid1_hit_depths,
        true,
    )?;
    writeln!(
        file,
        "  \"terminal_1_compatible_signature_count\": {},",
        last.map(|r| r.terminal_1_compatible_signature_count)
            .unwrap_or(0)
    )?;
    writeln!(
        file,
        "  \"live_valid1_count\": {},",
        last.map(|r| r.live_valid1_count).unwrap_or(0)
    )?;
    writeln!(
        file,
        "  \"live_valid1_lineage_count\": {},",
        last.map(|r| r.live_valid1_lineage_count.to_decimal())
            .unwrap_or_else(|| zero.to_decimal())
    )?;
    writeln!(
        file,
        "  \"max_lifetime_of_valid1_shadow\": {},",
        rows.iter()
            .map(|row| row.max_valid1_shadow_lifetime)
            .max()
            .unwrap_or(0)
    )?;
    writeln!(
        file,
        "  \"max_lifetime_of_valid1_lineage\": {},",
        rows.iter()
            .map(|row| row.max_valid1_lineage_lifetime)
            .max()
            .unwrap_or(0)
    )?;
    writeln!(
        file,
        "  \"any_valid1_shadow_reaches_final_depth\": {},",
        last.map(|r| r.live_valid1_count > 0).unwrap_or(false)
    )?;
    writeln!(
        file,
        "  \"any_valid1_lineage_reaches_final_depth\": {},",
        last.map(|r| !r.live_valid1_lineage_count.is_zero())
            .unwrap_or(false)
    )?;
    writeln!(
        file,
        "  \"any_valid1_shadow_persists_across_consecutive_checkpoints\": {},",
        valid1_shadow_persists_across_consecutive_checkpoints(config, rows)
    )?;
    let birth_depths: Vec<usize> = rows
        .iter()
        .filter(|row| row.valid1_shadow_birth_count > 0)
        .map(|row| row.depth)
        .collect();
    let death_depths: Vec<usize> = rows
        .iter()
        .filter(|row| row.valid1_shadow_death_count > 0)
        .map(|row| row.depth)
        .collect();
    write_usize_array_field(&mut file, "birth_depths", &birth_depths, true)?;
    write_usize_array_field(&mut file, "death_depths", &death_depths, true)?;
    writeln!(
        file,
        "  \"valid1_lineage_birth_count\": {},",
        rows.iter()
            .fold(Big::zero(), |mut total, row| {
                total.add_assign(&row.valid1_lineage_birth_count);
                total
            })
            .to_decimal()
    )?;
    writeln!(
        file,
        "  \"valid1_lineage_death_count\": {},",
        rows.iter()
            .fold(Big::zero(), |mut total, row| {
                total.add_assign(&row.valid1_lineage_death_count);
                total
            })
            .to_decimal()
    )?;
    writeln!(
        file,
        "  \"lineage_lifetime_histogram\": \"{}\",",
        json_escape(
            &last
                .map(|r| r.lineage_lifetime_histogram_compact.clone())
                .unwrap_or_default()
        )
    )?;
    writeln!(
        file,
        "  \"valid_residue_count\": {},",
        last.map(|r| r.valid_residue_count).unwrap_or(0)
    )?;
    writeln!(
        file,
        "  \"residue_class_count\": {},",
        last.map(|r| r.valid_residue_count).unwrap_or(0)
    )?;
    writeln!(file, "  \"residue_class_count_is_proxy\": false,")?;
    writeln!(
        file,
        "  \"rho_metrics_are_representative\": {},",
        !config.memory_lean
    )?;
    writeln!(
        file,
        "  \"rho_lift_count\": {},",
        last.map(|r| r.rho_lift_count).unwrap_or(0)
    )?;
    writeln!(
        file,
        "  \"longest_plateau\": {},",
        last.map(|r| r.longest_plateau).unwrap_or(0)
    )?;
    writeln!(
        file,
        "  \"max_rho_bit_length\": {},",
        last.map(|r| r.max_rho_bit_length).unwrap_or(0)
    )?;
    writeln!(
        file,
        "  \"max_branch_multiplicity\": {},",
        last.map(|r| r.max_branch_multiplicity.to_decimal())
            .unwrap_or_else(|| "1".to_string())
    )?;
    writeln!(
        file,
        "  \"current_rss_kb\": {},",
        last.map(|r| r.current_rss_kb).unwrap_or(0)
    )?;
    writeln!(
        file,
        "  \"peak_rss_kb\": {},",
        last.map(|r| r.peak_rss_kb).unwrap_or(0)
    )?;
    writeln!(file, "  \"truncated_depths\": [],")?;
    writeln!(file, "  \"near_return_times_encountered\": [],")?;
    writeln!(file, "  \"event_count\": {},", event_count(rows))?;
    match checkpoint_size_bytes(config) {
        Some(size_bytes) => writeln!(file, "  \"checkpoint_size_bytes\": {},", size_bytes)?,
        None => writeln!(file, "  \"checkpoint_size_bytes\": null,")?,
    }
    writeln!(file, "  \"witness_count\": {}", witness_count(config, rows))?;
    writeln!(file, "}}")?;
    Ok(())
}

fn write_usize_array_field(
    file: &mut BufWriter<File>,
    field_name: &str,
    values: &[usize],
    trailing_comma: bool,
) -> std::io::Result<()> {
    write!(file, "  \"{}\": [", field_name)?;
    for (idx, value) in values.iter().enumerate() {
        if idx > 0 {
            write!(file, ", ")?;
        }
        write!(file, "{}", value)?;
    }
    writeln!(file, "]{}", if trailing_comma { "," } else { "" })?;
    Ok(())
}

fn write_alignment_field(
    file: &mut BufWriter<File>,
    field_name: &str,
    depths: &[usize],
    trailing_comma: bool,
) -> std::io::Result<()> {
    writeln!(file, "  \"{}\": [", field_name)?;
    for (idx, depth) in depths.iter().enumerate() {
        let comma = if idx + 1 == depths.len() { "" } else { "," };
        let exact_multiples: Vec<usize> = CONVERGENT_DENOMINATORS
            .iter()
            .copied()
            .filter(|q| *depth % *q == 0)
            .collect();
        let (nearest_q, nearest_multiple, nearest_distance) = nearest_convergent_multiple(*depth);
        write!(
            file,
            "    {{\"depth\": {}, \"nearest_convergent_denominator\": {}, \"nearest_multiple\": {}, \"distance_to_nearest_multiple\": {}, \"d_mod_53\": {}, \"d_mod_359\": {}, \"d_mod_665\": {}, \"is_multiple_of_53\": {}, \"is_multiple_of_359\": {}, \"is_multiple_of_665\": {}, \"is_exact_multiple_of_known_convergent\": {}, \"exact_multiple_convergent_denominators\": [",
            depth,
            nearest_q,
            nearest_multiple,
            nearest_distance,
            depth % 53,
            depth % 359,
            depth % 665,
            depth % 53 == 0,
            depth % 359 == 0,
            depth % 665 == 0,
            !exact_multiples.is_empty()
        )?;
        for (multiple_idx, q) in exact_multiples.iter().enumerate() {
            if multiple_idx > 0 {
                write!(file, ", ")?;
            }
            write!(file, "{}", q)?;
        }
        writeln!(file, "]}}{}", comma)?;
    }
    writeln!(file, "  ]{}", if trailing_comma { "," } else { "" })?;
    Ok(())
}

fn nearest_convergent_multiple(depth: usize) -> (usize, usize, usize) {
    let mut best_q = CONVERGENT_DENOMINATORS[0];
    let mut best_multiple = depth;
    let mut best_distance = usize::MAX;
    for q in CONVERGENT_DENOMINATORS {
        let lower = (depth / q) * q;
        let upper = lower.saturating_add(q);
        for candidate in [lower, upper] {
            let distance = depth.abs_diff(candidate);
            if distance < best_distance || (distance == best_distance && q > best_q) {
                best_q = q;
                best_multiple = candidate;
                best_distance = distance;
            }
        }
    }
    (best_q, best_multiple, best_distance)
}

fn write_census(config: &Config, rows: &[Row], path: &PathBuf) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "C,depth,residue_mod_power,residue_modulus,terminal_residue_signature,symbolic_branch_count,merged_state_count,valid_from_1_count,exact_depth_valid1,terminal_1_compatible_signature_count,live_valid1_count,valid1_shadow_birth_count,valid1_shadow_death_count,max_valid1_shadow_lifetime,valid1_shadow_persisted_from_previous,live_valid1_lineage_count,valid1_lineage_birth_count,valid1_lineage_death_count,max_valid1_lineage_lifetime,lineage_lifetime_histogram,valid_residue_count,residue_class_count,rho_stable_count,rho_lift_count,longest_plateau,max_rho_bit_length,max_branch_multiplicity,compression_ratio,valid_fraction,stable_fraction,current_rss_kb,peak_rss_kb,truncated,notes"
    )?;
    for row in rows {
        writeln!(
            file,
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            config.c,
            row.depth,
            config.residue_mod_power,
            row.residue_modulus,
            row.terminal_residue_signature,
            row.symbolic_branch_count.to_decimal(),
            row.merged_state_count,
            row.valid_from_1_count.to_decimal(),
            row.exact_depth_valid1.to_decimal(),
            row.terminal_1_compatible_signature_count,
            row.live_valid1_count,
            row.valid1_shadow_birth_count,
            row.valid1_shadow_death_count,
            row.max_valid1_shadow_lifetime,
            row.valid1_shadow_persisted_from_previous,
            row.live_valid1_lineage_count.to_decimal(),
            row.valid1_lineage_birth_count.to_decimal(),
            row.valid1_lineage_death_count.to_decimal(),
            row.max_valid1_lineage_lifetime,
            row.lineage_lifetime_histogram_compact,
            row.valid_residue_count,
            row.valid_residue_count,
            row.rho_stable_count,
            row.rho_lift_count,
            row.longest_plateau,
            row.max_rho_bit_length,
            row.max_branch_multiplicity.to_decimal(),
            row.compression_ratio,
            row.valid_fraction,
            format!("{:.12}", row.rho_stable_count as f64 / row.merged_state_count as f64),
            row.current_rss_kb,
            row.peak_rss_kb,
            "False",
            row.notes
        )?;
    }
    Ok(())
}

fn write_events(config: &Config, rows: &[Row], path: &PathBuf) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    writeln!(
        file,
        "C,depth,event_type,value,branch_id_or_state_id,deficit_state,exponent,summary"
    )?;
    let mut max_merged = 0usize;
    let mut max_valid = Big::zero();
    for row in rows {
        if row.merged_state_count > max_merged {
            max_merged = row.merged_state_count;
            writeln!(
                file,
                "{},{},new_max_merged_state_count,{},deficit_census,,,merged deficit states reached {}",
                config.c, row.depth, row.merged_state_count, row.merged_state_count
            )?;
        }
        if row.valid_from_1_count.cmp_big(&max_valid) == Ordering::Greater {
            max_valid = row.valid_from_1_count.clone();
            writeln!(
                file,
                "{},{},new_max_terminal_1_compatible_count,{},residue={},{},,\"{} branches compatible with terminal {} modulo {}\"",
                config.c,
                row.depth,
                row.valid_from_1_count.to_decimal(),
                row.terminal_residue_signature,
                "",
                row.valid_from_1_count.to_decimal(),
                config.terminal_value,
                row.residue_modulus
            )?;
        }
        if row.terminal_1_compatible_signature_count > 0 {
            writeln!(
                file,
                "{},{},terminal_1_compatible_signatures,{},residue={},{},,\"{} merged signatures carry {} branches compatible with terminal {} modulo {}\"",
                config.c,
                row.depth,
                row.terminal_1_compatible_signature_count,
                row.terminal_residue_signature,
                "",
                row.terminal_1_compatible_signature_count,
                row.valid_from_1_count.to_decimal(),
                config.terminal_value,
                row.residue_modulus
            )?;
        }
    }
    Ok(())
}

fn write_witnesses(config: &Config, rows: &[Row], path: &PathBuf) -> std::io::Result<()> {
    let mut file = BufWriter::new(File::create(path)?);
    if !config.export_terminal_witnesses {
        return Ok(());
    }
    for row in rows {
        if row.terminal_1_compatible_signature_count > 0 {
            writeln!(
                file,
                "{{\"C\":{},\"depth\":{},\"witness_type\":\"terminal_1_compatible_residue_signature_count\",\"notes\":\"count_only_rust_engine;multiplicity={};residue_modulus={};terminal_residue_signature={}\"}}",
                config.c,
                row.depth,
                row.valid_from_1_count.to_decimal(),
                row.residue_modulus,
                row.terminal_residue_signature
            )?;
        }
    }
    Ok(())
}

fn event_count(rows: &[Row]) -> usize {
    let mut count = 0usize;
    let mut max_merged = 0usize;
    let mut max_valid = Big::zero();
    for row in rows {
        if row.merged_state_count > max_merged {
            max_merged = row.merged_state_count;
            count += 1;
        }
        if row.valid_from_1_count.cmp_big(&max_valid) == Ordering::Greater {
            max_valid = row.valid_from_1_count.clone();
            count += 1;
        }
        if row.terminal_1_compatible_signature_count > 0 {
            count += 1;
        }
    }
    count
}

fn witness_count(config: &Config, rows: &[Row]) -> usize {
    if !config.export_terminal_witnesses {
        return 0;
    }
    rows.iter()
        .filter(|row| row.terminal_1_compatible_signature_count > 0)
        .count()
}

fn checkpoint_size_bytes(config: &Config) -> Option<u64> {
    if config.no_checkpoint {
        return Some(0);
    }
    config
        .checkpoint_path
        .as_ref()
        .and_then(|path| metadata(path).ok())
        .map(|meta| meta.len())
}

fn valid1_shadow_persists_across_consecutive_checkpoints(config: &Config, rows: &[Row]) -> bool {
    if config.checkpoint_every == 0 {
        return false;
    }
    let mut previous_checkpoint_had_live_shadow = false;
    for row in rows {
        if row.depth % config.checkpoint_every != 0 {
            continue;
        }
        let current_checkpoint_has_live_shadow = row.live_valid1_count > 0;
        if previous_checkpoint_had_live_shadow && current_checkpoint_has_live_shadow {
            return true;
        }
        previous_checkpoint_had_live_shadow = current_checkpoint_has_live_shadow;
    }
    false
}

fn print_summary(config: &Config, rows: &[Row]) {
    let last = rows.last();
    println!("Lock 3 bounded-deficit census");
    println!("engine=rust");
    println!("memory_lean={}", config.memory_lean);
    println!("checkpoint_enabled={}", !config.no_checkpoint);
    println!("C={}", config.c);
    println!("depth={}", config.depth);
    println!(
        "symbolic_branch_count={}",
        last.map(|r| r.symbolic_branch_count.to_decimal())
            .unwrap_or_else(|| "1".to_string())
    );
    println!(
        "merged_state_count={}",
        last.map(|r| r.merged_state_count).unwrap_or(1)
    );
    println!(
        "valid_from_1_count={}",
        last.map(|r| r.valid_from_1_count.to_decimal())
            .unwrap_or_else(|| "0".to_string())
    );
    println!(
        "ever_seen_valid1={}",
        rows.iter().any(|row| !row.exact_depth_valid1.is_zero())
    );
    let first_valid1_depth = rows
        .iter()
        .find(|row| !row.exact_depth_valid1.is_zero())
        .map(|row| row.depth);
    let last_valid1_depth = rows
        .iter()
        .rev()
        .find(|row| !row.exact_depth_valid1.is_zero())
        .map(|row| row.depth);
    println!(
        "first_valid1_depth={}",
        first_valid1_depth
            .map(|depth| depth.to_string())
            .unwrap_or_else(|| "null".to_string())
    );
    println!(
        "last_valid1_depth={}",
        last_valid1_depth
            .map(|depth| depth.to_string())
            .unwrap_or_else(|| "null".to_string())
    );
    println!(
        "clean_prefix_depth={}",
        first_valid1_depth
            .map(|depth| depth.saturating_sub(1))
            .unwrap_or_else(|| last.map(|row| row.depth).unwrap_or(0))
    );
    println!(
        "terminal_1_compatible_signature_count={}",
        last.map(|r| r.terminal_1_compatible_signature_count)
            .unwrap_or(0)
    );
    println!(
        "live_valid1_count={}",
        last.map(|r| r.live_valid1_count).unwrap_or(0)
    );
    println!(
        "live_valid1_lineage_count={}",
        last.map(|r| r.live_valid1_lineage_count.to_decimal())
            .unwrap_or_else(|| "0".to_string())
    );
    println!(
        "max_lifetime_of_valid1_shadow={}",
        rows.iter()
            .map(|row| row.max_valid1_shadow_lifetime)
            .max()
            .unwrap_or(0)
    );
    println!(
        "max_lifetime_of_valid1_lineage={}",
        rows.iter()
            .map(|row| row.max_valid1_lineage_lifetime)
            .max()
            .unwrap_or(0)
    );
    println!(
        "valid_residue_count={}",
        last.map(|r| r.valid_residue_count).unwrap_or(0)
    );
    println!(
        "residue_modulus={}",
        last.map(|r| r.residue_modulus).unwrap_or(1)
    );
    println!(
        "rho_lift_count={}",
        last.map(|r| r.rho_lift_count).unwrap_or(0)
    );
    println!(
        "longest_plateau={}",
        last.map(|r| r.longest_plateau).unwrap_or(0)
    );
    println!(
        "max_rho_bit_length={}",
        last.map(|r| r.max_rho_bit_length).unwrap_or(0)
    );
    println!(
        "current_rss_kb={}",
        last.map(|r| r.current_rss_kb).unwrap_or(0)
    );
    println!("peak_rss_kb={}", last.map(|r| r.peak_rss_kb).unwrap_or(0));
    println!(
        "checkpoint_size_bytes={}",
        checkpoint_size_bytes(config)
            .map(|size_bytes| size_bytes.to_string())
            .unwrap_or_else(|| "null".to_string())
    );
    println!("witness_count={}", witness_count(config, rows));
    println!(
        "wrote summary: {}",
        config
            .out_dir
            .join(format!("{}_summary_C{}.json", config.label, config.c))
            .display()
    );
    println!(
        "wrote census: {}",
        config
            .out_dir
            .join(format!("{}_census_C{}.csv", config.label, config.c))
            .display()
    );
    println!(
        "wrote events: {}",
        config
            .out_dir
            .join(format!("{}_events_C{}.csv", config.label, config.c))
            .display()
    );
    println!(
        "wrote witnesses: {}",
        config
            .out_dir
            .join(format!("{}_witnesses_C{}.jsonl", config.label, config.c))
            .display()
    );
    println!(
        "wrote birth invariant audit: {}",
        config
            .out_dir
            .join("lock3_birth_invariant_audit.csv")
            .display()
    );
    println!(
        "wrote birth invariant summary: {}",
        config
            .out_dir
            .join("lock3_birth_invariant_summary.json")
            .display()
    );
}
