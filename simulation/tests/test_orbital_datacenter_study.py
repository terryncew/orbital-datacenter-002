#!/usr/bin/env python3
"""Verification test suite for the orbital data center 002 study.

Runs cleanly under both standard python3 and python3 -O with
-W error::DeprecationWarning. All values are executed values from the
shipped code, not from any earlier report text.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from falsify_c6_screen import audit_and_repair_002_screen, corner_sweep_summary  # noqa: E402
from orbital_datacenter_study import (  # noqa: E402
    ARCHITECTURES,
    compute_exact_c3_parity_crossover,
    evaluate_architecture,
)


def _step_shells(step_path: Path) -> list[dict]:
    """Parse the STEP file into per-shell (V, E, F) counts."""
    text = step_path.read_text(encoding="utf-8")
    ents: dict[int, tuple[str, str]] = {}
    for m in re.finditer(r"#(\d+)\s*=\s*([A-Z_0-9]+)\((.*?)\);\s*$", text, re.M | re.S):
        ents[int(m.group(1))] = (m.group(2), m.group(3))

    def refs(s: str) -> list[int]:
        return [int(x) for x in re.findall(r"#(\d+)", s)]

    out = []
    for sh, (t, args) in ents.items():
        if t != "CLOSED_SHELL":
            continue
        faces = refs(args)
        verts: set[int] = set()
        edges: set[int] = set()
        for f in faces:
            for b in refs(ents[f][1]):
                if ents[b][0] in ("FACE_OUTER_BOUND", "FACE_BOUND"):
                    for loop in refs(ents[b][1]):
                        for ec in refs(ents[loop][1]):
                            edges.add(ec)
                            vr = refs(ents[ec][1])
                            verts.update(vr[:2])
        out.append({"shell": sh, "V": len(verts), "E": len(edges), "F": len(faces)})
    return out


class TestOrbitalDatacenter002(unittest.TestCase):
    def test_01_recovered_screen_manifest_and_reproduction(self) -> None:
        audit = audit_and_repair_002_screen()
        manifest = audit["recovered_screen_manifest_verification"]
        # The included recovered files verify against the included manifest
        # (hashes computed at runtime). No hash of any file outside this
        # package is asserted.
        if not manifest["all_match"]:
            raise AssertionError(f"Recovered screen manifest mismatch: {manifest}")
        if set(manifest["files_verified"]) != {"tournament.py", "test_frontier.py"}:
            raise AssertionError(f"Unexpected manifest contents: {manifest}")
        base = audit["reproduced_002_baseline_1mw"]
        if abs(base["C0_modern_radiator_kg_kw"] - 21.85) > 0.02:
            raise AssertionError("Failed to reproduce C0 = 21.85 kg/kW")
        if abs(base["C1_structural_heat_pipe_kg_kw"] - 17.95) > 0.02:
            raise AssertionError("Failed to reproduce C1 = 17.95 kg/kW")
        if abs(base["C6_truly_light_bus_kg_kw"] - 11.93) > 0.02:
            raise AssertionError("Failed to reproduce C6 = 11.93 kg/kW")

    def test_02_c6_falsification_waterfall_and_spacex_ai1_boundary(self) -> None:
        audit = audit_and_repair_002_screen()
        wf = audit["c6_falsification_waterfall_1mw"]
        if not (
            wf["unrepaired_c6_kg_kw"]
            < wf["after_F002_1_boom_and_harness_mass_kg_kw"]
            < wf["after_F002_2_20K_junction_to_radiator_drop_kg_kw"]
            < wf["after_F002_3_view_factor_and_plume_ir_kg_kw"]
            < wf["after_F002_4_launch_spine_and_eclipse_battery_kg_kw"]
        ):
            raise AssertionError(f"C6 falsification waterfall not strictly monotonic: {wf}")
        if abs(wf["after_F002_4_launch_spine_and_eclipse_battery_kg_kw"] - 19.44) > 0.02:
            raise AssertionError("Repaired C6 screen must be 19.44 kg/kW")
        if abs(wf["net_hidden_mass_omission_pct"] - 62.95) > 0.05:
            raise AssertionError("Hidden mass omission must be +62.95%")
        ai1 = audit["spacex_starmind_ai1_boundary_audit"]
        if abs(ai1["mass_kg_per_kw_if_250kw_peak_denominator"] - 13.33) > 0.02:
            raise AssertionError("AI1 250kW peak basis should be 13.33 kg/kW")
        if abs(ai1["mass_kg_per_kw_if_175kw_continuous_denominator"] - 19.05) > 0.02:
            raise AssertionError("AI1 175kW average basis should be 19.05 kg/kW")
        if ai1["all_in_continuous_it_kg_per_kw_credible_range"] != [19.05, 24.80]:
            raise AssertionError("AI1 all-in continuous range must be the assigned 19.05-24.80 kg/kW")
        # The withdrawn "22.29 kg/kW modeled in Arm B" figure must not appear.
        if "22.29" in json.dumps(audit):
            raise AssertionError("Withdrawn 22.29 kg/kW figure still present in audit output")
        corners = corner_sweep_summary()
        if corners["grid_cases"] != 216 or corners["kg_per_kw_range"] != [11.93, 21.64]:
            raise AssertionError(f"216-corner sweep mismatch: {corners}")
        if corners["kg_per_kw_median_grid"] != 16.25 or corners["cases_below_spacex_claim_metric"] != 25:
            raise AssertionError(f"216-corner sweep mismatch: {corners}")

    def test_03_all_16_architectures_across_1mw_4mw_16mw_and_3_horizons(self) -> None:
        if len(ARCHITECTURES) != 16:
            raise AssertionError("Must evaluate exactly 16 architectures (A through P)")
        if [a.code for a in ARCHITECTURES] != list("ABCDEFGHIJKLMNOP"):
            raise AssertionError("Architecture codes must be A through P in order")
        for mw in (1.0, 4.0, 16.0):
            for spec in ARCHITECTURES:
                res = evaluate_architecture(spec, power_mw=mw, launch_price_usd_kg=500.0)
                for h in ("5yr", "7yr", "20yr"):
                    if res["economics"][h]["total_tco_usd_m"] <= 0:
                        raise AssertionError(f"Non-positive TCO for {spec.code} at {mw}MW {h}")

    def test_04_negative_controls_and_broken_arms_h_i_j_k_m(self) -> None:
        evals = {a.code: evaluate_architecture(a, 4.0, 500.0) for a in ARCHITECTURES}
        # Arm H (126C hot compute) must have >2.5x higher failure rate than Arm E
        if evals["H"]["effective_annual_failure_rate"] < 2.5 * evals["E"]["effective_annual_failure_rate"]:
            raise AssertionError("Arm H failed to reflect Arrhenius high-temperature reliability penalty")
        # Arm H's effective rate is capped at 0.35/yr in the model
        if evals["H"]["effective_annual_failure_rate"] != 0.35:
            raise AssertionError("Arm H effective annual failure rate must be the 0.35 cap")
        # Arm I (coplanar PV+radiator shared film) must require >2.2x more radiator area than Arm E
        if evals["I"]["rad_area_m2"] < 2.2 * evals["E"]["rad_area_m2"]:
            raise AssertionError("Arm I failed to reflect single-sided view factor and solar heating conflict")
        # Arm K (Starship hull retrofit) must be heavier per kW than modular Arm D
        if evals["K"]["specific_mass_kg_per_kw"] <= evals["D"]["specific_mass_kg_per_kw"]:
            raise AssertionError("Arm K failed to account for retained Starship upper-stage inert mass")
        # Arm M (null control) must be the heaviest and among the most expensive
        if evals["M"]["specific_mass_kg_per_kw"] != max(v["specific_mass_kg_per_kw"] for v in evals.values()):
            raise AssertionError("Arm M null control must be the heaviest architecture")
        if evals["J"]["economics"]["20yr"]["tco_per_mw_usd_m"] < evals["O"]["economics"]["20yr"]["tco_per_mw_usd_m"]:
            raise AssertionError("Fluid-QDC Arm J must not beat reusable-spine Arm O on 20-yr TCO")

    def test_05_round1_n_and_round2_o_pareto_improvements_over_orbital_incumbents(self) -> None:
        evals = {a.code: evaluate_architecture(a, 4.0, 500.0) for a in ARCHITECTURES}
        # Round 1 Arm N must beat B, C, D, E, F, G in specific mass and 7-yr TCO
        for inc in ("B", "C", "D", "E", "F", "G"):
            if evals["N"]["specific_mass_kg_per_kw"] >= evals[inc]["specific_mass_kg_per_kw"]:
                raise AssertionError(f"Round 1 Arm N did not beat {inc} in specific mass")
        # Round 2 Arm O (20-yr reusable spine + dry-clamped blades) must beat Round 1 Arm N and fluid-QDC Arm J in 20-yr TCO
        o_20 = evals["O"]["economics"]["20yr"]["cost_per_delivered_kw_yr_usd"]
        n_20 = evals["N"]["economics"]["20yr"]["cost_per_delivered_kw_yr_usd"]
        j_20 = evals["J"]["economics"]["20yr"]["cost_per_delivered_kw_yr_usd"]
        if not (o_20 < n_20 and o_20 < j_20):
            raise AssertionError(f"Round 2 Arm O ({o_20}) did not beat Arm N ({n_20}) and Arm J ({j_20}) over 20 years")
        # Arm O vs conventional Arm D: -36.7% on 20-yr TCO per MW
        o_tco = evals["O"]["economics"]["20yr"]["tco_per_mw_usd_m"]
        d_tco = evals["D"]["economics"]["20yr"]["tco_per_mw_usd_m"]
        if abs((o_tco - d_tco) / d_tco * 100.0 + 36.7) > 0.15:
            raise AssertionError(f"Arm O vs Arm D TCO cut must be -36.7%, got {(o_tco - d_tco) / d_tco * 100.0:.2f}%")

    def test_06_c3_economic_closure_bound_and_zero_launch_cost_falsifier(self) -> None:
        cross = compute_exact_c3_parity_crossover()
        # Even at $0/kg launch, current space hardware prices leave Arm O > 1.15x Terrestrial Arm A
        if cross["orbital_o_at_zero_launch_cost_ratio_vs_earth"] <= 1.15:
            raise AssertionError("Failed to preserve non-launch hardware/insurance bound at $0/kg launch")
        if abs(cross["orbital_o_at_zero_launch_cost_ratio_vs_earth"] - 1.169) > 0.005:
            raise AssertionError("Arm O at $0/kg must be 1.169x terrestrial")
        # The sweep must identify winning points, and only with deep hardware
        # reduction: no winning point exists at the 1.00x hardware multiplier,
        # and none at $1,500/kg launch. The headline joint condition is
        # launch <= $200/kg AND the 0.55x multiplier (0.963x there).
        winning_pts = [p for p in cross["crossover_sweep"] if p["beats_terrestrial_c3"]]
        if not winning_pts:
            raise AssertionError("Crossover sweep must identify the exact joint threshold where C3 parity closes")
        if any(p["space_hw_cost_multiplier"] == 1.00 for p in winning_pts):
            raise AssertionError("No parity point may exist at the 1.00x hardware multiplier")
        if any(p["launch_price_usd_kg"] == 1500.0 for p in winning_pts):
            raise AssertionError("No parity point may exist at $1,500/kg launch")
        # $500/kg + 0.55x is 1.003 — NOT parity.
        near = [p for p in cross["crossover_sweep"]
                if p["launch_price_usd_kg"] == 500.0 and p["space_hw_cost_multiplier"] == 0.55][0]
        if abs(near["cost_ratio_orbital_to_terrestrial"] - 1.003) > 0.005 or near["beats_terrestrial_c3"]:
            raise AssertionError("$500/kg + 0.55x must be 1.003x, not parity")
        # D-002-13: the electricity breakeven is COMPUTED by bisection in the
        # code, not hardcoded. The earlier 0.135 $/kWh figure is withdrawn: it
        # must not appear in the crossover output, and the computed breakevens
        # are $0.3310/kWh at $500/kg launch and $0.2541/kWh at $0/kg launch.
        req = cross["minimum_joint_crossover_requirements_for_c3_parity"]
        if "or_terrestrial_electricity_price_above_usd_kwh" in req:
            raise AssertionError("Withdrawn 0.135 $/kWh threshold must not appear in crossover output")
        if abs(req["terrestrial_electricity_breakeven_usd_kwh_at_500_usd_kg_launch"] - 0.3310) > 0.002:
            raise AssertionError("Electricity breakeven at $500/kg launch must be $0.3310/kWh")
        if abs(req["terrestrial_electricity_breakeven_usd_kwh_at_zero_launch"] - 0.2541) > 0.002:
            raise AssertionError("Electricity breakeven at $0/kg launch must be $0.2541/kWh")

    def test_07_tvac_coupon_cad_euler_closure_and_environmental_unknown_honesty(self) -> None:
        cad_dir = HERE.parent / "cad_and_drawings"
        step_path = cad_dir / "o_round2_hotswap_ohp_spine_coupon.step"
        stl_path = cad_dir / "o_round2_hotswap_ohp_spine_coupon.stl"
        if not step_path.exists() or not stl_path.exists():
            raise AssertionError(f"Missing TVAC coupon CAD in {cad_dir}")
        text = step_path.read_text(encoding="utf-8")
        if "AUTOMOTIVE_DESIGN" not in text or "10303 214" not in text:
            raise AssertionError("STEP file must be ISO-10303-21 AP214")
        if text.count("MANIFOLD_SOLID_BREP") != 12:
            raise AssertionError("STEP file must contain 12 MANIFOLD_SOLID_BREP solids")
        shells = _step_shells(step_path)
        if len(shells) != 12:
            raise AssertionError(f"STEP file must contain 12 closed shells, found {len(shells)}")
        for sh in shells:
            if sh["V"] - sh["E"] + sh["F"] != 2:
                raise AssertionError(f"Shell #{sh['shell']} fails Euler V-E+F=2: {sh}")
        xs: list[float] = []
        ys: list[float] = []
        zs: list[float] = []
        for line in stl_path.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 4 and parts[0] == "vertex":
                xs.append(float(parts[1]))
                ys.append(float(parts[2]))
                zs.append(float(parts[3]))
        bbox = (round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1), round(max(zs) - min(zs), 1))
        if bbox != (160.0, 120.0, 8.8):
            raise AssertionError(f"STL bounding box must be 160.0 x 120.0 x 8.8 mm, got {bbox}")
        orb_o = evaluate_architecture(next(a for a in ARCHITECTURES if a.code == "O"), 4.0, 500.0)
        if not str(orb_o["environmental_20yr_per_mw"]["stratospheric_erf_and_ozone_multiplier"]).startswith("UNKNOWN"):
            raise AssertionError("Uncalibrated stratospheric multiplier must remain explicitly UNKNOWN")

    def test_08_scale_invariance_arm_p_separation_and_bcg_disclosure(self) -> None:
        # Cost model is scale-invariant BY ASSUMPTION (no learning curve or
        # volume discount): Arm O 20-yr TCO per MW identical at 1/4/16 MW.
        tcos = {
            mw: evaluate_architecture(next(a for a in ARCHITECTURES if a.code == "O"), mw, 500.0)["economics"]["20yr"]["tco_per_mw_usd_m"]
            for mw in (1.0, 4.0, 16.0)
        }
        if len(set(tcos.values())) != 1 or abs(list(tcos.values())[0] - 272.65) > 0.01:
            raise AssertionError(f"Arm O 20-yr TCO must be scale-invariant at $272.65M/MW, got {tcos}")
        # Arm P gross and net must stay strictly separate.
        p = evaluate_architecture(next(a for a in ARCHITECTURES if a.code == "P"), 4.0, 500.0)["economics"]["20yr"]
        if abs(p["tco_per_mw_usd_m"] - 273.44) > 0.01:
            raise AssertionError("Arm P gross 20-yr TCO must be $273.44M/MW")
        if abs(p["dual_use_net_tco_per_mw_usd_m"] - 176.44) > 0.01:
            raise AssertionError("Arm P net 20-yr TCO must be $176.44M/MW")
        if abs(p["dual_use_net_cost_per_c3_kw_yr_usd"] - 11807.05) > 0.01:
            raise AssertionError("Arm P net cost must be $11,807.05/kW-yr")
        if p["dual_use_net_tco_per_mw_usd_m"] >= p["tco_per_mw_usd_m"]:
            raise AssertionError("Arm P net must be strictly below gross")
        # Terrestrial Arm A sits BELOW BCG's terrestrial range — the headline
        # 1.239x ratio depends on the model's own, more optimistic benchmark.
        a = evaluate_architecture(next(x for x in ARCHITECTURES if x.code == "A"), 4.0, 500.0)["economics"]["20yr"]
        if abs(a["tco_per_mw_usd_m"] - 220.0) > 0.01:
            raise AssertionError("Terrestrial Arm A 20-yr TCO must be $220.0M/MW")
        if not a["tco_per_mw_usd_m"] < 230.0:
            raise AssertionError("Arm A $220M/MW must sit below BCG's $230M/MW low end")
        if abs(a["cost_per_delivered_kw_yr_usd"] - 12077.26) > 0.01:
            raise AssertionError("Terrestrial Arm A must cost $12,077.26/kW-yr")


if __name__ == "__main__":
    unittest.main()
