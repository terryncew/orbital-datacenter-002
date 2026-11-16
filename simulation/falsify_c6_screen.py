#!/usr/bin/env python3
"""Falsification and repair of the independent first-order screening model
(simulation/recovered_screen/tournament.py).

Quantifies the 4 optimistic assumptions in the screen (F002-1 through F002-4)
that artificially flatter C6_truly_light_bus (11.93 kg/kW), and reconciles
SpaceX Starmind AI1's 75 kW/ton claim across peak vs continuous IT power and
system mass boundaries. A fifth effect, end-of-life PV degradation, applies
in the full-system Arm G specification (see orbital_datacenter_study.py),
not in this screen.

The F002-1/2/3 adders are ASSUMED engineering inputs hardcoded here, not
measurements: the flown iROSA flysheet publishes no per-m2 boom mass.

Public research code. Computational study only.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECOVERED_SCREEN_DIR = HERE / "recovered_screen"
sys.path.insert(0, str(RECOVERED_SCREEN_DIR))

import tournament as orig_002  # noqa: E402


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_recovered_screen_manifest() -> dict:
    """Check the included recovered screen files against the included manifest.

    Computes SHA-256 at runtime from the files shipped in
    simulation/recovered_screen/ and compares against
    simulation/recovered_screen/SHA256SUMS.txt. No hash of any file outside
    this package is asserted.
    """
    manifest_path = RECOVERED_SCREEN_DIR / "SHA256SUMS.txt"
    if not manifest_path.exists():
        raise RuntimeError(f"Missing recovered screen manifest: {manifest_path}")
    checked: list[str] = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split("  ", 1)
        target = RECOVERED_SCREEN_DIR / rel
        if not target.exists():
            raise RuntimeError(f"Recovered screen file missing: {target}")
        actual = sha256_file(target)
        if actual != expected:
            raise RuntimeError(f"Recovered screen hash mismatch on {rel}: {actual} != {expected}")
        checked.append(rel)
    return {
        "manifest": "simulation/recovered_screen/SHA256SUMS.txt",
        "files_verified": checked,
        "all_match": True,
    }


def corner_sweep_summary() -> dict:
    """216-corner adversarial sweep over the C6 design (computed, not written).

    Equally enumerated assumption corners, NOT a probability distribution.
    Returns the range, median, and count below the 13.33 kg/kW SpaceX metric.
    """
    from dataclasses import replace as _replace
    from itertools import product as _product

    base = next(a for a in orig_002.ARMS if a.name == "C6_truly_light_bus")
    masses = []
    below = 0
    for pv_dens, rad_dens, rad_c, sun_frac, margin in _product(
        [0.85, 1.2, 1.6, 2.0], [2.2, 3.5, 5.0], [75, 85, 91], [0.95, 0.98, 0.995], [0.10, 0.15]
    ):
        a = _replace(base, pv_kg_m2=pv_dens, rad_areal_kg_m2=rad_dens,
                     rad_c=rad_c, sunlight_fraction=sun_frac, sys_margin_fraction=margin)
        m = orig_002.calculate(a, 1)["mass_kg_kw"]
        masses.append(m)
        if m < orig_002.SPACEX_CLAIMED_KG_PER_KW:
            below += 1
    masses.sort()
    return {
        "grid_cases": len(masses),
        "not_a_probability": "All equally enumerated sensitivity corners, NOT an estimated probability distribution",
        "kg_per_kw_range": [round(masses[0], 2), round(masses[-1], 2)],
        "kg_per_kw_median_grid": round(masses[len(masses) // 2], 2),
        "cases_below_spacex_claim_metric": below,
    }



def audit_and_repair_002_screen() -> dict:
    # 1. Verify the included recovered screen files against the included manifest.
    #    Hashes are computed at runtime from the shipped files; nothing outside
    #    this package is asserted here.
    manifest = verify_recovered_screen_manifest()
    if not manifest["all_match"]:
        raise RuntimeError(f"Recovered screen manifest mismatch: {manifest}")

    # 2. Reproduce original 002 C0, C1, C6 at 1 MW and 4 MW
    c0_orig_1mw = orig_002.calculate(next(a for a in orig_002.ARMS if a.name == "C0_modern_radiator"), 1.0)
    c1_orig_1mw = orig_002.calculate(next(a for a in orig_002.ARMS if a.name == "C1_structural_heat_pipe"), 1.0)
    c6_arm = next(a for a in orig_002.ARMS if a.name == "C6_truly_light_bus")
    c6_orig_1mw = orig_002.calculate(c6_arm, 1.0)
    c6_orig_4mw = orig_002.calculate(c6_arm, 4.0)

    # 3. Quantify the 4 specific physical flatterers in C6_truly_light_bus (11.93 kg/kW)
    #    (assumed inputs — see the module docstring)
    pv_boom_and_harness_adder_kg_m2 = 0.52
    rad_boom_and_manifold_adder_kg_m2 = 0.95
    real_delta_t_j_rad_k = 20.0
    repaired_rad_c = c6_arm.junction_c - real_delta_t_j_rad_k  # 78.0 C
    repaired_view_factor = 0.78
    repaired_absorbed_w_m2 = 105.0
    launch_strongback_and_gnc_kg_kw = 1.85

    c6_step1 = orig_002.replace(
        c6_arm,
        pv_kg_m2=round(c6_arm.pv_kg_m2 + pv_boom_and_harness_adder_kg_m2, 3),
        rad_areal_kg_m2=round(c6_arm.rad_areal_kg_m2 + rad_boom_and_manifold_adder_kg_m2, 3),
    )
    r_step1 = orig_002.calculate(c6_step1, 1.0)

    c6_step2 = orig_002.replace(c6_step1, rad_c=repaired_rad_c)
    r_step2 = orig_002.calculate(c6_step2, 1.0)

    c6_step3 = orig_002.replace(c6_step2, view_factor=repaired_view_factor, absorbed_w_m2=repaired_absorbed_w_m2)
    r_step3 = orig_002.calculate(c6_step3, 1.0)

    c6_step4 = orig_002.replace(
        c6_step3,
        battery_kg_kw=0.85,
        bus_and_comms_kg_kw=round(c6_arm.bus_and_comms_kg_kw + launch_strongback_and_gnc_kg_kw, 3),
        structural_mass_credit_kg_kw=0.45,
    )
    r_step4 = orig_002.calculate(c6_step4, 1.0)

    # 4. SpaceX Starmind AI1 (250 kW peak / 175 kW avg, 75 kW/ton, 30m x 75m) Boundary Reconciliation
    ai1_peak_kw = 250.0
    ai1_avg_kw = 175.0
    ai1_claimed_kw_per_ton = 75.0
    ai1_implied_sat_mass_kg_if_peak_num = (ai1_peak_kw / ai1_claimed_kw_per_ton) * 1000.0  # 3,333.3 kg
    ai1_kg_per_kw_peak_basis = 1000.0 / ai1_claimed_kw_per_ton  # 13.33 kg/kW_peak
    ai1_kg_per_kw_avg_basis_from_peak_mass = ai1_implied_sat_mass_kg_if_peak_num / ai1_avg_kw  # 19.05 kg/kW_avg
    ai1_all_in_continuous_kg_per_kw_range = [19.05, 24.80]

    return {
        "recovered_screen_manifest_verification": manifest,
        "reproduced_002_baseline_1mw": {
            "C0_modern_radiator_kg_kw": c0_orig_1mw["mass_kg_kw"],
            "C1_structural_heat_pipe_kg_kw": c1_orig_1mw["mass_kg_kw"],
            "C6_truly_light_bus_kg_kw": c6_orig_1mw["mass_kg_kw"],
            "C6_4mw_total_mass_t": c6_orig_4mw["total_mass_t"],
            "C6_4mw_pv_area_m2": c6_orig_4mw["pv_area_m2"],
            "C6_4mw_rad_area_m2": c6_orig_4mw["rad_area_m2"],
        },
        "c6_falsification_waterfall_1mw": {
            "unrepaired_c6_kg_kw": c6_orig_1mw["mass_kg_kw"],
            "after_F002_1_boom_and_harness_mass_kg_kw": r_step1["mass_kg_kw"],
            "after_F002_2_20K_junction_to_radiator_drop_kg_kw": r_step2["mass_kg_kw"],
            "after_F002_3_view_factor_and_plume_ir_kg_kw": r_step3["mass_kg_kw"],
            "after_F002_4_launch_spine_and_eclipse_battery_kg_kw": r_step4["mass_kg_kw"],
            "net_hidden_mass_omission_pct": round((r_step4["mass_kg_kw"] - c6_orig_1mw["mass_kg_kw"]) / c6_orig_1mw["mass_kg_kw"] * 100.0, 2),
        },
        "spacex_starmind_ai1_boundary_audit": {
            "source_url": "https://www.spacex.com/spacexai/starmind",
            "kessel_rack_source_url": "https://mlq.ai/news/spacex-is-designing-kessel-a-72-gpu-nvidia-rubin-rack-for-data-centers-in-space-report-says/",
            "deployed_height_m": 30.0,
            "deployed_wingspan_m": 75.0,
            "compute_payload_peak_kw": ai1_peak_kw,
            "compute_payload_average_kw": ai1_avg_kw,
            "claimed_vehicle_efficiency_kw_per_ton": ai1_claimed_kw_per_ton,
            "mass_kg_per_kw_if_250kw_peak_denominator": round(ai1_kg_per_kw_peak_basis, 2),
            "mass_kg_per_kw_if_175kw_continuous_denominator": round(ai1_kg_per_kw_avg_basis_from_peak_mass, 2),
            "all_in_continuous_it_kg_per_kw_credible_range": ai1_all_in_continuous_kg_per_kw_range,
            "boundary_verdict": (
                "SpaceX's 75 kW/ton (13.33 kg/kW) corresponds to 250 kW peak payload power on a ~3.33 t dry satellite. "
                "Normalized to 175 kW continuous average compute power on the same 3.33 t vehicle, specific mass is "
                "19.05 kg/kW before wet propellant and replacement spares. The all-in continuous range is stated as "
                "assigned, 19.05-24.80 kg/kW; no code computes a point value inside that range."
            ),
        },
    }


if __name__ == "__main__":
    res = audit_and_repair_002_screen()
    print(json.dumps(res, indent=2))
