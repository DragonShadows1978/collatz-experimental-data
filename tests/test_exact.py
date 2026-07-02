from collatz_experimental_data.exact import (
    affine_for_word,
    analyze_orbit,
    analyze_corridor_bound,
    analyze_macro_corridors,
    analyze_k53_capacity,
    analyze_lock2_scan,
    analyze_lock3_backward,
    analyze_lock3_census,
    analyze_post_k53_behavior,
    analyze_scaling_sweep,
    analyze_tail_law,
    count_high_credit_steps,
    exponent_prefix_from_start,
    find_macro_corridor_ranges,
    k53_length_from_bits,
    odd_syracuse_step,
    required_reserve_for_gap,
    reserve_profile,
    simulate_orbit,
    lock2_word_row,
    lock3_backward_from_terminal,
    lock3_critical_word,
    lock3_deficit_path,
    lock3_inverse_step,
    lock3_mod3_gate_residue,
    lock3_rho_for_prefix,
    v2,
)


def test_v2_and_odd_step() -> None:
    assert v2(40) == 3
    assert odd_syracuse_step(3) == (5, 1)
    assert odd_syracuse_step(5) == (1, 4)


def test_affine_for_word_matches_known_prefix() -> None:
    length, A, B = affine_for_word([1, 4])
    assert (length, A, B) == (2, 5, 5)
    assert (3**length * 3 + B) // (2**A) == 1


def test_simulate_orbit_records_all_exponents() -> None:
    steps = simulate_orbit(3)
    assert [s.a for s in steps[:2]] == [1, 4]
    assert steps[-1].d_after < 0


def test_record_holder_max_reserve() -> None:
    result = analyze_orbit(19638399, max_steps=1000)
    assert result["max_reserve"] == 22
    assert result["num_segments"] == 10


def test_fast_profile_matches_full_analysis() -> None:
    full = analyze_orbit(159487, max_steps=1000)
    fast = reserve_profile(159487, max_steps=1000)
    assert fast["max_reserve"] == full["max_reserve"]
    assert fast["crossing_time"] == full["crossing_time"]


def test_macro_corridor_boundaries() -> None:
    assert find_macro_corridor_ranges([0, 1, 3, 2, 1, 0, 1], drop_tolerance=2) == [
        (0, 4),
        (5, 6),
    ]


def test_macro_corridors_for_new_record() -> None:
    rows = analyze_macro_corridors(80049391, max_steps=1000)
    assert rows
    assert max(row.d_peak for row in rows) == 23


def test_required_reserve_for_gap_under_a2_walk() -> None:
    assert required_reserve_for_gap(0) == 0
    assert required_reserve_for_gap(306, start_step=74) == 127


def test_post_k53_behavior_for_new_record() -> None:
    stats, steps = analyze_post_k53_behavior([80049391], max_steps=1000)
    assert len(stats) == 1
    assert stats[0].post_steps == len(steps)
    assert stats[0].k53_exit_step == 74
    assert stats[0].exit_reserve == 21


def test_k53_capacity_helpers() -> None:
    assert count_high_credit_steps(0, 53) == 31
    assert k53_length_from_bits(396) == 249


def test_k53_capacity_requirement_scale() -> None:
    _, requirements = analyze_k53_capacity([80049391], required_reserves=[128])
    assert requirements[0].direct_min_corridor_length_at_credit_density == 219
    assert requirements[0].instruction_min_corridor_length == 375
    assert requirements[0].min_starting_bit_length == 595
    assert requirements[0].expected_starts_log10_lower_bound > 38


def test_corridor_bound_outputs() -> None:
    observed, synthetic, ceiling = analyze_corridor_bound(
        [80049391],
        bit_lengths=[50],
        samples_per_bit_length=2,
        max_steps=200,
    )
    assert observed[0].length == 74
    assert len(synthetic) == 2
    assert ceiling[0].bit_length == 50
    assert ceiling[0].max_corridor_length == 31


def test_scaling_sweep_smoke() -> None:
    summary, fits, kill = analyze_scaling_sweep(
        bit_lengths=[50],
        thresholds=[0.5],
        samples_per_bit_length=2,
        max_steps=200,
        workers=1,
        chunk_size=1,
    )
    assert len(summary) == 1
    assert len(fits) == 3
    assert len(kill) == 2


def test_tail_law_smoke(tmp_path) -> None:
    scan = tmp_path / "scan.csv"
    scan.write_text(
        "start,max_reserve,time_max,crossing_time,growth_steps\n"
        "11,25,1,2,1\n"
        "13,24,1,2,1\n"
        "15,23,1,2,1\n"
    )
    thresholds, fits, projections, zero = analyze_tail_law(
        [(1, 20, scan)],
        min_threshold=23,
        fit_min_thresholds=[23],
        target_reserves=[26],
    )
    assert [row.count_at_least_threshold for row in thresholds] == [3, 2, 1]
    assert len(fits) == 1
    assert projections[0].target_reserve == 26
    assert zero[0].threshold_reserve == 26


def test_lock2_word_rows() -> None:
    all_twos = lock2_word_row((2, 2))
    assert all_twos.is_all_twos
    assert all_twos.margin == 0

    nontrivial = lock2_word_row((3,))
    assert nontrivial.margin == 64
    assert nontrivial.rho == 13
    assert nontrivial.first_contractivity_index == 1


def test_lock2_scan_smoke() -> None:
    summary, near_rows, all_rows, predictions, small_rho = analyze_lock2_scan(
        Amax=8,
        top_n=10,
        include_all_rows=False,
    )
    assert summary["lock2_holds_in_scan"] is True
    assert summary["all_twos_zero_margins"] == 4
    assert summary["nontrivial_zero_margins"] == 0
    assert summary["negative_margins"] == 0
    assert near_rows
    assert all_rows == []
    assert predictions == []
    assert small_rho


def test_lock2_first_contractivity_scan_smoke() -> None:
    summary, near_rows, _, predictions, small_rho = analyze_lock2_scan(
        Amax=12,
        top_n=10,
        first_contractivity_only=True,
    )
    assert summary["first_contractivity_only"] is True
    assert summary["lock2_holds_in_scan"] is True
    assert summary["contractive_words"] == summary["first_contractivity_words"]
    assert near_rows
    assert predictions == []
    assert small_rho


def test_lock2_prediction_knobs_smoke() -> None:
    summary, _, _, predictions, _ = analyze_lock2_scan(
        Amax=12,
        top_n=5,
        first_contractivity_only=True,
        predict_rho_slack_min=4,
        predict_theta_candidate_min=1,
        prediction_top_n=5,
    )
    assert summary["prediction_match_count"] > 0
    assert predictions
    assert all(row.rho_bit_slack >= 4 for row in predictions)
    assert all(row.theta_candidate_odd_count >= 1 for row in predictions)


def test_lock3_inverse_step_and_mod3_gate() -> None:
    assert lock3_inverse_step(1, 2) == 1
    assert lock3_inverse_step(5, 1) == 3
    assert lock3_inverse_step(1, 1) is None
    assert lock3_mod3_gate_residue(2) == 1
    assert lock3_mod3_gate_residue(1) == 2


def test_lock3_c0_critical_word_and_deficit_path() -> None:
    word = lock3_critical_word(12)
    assert word == (1, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 2)
    assert lock3_deficit_path(word) == (0,) * 13


def test_lock3_rho_stabilizes_for_known_finite_start() -> None:
    word = exponent_prefix_from_start(3, 2)
    assert word == (1, 4)
    assert lock3_rho_for_prefix(word[:1]) == 3
    assert lock3_rho_for_prefix(word) == 3


def test_lock3_backward_analyzer_c0_smoke() -> None:
    summary, survivor_rows, path_rows, lift_rows = analyze_lock3_backward(C=0, depth=8)
    assert summary["C"] == 0
    assert summary["max_depth"] == 8
    assert len(survivor_rows) == 8
    assert survivor_rows[-1].total_budget_paths == 1
    assert survivor_rows[-1].branch_count == 1
    assert path_rows[0].exponent_word == "1,2,1,2,1,2,2,1"
    assert lift_rows


def test_lock3_census_counts_c1_without_truncation() -> None:
    summary, rows, events, witnesses = analyze_lock3_census(C=1, depth=20, residue_mod_power=8)
    _, _, path_rows, _ = analyze_lock3_backward(C=1, depth=20, max_path_rows=60000)
    modular_valid_from_1 = sum(
        1 for row in path_rows if row.residue_class % (3**8) == 1
    )
    assert summary["mode"] == "census"
    assert summary["merge_strategy"] == "deficit_state_and_terminal_residue_signature"
    assert summary["symbolic_branch_count"] == rows[-1].symbolic_branch_count
    assert rows[-1].merged_state_count > 2
    assert rows[-1].symbolic_branch_count > rows[-1].merged_state_count
    assert rows[-1].residue_modulus == 3**8
    assert rows[-1].valid_from_1_count == modular_valid_from_1
    assert rows[-1].valid_residue_count == rows[-1].residue_class_count
    assert rows[-1].truncated is False
    assert events
    assert witnesses


def test_lock3_trivial_all_twos_backward_cycle() -> None:
    valid, ancestor, failure_depth, reason = lock3_backward_from_terminal((2, 2, 2), 1)
    assert valid is True
    assert ancestor == 1
    assert failure_depth is None
    assert reason == ""
