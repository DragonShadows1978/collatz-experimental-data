#!/usr/bin/env python3
import json
from pathlib import Path
from species_orbit import is_one_step_species, one_odd_step, species_member, steps_to_species
ART = Path(__file__).resolve().parents[1] / "artifacts"

def test_species_cert():
    for k in (1, 5, 10, 20):
        x = species_member(k)
        assert is_one_step_species(x)[0]
        assert one_odd_step(x) == 1

def test_steps():
    r = steps_to_species(7, 10000)
    assert r["hit"]
    assert r["steps_to_species"] >= 0

def test_art():
    d = json.loads((ART / "summary.json").read_text())
    assert d["gates"]["n_starts"] >= 200
    assert d["predictions"]["U10.4"]["verdict"] == "CONFIRMED"

if __name__ == "__main__":
    test_species_cert(); print("PASS cert")
    test_steps(); print("PASS steps")
    test_art(); print("PASS art")
    print("ALL G10 TESTS PASSED")
