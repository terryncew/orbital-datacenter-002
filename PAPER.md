# Reusable Thermal-Structural Spines for Orbital Computing: A 16-Architecture Engineering and Lifecycle Cost Study

**Status: computational, AI-assisted research.** All results in this paper
are modeled outputs of the accompanying simulation code. No orbital
prototype has been built, no vacuum thermal test has passed, and no
independent environmental advantage has been established. The TVAC coupon
test described in Section 4.7 is the falsification gate for the central
engineering claim. Nothing in this paper is demonstrated hardware
performance.

**Acceptance boundary.** This is a computational engineering study. No
orbital prototype has been built, no vacuum thermal test has passed, no
independent environmental advantage has been established. Every result is
labeled: measured fact / literature parameter / assumed engineering input /
simulation prediction.

**Evaluator custody.** Evaluation was performed by an internally separated
harness (INTERNAL_SEPARATED_HARNESS); it has not been externally
independently accepted. Internal test passage does not constitute external
physical or third-party acceptance.

*Reproduction: `python3 simulation/run_reproduction.py` regenerates every
number, figure, and table in this paper from the code. Evidence, leaderboard,
and manifest: `evidence/`, `SHA256SUMS.txt`.*

## Abstract

We compare sixteen orbital and terrestrial computing architectures at 1, 4,
and 16 MW over 5-, 7-, and 20-year horizons, for general AI for terrestrial
users (Regime C3) and for space-native work (Regimes C1/C2), using a
Stefan–Boltzmann radiative model with a coupled junction-to-radiator thermal
chain, a reliability and availability model, Starship packaging bounds, and a
lifecycle cost model including launch, servicing, insurance, and silicon
refresh. The study opens by falsifying its own most attractive screen
result: a thin-film "truly light" bus claimed at 11.93 kg/kW rises to
19.44 kg/kW once omitted booms, harness, a realistic 20 K
junction-to-radiator drop, view-factor shadowing, and launch strongback are
restored (+62.95% hidden mass), and to 20.66 kg/kW as a full system with
end-of-life degradation. Three invention rounds then recover the mass
honestly: direct 800 V HVDC with a backside structural heat-pipe spine
(Arm N, 14.58 kg/kW), a 20-year reusable spine with dry-clamped hot-swappable
compute blades (Arm O, 15.60 kg/kW), and a dual-use variant (Arm P). Arm O
cuts 20-year cost by 36.7% against the conventional modular orbital
incumbent (Arm D) and by 33.4% against the modeled SpaceX AI1 reference
(Arm B), and cuts re-entry alumina by 94.7% against Arm D. It still loses
to terrestrial clean-grid compute for general AI: $272.65M/MW
($14,960.66/kW-yr) against $220.0M/MW ($12,077.26/kW-yr), a ratio of 1.239×
at $500/kg launch — and 1.169× even at $0/kg launch, because the gap is
mostly non-launch hardware, servicing, and insurance, not launch. Parity
needs launch at or below $200/kg *and* at least a 45% space-hardware and
insurance cost reduction, or launch at or below $65/kg with a 70%
reduction. The dual-use Arm P reaches $176.4M/MW net only after an assumed
$4,850/kW-yr co-tenancy credit, which is an assumed input, not a market
price, and is reported strictly separately. The split verdict is the
finding: a reusable spine makes orbital computing substantially cheaper
than any conventional orbital design, and still not cheaper than Earth for
general AI. The decisive physical test — a thermal-vacuum coupon
measurement of the dry-clamp interface — is outstanding and could reject
the central claim.

## 1. Introduction

The orbital data-center proposition is simple to state and hard to settle:
space offers continuous sunlight and a cold sink, but everything launched
must be paid for by mass, and the hardware still needs power, storage, and
shielding. An orbital facility could in principle reduce terrestrial
demands for land, water, and grid electricity — the terrestrial benchmark in
this study uses closed-loop dry cooling with 0.0 L/kWh direct water — but
that possibility does not automatically establish an environmental benefit,
because launch and re-entry put black carbon and alumina into the
stratosphere, where their forcing and ozone effects are uncalibrated
(Section 3.7). Any environmental claim has to survive that ledger, not
just the terrestrial savings.

Two recent analyses frame the bounds. Turyshev (JPL/Caltech) finds a 1 MW
orbital anchor needs 5,640 m² of photovoltaics and 2,500 m² of radiator, at
29.4 kg/kW for power, storage, and radiator and 34–59 kg/kW total, and
concludes space-native processing (C1) and communications-integrated edge
compute (C2) are credible early while general terrestrial compute (C3)
closes only for low communication intensity, high utilization, long life,
and very low cost [1]. A follow-up on operations finds 393–419 standardized
operations per MW-year and 5.3–9.0 t/(MW-year) of logistics [2] — a direct
challenge to any servicing model that assumes cheap hands in orbit. The
ICEF roadmap finds that supplying 10% of projected 2030 AI data-center
demand from orbit would require at least 700 Starship-sized launches per
year in perpetuity, and warns that weights claimed by leading developers
appear highly optimistic [7]. The U.S. GAO notes that space does not cool
hardware efficiently and that cooling at data-center scale is unproven [10].
Google's Project Suncatcher has flown a 4-TPU prototype (1 Oct 2026,
Transporter-18) but publishes no thermal design [3]; SpaceX's AI1 is
described on its product page as a 250 kW peak / 175 kW average design at
75 kW/ton [4], a figure whose denominator this study audits in Section 3.6.
BCG puts current 20-year orbital TCO at $660–750M/MW against $230–300M/MW
terrestrial, a 2.5–3× premium today, improving to ~1.5× realistically and
1.1–1.2× aggressively [5] — a benchmark this study's modeled costs sit well
below, which is itself a finding about the model's optimism (Section 4.5).

This study asks a narrower, answerable question: given a fixed thermal
model, which architectures win on mass, cost, and survival, at which scales
and horizons, and for which workload — and how sensitive are the answers to
the inputs? It starts by falsifying its own best screen result, then
invents in three rounds, preserves the failed designs, and reports the split
verdict with its sensitivities and its falsifier. We do not build hardware.
We model sixteen architectures, reject six, invent three, and report what
survives.

This is the second study in a pair. The first, called Orbital 001 here, is
an unpublished manuscript from the same program (a structural-thermal study
at 1–1,000 kW on a 5-year horizon). Where this paper compares the two, it
states the method differences explicitly (Section 4.3); 001's results are
summarized for comparison only and are not republished here.

## 2. Methods

### 2.1 Model

The model is `simulation/orbital_datacenter_study.py` (standard library
only) plus the recovered first-order screen in
`simulation/recovered_screen/tournament.py` and its falsification in
`simulation/falsify_c6_screen.py`. All equations below are implemented
there; the paper states them so a reader can check the code against the
claims.

**Radiative flux.** Two-sided Stefan–Boltzmann emission with view factor,
emissivity, background temperature, and absorbed environmental flux:

$$q = 2 \cdot v_f \cdot \varepsilon \cdot \sigma \cdot (T_{rad}^4 - T_{bg}^4) - q_{abs}$$

with σ = 5.670374419×10⁻⁸ W/m²K⁴ and T_bg = 220 K. The radiator temperature
is T_rad = T_junction − ΔT_chain. Radiator area is waste heat (IT power plus
conversion and thermal-auxiliary losses) divided by flux; PV area is system
power (including a system margin) divided by end-of-life PV output
(BOL W/m² × degradation over the bus life, capped at 10 years, × sunlight
fraction).

**Spacecraft mass.** Total launched mass per kW is PV mass plus radiator
mass (panel plus boom/manifold areal densities) plus compute-and-shield,
battery, and bus/strongback/communications mass, minus a structural credit
capped at 65% of bus mass:

$$m = A_{PV}\rho_{PV} + A_{rad}\rho_{rad} + m_{compute} + m_{battery} + m_{bus} - \min(m_{credit}, 0.65\, m_{bus})$$

**Packaging and launch.** Stowed volume is PV and radiator area times
stow thickness, times a packaging void factor, plus a volumetric allowance
for compute, battery, and bus mass. Launches are the maximum of the
mass bound (ceil of total mass / 100 t) and the extended-ogive volume bound
(ceil of stowed volume / 905 m³); the standard-ogive count (665 m³) is also
reported. The 665/905 m³ volumes are computed from the 2020 Starship Users
Guide dimensions (9 m outer diameter, 8 m dynamic envelope, extended volume
up to 22 m height) [8]; the guide is a preliminary document and the volume
bound is not a certified usable payload or interface.

**Reliability and availability.** Effective annual failure rate is the base
rate times an Arrhenius multiplier (E_a = 0.70 eV, reference 88 °C),
capped at 0.35/yr. Delivered compute years multiply sunlight fraction,
optical crosslink efficiency, MMOD survival (base 5-year survival raised to
horizon/5), and a failure derate. The nominal compute density is
22 TFLOPS/kW (dense FP16) — an assumed engineering input; absolute
TFLOPS-yr/$ scales with it, cost ratios do not.

**Economics.** Silicon costs $45,000/kW-IT per 5-year generation, identical
on Earth and in orbit: $180M/MW over 20 years (4 generations). Terrestrial
Arm A: facility $14M/MW, electricity $679.08/kW-yr at $0.068/kWh × PUE 1.14,
plus $620.92/kW-yr operations — non-silicon $40M/MW, $2,195.86/delivered
kW-yr. Orbital arms: PV, radiator, and bus hardware, launch at $500/kg
baseline (swept to $0/kg), insurance and spares (12% of hardware plus a
failure-driven term), and ground operations. Arms with cartridge servicing
(Arms J, O, P) deploy the bus once per bus life and swap only compute
cartridges per silicon generation, with a servicing-tug overhead fraction
(0.38 for Arm J, 0.14 for Arms O/P) and a 1.18× launch factor on swaps.
All other orbital arms replace the whole spacecraft per bus life or per
silicon generation, whichever is more frequent. Cost per delivered kW-yr
divides total cost by delivered compute years. The crossover sweep
(`compute_exact_c3_parity_crossover()`) re-evaluates Arm O across launch
prices ($1,500–$0/kg) and hardware cost multipliers (1.00×/0.55×/0.30×/0.20×),
scaling PV/radiator/bus capex, insurance, failure rate, and crosslink
efficiency together.

**Workload metrics.** Regime C3 (general AI) is cost per delivered kW-yr
and delivered TFLOPS-yr/$. Regime C1/C2 (space-native EO/SAR and sovereign
relay work) enters only through Arm P's assumed co-tenancy credit, reported
strictly separately from unsubsidized C3 (Section 3.5).

**Environmental ledger.** Launch black carbon at 0.020 kg per kg launched
(20 kg/t) — a model factor, and different from the 0.042 kg/kg used in the
001 study, so ledger totals are not comparable across studies. Re-entry
alumina is total launched mass over the horizon times an assigned ablation
fraction (0.48 default, 0.19 for Arm N, 0.09 for Arms O/P). Lifecycle CO₂e
is 14.5 t per tonne launched plus 680 t fixed — a rough model. The
stratospheric radiative-forcing and ozone multiplier is recorded as UNKNOWN
(±300% spread), not estimated.

**Labeling.** Every result in this paper is one of four kinds, and the
paper says which: **measured fact** (a published figure or a value
reproduced from executed code), **literature parameter** (a value taken from
a cited source), **assumed engineering input** (a number the model assigns
with no cited measurement), or **simulation prediction** (a model output).
The decisive assumed inputs are named in Section 2.2 and again wherever
they drive a headline number.

### 2.2 Architectures

Sixteen arms, A–P. Arms A–M are baselines, references, controls, and
rejected designs; Arms N, O, P are the three invention rounds. Reference
arms B and C are **modeled references informed by public parameters, not
measured performance of any company's hardware**: Arm B uses the AI1 power
figures from SpaceX's product page with modeled thermal and bus parameters;
Arm C uses the Suncatcher paper's orbital parameters (81 satellites,
650 km) with an assumed thermal stack the paper does not publish. The full
parameter set is in the code; the decisive assigned inputs are:

| Arm | Design | T_j (°C) | ΔT (K) | ε | v_f | q_abs (W/m²) | Rad panel (kg/m²) | PV BOL (W/m²) | PV blanket (kg/m²) | Battery (kg/kW) | Elec loss | Bus life (yr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | Terrestrial clean-grid dry cool | 78 | 33.0 | — | — | — | — | — | — | — | — | 20 |
| B | Modeled SpaceX AI1 | 96 | 14.0 | 0.90 | 0.84 | 88 | 3.60 | 265 | 1.05 | 0.80 | 0.060 | 5 |
| C | Modeled Suncatcher-class | 88 | 16.0 | 0.88 | 0.82 | 95 | 4.50 | 260 | 1.25 | 0.95 | 0.065 | 5 |
| D | Conventional modular PV + radiator | 95 | 18.0 | 0.86 | 0.82 | 95 | 4.65 | 255 | 1.35 | 1.45 | 0.065 | 5 |
| E | Thin structural OHP, realistic PV | 95 | 14.0 | 0.91 | 0.83 | 90 | 3.45 | 265 | 1.20 | 1.05 | 0.060 | 5 |
| F | Integrated thermal/structure/power tiles | 96 | 12.5 | 0.90 | 0.82 | 92 | 3.55 | 265 | 1.10 | 0.90 | 0.085 | 5 |
| G | Thin-film PV + separate radiator (repaired C6) | 98 | 20.0 | 0.88 | 0.78 | 105 | 2.20 | 250 | 0.85 | 0.85 | 0.085 | 5 |
| H | Hot silicon, 126 °C junction | 126 | 18.0 | 0.90 | 0.82 | 95 | 3.65 | 265 | 1.15 | 0.90 | 0.095 | 5 |
| I | Coplanar shared solar/radiator film | 95 | 32.0 | 0.84 | 0.46 | 185 | 3.80 | 215 | 0.95 | 1.15 | 0.075 | 5 |
| J | 20-yr bus, fluid-QDC cartridges | 95 | 17.0 | 0.90 | 0.82 | 95 | 4.20 | 265 | 1.25 | 1.30 | 0.065 | 20 |
| K | Starship hull retrofit | 95 | 16.0 | 0.88 | 0.80 | 100 | 4.10 | 260 | 1.20 | 1.25 | 0.065 | 10 |
| L | Federated constellation scheduler | 95 | 14.0 | 0.90 | 0.83 | 90 | 3.50 | 265 | 1.15 | 1.55 | 0.065 | 5 |
| M | Null control, no credits | 92 | 20.0 | 0.82 | 0.74 | 120 | 5.40 | 245 | 1.95 | 3.80 | 0.080 | 5 |
| N | Round 1: direct 800 V HVDC + backside OHP spine | 98 | 11.5 | 0.92 | 0.85 | 82 | 3.15 | 285 | 0.98 | 0.55 | 0.032 | 7 |
| O | Round 2: 20-yr reusable spine, hot-swap blades | 98 | 12.8 | 0.92 | 0.85 | 82 | 3.25 | 285 | 1.04 | 0.65 | 0.032 | 20 |
| P | Round 3: dual-use spine (Arm O + C1/C2 duty) | 98 | 12.8 | 0.92 | 0.85 | 82 | 3.25 | 285 | 1.04 | 0.65 | 0.032 | 20 |

Arm O's decisive inputs are the 20-year bus life (the solar, radiator, and
optical spine stay in orbit), the 0.14 servicing-tug overhead, the 3.75
kg/kW dry-clamped compute blade swapped every 5 years, the 1.35 kg/kW
structural credit, and the 0.09 alumina ablation fraction. Arm P is Arm O
hardware with 18% of duty allocated to space-native EO/SAR/sovereign
optical relay and an assumed $4,850/kW-yr co-tenancy credit — an assumed
engineering input, not a market price.

### 2.3 Procedure

Three rounds, after an independent first-order screen. The recovered screen
(eleven arms C0–C10, 1 MW and 4 MW) produced the C6 claim of 11.93 kg/kW.
The falsification audit (Section 3.2) repaired it. Round 1 invented Arm N
on the repaired baseline. Round 2 invented Arm O, reusing the expensive
outer infrastructure and swapping only compute blades. Figure 3 is the
engineering illustration of Arm O: the structural heat-pipe spine, the
replaceable compute blades, the dry-clamp interfaces, the radiators, and
the solar array, drawn from the modeled geometry. No modeled deployed span
exists in the code; the diagram states that it is not to scale. Round 3 split the
workload: Arm P keeps Arm O hardware and prices the dual-use case
separately, so that no dual-use credit can leak into the pure-C3 verdict.
Sensitivity analysis re-evaluated the C6 claim across a 216-corner grid of
assumption combinations (`corner_sweep_summary()` in the code).

## 3. Results

### 3.1 Sixteen-architecture leaderboard (4 MW, $500/kg launch, 20-yr horizon)

| Arm | Mass (kg/kW) | Total mass (t) | PV (m²) | Rad (m²) | Vol (m³) | Launches | TCO 5yr ($M/MW) | TCO 7yr ($M/MW) | TCO 20yr ($M/MW) | Cost ($/kW-yr) | TFLOPS-yr/$ | Al₂O₃ (kg/MW) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A Terrestrial** | 0.00 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 55.00 | 77.00 | **220.00** | **12,077.26** | 0.0018 | 0.0 |
| B AI1 (modeled) | 18.08 | 72.33 | 19,336.7 | 3,980.9 | 623.3 | 1 | 102.34 | 143.27 | 409.36 | 26,343.43 | 0.0008 | 34,716.0 |
| C Suncatcher (modeled) | 24.10 | 96.40 | 20,129.7 | 4,916.2 | 703.7 | 1 | 104.74 | 146.64 | 418.96 | 27,676.31 | 0.0008 | 46,270.8 |
| D Conventional | 25.29 | 101.15 | 20,774.5 | 4,718.2 | 703.7 | 2 | 107.72 | 150.81 | 430.88 | 26,554.45 | 0.0008 | 48,552.0 |
| E Thin structural OHP | 19.26 | 77.03 | 19,352.3 | 4,031.1 | 634.4 | 1 | 98.45 | 137.83 | 393.79 | 23,044.72 | 0.0010 | 36,975.6 |
| F Integrated tiles | 19.66 | 78.64 | 19,667.3 | 4,089.7 | 647.8 | 1 | 103.61 | 145.06 | 414.46 | 26,162.49 | 0.0008 | 37,746.0 |
| G Repaired C6 | 20.66 | 82.65 | 22,372.8 | 4,887.3 | 745.6 | 1 | 119.60 | 167.44 | 478.41 | 37,759.65 | 0.0006 | 39,669.6 |
| H Hot silicon | 18.92 | 75.70 | 19,915.2 | 2,996.0 | 588.6 | 1 | 173.83 | 243.36 | 695.33 | 85,949.79 | 0.0003 | 36,333.6 |
| I Coplanar film | 34.72 | 138.87 | 24,901.2 | 16,037.6 | 1,405.7 | 2 | 137.87 | 193.02 | 551.47 | 38,059.95 | 0.0006 | 66,658.8 |
| J Fluid-QDC cartridges | 24.04 | 96.15 | 20,680.7 | 4,442.3 | 695.7 | 1 | 79.02 | 110.63 | 316.08 | 21,167.95 | 0.0010 | 20,679.6 |
| K Hull retrofit | 32.61 | 130.46 | 21,748.9 | 4,613.3 | 813.5 | 2 | 119.55 | 167.36 | 478.18 | 29,053.25 | 0.0008 | 62,618.4 |
| L Federated constellation | 21.12 | 84.47 | 19,925.1 | 4,118.0 | 662.8 | 1 | 107.28 | 150.19 | 429.13 | 31,487.82 | 0.0007 | 40,544.4 |
| M Null control | 39.14 | 156.58 | 24,019.8 | 6,356.1 | 893.7 | 2 | 122.32 | 171.25 | 489.28 | 33,731.01 | 0.0007 | 75,157.2 |
| **N Round 1 spine** | **14.58** | **58.34** | **17,305.2** | **3,457.2** | **406.3** | **1** | **89.38** | **125.13** | **357.52** | **19,983.01** | **0.0011** | **11,084.6** |
| **O Round 2 spine** | **15.60** | **62.42** | **17,709.2** | **3,520.1** | **428.3** | **1** | **68.16** | **95.43** | **272.65** | **14,960.66** | **0.0015** | **2,558.7** |
| **P Round 3 dual-use** | **15.80** | **63.22** | **17,709.2** | **3,520.1** | **430.2** | **1** | **68.36** | **95.71** | **273.44** | **15,004.34** | **0.0015** | **2,607.5** |

Arm P's unsubsidized cost is $15,004.34/kW-yr; its net cost after the
assumed credit is $11,807.05/kW-yr (Section 3.5). No orbital arm beats
terrestrial Arm A on 20-year cost per delivered kW-yr. Arm O is the best
orbital arm on cost, Arm N the lightest, and Arm M the heaviest by design:
the null control exists to show what the model produces with no credits and
no bonuses at all (39.14 kg/kW, $489.28M/MW). Figure 1, panel A, plots this
leaderboard.

### 3.2 C6 falsification waterfall

The recovered screen's most attractive claim was C6, a thin-film PV plus
light structural bus at **11.93 kg/kW** (1 MW screen; C0 conventional
21.85, C1 structural 17.95). The falsification audit restores four omitted
or optimistic inputs, one step at a time:

| Step | Repair (assumed engineering input) | C6 (kg/kW) |
|---|---|---|
| Unrepaired screen | — | 11.93 |
| F002-1 | Booms and harness: +0.52 kg/m² PV, +0.95 kg/m² radiator | 15.20 |
| F002-2 | Realistic 20.0 K junction-to-radiator drop (T_rad 78 °C, not 91 °C) | 15.71 |
| F002-3 | 3D mutual view-factor shadowing (F = 0.78) and 105 W/m² absorbed flux | 16.34 |
| F002-4 | Launch strongback +1.85 kg/kW, eclipse battery 0.85 kg/kW, structural credit capped at 0.45 kg/kW | 19.44 |

Net hidden omission: **+62.95%**. Figure 1, panel B, plots the waterfall.
The full-system version, Arm G, is
**20.66 kg/kW** and $478.41M/MW — the extra mass comes from 2.8%/yr
thin-film end-of-life degradation (pv_deg_per_yr = 0.028) and the full
reliability and servicing model. The F002-1 adders and the F002-2/3 inputs
are assumed engineering inputs hardcoded in the falsify script, not
measurements: the flown iROSA flysheet publishes no per-m2 boom mass [9].
(The script's docstring in an earlier version said "5 assumptions" but
implemented 4 waterfall steps; the fifth effect, end-of-life degradation,
applies in the Arm G specification. This paper states 4 screen steps plus
degradation.)

The claim is fragile, not just wrong at the point value. A 216-corner
adversarial grid over PV areal mass, radiator density, radiator
temperature, sunlight fraction, and system margin gives a C6 range of
**11.93–21.64 kg/kW, median 16.25**, with only **25 of 216 corners below
13.33 kg/kW** — the SpaceX metric the claim appeared to beat. The corners
are equally enumerated, not a probability distribution. Disposition:
**REJECT** the 11.93 kg/kW claim; adopt the repaired Arm G as the honest
version of the design.

### 3.3 Scaling (1/4/16 MW) and launch counts

The cost model is **scale-invariant by assumption**: $272.65M/MW for Arm O
at 1, 4, and 16 MW alike, with no learning curve and no volume discount.
That is an assumption, not a finding (D-002-9). What changes with scale is
packaging:

| Scale | Arm B launches (mass / std / ext) | Arm D launches | Arm O launches | Arm O stowed volume (m³) |
|---|---|---|---|---|
| 1 MW | 1 / 1 / 1 | 1 | 1 | 107.1 |
| 4 MW | 1 / 1 / 1 | 2 | 1 | 428.3 |
| 16 MW | 3 / 4 / 3 | 5 | 3 (2 by extended volume) | 1,713.2 |

At 4 MW, Arm O fits one launch in a standard 665 m³ ogive while Arm D
needs two. At 16 MW, Arm B needs 3 launches by mass and extended volume
(4 by standard volume), Arm D needs 5, and Arm O needs 3 (2 by extended
volume). These are mass and idealized packing-volume bounds, not certified
manifests: fold and deployment geometry, attitude stability, interconnects,
and MMOD survival could make a configuration impossible even when it fits
the cylinder.

### 3.4 Arm O economics and the parity boundary

Arm O at 4 MW, $500/kg launch, 20 years: **$272.65M/MW,
$14,960.66/kW-yr**, against terrestrial Arm A's $220.0M/MW,
$12,077.26/kW-yr — **1.239× Earth**. The decomposition (per MW, 20 yr):
silicon $180.00M (common to both sides), bus hardware $35.46M, launch
$15.37M, insurance/spares/operations $41.82M — non-silicon $92.65M, or
$5,083.75/kW-yr against terrestrial non-silicon $2,195.86/kW-yr. At
$100/kg launch Arm O is $260.35M/MW (1.183×). At **$0/kg launch** it is
still **$257.28M/MW, $14,117.33/kW-yr (1.169× all-in)** and
**$4,240.42/kW-yr non-silicon (1.931× terrestrial non-silicon)**. Free
launch does not close the gap, because the gap is mostly not launch: it is
space hardware, servicing, radiation spares, and insurance.

The full crossover sweep (ratio of Arm O to terrestrial Arm A cost per
delivered kW-yr; < 1.000 wins):

| Launch ($/kg) | 1.00× hardware | 0.55× (45% cut) | 0.30× (70% cut) | 0.20× (80% cut) |
|---|---|---|---|---|
| 1,500 | 1.378 | 1.138 | 1.045 | 1.016 |
| 500 | 1.239 | 1.003 | 0.913 | 0.884 |
| 200 | 1.197 | **0.963** | 0.873 | 0.845 |
| 100 | 1.183 | 0.949 | 0.860 | 0.832 |
| 65 | 1.178 | 0.944 | **0.855** | 0.827 |
| 20 | 1.172 | 0.938 | 0.849 | 0.821 |
| 0 | 1.169 | 0.936 | 0.847 | 0.819 |

Parity conditions, from the executed sweep: **both** launch ≤ $200/kg
**and** ≥45% space-hardware/insurance reduction (0.55× →
$11,626.24/kW-yr = 0.963×); **or** 0.30× at ≤ $65/kg →
$10,329.94/kW-yr = 0.855×; **or** terrestrial firm clean electricity at or
above the computed breakeven — **$0.3310/kWh at $500/kg launch,
$0.2541/kWh at $0/kg launch** — where Arm A's cost per delivered kW-yr
equals Arm O's. Two cautions. First, at $500/kg with the 0.55× multiplier
the ratio is 1.003 — **not** parity; a single improvement is never enough
at current launch prices. Second, an earlier version of this study stated
$0.135/kWh as the electricity parity condition; that figure is **withdrawn**
(D-002-13) — direct evaluation gives Arm A at $0.135/kWh as
$12,811.88/kW-yr, still below Arm O at $500/kg ($14,960.66) and below Arm O
at $0/kg ($14,117.33). The breakevens above are computed by the code, not
asserted. The sweep's launch and hardware conditions, by contrast, are
computed directly and reproduce.

Figure 2 plots the crossover curves and the 5/7/20-year horizon comparison.

### 3.5 Arm P dual-use, kept strictly separate

Arm P is Arm O hardware with 18% of duty allocated to space-native
EO/SAR/sovereign optical relay work. Gross 20-year cost is $273.44M/MW
($15,004.34/kW-yr). After an **assumed $4,850/kW-yr co-tenancy credit** it
is **$176.44M/MW net ($11,807.05/kW-yr)** — below terrestrial Arm A's
$12,077.26/kW-yr on the remaining C3 duty. The credit is a hardcoded
assumed engineering input, not a market price: no buyer, no contract, and
no price discovery stand behind it. The net figure is therefore reported
strictly separately from unsubsidized C3 throughout this paper, and the
pure-C3 verdict (Section 3.4) does not use it. What Arm P shows is
conditional: *if* 18% of a spine's duty can be sold at $4,850/kW-yr for
work that can only be done in orbit, *then* the remaining general-AI duty
is roughly at terrestrial parity. The "if" is the whole claim, and it is
untested. Disposition: **LIMITED GO for orbit-advantaged dual-use
workloads only; NOT pure C3 parity.**

### 3.6 The SpaceX AI1 denominator audit (including the envelope instability)

SpaceX's product page states the Starmind AI1 envelope as 30 m × 75 m,
250 kW peak / 175 kW average, 75 kW/ton [4]. The audit is arithmetic, not a
measurement of SpaceX hardware:

- 250 kW peak / 75 kW per ton = 3,333.3 kg implied dry mass; 13.33 kg/kW
  on the peak denominator.
- The same 3,333.3 kg / 175 kW continuous average = **19.05 kg/kW**.
- The all-in continuous IT boundary is stated as an **assigned range,
  19.05–24.80 kg/kW** (wet propellant and replacement spares included at
  the top end). No code computes a point value inside that range.

Arm B, the modeled AI1 reference, is 18.08 kg/kW dry at 4 MW — between
the two denominators, and inside the assigned range. A figure withdrawn
from this study, "22.29 kg/kW modeled in Arm B," appears only as a
hardcoded string in an earlier falsification script; no code computes it
(D-002-3). Do not use it.

**Envelope instability — disclosed.** The public envelope is not stable
across hosts. On 24 Aug 2026, new.spacex.com served a *smaller* envelope
the same day: 150 kW peak / 120 kW average / 70 kW/ton / 20 m × 70 m. On
that envelope: 150 / 70 = 2,142.9 kg; / 120 kW average = **17.86 kg/kW**.
The 001 paper used yet another envelope, the 150 kW peak design from the
June 2026 SEC filing [11]. This paper uses the www envelope (250 kW) as
its primary basis and states the alternate (17.86 kg/kW continuous) here,
because the audit's conclusion depends on which envelope is in force:
on the www envelope the claimed 13.33 kg/kW is a peak-power figure and the
continuous figure is 19.05; on the smaller envelope the continuous figure
is 17.86. Either way, the 13.33 kg/kW number is not a continuous-average
specific mass, and any comparison that treats it as one is a denominator
error. Disposition: **HOLD for denominator verification.**

The Kessel 72-GPU Rubin rack is secondary reporting (mlq.ai / Tom's
Hardware, Nov 2026), attributed as reported, not confirmed [12].

### 3.7 Environmental ledger

20-year ledger per MW, at $500/kg launch (simulation prediction; factors
are assumed inputs except where noted):

| Arm | Black carbon (kg) | Al₂O₃ (kg) | CO₂e (t) |
|---|---|---|---|
| A Terrestrial | 0.0 | 0.0 | 1,420.0 |
| B AI1 (modeled) | 1,446.5 | 34,716.0 | 1,728.7 |
| C Suncatcher (modeled) | 1,927.9 | 46,270.8 | 2,077.8 |
| D Conventional | 2,023.0 | 48,552.0 | 2,146.7 |
| E Thin structural OHP | 1,540.7 | 36,975.6 | 1,797.0 |
| F Integrated tiles | 1,572.8 | 37,746.0 | 1,820.2 |
| G Repaired C6 | 1,652.9 | 39,669.6 | 1,878.4 |
| H Hot silicon | 1,513.9 | 36,333.6 | 1,777.6 |
| I Coplanar film | 2,777.4 | 66,658.8 | 2,693.7 |
| J Fluid-QDC cartridges | 861.7 | 20,679.6 | 1,304.7 |
| K Hull retrofit | 2,609.1 | 62,618.4 | 2,571.6 |
| L Federated constellation | 1,689.3 | 40,544.4 | 1,904.8 |
| M Null control | 3,131.5 | 75,157.2 | 2,950.4 |
| N Round 1 spine | 1,166.8 | 11,084.6 | 1,525.9 |
| O Round 2 spine | 568.6 | 2,558.7 | 1,092.2 |
| P Round 3 dual-use | 579.5 | 2,607.5 | 1,100.1 |

Arm O's ledger improves on Arm D because the reusable spine launches far
less mass over 20 years (113.72 t total, against Arm D's 404.6 t) and
because its assigned ablation fraction is 0.09 against the 0.48 default:
2,558.7 vs 48,552.0 kg/MW, **−94.7%**. Both halves of that improvement
carry caveats. The mass half is a model output; the fraction half is an
assigned input (D-002-11), and the fractions assume a large share of the
vehicle ablates as alumina — an upper-bound framing, where Ferreira et al.
model ~0.12 kg Al₂O₃ per kg of satellite [16]. Terrestrial Arm A launches nothing and ablates nothing, but its
1,420.0 t CO₂e is a fixed model input, not a computed grid mix. The
stratospheric radiative-forcing and ozone multiplier is UNKNOWN by design
(±300% spread): Revell et al. find alumina alone has little impact on
ozone in the quantities modeled, with chlorine from solid motors and black
carbon driving the loss [14], while Barker et al. report ~20 t of black
carbon per Falcon 9 launch [15] — on a per-launched-kg basis substantially
higher than this ledger's 0.020 kg/kg factor, so the ledger's black-carbon
figures should be read as a lower bound pending a propellant-based
accounting. **No independent environmental advantage is established:**
orbital computing avoids terrestrial land, water, and grid electricity and
adds stratospheric pollutants whose forcing is uncalibrated. That is the
ledger, not a verdict.

### 3.8 Excluded: the held-out stress case

A held-out, unfamiliar-configuration replay (an 8 MW, 53° LEO case run
through a separate internal engine) is **excluded from this paper**. It
carries no tournament science: it was produced by a separate evaluation
exercise, not by the tournament model, and its numbers cannot be checked
against the code in this package. Publishing them would ask the reader to
trust an engine they cannot run. The exclusion is deliberate and is stated
here so the absence is not mistaken for an oversight. The paper's claims
rest only on the tournament, the screen, and the falsification audit in
`simulation/`.

## 4. Discussion

### 4.1 What the Arm O result does and does not mean

Arm O is a genuine improvement inside the model: a 20-year reusable spine
with 3.75 kg/kW blades swapped every 5 years cuts 20-year orbital TCO by
36.7% against the conventional modular incumbent and by 33.4% against the
modeled AI1 reference, with the highest availability of any orbital arm
(0.9145) and the lowest failure rate (0.0348/yr). It does not mean orbital
computing is competitive for general AI. At $500/kg launch it is 1.239×
terrestrial; at $0/kg it is 1.169×. The mechanism that survives is reuse:
the expensive parts (solar, radiator, optical spine) are launched once,
and only the cheap, fast-depreciating part (compute) is refreshed. The
mechanism that does not survive is the hope that cheaper launch alone
closes the gap — it cannot, because launch is $15.37M of a $92.65M
non-silicon total per MW. The result is therefore a statement about
*where the money is*: in space hardware, servicing, and insurance, not in
the rocket. And the result is contingent on the untested dry-clamp
interface (Section 4.7): if blades cannot be hot-swapped in vacuum at the
modeled thermal resistance, Arm O reverts to Arm N economics or worse.

### 4.2 Why terrestrial wins general AI

The C3 result is not close and does not depend on the radiator. The
non-thermal spacecraft floor — PV, eclipse storage, bus, shielding, and
communications — plus launch, replenishment, insurance, and operations
makes even a zero-mass radiator more expensive per compute-year than
terrestrial clean-grid power. This is the Turyshev conclusion [1]
reproduced from inside the model: general AI belongs on Earth unless
launch becomes nearly free *and* the bus-mass floor collapses *and*
space-hardware costs fall by roughly half. At $100/kg the best orbital arm
is still 1.183× terrestrial. The negative result is the paper's most robust
finding, because it survives the most optimistic launch price in the sweep
and because it is driven by the cost structure, not by any single thermal
parameter. The one honest exception is dual-use work (Section 3.5), where
the data is already in orbit and the alternative is downlinking it all —
and even there the case rests on an assumed price.

### 4.3 How 001 and 002 differ (method reconciliation)

001 and 002 are different studies with different methods. Their absolute
$/kW-yr figures are **not comparable across studies**, and this section
states why, so no reader combines them.

| | 001 | 002 |
|---|---|---|
| Horizon | 5 yr | 20 yr |
| Launch baseline | $1,500/kg | $500/kg |
| Scales | 1 / 150 / 1,000 kW | 1 / 4 / 16 MW |
| Silicon accounting | Hardware $3,600/kW once; **no silicon refresh** | $45,000/kW-IT per 5-yr generation = $180M/MW over 20 yr |
| Terrestrial cost | $1,384.33/kW-yr | $12,077.26/kW-yr |
| Best orbital cost | $10,495.60/kW-yr (A10) | $14,960.66/kW-yr (Arm O) |
| Ratio (headline) | 9.72× on TFLOPS-yr/$ (A11/A10) | 1.239× on $/kW-yr (Arm O / Arm A) |
| Thermal headline | 60% coupled thermal-mass cut (A09 vs A04, 150 kW) | C6 falsified 11.93 → 19.44 kg/kW; Arm O 15.60 kg/kW |
| Scenes headline | 3.06× scenes/$ (A10 vs A11) | Arm P net only, on an assumed credit |

The absolute figures are 8.7× apart ($12,077.26 vs $1,384.33
terrestrial), driven by the silicon-refresh accounting: 001 charged
hardware once over 5 years, 002 charges four silicon generations over 20
years, and the $180M/MW silicon cost is common to both sides in 002. Only
within-study ratios are comparable, and even those use different metrics
(TFLOPS-yr/$ in 001, $/kW-yr in 002). The ratio shrank mainly because the
common $180M/MW silicon cost on both sides compresses any ratio toward
1.0; cheaper silicon would widen the ratio toward the non-silicon ratio
(1.931× at $0/kg). Also, 001's 60% thermal claim (A09 vs A04, 150 kW) and
3.06× scenes/$ claim are 001-only; 002 does not re-derive them. 002's Arm
E (19.26 kg/kW) is the descendant of 001's structural-OHP idea with
realistic PV; 002's Arm G is the repaired C6. The two studies agree on the
qualitative verdict — terrestrial wins general AI — and disagree on nothing
else that matters, because they do not measure the same thing.

### 4.4 The reference architectures are models, not products

Arms B and C exist in this paper as parameterized references. The
Suncatcher paper publishes no thermal design [3], so Arm C's thermal stack
is an assumption that could be wrong in either direction; the AI1 power
figures are a product-page snapshot that the vendor itself revises across
hosts (Section 3.6). Treating either arm as a company's measured
performance would be a category error, and the paper does not do so. The
leaderboard's meaningful comparisons are Arm O and Arm N against Arm D
(the incumbent control) and Arm A (the terrestrial control), all defined
inside the model. Likewise, Arms H, I, J, K, and M are preserved failures
and controls, not proposals: hot silicon cooks itself (effective failure
rate 0.35/yr, the model cap, against 0.046/yr for Arm E), the coplanar
film fights its own sunlight (16,037.6 m² of radiator, 34.72 kg/kW), the
fluid-QDC cartridges pay 38% servicing overhead and still cost more than
the dry-clamp spine, the hull retrofit carries retained inert mass, and
the null control shows the floor with no credits at all.

### 4.5 The BCG terrestrial-benchmark discrepancy (D-002-4)

Arm A, the model's terrestrial benchmark, costs **$220M/MW over 20 years
— below BCG's terrestrial range of $230–300M/MW** (BCG, Aug 2026,
verified live) [5]. The headline 1.239× ratio therefore depends on the
model's own terrestrial benchmark, which is more optimistic than BCG's.
Ratio sensitivity, holding Arm O at $272.65M/MW:

| Terrestrial benchmark | Arm O ratio |
|---|---|
| Model's own Arm A, $220M/MW | 1.239× |
| BCG low end, $230M/MW | 1.185× |
| BCG midpoint, $262M/MW | 1.04× |
| BCG high end, $300M/MW | 0.91× (orbital wins) |

At BCG's high end, the verdict flips. The paper's headline is the
model-internal ratio, and the sensitivity is printed alongside it so the
reader can see what the benchmark choice buys. Two further cautions: BCG's
orbital figure is $660–750M/MW at today's costs, not 002's modeled future
costs — do not present BCG as validating 002's absolutes; and BCG's own
outlook is ~1.5× realistic improvement and 1.1–1.2× aggressive, which is a
different claim from this study's 1.239× at modeled future costs. The
honest summary is that the orbital-vs-terrestrial gap for general AI is
somewhere between "orbital wins at BCG's pessimistic terrestrial end" and
"1.24× at the model's optimistic terrestrial end," and the model cannot
tell the reader which end is right.

### 4.6 Prior art and the narrow novelty claim for Arm O

Each element of Arm O exists separately. Structural oscillating-heat-pipe
panels were studied in 001 (A09/A10) and exist as vendor products
(ThermAvant structural OHP radiators [13]; ACT honeycomb radiator panels
with embedded heat pipes [19]). Deployable PV is flown (iROSA [9]).
Direct high-voltage DC distribution, dry thermal interfaces, and
hot-swappable modules are all established practice in terrestrial and
space systems. The novelty claim in this paper is therefore narrow and
explicit: **a 20-year reusable solar + OHP radiator + optical spine in
orbit, with only dry-clamped compute blades (3.75 kg/kW) swapped every 5
years, so that silicon refresh does not force replacement of the expensive
outer infrastructure**. No single prior art combines a long-life reusable
spine with a dry-clamp hot-swap blade interface as the refresh mechanism.
That is a combination claim, not an invention-of-the-elements claim, and it
is stated as such because the elements are all prior art. The claim is
also untested: the interface is a coupon design, not a flown mechanism,
and the operations burden the Turyshev follow-up documents (393–419
operations per MW-year [2]) is a standing challenge to the servicing model.

### 4.7 The falsification test

The single most important remaining test is a thermal-vacuum (TVAC)
coupon measurement of the **dry-clamp vacuum thermal interface** of the
Arm O hot-swap blade: pyrolytic graphite sheet (PGS) plus multi-spring
thermal interface material, dry-clamped, no fluid quick-disconnects. The
coupon is 160.0 × 120.0 × 8.8 mm, a 12-shell ISO-10303-21 AP214
MANIFOLD_SOLID_BREP STEP model (Euler V−E+F=2 on all shells, verified in
the test suite), with DXF/STL/SVG drawings in `cad_and_drawings/`. Figure 4
shows the coupon (top view and cross-section) with gates G1–G4. Gates:

- **G1** — dry mass ≤ 62% of an equal-footprint solid Al-6061-T6 plate at
  matched bending stiffness EI (±5%).
- **G2** — helium leak < 1×10⁻⁸ atm-cc/s at 1.5× maximum working pressure
  across 8 cellular OHP loops.
- **G3/G4** — dry-clamp vacuum thermal interface dT_clamp ≤ 1.8 K at
  1×10⁻⁵ Torr after 20 latch/unlatch cycles.
- **Reject Arm O and revert to Arm N if dT_clamp > 3.5 K.**

The coupon is non-energized only; energized testing is on hold pending
external PE/EHS signoff. The dT_clamp gate is the sharp one, because the
modeled Arm O advantage rests on the assumption that a dry clamp in vacuum
transfers heat at the modeled resistance across many mate/demate cycles.
If the coupon shows dT_clamp above 3.5 K, the reusable-spine economics
collapse regardless of the mass numbers. The microgravity oscillation
startup threshold from the 001 study remains a separate outstanding test
for the structural-OHP panel itself; 002 does not re-derive it.

## 5. Limitations

Labeled by category, as the results require.

**Demonstrated software behavior (executed, reproducible).** The tournament
reproduces deterministically; the 8-test suite passes in standard and `-O`
modes; the C6 waterfall, the 216-corner sweep, the crossover sweep, and the
AI1 audit reproduce from the shipped code; the STEP coupon verifies
(12 closed shells, Euler V−E+F=2 on every shell; STL bounding box
160.0 × 120.0 × 8.8 mm). The leaderboard, scaling, launch-count, crossover,
and environmental numbers in this paper are outputs of that code.

**Modeled engineering performance (computed, not measured).** All sixteen
architecture evaluations, the Arm O and Arm N figures, the cost figures,
the failure rates and availabilities, the launch counts, and the
environmental ledger. These depend on assigned inputs listed in Section
2.2 and on the assumptions in `simulation/README.md`. The nominal compute
density (22 TFLOPS/kW) is an assumed input; absolute TFLOPS-yr/$ scales
with it, ratios do not. The cost model is scale-invariant by assumption.
Starship volume bounds are computed from a preliminary 2020 guide, not a
certified interface. Arm O's hardware cost is modeled below the
conventional incumbent's on a per-m² basis, and its 20-year bus life is
assumed, not demonstrated.

**Untested hypotheses.** That a dry-clamped PGS/multi-spring interface
holds dT_clamp ≤ 1.8 K in vacuum after 20 mate/demate cycles; that a
20-year solar/radiator/optical spine survives micrometeoroids, radiation,
and thermal cycling with the modeled failure rate (0.019/yr base); that
servicing tugs can swap blades at 14% overhead; that 18% dual-use duty
can be sold at $4,850/kW-yr; that the 0.09 alumina ablation fraction for a
reusable spine is representative; that the F002 repair adders are the right
size (they are assumed, and the iROSA flysheet publishes no per-m² boom
mass to check them against). Each is falsifiable by the test in Section 4.7
or by measurement of the named input.

**What this paper does not claim.** No flight qualification, no measured
thermal performance, no cost certainty, no environmental impact assessment
(the radiative-forcing multiplier is UNKNOWN by design), no statement about
any company's actual hardware, and no market price for dual-use capacity.
An earlier version of this work contained stale tables and a withdrawn
figure; all are corrected or removed, and the full corrections log is in
`VERIFICATION.md` (D-002-1..D-002-12, plus additional findings D-002-13..
D-002-15).

## 6. Conclusion

A reusable thermal-structural spine can, in the model, cut orbital
20-year cost by 37% against the conventional orbital incumbent — and it
still does not make orbital data centers competitive for general AI. The
economics are decided by the bus, the servicing, and the insurance, not
the radiator and not the rocket: free launch leaves Arm O 1.169×
terrestrial. Orbital computing earns its place only where the data is
already in orbit and the work is worth paying for there, or where a
reusable spine's dual-use duty can be sold at an assumed price that no
market has yet confirmed. That is a smaller claim than the orbital
data-center pitch, and it is the one the numbers support. The next step is
not more simulation. It is a coupon in a vacuum chamber, clamped, latched,
and measured.

## References

[1] Turyshev, S. G., "Orbital Data Centers: Spacecraft Constraints and
Economic Viability", arXiv:2604.27197 (29 Apr 2026).
https://arxiv.org/abs/2604.27197

[2] Turyshev, S. G., follow-up on orbital data-center operations and
maintenance, arXiv:2608.27499 (2026). 393–419 standardized operations per
MW-year; 5.3–9.0 t/(MW-year) logistics.
https://arxiv.org/abs/2608.27499

[3] Agüera y Arcas, Beals et al. (Google), "Towards a future space-based,
highly scalable AI infrastructure system design" (Project Suncatcher),
2025; arXiv:2511.19468; Joule, 1 Oct 2026.
https://services.google.com/fh/files/misc/suncatcher_paper.pdf

[4] SpaceX, Starmind AI1 product page (www envelope: 250 kW peak /
175 kW average / 75 kW/ton / 30 m × 75 m).
https://www.spacex.com/spacexai/starmind

[5] BCG (Elbert, Werle, Nasr, O'Niell), "Space-Based Data Centers: Cost
and Outlook to 2040", 27 Aug 2026. 20-yr TCO $660–750M/MW orbital vs
$230–300M/MW terrestrial; 2.5–3× premium today, ~1.5× realistic
improvement, 1.1–1.2× aggressive.
https://www.bcg.com/publications/2026/space-based-data-centers-cost-outlook

[6] Gaalema, Indyk, Staley, "Reduced-Mass Orbital AI Inference via
Integrated Solar, Compute, and Radiator Panels", arXiv:2604.07760
(9 Apr 2026). Integrated solar/compute/radiator panels; claims
>100 kW/ton, 16 MW / 150 t, junction ~40 °C.
https://arxiv.org/abs/2604.07760

[7] ICEF, Sandalow et al., "Space-Based Data Centers Roadmap: The Case
for Caution", working paper, Nov 2026 (not peer-reviewed). 10% of 2030 AI
demand from orbit = 700+ Starship launches/yr in perpetuity; 50× satellite
increase; "weights claimed by leading developers appear highly optimistic
and beyond currently-proven technology."
https://icef.go.jp/wp-content/themes/icef_new/pdf/roadmap/2026/ICEF%20Space-Based%20Data%20Centers%20Roadmap%20Nov%202026.pdf

[8] SpaceX, Starship Users Guide Rev 1.0 (Mar 2020). 9 m outer diameter,
8 m dynamic envelope, extended volume up to 22 m height. The 665 m³
(standard) / 905 m³ (extended) volumes are computed from the guide's
dimensions, not guide-quoted figures. The guide is a 2020 preliminary
document; the volume bound is not a certified usable payload or interface.
https://spacex.relayto.com/e/starship-users-guide-37uiuuepbks0x/SDpUqC8k3

[9] NASA / Redwire, ISS Roll-Out Solar Array (iROSA) / ROSA: flown
(8 wings, ~28 kW each, composite booms).
https://www.nasa.gov/directorates/stmd/impact-story-roll-out-solar-arrays/

[10] U.S. Government Accountability Office, "Science & Tech Spotlight:
Data Centers in Space", GAO-26-109012 (April 2026).
https://www.gao.gov/products/gao-26-109012

[11] SpaceX, SEC Free Writing Prospectus (filed 9 Jun 2026, Reg. No.
333-296070), CFO interview and Musk/Dahl/Huot conversation. AI1 first
design: 150 kW peak / 120 kW sustained.
https://www.sec.gov/Archives/edgar/data/1181412/000162828026041761/fwp_cfointerview.htm

[12] mlq.ai / Tom's Hardware, Nov 2026 (secondary reporting, not
confirmed): Kessel 72-GPU Rubin rack for SpaceX AI1.
https://mlq.ai/news/spacex-is-designing-kessel-a-72-gpu-nvidia-rubin-rack-for-data-centers-in-space-report-says/

[13] ThermAvant Technologies, oscillating heat pipe product documentation
and catalogue. OHP heat spreaders, transporters, and heat sinks at TRL 9;
OHP satellite radiators at TRL 7; structural OHP panels at 1.6 g/cm³
effective density; first flight 2017 (ASETS-II, X-37B).
https://www.thermavant.com/oscillating-heat-pipes

[14] Revell, L. E. et al., "Near-future rocket launches could slow ozone
recovery", Communications Earth & Environment (2025).
https://pmc.ncbi.nlm.nih.gov/articles/PMC12148926/

[15] Barker, C., Marais, E. et al., "Radiative Forcing and Ozone
Depletion of a Decade of Satellite Megaconstellation Missions", Earth's
Future (2026), DOI 10.1029/2025EF007229. ~20 t black carbon per Falcon 9
launch; ~870 t black carbon/yr by 2029.

[16] Ferreira et al., re-entry alumina modelling, Geophysical Research
Letters (2024). ~0.12 kg Al₂O₃ per kg of satellite.

[17] Sharma, S. P., "Impact of Spaceflight on Earth's Atmosphere:
Climate, Ozone, and the Upper Atmosphere", NASA/TM−20240013276 (Oct 2024).
https://ntrs.nasa.gov/api/citations/20240013276/downloads/NASA-TM-20240013276-V6.pdf

[18] Presler, A. F., Coles, C. E., Diem-Kirsop, P., & White, K. A.,
"Liquid droplet radiator program at the NASA Lewis Research Center" (1985).
https://ntrs.nasa.gov/citations/19870035127

[19] JAXA SDS-4 / IHTC-17 2023 review, "Toward LEO Applications: The
Scientific Journey of the Space Pulsating Heat Pipe".
https://arxiv.org/pdf/2312.11055

[20] Advanced Cooling Technologies, honeycomb radiator panels; Beyond
Gravity, thermo-structural radiator panels (vendor catalogues). Nearest
prior art for structure + radiator + embedded heat pipe in one panel;
neither integrates an electrical power bus as a fourth function, and
neither uses an oscillating heat pipe as the primary-structure load path.

## Appendix A. Corrections log (summary)

An earlier version's text disagreed with its own executed code, and
the source material it was checked against contained stale figures. All are
corrected in this paper and in the code; the executed values win. The full
log with before/after values is in `VERIFICATION.md`. Headlines: the
held-out replay numbers are excluded entirely (stale, and from an engine
not in this package); the "22.29 kg/kW modeled in Arm B" figure is
withdrawn (no derivation in code); Arm O's non-silicon cost at $0/kg is
$4,240.42/kW-yr (1.931×), not $4,235.93 (1.929×); the $0.135/kWh
electricity parity threshold is withdrawn (direct evaluation disproves it;
the code now computes the breakeven: $0.3310/kWh at $500/kg launch,
$0.2541/kWh at $0/kg); the Arm H
"3.92× Arrhenius" figure is not reproduced by the code (executed
multiplier 8.51×, effective rate capped at 0.35/yr); the falsify script's
"5 assumptions" is corrected to 4 screen steps plus end-of-life
degradation in Arm G; the earlier version's C6, Arm N, and Arm O figures
are replaced with executed values wherever they differed; regenerated
figures are not byte-identical to earlier PNGs and are regenerated with
fixed labels.

## Appendix B. Reproduction

```sh
python3 -m venv .venv
.venv/bin/pip install -r simulation/requirements.txt
python3 simulation/run_reproduction.py
```

This regenerates the C6 falsification audit, the 16-arm tournament, the
corner sweep, the leaderboard CSV and evidence JSON, verifies
byte-determinism of the evidence across two runs, generates Figures 1–4
(via `simulation/generate_figures.py`, included in the tree — the script
fails loudly with a clear message if it is absent), verifies the TVAC coupon
CAD, runs the 8-test suite in standard and `-O` modes, and writes
`SHA256SUMS.txt` last. `PAPER.pdf` is a rendering of `PAPER.md` (WeasyPrint
70.0) with Figures 1–4 embedded at their callout points; the Markdown is
authoritative. Verified environment: Python 3.12.3, matplotlib 3.8.4, Pillow
10.2.0, numpy 1.26.4 (see `simulation/requirements.txt`).
