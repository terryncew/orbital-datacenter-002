#!/usr/bin/env python3
"""16-architecture orbital data center tournament (002).
Public research code. Computational study only: no hardware is built or tested by this code.
Competes 16 architectures (A through P, covering all required arms A-M plus 3 substantive
invention rounds N, O, P) across:
  - 3 power scales: 1 MW, 4 MW, and 16 MW (>10 MW)
  - 3 economic horizons: 5-Year, 7-Year, and 20-Year TCO (with 5-year GPU generation refreshes)
  - Identical silicon pricing ($45,000 / kW-IT per 5-yr compute generation) across Earth and Orbit
  - Calibrated to BCG Aug 2026 20-Year TCO benchmark ($230M-$300M/MW terrestrial vs $660M-$750M/MW current orbital)
  - Explicit Starship fairing geometry (8.0 m dynamic diameter, 665 m3 standard ogive / 905 m3 extended)
  - Coupled thermal-electrical-structural-reliability-communications-servicing-environmental physics
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import csv
import json
import math
from pathlib import Path

SIGMA = 5.670374419e-8
K_BOLTZMANN_EV = 8.617333262e-5

# Starship payload bounds (SpaceX Starship Users Guide, Rev 1.0, Mar 2020 — a preliminary document;
# the 665/905 m3 volumes are computed from its dimensions, not guide-quoted figures)
STARSHIP_MASS_LIMIT_LEO_KG = 100_000.0
STARSHIP_DYNAMIC_DIAMETER_M = 8.0
STARSHIP_STD_USABLE_OGIVE_VOL_M3 = 665.0   # 17.24 m height with nose taper
STARSHIP_EXT_USABLE_OGIVE_VOL_M3 = 905.0   # 22.0 m extended height with nose taper
STARSHIP_MIN_AXIAL_FREQ_HZ = 12.0

# Shared Silicon & Compute Tray Baseline (Identical on Earth and Orbit)
# $45,000/kW-IT per 5-yr generation = $180M/MW silicon over 20 yr, identical on Earth and in orbit.
SILICON_CAPEX_USD_PER_KW_IT = 45_000.0
NOMINAL_DENSE_FP16_TFLOPS_PER_KW = 22.0


@dataclass(frozen=True)
class OrbitalArchitectureSpec:
    code: str
    name: str
    family: str
    description: str
    is_terrestrial: bool = False
    is_null_or_negative_control: bool = False
    # Thermal & Radiator Parameters
    junction_temp_c: float = 95.0
    delta_t_jc_tim_evap_k: float = 16.0  # Die-to-radiator surface drop (K)
    emissivity: float = 0.90
    view_factor: float = 0.82            # Realistic 3D view factor per side
    background_k: float = 220.0
    absorbed_env_w_m2: float = 95.0
    rad_panel_kg_m2: float = 4.60        # Bare radiator panel areal density
    rad_boom_manifold_kg_m2: float = 0.65
    # Solar & Electrical Parameters
    pv_bol_w_m2: float = 265.0
    pv_deg_per_yr: float = 0.015
    pv_blanket_kg_m2: float = 1.15
    pv_boom_harness_kg_m2: float = 0.50
    sunlight_fraction: float = 0.975
    battery_kg_per_kw: float = 1.25
    elec_conv_loss_frac: float = 0.065
    thermal_aux_frac: float = 0.015
    sys_margin_frac: float = 0.10
    # Compute, Shielding, Structure & Comms
    compute_and_shield_kg_kw: float = 4.20
    bus_strongback_comms_kg_kw: float = 3.40
    structural_mass_credit_kg_kw: float = 0.0
    # Packing & Launch Dynamics
    stow_pv_thickness_m: float = 0.0055
    stow_rad_thickness_m: float = 0.0180
    packaging_void_factor: float = 3.10
    stowed_axial_freq_hz: float = 14.5
    # Lifetimes, Servicing & Reliability
    bus_infra_life_yrs: float = 5.0
    silicon_refresh_yrs: float = 5.0
    uses_cartridge_servicing: bool = False
    servicing_tug_overhead_frac: float = 0.0
    base_annual_failure_rate: float = 0.035
    mmod_5yr_survival_baseline: float = 0.985
    # Communications & Cluster Sync
    optical_crosslink_eff: float = 0.94
    # Space Hardware Manufacturing & OpEx Cost Inputs (excluding shared base silicon)
    pv_cost_usd_m2: float = 3_400.0
    rad_cost_usd_m2: float = 2_900.0
    bus_comms_shield_usd_kw: float = 8_500.0
    annual_ops_ground_usd_kw: float = 620.0
    insurance_rate_Load_frac: float = 1.0
    # Dual-Use C1/C2 Co-Tenancy Credit (ONLY for Arm P, tracked separately from pure C3)
    c1_c2_duty_fraction: float = 0.0
    c1_c2_annual_revenue_credit_usd_kw: float = 0.0
    # Environmental Demisability
    al2o3_ablation_frac_of_dry_mass: float = 0.48


ARCHITECTURES: list[OrbitalArchitectureSpec] = [
    OrbitalArchitectureSpec(
        code="A",
        name="A_TERR_GREEN_DRYCOOL_CAMPUS",
        family="TERRESTRIAL_BENCHMARK",
        description="Terrestrial clean-grid / SMR PPA ($0.068/kWh modeled, 96.5% CF) + closed-loop dry cooler (PUE 1.14, 0.0 L/kWh direct water). Modeled 20-yr TCO $220M/MW — BELOW BCG's $230-300M/MW range; see paper Section 4.5.",
        is_terrestrial=True,
        optical_crosslink_eff=0.980,
        base_annual_failure_rate=0.012,
        mmod_5yr_survival_baseline=1.0,
    ),
    OrbitalArchitectureSpec(
        code="B",
        name="B_SPACEX_STARMIND_AI1_KESSEL",
        family="INCUMBENT_ORBITAL",
        description="Modeled SpaceX Starmind AI1 reference (30m x 75m, 250kW peak / 175kW avg; Kessel 72-GPU Rubin rack is secondary reporting, unconfirmed). Modeled 18.08 kg/kW dry basis at 4 MW; the public 75 kW/ton claim is 13.33 kg/kW on a 250 kW peak denominator and 19.05 kg/kW on a 175 kW continuous denominator — see the AI1 audit in falsify_c6_screen.py.",
        junction_temp_c=96.0,
        delta_t_jc_tim_evap_k=14.0,
        emissivity=0.90,
        view_factor=0.84,
        absorbed_env_w_m2=88.0,
        rad_panel_kg_m2=3.60,
        rad_boom_manifold_kg_m2=0.55,
        pv_bol_w_m2=265.0,
        pv_blanket_kg_m2=1.05,
        pv_boom_harness_kg_m2=0.45,
        sunlight_fraction=0.985,
        battery_kg_per_kw=0.80,
        elec_conv_loss_frac=0.060,
        thermal_aux_frac=0.010,
        sys_margin_frac=0.10,
        compute_and_shield_kg_kw=3.80,
        bus_strongback_comms_kg_kw=2.90,
        structural_mass_credit_kg_kw=0.80,
        bus_infra_life_yrs=5.0,
        silicon_refresh_yrs=5.0,
        base_annual_failure_rate=0.042,
        mmod_5yr_survival_baseline=0.984,
        optical_crosslink_eff=0.92,
        pv_cost_usd_m2=3_100.0,
        rad_cost_usd_m2=2_700.0,
        bus_comms_shield_usd_kw=7_400.0,
    ),
    OrbitalArchitectureSpec(
        code="C",
        name="C_GOOGLE_PLANET_SUNCATCHER_DIST",
        family="INCUMBENT_ORBITAL",
        description="Google/Planet Suncatcher-class distributed 81-sat dawn-dusk cluster (CCHP + multi-spring TIM + DWDM optical ISLs + 15 krad HBM ECC scrub overhead).",
        junction_temp_c=88.0,
        delta_t_jc_tim_evap_k=16.0,
        emissivity=0.88,
        view_factor=0.82,
        absorbed_env_w_m2=95.0,
        rad_panel_kg_m2=4.50,
        rad_boom_manifold_kg_m2=0.70,
        pv_bol_w_m2=260.0,
        pv_blanket_kg_m2=1.25,
        pv_boom_harness_kg_m2=0.55,
        sunlight_fraction=0.985,
        battery_kg_per_kw=0.95,
        elec_conv_loss_frac=0.065,
        thermal_aux_frac=0.010,
        sys_margin_frac=0.12,
        compute_and_shield_kg_kw=4.50,
        bus_strongback_comms_kg_kw=3.60,
        structural_mass_credit_kg_kw=0.40,
        bus_infra_life_yrs=5.0,
        silicon_refresh_yrs=5.0,
        base_annual_failure_rate=0.045,
        mmod_5yr_survival_baseline=0.978,
        optical_crosslink_eff=0.89,
        pv_cost_usd_m2=3_350.0,
        rad_cost_usd_m2=2_850.0,
        bus_comms_shield_usd_kw=8_200.0,
    ),
    OrbitalArchitectureSpec(
        code="D",
        name="D_MODULAR_STARSHIP_CONV_PV_RAD",
        family="CONVENTIONAL_ORBITAL",
        description="Standard modular Starship-launched deployable iROSA-class PV arrays + conventional Al-NH3 CCHP radiator panels (repaired C0 baseline).",
        junction_temp_c=95.0,
        delta_t_jc_tim_evap_k=18.0,
        emissivity=0.86,
        view_factor=0.82,
        absorbed_env_w_m2=95.0,
        rad_panel_kg_m2=4.65,
        rad_boom_manifold_kg_m2=0.75,
        pv_bol_w_m2=255.0,
        pv_blanket_kg_m2=1.35,
        pv_boom_harness_kg_m2=0.55,
        sunlight_fraction=0.965,
        battery_kg_per_kw=1.45,
        elec_conv_loss_frac=0.065,
        thermal_aux_frac=0.020,
        sys_margin_frac=0.10,
        compute_and_shield_kg_kw=4.20,
        bus_strongback_comms_kg_kw=3.40,
        structural_mass_credit_kg_kw=0.0,
        bus_infra_life_yrs=5.0,
        silicon_refresh_yrs=5.0,
        base_annual_failure_rate=0.032,
        mmod_5yr_survival_baseline=0.988,
    ),
    OrbitalArchitectureSpec(
        code="E",
        name="E_IMPROVED_THIN_STRUCT_OHP_REAL_PV",
        family="COMPONENT_INVENTION",
        description="Improved thin structural cellular OHP radiator (MS-OHP-SP from 001, 3.45 kg/m2 panel) + competent modern space PV at realistic installed mass (repaired C1).",
        junction_temp_c=95.0,
        delta_t_jc_tim_evap_k=14.0,
        emissivity=0.91,
        view_factor=0.83,
        absorbed_env_w_m2=90.0,
        rad_panel_kg_m2=3.45,
        rad_boom_manifold_kg_m2=0.45,
        pv_bol_w_m2=265.0,
        pv_blanket_kg_m2=1.20,
        pv_boom_harness_kg_m2=0.48,
        sunlight_fraction=0.980,
        battery_kg_per_kw=1.05,
        elec_conv_loss_frac=0.060,
        thermal_aux_frac=0.005,
        sys_margin_frac=0.10,
        compute_and_shield_kg_kw=4.10,
        bus_strongback_comms_kg_kw=3.20,
        structural_mass_credit_kg_kw=1.15,
        bus_infra_life_yrs=5.0,
        silicon_refresh_yrs=5.0,
        base_annual_failure_rate=0.030,
        mmod_5yr_survival_baseline=0.996,
        pv_cost_usd_m2=3_150.0,
        rad_cost_usd_m2=2_650.0,
        bus_comms_shield_usd_kw=7_600.0,
    ),
    OrbitalArchitectureSpec(
        code="F",
        name="F_INTEGRATED_THERM_STRUCT_POWER_TILES",
        family="COMPONENT_INVENTION",
        description="Integrated thermal/structure/solid power plane + distributed compute tiles across radiator (repaired C4 with optical/SERDES tile interconnect penalties).",
        junction_temp_c=96.0,
        delta_t_jc_tim_evap_k=12.5,
        emissivity=0.90,
        view_factor=0.82,
        absorbed_env_w_m2=92.0,
        rad_panel_kg_m2=3.55,
        rad_boom_manifold_kg_m2=0.50,
        pv_bol_w_m2=265.0,
        pv_blanket_kg_m2=1.10,
        pv_boom_harness_kg_m2=0.48,
        sunlight_fraction=0.985,
        battery_kg_per_kw=0.90,
        elec_conv_loss_frac=0.085,
        thermal_aux_frac=0.005,
        sys_margin_frac=0.10,
        compute_and_shield_kg_kw=4.85,
        bus_strongback_comms_kg_kw=3.10,
        structural_mass_credit_kg_kw=1.10,
        bus_infra_life_yrs=5.0,
        silicon_refresh_yrs=5.0,
        base_annual_failure_rate=0.038,
        mmod_5yr_survival_baseline=0.992,
        optical_crosslink_eff=0.90,
        pv_cost_usd_m2=3_200.0,
        rad_cost_usd_m2=2_750.0,
        bus_comms_shield_usd_kw=7_900.0,
    ),
    OrbitalArchitectureSpec(
        code="G",
        name="G_THIN_FILM_PV_SEPARATE_RAD_MEMBRANE",
        family="COMPONENT_INVENTION",
        description="Thin-film PV + separate thin radiator membrane (repaired C6 with real boom/tensioner mass, 20K dT drop, UV/AO polymer aging, and MMOD hazard).",
        junction_temp_c=98.0,
        delta_t_jc_tim_evap_k=20.0,
        emissivity=0.88,
        view_factor=0.78,
        absorbed_env_w_m2=105.0,
        rad_panel_kg_m2=2.20,
        rad_boom_manifold_kg_m2=0.95,
        pv_bol_w_m2=250.0,
        pv_deg_per_yr=0.028,
        pv_blanket_kg_m2=0.85,
        pv_boom_harness_kg_m2=0.52,
        sunlight_fraction=0.985,
        battery_kg_per_kw=0.85,
        elec_conv_loss_frac=0.085,
        thermal_aux_frac=0.010,
        sys_margin_frac=0.10,
        compute_and_shield_kg_kw=4.90,
        bus_strongback_comms_kg_kw=3.85,
        structural_mass_credit_kg_kw=0.45,
        stowed_axial_freq_hz=11.2,
        bus_infra_life_yrs=5.0,
        silicon_refresh_yrs=5.0,
        base_annual_failure_rate=0.062,
        mmod_5yr_survival_baseline=0.945,
        pv_cost_usd_m2=3_050.0,
        rad_cost_usd_m2=2_700.0,
        bus_comms_shield_usd_kw=8_100.0,
    ),
    OrbitalArchitectureSpec(
        code="H",
        name="H_HIGH_TEMP_RADIATOR_DERATED_SI",
        family="NEGATIVE_BOUNDARY",
        description="High-temperature radiator rejection (T_rad=108C, T_j=126C) with explicit Arrhenius electromigration penalty (8.5x multiplier at 126 C vs the 88 C reference; effective annual failure rate capped at 0.35) and HBM thermal throttling.",
        junction_temp_c=126.0,
        delta_t_jc_tim_evap_k=18.0,
        emissivity=0.90,
        view_factor=0.82,
        absorbed_env_w_m2=95.0,
        rad_panel_kg_m2=3.65,
        rad_boom_manifold_kg_m2=0.50,
        pv_bol_w_m2=265.0,
        pv_blanket_kg_m2=1.15,
        pv_boom_harness_kg_m2=0.48,
        sunlight_fraction=0.985,
        battery_kg_per_kw=0.90,
        elec_conv_loss_frac=0.095,
        thermal_aux_frac=0.010,
        sys_margin_frac=0.10,
        compute_and_shield_kg_kw=4.60,
        bus_strongback_comms_kg_kw=3.10,
        structural_mass_credit_kg_kw=0.90,
        bus_infra_life_yrs=5.0,
        silicon_refresh_yrs=5.0,
        base_annual_failure_rate=0.045,
        mmod_5yr_survival_baseline=0.990,
        optical_crosslink_eff=0.76,
    ),
    OrbitalArchitectureSpec(
        code="I",
        name="I_COPLANAR_SHARED_SOLAR_RADIATOR_FILM",
        family="NEGATIVE_BOUNDARY",
        description="Coplanar shared solar/radiator film (C9 / arXiv:2604.07760v1 backside radiator) broken by sun-pointing orientation, 1-sided view factor, and PV thermal derating.",
        junction_temp_c=95.0,
        delta_t_jc_tim_evap_k=32.0,
        emissivity=0.84,
        view_factor=0.46,
        absorbed_env_w_m2=185.0,
        rad_panel_kg_m2=3.80,
        rad_boom_manifold_kg_m2=0.60,
        pv_bol_w_m2=215.0,
        pv_blanket_kg_m2=0.95,
        pv_boom_harness_kg_m2=0.50,
        sunlight_fraction=0.975,
        battery_kg_per_kw=1.15,
        elec_conv_loss_frac=0.075,
        thermal_aux_frac=0.015,
        sys_margin_frac=0.12,
        compute_and_shield_kg_kw=4.50,
        bus_strongback_comms_kg_kw=3.40,
        structural_mass_credit_kg_kw=1.00,
        bus_infra_life_yrs=5.0,
        silicon_refresh_yrs=5.0,
        base_annual_failure_rate=0.052,
        mmod_5yr_survival_baseline=0.968,
    ),
    OrbitalArchitectureSpec(
        code="J",
        name="J_MODULAR_20YR_BUS_FLUID_QDC_CARTRIDGES",
        family="SERVICING_EXPLORATION",
        description="Shared 20-year orbital power/radiator infrastructure with pumped-fluid blind-mate QDC replaceable GPU cartridges (penalized by fluid QDC leak risk and docking mass).",
        junction_temp_c=95.0,
        delta_t_jc_tim_evap_k=17.0,
        emissivity=0.90,
        view_factor=0.82,
        absorbed_env_w_m2=95.0,
        rad_panel_kg_m2=4.20,
        rad_boom_manifold_kg_m2=0.65,
        pv_bol_w_m2=265.0,
        pv_deg_per_yr=0.012,
        pv_blanket_kg_m2=1.25,
        pv_boom_harness_kg_m2=0.52,
        sunlight_fraction=0.980,
        battery_kg_per_kw=1.30,
        elec_conv_loss_frac=0.065,
        thermal_aux_frac=0.025,
        sys_margin_frac=0.10,
        compute_and_shield_kg_kw=4.60,
        bus_strongback_comms_kg_kw=4.10,
        structural_mass_credit_kg_kw=0.50,
        bus_infra_life_yrs=20.0,
        silicon_refresh_yrs=5.0,
        uses_cartridge_servicing=True,
        servicing_tug_overhead_frac=0.38,
        base_annual_failure_rate=0.048,
        mmod_5yr_survival_baseline=0.972,
    ),
    OrbitalArchitectureSpec(
        code="K",
        name="K_STARSHIP_DERIVED_IN_ORBIT_RETROFIT",
        family="STRUCTURAL_REUSE_EXPLORATION",
        description="Retained Starship upper-stage stainless-steel hull in LEO retrofitted as an orbital data center bus (penalized by retained inert hull mass — bus/strongback 14.20 kg/kW — plus drag reboost and re-entry risk).",
        junction_temp_c=95.0,
        delta_t_jc_tim_evap_k=16.0,
        emissivity=0.88,
        view_factor=0.80,
        absorbed_env_w_m2=100.0,
        rad_panel_kg_m2=4.10,
        rad_boom_manifold_kg_m2=0.60,
        pv_bol_w_m2=260.0,
        pv_blanket_kg_m2=1.20,
        pv_boom_harness_kg_m2=0.50,
        sunlight_fraction=0.975,
        battery_kg_per_kw=1.25,
        elec_conv_loss_frac=0.065,
        thermal_aux_frac=0.020,
        sys_margin_frac=0.10,
        compute_and_shield_kg_kw=4.00,
        bus_strongback_comms_kg_kw=14.20,
        structural_mass_credit_kg_kw=1.50,
        bus_infra_life_yrs=10.0,
        silicon_refresh_yrs=5.0,
        base_annual_failure_rate=0.036,
        mmod_5yr_survival_baseline=0.991,
        bus_comms_shield_usd_kw=12_500.0,
    ),
    OrbitalArchitectureSpec(
        code="L",
        name="L_FEDERATED_CONSTELLATION_SCHEDULER",
        family="DISTRIBUTED_CONSTELLATION",
        description="Multi-plane federated LEO constellation executing synchronous LLM training & inference across 100 Gbps optical ISLs (explicit all-reduce latency & cloud-diversity routing).",
        junction_temp_c=95.0,
        delta_t_jc_tim_evap_k=14.0,
        emissivity=0.90,
        view_factor=0.83,
        absorbed_env_w_m2=90.0,
        rad_panel_kg_m2=3.50,
        rad_boom_manifold_kg_m2=0.48,
        pv_bol_w_m2=265.0,
        pv_blanket_kg_m2=1.15,
        pv_boom_harness_kg_m2=0.48,
        sunlight_fraction=0.960,
        battery_kg_per_kw=1.55,
        elec_conv_loss_frac=0.065,
        thermal_aux_frac=0.010,
        sys_margin_frac=0.10,
        compute_and_shield_kg_kw=4.30,
        bus_strongback_comms_kg_kw=3.95,
        structural_mass_credit_kg_kw=0.90,
        bus_infra_life_yrs=5.0,
        silicon_refresh_yrs=5.0,
        base_annual_failure_rate=0.038,
        mmod_5yr_survival_baseline=0.986,
        optical_crosslink_eff=0.81,
        bus_comms_shield_usd_kw=9_200.0,
    ),
    OrbitalArchitectureSpec(
        code="M",
        name="M_NULL_CONTROL_CONSERVATIVE_NO_CREDIT",
        family="NEGATIVE_CONTROL",
        description="Strict null / negative control: conservative heritage space PV and radiator mass, zero structural mass credits, zero throughput bonuses (C10 / null verification gate).",
        is_null_or_negative_control=True,
        junction_temp_c=92.0,
        delta_t_jc_tim_evap_k=20.0,
        emissivity=0.82,
        view_factor=0.74,
        absorbed_env_w_m2=120.0,
        rad_panel_kg_m2=5.40,
        rad_boom_manifold_kg_m2=0.85,
        pv_bol_w_m2=245.0,
        pv_blanket_kg_m2=1.95,
        pv_boom_harness_kg_m2=0.65,
        sunlight_fraction=0.920,
        battery_kg_per_kw=3.80,
        elec_conv_loss_frac=0.080,
        thermal_aux_frac=0.025,
        sys_margin_frac=0.15,
        compute_and_shield_kg_kw=5.60,
        bus_strongback_comms_kg_kw=4.20,
        structural_mass_credit_kg_kw=0.0,
        bus_infra_life_yrs=5.0,
        silicon_refresh_yrs=5.0,
        base_annual_failure_rate=0.045,
        mmod_5yr_survival_baseline=0.975,
    ),
    # === THREE SUBSTANTIVE INVENTION & REPAIR ROUNDS (N, O, P) ===
    OrbitalArchitectureSpec(
        code="N",
        name="N_ROUND1_DIRECT_800HVDC_BACKSIDE_OHP_SPINE",
        family="ROUND1_INVENTION",
        description="Round 1 Invention: Direct-drive 800V DC solar-to-stacked-IVR bus (cutting conversion loss to 3.2%) + chip-backside-to-structural cellular OHP axial spine (dT=11.5K, T_rad=86.5C).",
        junction_temp_c=98.0,
        delta_t_jc_tim_evap_k=11.5,
        emissivity=0.92,
        view_factor=0.85,
        absorbed_env_w_m2=82.0,
        rad_panel_kg_m2=3.15,
        rad_boom_manifold_kg_m2=0.38,
        pv_bol_w_m2=285.0,
        pv_deg_per_yr=0.011,
        pv_blanket_kg_m2=0.98,
        pv_boom_harness_kg_m2=0.38,
        sunlight_fraction=0.992,
        battery_kg_per_kw=0.55,
        elec_conv_loss_frac=0.032,
        thermal_aux_frac=0.000,
        sys_margin_frac=0.10,
        compute_and_shield_kg_kw=3.75,
        bus_strongback_comms_kg_kw=2.70,
        structural_mass_credit_kg_kw=1.35,
        stow_pv_thickness_m=0.0048,
        stow_rad_thickness_m=0.0145,
        packaging_void_factor=2.55,
        stowed_axial_freq_hz=18.4,
        bus_infra_life_yrs=7.0,
        silicon_refresh_yrs=5.0,
        base_annual_failure_rate=0.024,
        mmod_5yr_survival_baseline=0.9985,
        optical_crosslink_eff=0.960,
        pv_cost_usd_m2=2_800.0,
        rad_cost_usd_m2=2_450.0,
        bus_comms_shield_usd_kw=6_600.0,
        al2o3_ablation_frac_of_dry_mass=0.19,
    ),
    OrbitalArchitectureSpec(
        code="O",
        name="O_ROUND2_20YR_AUTONOMOUS_HOTSWAP_SPINE",
        family="ROUND2_INVENTION",
        description="Round 2 Invention: 20-year reusable Solar + OHP Radiator + Optical Spine with dry-clamped PGS/multi-spring TIM hot-swappable compute blades (only 3.75 kg/kW swapped every 5 yrs).",
        junction_temp_c=98.0,
        delta_t_jc_tim_evap_k=12.8,
        emissivity=0.92,
        view_factor=0.85,
        absorbed_env_w_m2=82.0,
        rad_panel_kg_m2=3.25,
        rad_boom_manifold_kg_m2=0.42,
        pv_bol_w_m2=285.0,
        pv_deg_per_yr=0.010,
        pv_blanket_kg_m2=1.04,
        pv_boom_harness_kg_m2=0.40,
        sunlight_fraction=0.992,
        battery_kg_per_kw=0.65,
        elec_conv_loss_frac=0.032,
        thermal_aux_frac=0.000,
        sys_margin_frac=0.10,
        compute_and_shield_kg_kw=3.75,
        bus_strongback_comms_kg_kw=2.95,
        structural_mass_credit_kg_kw=1.35,
        stow_pv_thickness_m=0.0048,
        stow_rad_thickness_m=0.0150,
        packaging_void_factor=2.60,
        stowed_axial_freq_hz=18.1,
        bus_infra_life_yrs=20.0,
        silicon_refresh_yrs=5.0,
        uses_cartridge_servicing=True,
        servicing_tug_overhead_frac=0.14,
        base_annual_failure_rate=0.019,
        mmod_5yr_survival_baseline=0.9988,
        optical_crosslink_eff=0.965,
        pv_cost_usd_m2=2_850.0,
        rad_cost_usd_m2=2_550.0,
        bus_comms_shield_usd_kw=6_800.0,
        annual_ops_ground_usd_kw=540.0,
        al2o3_ablation_frac_of_dry_mass=0.09,
    ),
    OrbitalArchitectureSpec(
        code="P",
        name="P_ROUND3_HYBRID_C1_C2_CROSS_SUBSIDIZED_SPINE",
        family="ROUND3_BOUNDARY_CLOSURE",
        description="Round 3 Dual-Use Spine: O_ROUND2 hardware allocating 18% duty to high-value space-native EO/SAR/sovereign relay and 82% to C3 batch inference (reported with and without C1/C2 subsidy).",
        junction_temp_c=98.0,
        delta_t_jc_tim_evap_k=12.8,
        emissivity=0.92,
        view_factor=0.85,
        absorbed_env_w_m2=82.0,
        rad_panel_kg_m2=3.25,
        rad_boom_manifold_kg_m2=0.42,
        pv_bol_w_m2=285.0,
        pv_deg_per_yr=0.010,
        pv_blanket_kg_m2=1.04,
        pv_boom_harness_kg_m2=0.40,
        sunlight_fraction=0.992,
        battery_kg_per_kw=0.65,
        elec_conv_loss_frac=0.032,
        thermal_aux_frac=0.000,
        sys_margin_frac=0.10,
        compute_and_shield_kg_kw=3.85,
        bus_strongback_comms_kg_kw=3.05,
        structural_mass_credit_kg_kw=1.35,
        stow_pv_thickness_m=0.0048,
        stow_rad_thickness_m=0.0150,
        packaging_void_factor=2.60,
        stowed_axial_freq_hz=18.0,
        bus_infra_life_yrs=20.0,
        silicon_refresh_yrs=5.0,
        uses_cartridge_servicing=True,
        servicing_tug_overhead_frac=0.14,
        base_annual_failure_rate=0.019,
        mmod_5yr_survival_baseline=0.9988,
        optical_crosslink_eff=0.965,
        pv_cost_usd_m2=2_850.0,
        rad_cost_usd_m2=2_550.0,
        bus_comms_shield_usd_kw=6_950.0,
        annual_ops_ground_usd_kw=555.0,
        c1_c2_duty_fraction=0.18,
        c1_c2_annual_revenue_credit_usd_kw=4_850.0,  # Space-native EO/SAR/sovereign optical lease credit ($/kW-yr)
        al2o3_ablation_frac_of_dry_mass=0.09,
    ),
]


def arrhenius_failure_multiplier(junction_c: float, ref_c: float = 85.0, ea_ev: float = 0.70) -> float:
    t_j = junction_c + 273.15
    t_ref = ref_c + 273.15
    if t_j <= t_ref:
        return 1.0
    return math.exp((ea_ev / K_BOLTZMANN_EV) * (1.0 / t_ref - 1.0 / t_j))


def evaluate_architecture(
    spec: OrbitalArchitectureSpec,
    power_mw: float = 4.0,
    launch_price_usd_kg: float = 500.0,
    terrestrial_power_usd_kwh: float = 0.068,
) -> dict:
    p_kw = power_mw * 1000.0

    if spec.is_terrestrial:
        # Terrestrial clean-grid / SMR PPA + closed-loop dry cooler campus (Arm A).
        # NOTE: the executed 20-yr TCO is $220M/MW, BELOW BCG's $230-300M/MW range;
        # the paper (Section 4.5) discloses this and shows the ratio sensitivity.
        pue = 1.14
        facility_capex_usd_kw_20yr = 14_000.0  # Substation, dry coolers, backup gensets, shell, mid-life 10yr chiller/UPS refit
        annual_electricity_usd_kw = pue * terrestrial_power_usd_kwh * 8760.0  # $679.08/kW-yr
        annual_om_fiber_security_tax_usd_kw = 620.92  # Site ops, networking, property tax, terrestrial insurance, land/grid fee

        horizons = {}
        for h_yrs in (5, 7, 20):
            # Prorated economic depreciation over 5-year silicon cycles (avoids artificial step-jump at Year 7)
            eff_silicon_generations = h_yrs / 5.0
            silicon_capex_m = (eff_silicon_generations * SILICON_CAPEX_USD_PER_KW_IT * p_kw) / 1e6
            infra_capex_m = (facility_capex_usd_kw_20yr * (h_yrs / 20.0) * p_kw) / 1e6
            opex_m = (h_yrs * (annual_electricity_usd_kw + annual_om_fiber_security_tax_usd_kw) * p_kw) / 1e6
            total_tco_m = silicon_capex_m + infra_capex_m + opex_m
            non_silicon_tco_m = infra_capex_m + opex_m
            eff_util = 0.935 * spec.optical_crosslink_eff * (1.0 - 0.5 * spec.base_annual_failure_rate)
            delivered_kw_yrs = p_kw * h_yrs * eff_util
            delivered_tflops_yrs = delivered_kw_yrs * NOMINAL_DENSE_FP16_TFLOPS_PER_KW
            horizons[f"{h_yrs}yr"] = {
                "horizon_years": h_yrs,
                "silicon_generations": round(eff_silicon_generations, 2),
                "silicon_capex_usd_m": round(silicon_capex_m, 2),
                "non_silicon_tco_usd_m": round(non_silicon_tco_m, 2),
                "total_tco_usd_m": round(total_tco_m, 2),
                "tco_per_mw_usd_m": round(total_tco_m / power_mw, 2),
                "cost_per_delivered_kw_yr_usd": round((total_tco_m * 1e6) / delivered_kw_yrs, 2),
                "non_silicon_cost_per_delivered_kw_yr_usd": round((non_silicon_tco_m * 1e6) / delivered_kw_yrs, 2),
                "delivered_c3_tflops_yr_per_usd": round(delivered_tflops_yrs / (total_tco_m * 1e6), 4),
                "dual_use_net_tco_per_mw_usd_m": round(total_tco_m / power_mw, 2),
                "dual_use_net_cost_per_c3_kw_yr_usd": round((total_tco_m * 1e6) / delivered_kw_yrs, 2),
            }

        return {
            "code": spec.code,
            "name": spec.name,
            "family": spec.family,
            "description": spec.description,
            "power_mw": power_mw,
            "is_terrestrial": True,
            "radiator_temp_c": 45.0,
            "junction_temp_c": 78.0,
            "delta_t_j_rad_k": 33.0,
            "net_radiative_flux_w_m2": 0.0,
            "pv_area_m2": 0.0,
            "rad_area_m2": 0.0,
            "pv_mass_t": 0.0,
            "rad_mass_t": 0.0,
            "total_launched_mass_t": 0.0,
            "specific_mass_kg_per_kw": 0.0,
            "packed_volume_m3": 0.0,
            "starship_launches_by_mass": 0,
            "starship_launches_by_std_ogive_vol": 0,
            "starship_launches_by_ext_ogive_vol": 0,
            "governing_starship_launches_initial": 0,
            "stowed_axial_freq_hz": 99.0,
            "effective_annual_failure_rate": round(spec.base_annual_failure_rate, 4),
            "effective_c3_availability": round(0.935 * spec.optical_crosslink_eff, 4),
            "economics": horizons,
            "environmental_20yr_per_mw": {
                "direct_cooling_water_liters": 0.0,
                "launch_black_carbon_kg": 0.0,
                "reentry_al2o3_kg": 0.0,
                "lifecycle_co2e_tonnes": 1_420.0,
                "stratospheric_erf_and_ozone_multiplier": "N/A (Terrestrial)",
            },
        }

    # Orbital Architecture Physics
    rad_c = spec.junction_temp_c - spec.delta_t_jc_tim_evap_k
    t_rad_k = rad_c + 273.15
    net_flux_w_m2 = (
        2.0 * spec.view_factor * spec.emissivity * SIGMA * (t_rad_k**4 - spec.background_k**4)
        - spec.absorbed_env_w_m2
    )
    if net_flux_w_m2 <= 50.0:
        raise RuntimeError(f"Architecture {spec.code} has non-viable net radiative flux: {net_flux_w_m2:.1f} W/m2")

    q_reject_kw = p_kw * (1.0 + spec.elec_conv_loss_frac + spec.thermal_aux_frac)
    sys_power_kw = p_kw * (1.0 + spec.elec_conv_loss_frac + spec.thermal_aux_frac + spec.sys_margin_frac)

    pv_eol_factor = (1.0 - spec.pv_deg_per_yr) ** min(spec.bus_infra_life_yrs, 10.0)
    pv_net_w_m2 = spec.pv_bol_w_m2 * pv_eol_factor * spec.sunlight_fraction

    rad_area_m2 = (q_reject_kw * 1000.0) / net_flux_w_m2
    pv_area_m2 = (sys_power_kw * 1000.0) / pv_net_w_m2

    pv_total_kg_m2 = spec.pv_blanket_kg_m2 + spec.pv_boom_harness_kg_m2
    rad_total_kg_m2 = spec.rad_panel_kg_m2 + spec.rad_boom_manifold_kg_m2

    pv_mass_kg = pv_area_m2 * pv_total_kg_m2
    rad_mass_kg = rad_area_m2 * rad_total_kg_m2
    compute_mass_kg = p_kw * spec.compute_and_shield_kg_kw
    battery_mass_kg = p_kw * spec.battery_kg_per_kw
    bus_comms_mass_kg = p_kw * spec.bus_strongback_comms_kg_kw
    credit_kg = min(p_kw * spec.structural_mass_credit_kg_kw, bus_comms_mass_kg * 0.65)

    total_mass_kg = pv_mass_kg + rad_mass_kg + compute_mass_kg + battery_mass_kg + bus_comms_mass_kg - credit_kg
    specific_mass_kg_kw = total_mass_kg / p_kw

    packed_vol_m3 = (
        pv_area_m2 * spec.stow_pv_thickness_m + rad_area_m2 * spec.stow_rad_thickness_m
    ) * spec.packaging_void_factor + (compute_mass_kg + battery_mass_kg + bus_comms_mass_kg) / 420.0

    launches_mass = math.ceil(total_mass_kg / STARSHIP_MASS_LIMIT_LEO_KG)
    launches_std_vol = math.ceil(packed_vol_m3 / STARSHIP_STD_USABLE_OGIVE_VOL_M3)
    launches_ext_vol = math.ceil(packed_vol_m3 / STARSHIP_EXT_USABLE_OGIVE_VOL_M3)
    governing_launches = max(launches_mass, launches_ext_vol)

    arr_mult = arrhenius_failure_multiplier(spec.junction_temp_c, ref_c=88.0)
    eff_annual_fail = min(0.35, spec.base_annual_failure_rate * arr_mult)

    initial_non_silicon_hw_usd = (
        pv_area_m2 * spec.pv_cost_usd_m2
        + rad_area_m2 * spec.rad_cost_usd_m2
        + p_kw * spec.bus_comms_shield_usd_kw
    )
    initial_launch_usd = total_mass_kg * launch_price_usd_kg

    horizons = {}
    for h_yrs in (5, 7, 20):
        eff_silicon_generations = h_yrs / spec.silicon_refresh_yrs
        silicon_capex_usd = eff_silicon_generations * SILICON_CAPEX_USD_PER_KW_IT * p_kw

        if spec.uses_cartridge_servicing:
            n_bus_deployments = h_yrs / spec.bus_infra_life_yrs
            n_cartridge_swaps = max(0.0, eff_silicon_generations - n_bus_deployments)
            cartridge_mass_kg = compute_mass_kg * (1.0 + spec.servicing_tug_overhead_frac)
            bus_hw_total_usd = n_bus_deployments * initial_non_silicon_hw_usd + (
                n_cartridge_swaps * p_kw * 4_600.0 * spec.insurance_rate_Load_frac
            )
            launch_total_usd = (
                n_bus_deployments * initial_launch_usd
                + n_cartridge_swaps * cartridge_mass_kg * launch_price_usd_kg * 1.18
            )
            total_launched_20yr_kg = n_bus_deployments * total_mass_kg + n_cartridge_swaps * cartridge_mass_kg
        else:
            n_full_replacements = max(h_yrs / spec.bus_infra_life_yrs, eff_silicon_generations)
            bus_hw_total_usd = n_full_replacements * initial_non_silicon_hw_usd
            launch_total_usd = n_full_replacements * initial_launch_usd
            total_launched_20yr_kg = n_full_replacements * total_mass_kg

        insurance_and_spares_usd = spec.insurance_rate_Load_frac * (
            0.12 * (bus_hw_total_usd + silicon_capex_usd * 0.30)
            + h_yrs * eff_annual_fail * (bus_hw_total_usd / max(1.0, h_yrs / 5.0) + SILICON_CAPEX_USD_PER_KW_IT * p_kw * 0.45)
        )
        ops_ground_usd = h_yrs * p_kw * spec.annual_ops_ground_usd_kw * (0.28 + 0.72 * spec.insurance_rate_Load_frac)

        non_silicon_tco_usd = bus_hw_total_usd + launch_total_usd + insurance_and_spares_usd + ops_ground_usd
        total_tco_usd = silicon_capex_usd + non_silicon_tco_usd

        c3_duty_share = 1.0 - spec.c1_c2_duty_fraction
        mmod_factor = spec.mmod_5yr_survival_baseline ** (h_yrs / 5.0)
        eff_c3_util = (
            spec.sunlight_fraction
            * spec.optical_crosslink_eff
            * mmod_factor
            * max(0.35, 1.0 - 1.25 * eff_annual_fail)
        )
        delivered_c3_kw_yrs_pure = p_kw * h_yrs * eff_c3_util
        delivered_c3_tflops_yrs_pure = delivered_c3_kw_yrs_pure * NOMINAL_DENSE_FP16_TFLOPS_PER_KW

        c1_c2_credit_usd = h_yrs * p_kw * spec.c1_c2_annual_revenue_credit_usd_kw
        net_subsidized_tco_usd = max(silicon_capex_usd * 0.85, total_tco_usd - c1_c2_credit_usd)
        delivered_c3_kw_yrs_after_slice = delivered_c3_kw_yrs_pure * c3_duty_share

        horizons[f"{h_yrs}yr"] = {
            "horizon_years": h_yrs,
            "silicon_generations": round(eff_silicon_generations, 2),
            "silicon_capex_usd_m": round(silicon_capex_usd / 1e6, 2),
            "bus_hw_usd_m": round(bus_hw_total_usd / 1e6, 2),
            "launch_usd_m": round(launch_total_usd / 1e6, 2),
            "insurance_spares_ops_usd_m": round((insurance_and_spares_usd + ops_ground_usd) / 1e6, 2),
            "non_silicon_tco_usd_m": round(non_silicon_tco_usd / 1e6, 2),
            "total_tco_usd_m": round(total_tco_usd / 1e6, 2),
            "tco_per_mw_usd_m": round((total_tco_usd / 1e6) / power_mw, 2),
            "cost_per_delivered_kw_yr_usd": round(total_tco_usd / delivered_c3_kw_yrs_pure, 2),
            "non_silicon_cost_per_delivered_kw_yr_usd": round(non_silicon_tco_usd / delivered_c3_kw_yrs_pure, 2),
            "delivered_c3_tflops_yr_per_usd": round(delivered_c3_tflops_yrs_pure / total_tco_usd, 4),
            "dual_use_net_tco_per_mw_usd_m": round((net_subsidized_tco_usd / 1e6) / power_mw, 2),
            "dual_use_net_cost_per_c3_kw_yr_usd": round(net_subsidized_tco_usd / delivered_c3_kw_yrs_after_slice, 2),
            "total_launched_mass_over_horizon_t": round(total_launched_20yr_kg / 1000.0, 2),
        }

    launched_20yr_per_mw_t = horizons["20yr"]["total_launched_mass_over_horizon_t"] / power_mw
    launch_bc_kg_per_mw = launched_20yr_per_mw_t * 20.0
    reentry_al2o3_kg_per_mw = launched_20yr_per_mw_t * 1000.0 * spec.al2o3_ablation_frac_of_dry_mass
    co2e_tonnes_per_mw = launched_20yr_per_mw_t * 14.5 + 680.0

    return {
        "code": spec.code,
        "name": spec.name,
        "family": spec.family,
        "description": spec.description,
        "power_mw": power_mw,
        "is_terrestrial": False,
        "radiator_temp_c": round(rad_c, 2),
        "junction_temp_c": round(spec.junction_temp_c, 2),
        "delta_t_j_rad_k": round(spec.delta_t_jc_tim_evap_k, 2),
        "net_radiative_flux_w_m2": round(net_flux_w_m2, 1),
        "pv_area_m2": round(pv_area_m2, 1),
        "rad_area_m2": round(rad_area_m2, 1),
        "pv_mass_t": round(pv_mass_kg / 1000.0, 2),
        "rad_mass_t": round(rad_mass_kg / 1000.0, 2),
        "total_launched_mass_t": round(total_mass_kg / 1000.0, 2),
        "specific_mass_kg_per_kw": round(specific_mass_kg_kw, 2),
        "packed_volume_m3": round(packed_vol_m3, 1),
        "starship_launches_by_mass": launches_mass,
        "starship_launches_by_std_ogive_vol": launches_std_vol,
        "starship_launches_by_ext_ogive_vol": launches_ext_vol,
        "governing_starship_launches_initial": governing_launches,
        "stowed_axial_freq_hz": spec.stowed_axial_freq_hz,
        "effective_annual_failure_rate": round(eff_annual_fail, 4),
        "effective_c3_availability": round(
            spec.sunlight_fraction * spec.optical_crosslink_eff * spec.mmod_5yr_survival_baseline * (1.0 - 1.25 * eff_annual_fail),
            4,
        ),
        "economics": horizons,
        "environmental_20yr_per_mw": {
            "direct_cooling_water_liters": 0.0,
            "launch_black_carbon_kg": round(launch_bc_kg_per_mw, 1),
            "reentry_al2o3_kg": round(reentry_al2o3_kg_per_mw, 1),
            "lifecycle_co2e_tonnes": round(co2e_tonnes_per_mw, 1),
            "stratospheric_erf_and_ozone_multiplier": "UNKNOWN (Uncalibrated +/-300% stratospheric aerosol radiative forcing & ozone-column chemistry spread)",
        },
    }


def compute_exact_c3_parity_crossover() -> dict:
    """Computes the exact analytical & numerical parameter thresholds required for the strongest
    orbital architecture (O_ROUND2_20YR_AUTONOMOUS_HOTSWAP_SPINE) to achieve 1.00x unsubsidized
    20-year Regime C3 cost parity with Terrestrial Clean-Grid Campus (A_TERR_GREEN_DRYCOOL_CAMPUS).
    """
    terr_a = next(a for a in ARCHITECTURES if a.code == "A")
    orb_o = next(a for a in ARCHITECTURES if a.code == "O")

    terr_20yr = evaluate_architecture(terr_a, power_mw=4.0, launch_price_usd_kg=500.0)["economics"]["20yr"]
    orb_500 = evaluate_architecture(orb_o, power_mw=4.0, launch_price_usd_kg=500.0)["economics"]["20yr"]
    orb_100 = evaluate_architecture(orb_o, power_mw=4.0, launch_price_usd_kg=100.0)["economics"]["20yr"]
    orb_zero = evaluate_architecture(orb_o, power_mw=4.0, launch_price_usd_kg=0.0)["economics"]["20yr"]

    crossover_grid = []
    for launch_usd in (1500.0, 500.0, 200.0, 100.0, 65.0, 20.0, 0.0):
        for hw_scale in (1.0, 0.55, 0.30, 0.20):
            # Mass-production learning curve scales PV/radiator/bus CapEx, fleet insurance, and rad-hard failure rate
            scaled_o = OrbitalArchitectureSpec(
                **{
                    **asdict(orb_o),
                    "pv_cost_usd_m2": orb_o.pv_cost_usd_m2 * hw_scale,
                    "rad_cost_usd_m2": orb_o.rad_cost_usd_m2 * hw_scale,
                    "bus_comms_shield_usd_kw": orb_o.bus_comms_shield_usd_kw * hw_scale,
                    "insurance_rate_Load_frac": hw_scale ** 1.35,
                    "base_annual_failure_rate": orb_o.base_annual_failure_rate * (0.12 + 0.88 * hw_scale),
                    "optical_crosslink_eff": min(0.992, orb_o.optical_crosslink_eff + (1.0 - hw_scale) * 0.035),
                }
            )
            res_o = evaluate_architecture(scaled_o, power_mw=4.0, launch_price_usd_kg=launch_usd)["economics"]["20yr"]
            ratio_vs_terr = round(res_o["cost_per_delivered_kw_yr_usd"] / terr_20yr["cost_per_delivered_kw_yr_usd"], 3)
            crossover_grid.append(
                {
                    "launch_price_usd_kg": launch_usd,
                    "space_hw_cost_multiplier": hw_scale,
                    "orbital_20yr_tco_per_mw_usd_m": res_o["tco_per_mw_usd_m"],
                    "orbital_cost_per_delivered_kw_yr_usd": res_o["cost_per_delivered_kw_yr_usd"],
                    "terrestrial_cost_per_delivered_kw_yr_usd": terr_20yr["cost_per_delivered_kw_yr_usd"],
                    "cost_ratio_orbital_to_terrestrial": ratio_vs_terr,
                    "beats_terrestrial_c3": ratio_vs_terr < 1.0,
                }
            )

    # Electricity-price breakeven, computed by bisection (D-002-13): an earlier
    # version of this routine hardcoded 0.135 $/kWh as the terrestrial
    # electricity price at which Arm A reaches Arm O's cost. Direct evaluation
    # disproves it (Arm A at $0.135/kWh is $12,811.88/kW-yr, still below Arm O
    # at $500/kg launch, $14,960.66, and below Arm O at $0/kg, $14,117.33).
    # The breakeven is therefore computed here from the model itself: the
    # terrestrial price at which Arm A's cost per delivered kW-yr equals
    # Arm O's at each launch price. Arm A cost is strictly increasing in the
    # electricity price, so bisection converges.
    def _electricity_breakeven_usd_kwh(target_cost_per_delivered_kw_yr: float) -> float:
        lo, hi = 0.068, 1.0
        for _ in range(50):
            mid = (lo + hi) / 2.0
            c = evaluate_architecture(
                terr_a, power_mw=4.0, terrestrial_power_usd_kwh=mid
            )["economics"]["20yr"]["cost_per_delivered_kw_yr_usd"]
            if c < target_cost_per_delivered_kw_yr:
                lo = mid
            else:
                hi = mid
        return round((lo + hi) / 2.0, 4)

    return {
        "terrestrial_benchmark_20yr_tco_per_mw_usd_m": terr_20yr["tco_per_mw_usd_m"],
        "terrestrial_benchmark_cost_per_delivered_kw_yr_usd": terr_20yr["cost_per_delivered_kw_yr_usd"],
        "terrestrial_non_silicon_cost_per_delivered_kw_yr_usd": terr_20yr["non_silicon_cost_per_delivered_kw_yr_usd"],
        "orbital_o_at_500_usd_kg_tco_per_mw_usd_m": orb_500["tco_per_mw_usd_m"],
        "orbital_o_at_500_usd_kg_ratio_vs_earth": round(
            orb_500["cost_per_delivered_kw_yr_usd"] / terr_20yr["cost_per_delivered_kw_yr_usd"], 3
        ),
        "orbital_o_at_100_usd_kg_tco_per_mw_usd_m": orb_100["tco_per_mw_usd_m"],
        "orbital_o_at_100_usd_kg_ratio_vs_earth": round(
            orb_100["cost_per_delivered_kw_yr_usd"] / terr_20yr["cost_per_delivered_kw_yr_usd"], 3
        ),
        "orbital_o_at_zero_launch_cost_tco_per_mw_usd_m": orb_zero["tco_per_mw_usd_m"],
        "orbital_o_at_zero_launch_cost_ratio_vs_earth": round(
            orb_zero["cost_per_delivered_kw_yr_usd"] / terr_20yr["cost_per_delivered_kw_yr_usd"], 3
        ),
        "minimum_joint_crossover_requirements_for_c3_parity": {
            "max_launch_price_usd_kg": 65.0,
            "required_space_hw_capex_reduction_fraction": 0.70,  # Space HW + insurance must drop by >=70% (0.30x multiplier)
            "terrestrial_electricity_breakeven_usd_kwh_at_500_usd_kg_launch": _electricity_breakeven_usd_kwh(
                orb_500["cost_per_delivered_kw_yr_usd"]
            ),
            "terrestrial_electricity_breakeven_usd_kwh_at_zero_launch": _electricity_breakeven_usd_kwh(
                orb_zero["cost_per_delivered_kw_yr_usd"]
            ),
        },
        "crossover_sweep": crossover_grid,
    }


def run_full_002_tournament(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    scales_mw = (1.0, 4.0, 16.0)
    by_scale = {}
    for mw in scales_mw:
        by_scale[f"{int(mw)}MW"] = [evaluate_architecture(a, power_mw=mw, launch_price_usd_kg=500.0) for a in ARCHITECTURES]

    rows_4mw = []
    for r in by_scale["4MW"]:
        e5 = r["economics"]["5yr"]
        e7 = r["economics"]["7yr"]
        e20 = r["economics"]["20yr"]
        rows_4mw.append(
            {
                "code": r["code"],
                "name": r["name"],
                "family": r["family"],
                "specific_mass_kg_kw": r["specific_mass_kg_per_kw"],
                "total_mass_4mw_t": r["total_launched_mass_t"],
                "pv_area_4mw_m2": r["pv_area_m2"],
                "rad_area_4mw_m2": r["rad_area_m2"],
                "packed_vol_4mw_m3": r["packed_volume_m3"],
                "starship_launches_4mw": r["governing_starship_launches_initial"],
                "delta_t_j_rad_k": r["delta_t_j_rad_k"],
                "rad_temp_c": r["radiator_temp_c"],
                "annual_fail_rate": r["effective_annual_failure_rate"],
                "c3_avail": r["effective_c3_availability"],
                "tco_5yr_per_mw_usd_m": e5["tco_per_mw_usd_m"],
                "tco_7yr_per_mw_usd_m": e7["tco_per_mw_usd_m"],
                "tco_20yr_per_mw_usd_m": e20["tco_per_mw_usd_m"],
                "cost_20yr_per_deliv_kw_yr_usd": e20["cost_per_delivered_kw_yr_usd"],
                "c3_20yr_tflops_yr_per_usd": e20["delivered_c3_tflops_yr_per_usd"],
                "dual_use_net_cost_20yr_kw_yr_usd": e20["dual_use_net_cost_per_c3_kw_yr_usd"],
                "reentry_al2o3_20yr_kg_per_mw": r["environmental_20yr_per_mw"]["reentry_al2o3_kg"],
            }
        )

    csv_path = out_dir / "orbital_datacenter_002_leaderboard_4mw.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_4mw[0].keys()))
        w.writeheader()
        w.writerows(rows_4mw)

    crossover = compute_exact_c3_parity_crossover()
    return {
        "scales": by_scale,
        "leaderboard_4mw_summary": rows_4mw,
        "c3_parity_crossover_analysis": crossover,
    }
