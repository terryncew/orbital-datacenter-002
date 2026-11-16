# ORBITAL DATA CENTER 002 — Figures

Generator: `simulation/generate_figures.py` (matplotlib==3.8.4, numpy, Pillow;
see `simulation/requirements.txt`). Run `python3 simulation/generate_figures.py`
from the repository root to regenerate all four PNGs into `figures/`. Data are
read from the executed outputs — the leaderboard CSV and the evidence JSON —
via the `PUBLIC_CSV` / `PUBLIC_EVIDENCE` constants pointing at
`evidence/orbital_datacenter_002_leaderboard_4mw.csv` and
`evidence/orbital_datacenter_002_evidence.json`. No plotted number is typed
from report prose. All four PNGs were viewed rendered and fixed until no label
was truncated or overlapped, at full width and at 700 px wide.

## Fig. 1 — `fig1_16arm_tco_and_c6.png`

(A) 20-year all-in TCO leaderboard for all 16 arms at 4 MW and $500/kg
launch, from `evidence/orbital_datacenter_002_leaderboard_4mw.csv`
(`tco_20yr_per_mw_usd_m`): A $220M, B $409M, C $419M, D $431M, E $394M,
F $414M, G $478M, H $695M, I $551M, J $316M, K $478M, L $429M, M $489M,
N $358M, O $273M, P $273M per MW. Terrestrial Arm A is the dashed green
reference line. Arm P's NET value ($176.4M/MW, from
`evidence/orbital_datacenter_002_evidence.json`,
`tournament.scales.4MW[P].economics.20yr.dual_use_net_tco_per_mw_usd_m`) is
a diamond marker on the P row, not a second bar. (B) C6 falsification
waterfall from the evidence JSON `screen_002_audit.c6_falsification_waterfall_1mw`
(11.93 → 15.20 → 15.71 → 16.34 → 19.44 kg/kW, +62.95%), with Arm N
14.58 and Arm O 15.60 kg/kW from the leaderboard for recovery context, and
the SpaceX AI1 reference lines 13.33 kg/kW (250 kW peak) and 19.05 kg/kW
(175 kW avg).

Fixed vs the earlier figure generator (D-002-7): panel A now uses
short human-readable y-labels ("A: Terrestrial", "B: SpaceX AI1", …) instead
of the truncated raw code names; panel B x-labels are short and
complete ("Arm N / Round 1", "Arm O / Round 2") instead of the garbled
"Round 1 Arm N (Arm G)" / "Round 2 Arm O (800V Spine[20yr swap)".
Also fixed a rendering defect the original shared: literal `$` signs were
being swallowed by matplotlib mathtext (e.g. "$500/kg" vanished from axis
labels); all `$` are now escaped.

## Fig. 2 — `fig2_parity_and_horizons.png`

(A) C3 parity boundary: Arm O 20-yr cost per delivered kW-yr vs launch price
($1,500 → $0/kg) at space-hardware multipliers 1.00x, 0.55x, 0.30x, from the
evidence JSON `tournament.c3_parity_crossover_analysis.crossover_sweep`
(all seven grid points per curve), against the terrestrial Arm A line
$12,077.26/kW-yr. Parity annotations follow the executed sweep at grid
points, not interpolation: 0.55x first beats terrestrial at $200/kg
($11,626.24/kW-yr, 0.963x); 0.30x beats terrestrial at $65/kg
($10,329.94/kW-yr, 0.855x); 1.00x never crosses ($14,117.33/kW-yr even at
$0/kg). (B) 5-yr vs 7-yr vs 20-yr cost per delivered kW-yr for ALL 16 arms,
from `tournament.scales.4MW[*].economics.{5yr,7yr,20yr}.cost_per_delivered_kw_yr_usd`
(e.g. Arm O $14,906.87 / $14,914.03 / $14,960.66; Arm H $83,397 / $83,733 /
$85,950, off-scale because its availability is only 0.42).

Fixed vs the original: panel B shows all 16 arms with rotated short labels
instead of 9 of 16 with no stated selection (D-002-7). Same `$`-escaping fix
as Fig. 1.

## Fig. 3 — `fig3_arm_o_illustration.png`

New engineering schematic of Arm O (labeled diagram, not a render; the old
pumped-coolant spacecraft image was not reused — it portrays an architecture
that lost). Every dimension is from the executed model and leaderboard:
structural OHP spine, axial and load-bearing, with the 800 V HVDC bus inside
(3.2% conversion loss — verified for Arm O itself in the shipped tournament
code, `elec_conv_loss_frac=0.032` in the Arm O spec); replaceable compute blades, 3.75 kg/kW, swapped every 5 years
(4 generations over 20 years) while the spine is retained; dry-clamp
interface of pyrolytic graphite sheet + BeCu multi-spring wedge clamps,
0 fluid QDCs; radiator panels 3,520 m² at 85.2 °C; solar PV wings 17,709 m²
at 4 MW in dawn–dusk sun-synchronous orbit; thermal chain chip 98.0 °C,
dT 12.8 K, radiator 85.2 °C; deployment 62.42 t, 428.3 m³ stowed, 1 launch
in a standard 665 m³ Starship ogive fairing (Arm D needs 2); heat-flow path
blade → dry clamp → OHP spine → radiator → deep space. The detail inset is
the TVAC coupon cross-section (see Fig. 4). Captioned as a schematic with
modeled dimensions, not a CAD render of a built spacecraft.

Unverifiable dimension (exact gap): no deployed-span dimension exists
anywhere in the shipped code or evidence JSON — the figure states
this explicitly on the diagram ("Deployed span: NO modeled dimension exists
in the 002 code — shown not to scale") rather than inventing a span.

## Fig. 4 — `fig4_coupon.png`

The TVAC prototype coupon, drawn from the shipped CAD in
`cad_and_drawings/`. Top view to scale (160 × 120 mm) with the 8
cellular OHP loops, the removable 90 × 90 mm blade, the four N/S/E/W wedge
clamps, the two OHP fill/pinch bosses and the two PRT sensor bosses, and the
45 kPa kinematic wedge preload; cross-section with layer thicknesses to
scale (5.0 mm Al-6061-T6 OHP spine + 0.6 mm polyimide/Cu 800 V bus +
0.8 mm PGS + BeCu dry interface + 2.4 mm AlN/Al surrogate blade = 8.8 mm).
Acceptance gates beside it: G1 dry mass ≤ 62% of an equal-footprint solid
Al-6061-T6 plate at matched bending stiffness EI (±5%); G2 He leak
< 1×10⁻⁸ atm-cc/s at 1.5× max working pressure across all 8 loops;
G3 dry-clamp dT ≤ 1.8 K at 1×10⁻⁵ Torr after 20 latch/unlatch cycles
(50 W SELV); G4 falsifier — if dT_clamp > 3.5 K after 20 cycles, REJECT
Arm O and revert to Arm N. Non-energized only; energized testing on HOLD
pending external PE/EHS signoff.

Dimensions verified against the STEP file before drawing: all 96
CARTESIAN_POINTs span X 0–160.0, Y 0–120.0, Z 0–8.8 mm; 12 closed shells,
all Euler V−E+F = 2; layer thicknesses and the 90 × 90 mm blade footprint
match the blueprint SVG text. The layer stack sums exactly to the STEP
Z-extent (5.0 + 0.6 + 0.8 + 2.4 = 8.8 mm).
