# Reusable Thermal-Structural Spines for Orbital Computing

## A 16-Architecture Engineering and Lifecycle Cost Study

**Status: computational, AI-assisted research.** Every result in this
repository is a modeled output of the simulation code in `simulation/`. No
orbital prototype has been built, no vacuum thermal test has passed, and no
independent environmental advantage has been established. The TVAC coupon
test described in the paper is the falsification gate for the central
engineering claim. Nothing here is demonstrated hardware performance.

**Evaluator custody.** Evaluation was performed by an internally separated
harness (INTERNAL_SEPARATED_HARNESS); it has not been externally
independently accepted. Internal test passage does not constitute external
physical or third-party acceptance.

## What we found

We compared 16 orbital and terrestrial computing architectures at 1, 4, and
16 MW over 5-, 7-, and 20-year horizons, for general AI (Regime C3) and
space-native work (Regimes C1/C2).

| Finding | Value (4 MW, $500/kg launch, 20 yr) |
|---|---|
| "Truly light" bus C6, as screened | **11.93 kg/kW — REJECTED** |
| C6 after four repaired omissions | **19.44 kg/kW (+62.95%); 20.66 kg/kW as full-system Arm G** |
| Round 1 spine (Arm N), lightest architecture | **14.58 kg/kW, 58.34 t, one Starship launch** |
| Round 2 reusable spine (Arm O) vs conventional Arm D | **$272.65M vs $430.88M/MW — −36.7%** |
| Arm O vs modeled SpaceX AI1 (Arm B) | **$272.65M vs $409.36M/MW — −33.4%** |
| Arm O vs terrestrial Arm A, general AI | **$272.65M vs $220.0M/MW — 1.239× Earth** |
| Arm O at $0/kg launch | **$257.28M/MW — still 1.169× Earth** |
| Arm O re-entry Al₂O₃ vs Arm D | **2,558.7 vs 48,552.0 kg/MW — −94.7%** |
| Arm P dual-use, net after assumed $4,850/kW-yr credit | **$176.44M/MW ($11,807.05/kW-yr) — reported separately; the credit is assumed, not a market price** |
| Parity needs | **Launch ≤ $200/kg AND ≥45% space-hardware/insurance cut, or ≤ $65/kg AND 70% cut** |

The split verdict: **a reusable spine makes orbital computing
substantially cheaper than any conventional orbital design, and still not
cheaper than Earth for general AI.** Free launch does not close the gap,
because the gap is mostly space hardware, servicing, and insurance — not
launch. Failed designs (H/I/J/K/M, C6) and the negative result (terrestrial
wins C3) are preserved in the paper, not deleted.

## What is fragile

- The C6 claim was fragile and false at the point value: 216 assumption
  corners give 11.93–21.64 kg/kW, median 16.25, only 25/216 below
  13.33 kg/kW.
- The headline 1.239× ratio depends on the model's own terrestrial
  benchmark ($220M/MW), which sits below BCG's $230–300M/MW range. At
  BCG's high end the ratio is 0.91× (orbital wins). See PAPER.md
  Section 4.5.
- The $0.135/kWh electricity parity threshold stated by the crossover
  routine is **not reproduced** by direct evaluation (executed breakeven
  ≈$0.33/kWh at $500/kg). See VERIFICATION.md D-002-13.
- Arm O is contingent on the untested dry-clamp TVAC coupon gates
  (dT_clamp ≤ 1.8 K after 20 cycles; reject Arm O if > 3.5 K).

## Reproduce it

```sh
python3 -m venv .venv
.venv/bin/pip install -r simulation/requirements.txt
python3 simulation/run_reproduction.py
```

One command regenerates the C6 audit, the tournament, the corner sweep,
the leaderboard CSV and evidence JSON, verifies byte-determinism of the
evidence across two runs, generates the figures, verifies the TVAC coupon
CAD, runs the 8-test suite in standard and `-O` modes, and writes
`SHA256SUMS.txt` last. It exits 0 only if every step passes. Note:
`simulation/generate_figures.py` is included in this package; the reproducer
fails loudly with a clear message if it is absent. See
`simulation/README.md`.

## Contents

| Path | What it is |
|---|---|
| `PAPER.md` | The full paper: methodology, equations, assumptions, results, limitations, prior art, references, corrections log. |
| `SUMMARY.md` | Short accessible summary. |
| `CITATIONS.md` | Every cited source, verified to exist, with what it supports — and what was removed for failing verification. |
| `VERIFICATION.md` | Per-claim verification table and the full corrections log (D-002-1..D-002-12, plus additional findings D-002-13..D-002-15). |
| `THREADS.md` | Threads announcement text (268 characters). |
| `simulation/` | The tournament model, the C6 falsification audit, the recovered first-order screen, the one-command runner, and the 8-test suite. |
| `evidence/` | Regenerated evidence JSON and 4 MW leaderboard CSV. |
| `figures/` | Figures 1–2, regenerated from the reproduced data. |
| `cad_and_drawings/` | Non-energized TVAC coupon: STEP B-Rep (12 closed shells, Euler V−E+F=2 on every shell), STL, DXF, SVG blueprint. Stage 0 is inert only — energized testing is on hold pending external PE/EHS signoff. |

## The falsification test

The single most important remaining test is a thermal-vacuum (TVAC)
coupon measurement of the **dry-clamp vacuum thermal interface** of the
Arm O hot-swap blade (PGS + multi-spring TIM, no fluid quick-disconnects).
Gates: dry mass ≤ 62% of a solid Al-6061 control at equal bending
stiffness (±5%); helium leak < 1×10⁻⁸ atm·cc/s at 1.5× maximum working
pressure; dT_clamp ≤ 1.8 K at 1×10⁻⁵ Torr after 20 latch/unlatch cycles.
**Reject Arm O and revert to Arm N if dT_clamp > 3.5 K.** The modeled
reusable-spine advantage rests on the assumption that a dry clamp in vacuum
transfers heat at the modeled resistance across many mate/demate cycles. If
the coupon fails, the economics collapse regardless of the mass numbers.

## License

Apache License 2.0. See `LICENSE`.
