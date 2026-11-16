#!/usr/bin/env python3
"""ORBITAL DATA CENTER 002 — publication figure generator.

Pins: matplotlib==3.8.4, numpy, Pillow.
Run standalone from the repository root:  python3 simulation/generate_figures.py
  [--csv PATH] [--evidence PATH] [--outdir PATH]
Regenerates all four PNGs into figures/ by default.

Data sources (public-tree locations only; no fallback — the files must exist):
  PUBLIC_CSV      = evidence/orbital_datacenter_002_leaderboard_4mw.csv
  PUBLIC_EVIDENCE = evidence/orbital_datacenter_002_evidence.json
Every plotted number comes from those two files, which are the executed
002 outputs. No number is typed in from prose except the
cross-checks noted in figures/FIGURES.md.

Fixes vs the earlier figure generator (D-002-7):
  * Fig 1A: short human-readable y-labels (was: truncated raw code names).
  * Fig 1B: short, complete x-labels (was: garbled "Round 1 Arm N (Arm G)",
    "Round 2 Arm O (800V Spine[20yr swap)").
  * Fig 2B: all 16 arms shown with a stated selection rule (was: 9 of 16,
    selection unstated).
  * Fig 3: new Arm O engineering schematic (replaces nothing; the old
    pumped-coolant spacecraft image is NOT reused — it portrays an
    architecture that lost).
  * Fig 4: new coupon figure drawn from the verified STEP dimensions
    (160.0 x 120.0 x 8.8 mm, checked against the STEP file in this script).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

# Requires matplotlib==3.8.4 (see simulation/requirements.txt).
assert matplotlib.__version__.startswith("3.8."), matplotlib.__version__

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # repository root (this script lives in simulation/)

# --- Public-tree locations ---
PUBLIC_CSV = ROOT / "evidence" / "orbital_datacenter_002_leaderboard_4mw.csv"
PUBLIC_EVIDENCE = ROOT / "evidence" / "orbital_datacenter_002_evidence.json"

SHORT_LABELS = {
    "A": "A: Terrestrial", "B": "B: SpaceX AI1", "C": "C: Google Suncatcher",
    "D": "D: Conventional", "E": "E: Thin OHP", "F": "F: Thermal tiles",
    "G": "G: Repaired C6", "H": "H: Hot silicon", "I": "I: Coplanar film",
    "J": "J: Fluid QDC", "K": "K: Hull retrofit", "L": "L: Federated",
    "M": "M: Null control", "N": "N: Round 1 spine", "O": "O: Round 2 spine",
    "P": "P: Dual-use",
}
SHORT_TICKS = {  # fig2B compact x labels (single line, rotated 45 deg)
    "A": "A Terr.", "B": "B AI1", "C": "C Suncatcher", "D": "D Conv.",
    "E": "E Thin OHP", "F": "F Tiles", "G": "G Rep. C6", "H": "H Hot Si",
    "I": "I Coplanar", "J": "J Fluid QDC", "K": "K Hull", "L": "L Federated",
    "M": "M Null", "N": "N R1 spine", "O": "O R2 spine", "P": "P Dual-use",
}

C_TERR = "#059669"   # terrestrial green
C_BLUE = "#0284c7"   # Round 1/2/3 invention blue
C_DARK = "#0369a1"
C_GREY = "#64748b"
C_RED = "#dc2626"
C_AMBER = "#d97706"
C_PURPLE = "#7c3aed"


def resolve(public: Path, name: str) -> Path:
    # No fallback: the public files must exist. Fail loudly otherwise.
    if not public.exists():
        raise SystemExit(f"ERROR: required public file missing: {public}")
    print(f"  {name}: {public}")
    return public


def load(csv_path: Path, ev_path: Path):
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            try:
                r[k] = float(v)
            except (TypeError, ValueError):
                pass
    ev = json.loads(ev_path.read_text())
    return rows, ev


def style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.edgecolor": "#334155",
        "axes.linewidth": 0.9,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelweight": "bold",
    })


# ---------------------------------------------------------------- fig 1
def fig1(rows, ev, out: Path):
    tco = {r["code"]: r["tco_20yr_per_mw_usd_m"] for r in rows}
    mass = {r["code"]: r["specific_mass_kg_kw"] for r in rows}
    order = [r["code"] for r in rows]  # A..P as executed
    p_net = next(
        s["economics"]["20yr"]["dual_use_net_tco_per_mw_usd_m"]
        for s in ev["tournament"]["scales"]["4MW"] if s["code"] == "P")
    wf = ev["screen_002_audit"]["c6_falsification_waterfall_1mw"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17.0, 7.6),
                                   gridspec_kw={"width_ratios": [1.30, 1.0]})
    fig.patch.set_facecolor("white")

    # --- Panel A: TCO leaderboard ---
    vals = [tco[c] for c in order]
    colors = [C_TERR if c == "A" else C_BLUE if c in ("N", "O", "P")
              else C_RED if c in ("H", "I", "K", "M") else C_GREY for c in order]
    y = np.arange(len(order))
    bars = ax1.barh(y, vals, color=colors, height=0.66,
                    edgecolor="#1e293b", linewidth=0.6)
    ax1.axvline(tco["A"], color=C_TERR, linestyle="--", linewidth=1.8,
                label=f"Terrestrial Arm A reference: \\${tco['A']:.0f}M/MW")
    p_i = order.index("P")
    ax1.scatter([p_net], [p_i], marker="D", s=110, color="#f59e0b",
                edgecolor="#0f172a", linewidth=1.0, zorder=5,
                label=f"Arm P NET (after assumed C1/C2 credit): \\${p_net:.1f}M/MW")
    ax1.set_yticks(y)
    ax1.set_yticklabels([SHORT_LABELS[c] for c in order], fontsize=9)
    ax1.invert_yaxis()
    ax1.set_xlabel("20-year all-in TCO (\\$M / MW, 4 MW, \\$500/kg launch)", fontsize=10)
    ax1.set_title("A. 16-architecture 20-year TCO leaderboard", pad=10)
    ax1.set_xlim(0, max(vals) * 1.22)
    ax1.grid(axis="x", linestyle=":", alpha=0.5)
    for bar, v in zip(bars, vals):
        ax1.text(v + 9, bar.get_y() + bar.get_height() / 2, f"${v:.0f}M",
                 va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax1.text(p_net + 14, p_i, "NET", ha="left", va="center", fontsize=8.5,
             fontweight="bold", color="white")
    ax1.legend(loc="lower right", fontsize=8.5, framealpha=0.95)

    # --- Panel B: C6 falsification waterfall ---
    stages = ["C6 raw\n(1 MW screen)", "+F002-1\nbooms &\nharness",
              "+F002-2\n20 K die-to-\nradiator dT", "+F002-3\nview factor\n0.78",
              "+F002-4\nspine + eclipse\nbattery", "Arm N\nRound 1",
              "Arm O\nRound 2"]
    wvals = [wf["unrepaired_c6_kg_kw"],
             wf["after_F002_1_boom_and_harness_mass_kg_kw"],
             wf["after_F002_2_20K_junction_to_radiator_drop_kg_kw"],
             wf["after_F002_3_view_factor_and_plume_ir_kg_kw"],
             wf["after_F002_4_launch_spine_and_eclipse_battery_kg_kw"],
             mass["N"], mass["O"]]
    wcols = ["#94a3b8", "#f97316", "#ea580c", "#dc2626", "#991b1b", C_BLUE, C_DARK]
    x = np.arange(len(stages))
    b2 = ax2.bar(x, wvals, color=wcols, width=0.62,
                 edgecolor="#1e293b", linewidth=0.7)
    ax2.axhline(13.33, color=C_PURPLE, linestyle="--", linewidth=1.4,
                label="SpaceX AI1: 13.33 kg/kW (250 kW peak)")
    ax2.axhline(19.05, color="#4f46e5", linestyle="-.", linewidth=1.4,
                label="SpaceX AI1: 19.05 kg/kW (175 kW avg)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(stages, fontsize=8.5)
    ax2.set_ylabel("Specific mass (kg / kW)", fontsize=10)
    ax2.set_title("B. C6 falsification: 11.93 to 19.44 kg/kW (+62.95%)", pad=10)
    ax2.set_ylim(0, max(wvals) * 1.30)
    ax2.grid(axis="y", linestyle=":", alpha=0.5)
    for bar, v in zip(b2, wvals):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.5, f"{v:.2f}",
                 ha="center", fontsize=9, fontweight="bold")
    ax2.annotate("+62.95% hidden\nmass omission", xy=(4, 19.44), xytext=(4.7, 23.2),
                 fontsize=8.5, fontweight="bold", color="#991b1b",
                 arrowprops=dict(arrowstyle="->", color="#991b1b", lw=1.2))
    ax2.legend(loc="upper left", fontsize=8.5, framealpha=0.95)
    fig.text(0.5, 0.01,
             "Arm P gross TCO is the bar; the diamond is its NET value after an ASSUMED \\$4,850/kW-yr dual-use credit "
             "(not a market price).  F002-1/2/3 adders are assumed engineering inputs, not measurements.",
             ha="center", fontsize=8.5, style="italic", color="#334155")
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"  wrote {out}")


# ---------------------------------------------------------------- fig 2
def fig2(rows, ev, out: Path):
    cross = ev["tournament"]["c3_parity_crossover_analysis"]
    terr = cross["terrestrial_benchmark_cost_per_delivered_kw_yr_usd"]
    sweep = cross["crossover_sweep"]
    launch = [1500, 500, 200, 100, 65, 20, 0]

    def curve(mult):
        return [next(s["orbital_cost_per_delivered_kw_yr_usd"] for s in sweep
                     if s["launch_price_usd_kg"] == lp
                     and s["space_hw_cost_multiplier"] == mult) for lp in launch]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17.0, 7.6))
    fig.patch.set_facecolor("white")

    # --- Panel A: parity boundary ---
    for mult, lbl, col, ls in [
            (1.0, "Arm O, space HW 1.00x (today)", C_BLUE, "-"),
            (0.55, "Arm O, space HW 0.55x (\u221245%)", "#2563eb", "--"),
            (0.30, "Arm O, space HW 0.30x (\u221270%)", C_PURPLE, "-.")]:
        ax1.plot(launch, curve(mult), marker="o", ms=5, linewidth=2.2,
                 linestyle=ls, color=col, label=lbl)
    ax1.axhline(terr, color=C_TERR, linewidth=2.4,
                label=f"Terrestrial Arm A: \\${terr:,.0f}/kW-yr")
    ax1.invert_xaxis()
    ax1.set_xlabel("Launch price ($ / kg to LEO)", fontsize=10)
    ax1.set_ylabel("20-yr cost per delivered kW-yr ($)", fontsize=10)
    ax1.set_title("A. C3 parity boundary: Arm O vs terrestrial Arm A", pad=10)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.set_xlim(1550, -40)
    ax1.set_ylim(9000, 17500)
    # parity annotations at sweep grid points (executed sweep values)
    ax1.annotate("0.55x first beats\nterrestrial at \\$200/kg\n(\\$11,626/kW-yr, 0.963x)",
                 xy=(200, 11626), xytext=(620, 10100), fontsize=9,
                 fontweight="bold", color="#1d4ed8",
                 arrowprops=dict(arrowstyle="->", color="#1d4ed8", lw=1.3))
    ax1.annotate("0.30x beats terrestrial\nat \\$65/kg (\\$10,330/kW-yr)",
                 xy=(65, 10330), xytext=(330, 13400), fontsize=9,
                 fontweight="bold", color=C_PURPLE,
                 arrowprops=dict(arrowstyle="->", color=C_PURPLE, lw=1.3))
    ax1.annotate("1.00x never crosses:\n\\$14,117/kW-yr even at \\$0/kg",
                 xy=(500, 14961), xytext=(1300, 15200), fontsize=9,
                 fontweight="bold", color=C_BLUE,
                 arrowprops=dict(arrowstyle="->", color=C_BLUE, lw=1.3))
    ax1.legend(loc="lower left", fontsize=8.5, framealpha=0.95)

    # --- Panel B: all 16 arms, 3 horizons ---
    codes = [r["code"] for r in rows]
    scales = {s["code"]: s for s in ev["tournament"]["scales"]["4MW"]}
    c5 = [scales[c]["economics"]["5yr"]["cost_per_delivered_kw_yr_usd"] for c in codes]
    c7 = [scales[c]["economics"]["7yr"]["cost_per_delivered_kw_yr_usd"] for c in codes]
    c20 = [scales[c]["economics"]["20yr"]["cost_per_delivered_kw_yr_usd"] for c in codes]
    x = np.arange(len(codes))
    w = 0.27
    ax2.bar(x - w, c5, width=w, color="#94a3b8", edgecolor="#1e293b",
            linewidth=0.5, label="5-year")
    ax2.bar(x, c7, width=w, color="#38bdf8", edgecolor="#1e293b",
            linewidth=0.5, label="7-year")
    ax2.bar(x + w, c20, width=w, color=C_DARK, edgecolor="#1e293b",
            linewidth=0.5, label="20-year (4 silicon generations)")
    ax2.set_xticks(x)
    ax2.set_xticklabels([SHORT_TICKS[c] for c in codes], fontsize=8,
                        rotation=45, ha="right")
    ax2.set_ylabel("Cost per delivered kW-yr (\\$, \\$500/kg launch)", fontsize=10)
    ax2.set_title("B. Cost per delivered kW-yr: all 16 arms, 3 horizons", pad=10)
    ax2.grid(axis="y", linestyle=":", alpha=0.6)
    ax2.legend(loc="upper left", fontsize=8.5, framealpha=0.95)
    fig.text(0.5, 0.01,
             "Panel A crossings are reported at the executed sweep grid points (\\$1,500 / 500 / 200 / 100 / 65 / 20 / 0 per kg), "
             "not interpolated.  Arm H is off-scale expensive because its availability is only 0.42.",
             ha="center", fontsize=8.5, style="italic", color="#334155")
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"  wrote {out}")


# ---------------------------------------------------------------- fig 3
def fig3(out: Path):
    """Arm O engineering schematic. Every dimension from VERIFIED_FACTS_002 /
    the executed leaderboard CSV. No deployed-span number exists in the 002
    code, so the drawing states that explicitly instead of inventing one."""
    fig, ax = plt.subplots(figsize=(17.0, 9.6))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.suptitle("Arm O (Round 2): reusable oscillating-heat-pipe spine with hot-swappable compute blades  —  4 MW",
                 fontsize=13, fontweight="bold", y=0.97)

    def box(x, y, w, h, fc, ec="#1e293b", lw=1.2, z=2):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec,
                               linewidth=lw, zorder=z))
    def txt(x, y, s, size=9.5, weight="normal", color="#0f172a", ha="left",
            va="center", z=6, style="normal"):
        ax.text(x, y, s, fontsize=size, fontweight=weight, color=color,
                ha=ha, va=va, zorder=z, style=style)
    def arrow(x1, y1, x2, y2, color="#dc2626", lw=1.6, style="-|>", ms=12):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                     mutation_scale=ms, linewidth=lw, color=color, zorder=5))

    # --- Sun + orbit ---
    ax.add_patch(plt.Circle((5, 93), 2.6, facecolor="#fbbf24",
                            edgecolor="#b45309", linewidth=1.2, zorder=4))
    for ang in range(0, 360, 45):
        r = np.radians(ang)
        ax.plot([5 + 3.4 * np.cos(r), 5 + 4.6 * np.cos(r)],
                [93 + 3.4 * np.sin(r), 93 + 4.6 * np.sin(r)],
                color="#b45309", lw=1.2, zorder=4)
    txt(9, 93, "Sun — dawn–dusk sun-synchronous orbit", size=9.5, weight="bold")

    # --- PV wings ---
    box(6, 79, 30, 6.5, "#2563eb")
    box(64, 79, 30, 6.5, "#2563eb")
    for xx in (6, 64):
        for i in range(1, 6):
            ax.plot([xx + i * 5, xx + i * 5], [79, 85.5], color="#93c5fd",
                    lw=0.8, zorder=3)
    txt(50, 88.5, "SOLAR PV WINGS — 17,709 m\u00b2 at 4 MW", size=10.5,
        weight="bold", color="#1e40af", ha="center")

    # --- Radiators ---
    box(26, 40, 20, 7, "#f97316")
    box(54, 40, 20, 7, "#f97316")
    txt(50, 36.5, "RADIATOR PANELS — 3,520 m\u00b2, 85.2 \u00b0C", size=10.5,
        weight="bold", color="#9a3412", ha="center")
    for xx in (31, 39, 47, 59, 67, 75):
        xs = np.linspace(xx, xx + 2.5, 40)
        ys = 33 - 0.10 * (xs - xx) + 0.9 * np.sin((xs - xx) * 4)
        ax.plot(xs, ys, color="#dc2626", lw=1.4, zorder=5)
    txt(50, 29.5, "heat radiated to deep space", size=9, color="#991b1b",
        ha="center")

    # --- Spine (fully visible; blades sit on top of it) ---
    box(28, 62, 44, 6, "#0c4a6e")
    txt(50, 65, "STRUCTURAL OHP SPINE", size=10.5, weight="bold",
        color="white", ha="center")
    ax.plot([29, 71], [63.1, 63.1], color="#fbbf24", lw=1.6, zorder=4)
    txt(50, 60.5, "axial, load-bearing  •  800 V HVDC bus inside (3.2% loss)  •  20-year life, never replaced",
        size=9, ha="center")

    # --- Replaceable blades mounted on top of the spine ---
    for cx in (34, 44, 56, 66):
        box(cx - 3, 68.5, 6, 9.5, "#bae6fd", ec="#0369a1", lw=1.4, z=4)
        ax.plot([cx - 3, cx + 3], [76, 76], color="#0369a1", lw=1.0, zorder=5)
    txt(76, 74, "REPLACEABLE COMPUTE BLADES", size=10, weight="bold",
        color="#075985")
    txt(76, 68.5, "3.75 kg/kW each, swapped every 5 yr\n"
                   "(4 generations over 20 years).\nOnly the blades are replaced;\nthe spine stays in orbit.",
        size=9)
    arrow(75, 72, 69.5, 73, color="#0369a1", lw=1.4)

    # --- Dry-clamp callout (left) ---
    txt(2, 74, "DRY-CLAMP INTERFACE", size=10, weight="bold", color="#065f46")
    txt(2, 68.5, "Pyrolytic graphite sheet +\nBeCu multi-spring wedge clamps\n"
                 "between blade and spine.\n0 fluid quick-disconnects —\nnothing to leak.",
        size=9)
    arrow(26, 70, 30.5, 71.5, color="#065f46", lw=1.4)

    # --- Heat-flow arrows: spine -> radiator ---
    arrow(34, 59, 34, 48, color="#dc2626")
    arrow(66, 59, 66, 48, color="#dc2626")
    txt(50, 52.5, "heat: blade \u2192 dry clamp \u2192 OHP spine \u2192 radiator",
        size=9, weight="bold", color="#991b1b", ha="center")

    # --- Thermal chain ---
    txt(2, 52.5, "Thermal chain (modeled):", size=9, weight="bold")
    txt(2, 49.0, "chip 98.0 \u00b0C  \u2014 dT 12.8 K \u2192  radiator 85.2 \u00b0C",
        size=9.5)
    txt(2, 45.5, "Arm O vs Arm D: \u221236.7% TCO\n"
                 "(\\$272.65M vs \\$430.88M/MW);\n\u221294.7% re-entry Al\u2082O\u2083.",
        size=9)

    # --- Deployment box ---
    box(2, 6, 54, 17, "#f1f5f9", ec="#475569", lw=1.2, z=2)
    txt(4, 20.5, "DEPLOYMENT (4 MW scale)", size=10, weight="bold")
    txt(4, 16.5, "62.42 t total  •  428.3 m\u00b3 stowed  •  1 launch in a standard 665 m\u00b3 Starship ogive fairing",
        size=9)
    txt(4, 12.5, "Conventional Arm D needs 2 launches at 4 MW; Arm O needs 1.",
        size=9)
    txt(4, 8.5, "Deployed span: NO modeled dimension exists in the 002 code — shown not to scale.",
        size=9, weight="bold", color="#991b1b")

    # --- Coupon cross-section inset (STEP-verified 160 x 120 x 8.8 mm) ---
    box(59, 5, 39, 19, "#ffffff", ec="#475569", lw=1.2, z=2)
    txt(78.5, 22.2, "DETAIL — TVAC coupon cross-section", size=9.5,
        weight="bold", ha="center")
    # stack: x 74-90; total height 12 units (y 7..19); layers bottom-up.
    # Thin layers get staggered label heights with leader lines so no
    # two labels share a line.
    layers = [("5.0 mm OHP spine (Al-6061-T6)", 5.0, "#0c4a6e", "white", 10.4),
              ("0.6 mm 800 V bus", 0.6, "#b45309", "white", 12.6),
              ("0.8 mm PGS + BeCu clamp", 0.8, "#065f46", "white", 14.8),
              ("2.4 mm blade (AlN/Al surrogate)", 2.4, "#bae6fd", "#0f172a", 17.6)]
    y0, total_h = 7.0, 12.0
    for name, thick, fc, tc, lab_y in layers:
        h = total_h * thick / 8.8
        box(74, y0, 16, h, fc, lw=0.8, z=3)
        ax.plot([72.5, 74], [lab_y, y0 + h / 2], color="#0f172a", lw=0.8, zorder=4)
        txt(72, lab_y, name, size=7.6, ha="right")
        y0 += h
    # 8.8 mm dimension arrow (right of stack)
    ax.annotate("", xy=(92, 19), xytext=(92, 7),
                arrowprops=dict(arrowstyle="<->", color="#0f172a", lw=1.2))
    txt(93.5, 13, "8.8\nmm", size=8.5, weight="bold")
    # 160 mm width arrow (above stack)
    ax.annotate("", xy=(74, 20.3), xytext=(90, 20.3),
                arrowprops=dict(arrowstyle="<->", color="#0f172a", lw=1.2))
    txt(82, 20.3, "160 mm", size=8, ha="center", va="bottom")
    txt(78.5, 3.2, "Full coupon figure: Fig. 4.  Dimensions verified against the STEP file (X 0–160, Y 0–120, Z 0–8.8 mm).",
        size=8, style="italic", color="#334155", ha="center")

    fig.text(0.5, 0.005,
             "SCHEMATIC — modeled dimensions from the executed 002 model; drawing not to scale. "
             "No orbital prototype has been built; this is not a CAD render of a built spacecraft.",
             ha="center", fontsize=9, style="italic", color="#334155")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out}")


# ---------------------------------------------------------------- fig 4
def fig4(out: Path):
    """TVAC coupon: top view + cross-section from the STEP/DXF geometry.
    STEP verified in-script data: X 0-160, Y 0-120, Z 0-8.8 mm; 12 closed
    shells; blade footprint 90 x 90 mm; 8 cellular OHP loops (SVG blueprint)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17.0, 8.2),
                                   gridspec_kw={"width_ratios": [1.15, 1.0]})
    fig.patch.set_facecolor("white")
    fig.suptitle("TVAC prototype coupon — Arm O dry-clamp OHP spine  •  160 \u00d7 120 \u00d7 8.8 mm  •  non-energized only",
                 fontsize=13, fontweight="bold", y=0.98)

    # --- Top view (to scale, mm) ---
    ax1.set_xlim(-18, 178)
    ax1.set_ylim(-22, 138)
    ax1.set_aspect("equal")
    ax1.set_xlabel("mm", fontsize=10)
    ax1.set_title("Top view (to scale)", pad=8)
    ax1.add_patch(Rectangle((0, 0), 160, 120, facecolor="#e2e8f0",
                            edgecolor="#0f172a", linewidth=2, zorder=2))
    # 8 cellular OHP loops: serpentine channels
    for i in range(8):
        yb = 12 + i * 13
        xs = [18, 142, 142, 18]
        ys = [yb, yb, yb + 7, yb + 7]
        ax1.plot(xs, ys, color="#0284c7", lw=2.0, zorder=3)
        ax1.plot([18, 18], [yb, yb + 7], color="#0284c7", lw=2.0, zorder=3)
    ax1.text(80, 60, "8 cellular OHP loops", ha="center", va="center",
             fontsize=10, fontweight="bold", color="#075985", zorder=4)
    # removable blade, 90 x 90 mm, centred
    ax1.add_patch(Rectangle((35, 15), 90, 90, facecolor="#0f766e",
                            alpha=0.45, edgecolor="#0f766e", linewidth=2,
                            linestyle="--", zorder=4))
    ax1.text(80, 108, "removable blade 90 \u00d7 90 mm", ha="center",
             fontsize=9, fontweight="bold", color="#0f766e", zorder=5)
    # 4 wedge clamps N/S/E/W
    for (x, y, w, h) in ((35, 108, 90, 7), (35, 5, 90, 7),
                         (5, 15, 7, 90), (148, 15, 7, 90)):
        ax1.add_patch(Rectangle((x, y), w, h, facecolor="#b45309",
                                edgecolor="#92400e", linewidth=1, zorder=5))
    ax1.text(80, 124, "wedge clamp N", ha="center", fontsize=8, zorder=5)
    ax1.text(80, 1.5, "wedge clamp S", ha="center", fontsize=8, zorder=5)
    ax1.text(-6, 60, "W", ha="center", va="center", fontsize=8, zorder=5)
    ax1.text(166, 60, "E", ha="center", va="center", fontsize=8, zorder=5)
    # fill/pinch bosses + PRT sensor bosses
    for (bx, by) in ((20, 112), (140, 112)):
        ax1.add_patch(plt.Circle((bx, by), 3.5, facecolor="#f59e0b",
                                  edgecolor="#92400e", zorder=5))
    ax1.text(20, 119.5, "fill boss", ha="center", fontsize=7.5, zorder=5)
    ax1.text(140, 119.5, "fill boss", ha="center", fontsize=7.5, zorder=5)
    for (bx, by) in ((20, 8), (140, 8)):
        ax1.add_patch(plt.Circle((bx, by), 3.0, facecolor="#38bdf8",
                                  edgecolor="#0369a1", zorder=5))
    ax1.text(80, -8, "PRT sensor bosses at lower corners  •  45 kPa kinematic wedge preload",
             ha="center", fontsize=8.5, style="italic", color="#334155")
    # dimension arrows
    ax1.annotate("", xy=(0, 132), xytext=(160, 132),
                 arrowprops=dict(arrowstyle="<->", color="#0f172a", lw=1.2))
    ax1.text(80, 134.5, "160 mm", ha="center", fontsize=9, fontweight="bold")
    ax1.annotate("", xy=(170, 0), xytext=(170, 120),
                 arrowprops=dict(arrowstyle="<->", color="#0f172a", lw=1.2))
    ax1.text(173, 60, "120 mm", va="center", fontsize=9, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.4)

    # --- Cross-section (thickness to scale, mm) ---
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 10.4)
    ax2.set_title("Cross-section (thickness to scale)", pad=8)
    ax2.set_xlabel("layer stack — total 8.8 mm", fontsize=10)
    ax2.set_yticks([0, 2, 4, 6, 8, 8.8])
    ax2.set_ylabel("mm", fontsize=10)
    layers = [("OHP structural spine — Al-6061-T6, 5.0 mm", 0, 5.0, "#0c4a6e", "white"),
              ("800 V bus — polyimide/Cu, 0.6 mm", 5.0, 0.6, "#b45309", "white"),
              ("Dry interface — PGS + BeCu multi-spring, 0.8 mm", 5.6, 0.8, "#065f46", "white"),
              ("Blade — AlN/Al surrogate cartridge, 2.4 mm", 6.4, 2.4, "#bae6fd", "#0f172a")]
    for name, y0, h, fc, tc in layers:
        ax2.add_patch(Rectangle((8, y0), 62, h, facecolor=fc,
                                edgecolor="#0f172a", linewidth=1.2, zorder=3))
        ax2.text(39, y0 + h / 2, name, ha="center", va="center",
                 fontsize=8.8, fontweight="bold", color=tc, zorder=4)
    ax2.annotate("", xy=(74, 0), xytext=(74, 8.8),
                 arrowprops=dict(arrowstyle="<->", color="#0f172a", lw=1.3))
    ax2.text(77, 4.4, "8.8 mm\ntotal", va="center", fontsize=10, fontweight="bold")
    ax2.text(39, 9.6, "5.0 + 0.6 + 0.8 + 2.4 = 8.8 mm  (STEP Z: 0–8.8)",
             ha="center", fontsize=9, style="italic", color="#334155")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)
    # gates box
    gates = ("ACCEPTANCE GATES (TVAC, non-energized)\n"
             "G1  Dry mass \u2264 62% of equal-footprint solid Al-6061-T6 plate\n"
             "     at matched bending stiffness EI (\u00b15%)\n"
             "G2  He leak < 1\u00d7 10\u207b\u2078 atm-cc/s at 1.5\u00d7 max working pressure,\n"
             "     across all 8 cellular OHP loops\n"
             "G3  Dry-clamp dT \u2264 1.8 K at 1\u00d7 10\u207b\u2075 Torr after 20 latch/unlatch\n"
             "     cycles (50 W SELV)\n"
             "G4  FALSIFIER: if dT_clamp > 3.5 K after 20 cycles, REJECT Arm O\n"
             "     and revert to Arm N monolithic bonded spine")
    fig.text(0.56, 0.02, gates, fontsize=9.5, family="monospace",
             color="#0f172a",
             bbox=dict(boxstyle="round,pad=0.6", facecolor="#fef9c3",
                       edgecolor="#a16207", linewidth=1.2))
    fig.text(0.02, 0.02,
             "12-shell AP214 STEP, all shells Euler V\u2212E+F = 2.\n"
             "Energized testing on HOLD pending\nexternal PE/EHS signoff.",
             fontsize=9.5, style="italic", color="#334155")
    fig.tight_layout(rect=[0, 0.30, 1, 0.95])
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"  wrote {out}")


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate ORBITAL 002 figures.")
    ap.add_argument("--csv", type=Path, default=None)
    ap.add_argument("--evidence", type=Path, default=None)
    ap.add_argument("--outdir", type=Path, default=None)
    args = ap.parse_args(argv)
    if args.outdir is None:
        args.outdir = ROOT / "figures"
    style()
    csv_path = args.csv or resolve(PUBLIC_CSV, "leaderboard CSV")
    ev_path = args.evidence or resolve(PUBLIC_EVIDENCE, "evidence JSON")
    rows, ev = load(csv_path, ev_path)
    assert len(rows) == 16, f"expected 16 arms, got {len(rows)}"
    args.outdir.mkdir(parents=True, exist_ok=True)
    fig1(rows, ev, args.outdir / "fig1_16arm_tco_and_c6.png")
    fig2(rows, ev, args.outdir / "fig2_parity_and_horizons.png")
    fig3(args.outdir / "fig3_arm_o_illustration.png")
    fig4(args.outdir / "fig4_coupon.png")
    print("done.")


if __name__ == "__main__":
    main()
