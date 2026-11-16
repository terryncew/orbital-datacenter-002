# Simulation

Public research code for "Reusable Thermal-Structural Spines for Orbital
Computing: A 16-Architecture Engineering and Lifecycle Cost Study".
Computational study only: no hardware is built or tested by this code.

## Files

| File | What it is |
|---|---|
| `orbital_datacenter_study.py` | The 16-architecture tournament (A–P): coupled thermal, electrical, structural, reliability, communications, servicing, and lifecycle-cost model at 1/4/16 MW and 5/7/20-yr horizons, plus the exact C3 parity crossover sweep. Standard library only. |
| `falsify_c6_screen.py` | The C6 falsification audit: reproduces the recovered first-order screen (C0/C1/C6), applies the four repair steps F002-1–F002-4, runs the 216-corner adversarial sweep, and audits the SpaceX AI1 denominator. Verifies the included recovered screen files against the included manifest at runtime (hashes computed from the shipped files; no hash of any file outside this package is asserted). |
| `recovered_screen/tournament.py` | The recovered independent first-order screening model (11 arms C0–C10): two-sided Stefan–Boltzmann radiator flux, PV/radiator mass, Starship packaging bounds. Standard library only. |
| `recovered_screen/test_frontier.py` | The recovered screen's own 8 physics tests. |
| `recovered_screen/SHA256SUMS.txt` | Manifest for the two recovered screen files above. |
| `run_reproduction.py` | One-command reproducer (see below). |
| `generate_figures.py` | Included. Contract: runnable as `python3 simulation/generate_figures.py` from the repository root; reads `evidence/orbital_datacenter_002_evidence.json` and `evidence/orbital_datacenter_002_leaderboard_4mw.csv` and writes `figures/fig1_16arm_tco_and_c6.png`, `figures/fig2_parity_and_horizons.png`, `figures/fig3_arm_o_illustration.png`, and `figures/fig4_coupon.png`, exiting 0. `run_reproduction.py` fails loudly with a clear message if this file is absent. |
| `requirements.txt` | Pinned dependencies (matplotlib 3.8.4, numpy 1.26.4, Pillow 10.2.0; Python 3.12). |
| `tests/test_orbital_datacenter_study.py` | The 8-test verification suite. |

## How to run

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install -r simulation/requirements.txt
python3 simulation/run_reproduction.py
```

That regenerates the C6 audit, the tournament, the leaderboard CSV and the
evidence JSON, verifies byte-determinism of the evidence across two runs,
generates the figures, runs the 8-test suite in standard and `-O` modes,
and writes `SHA256SUMS.txt` last. It exits 0 only if every step passes.

The TVAC coupon CAD in `../cad_and_drawings/` is a shipped static artifact,
not regenerated: the STEP file is verified (12 closed shells, Euler
V−E+F=2 on every shell, 160.0 × 120.0 × 8.8 mm STL bounding box) by
`run_reproduction.py` and by test 07.

## What the model assumes (read before trusting any number)

- Silicon $45,000/kW-IT per 5-year generation ($180M/MW over 20 years),
  identical on Earth and in orbit. The common silicon cost compresses every
  cost ratio toward 1.0; see PAPER.md Section 4.3.
- Launch $500/kg baseline, swept to $0/kg. Cost is scale-invariant by
  assumption: no learning curve, no volume discount.
- Starship bounds: 100 t to LEO (published target, not a guarantee),
  665 m³ standard / 905 m³ extended ogive volumes computed from the 2020
  Starship Users Guide dimensions — not certified usable payload.
- The F002 repair adders (+0.52 kg/m² PV, +0.95 kg/m² radiator booms and
  harness; 20.0 K junction-to-radiator drop; view factor 0.78; 105 W/m²
  absorbed flux) are assumed engineering inputs, not measurements.
- Arm P's $4,850/kW-yr co-tenancy credit is a hardcoded assumed input,
  not a market price. Arm P net figures are always reported separately
  from unsubsidized C3 figures.
- Al₂O₃ ablation fractions (0.48 default, 0.09 for Arms O/P) are assigned,
  not measured. Black carbon 0.020 kg per kg launched is a model factor.
  The stratospheric radiative-forcing/ozone multiplier is UNKNOWN.
- The nominal compute density is 22 TFLOPS/kW (dense FP16). Absolute
  TFLOPS-yr/$ scales with it; cost ratios do not.
