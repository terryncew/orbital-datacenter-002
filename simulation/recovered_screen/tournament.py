#!/usr/bin/env python3
"""Independent first-principles screening, NOT validated spacecraft performance.
Models a launch-packable 1MW-10MW class orbital compute node.
Only compares constraints and sensitivities; no hidden 'space innovation' multiplier.
SPDX-License-Identifier: MIT
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import csv, json, math
from pathlib import Path

SIGMA=5.670374419e-8
STARSHIP_DESIGN_LEO_KG=100_000        # published target, not mission guarantee
STARSHIP_LEGACY_ENVELOPE_DIAMETER_M=8.0 # old user guide, not current guaranteed interface
STARSHIP_EXTENDED_ENVELOPE_HEIGHT_M=22.0 # historical user guide, mission specific
SPACEX_CLAIMED_KG_PER_KW=1000/75      # nominal quoted power/tonne, denominator unclear

@dataclass(frozen=True)
class Arm:
    name:str
    note:str
    rad_c:float=85.0
    emissivity:float=.85
    view_factor:float=.90 # two-sided view factor; mutual shadows may worsen
    background_k:float=220.0
    absorbed_w_m2:float=75.0
    rad_areal_kg_m2:float=4.6
    pvt_w_m2:float=250.0    # SpaceX AI1 design assumption
    pv_kg_m2:float=1.6
    sunlight_fraction:float=.97
    battery_kg_kw:float=1.0
    computer_and_shield_kg_kw:float=4.0
    bus_and_comms_kg_kw:float=3.0
    structural_mass_credit_kg_kw:float=0.0
    thermal_aux_fraction:float=0.02
    electric_loss_fraction:float=0.06
    sys_margin_fraction:float=0.10
    stow_pv_m:float=.005
    stow_rad_m:float=.018
    packaging_ratio:float=3.0
    junction_c:float=98.0
    mass_claim_comparable:bool=True

ARMS=[
    Arm('C0_modern_radiator','Conventional two-sided radiator, realistic interfaces; no structural integration.',rad_c=78,rad_areal_kg_m2=5.2, sunlight_fraction=.95,battery_kg_kw=1.5),
    Arm('C1_structural_heat_pipe','Structural heat pipes, high emissivity, less panel mass; numerical assumptions need independent coupon.',rad_c=86,emissivity=.90,rad_areal_kg_m2=3.85,structural_mass_credit_kg_kw=1.0, thermal_aux_fraction=.0),
    Arm('C2_film_solar','More mass-efficient photovoltaic film; unverified flight durability / 250W/m2 end-of-life.',rad_c=86,emissivity=.90,rad_areal_kg_m2=3.85,structural_mass_credit_kg_kw=1.0,pv_kg_m2=.85, thermal_aux_fraction=.0),
    Arm('C3_sunlit_orbit','Dawn-dusk orbit with near-continuous solar; operational orbit/communications trade-off.',rad_c=86,emissivity=.90,rad_areal_kg_m2=3.85,structural_mass_credit_kg_kw=1.0,pv_kg_m2=.85,sunlight_fraction=.995,battery_kg_kw=.15,thermal_aux_fraction=.0),
    Arm('C4_short_path_tiles','Spread compute across radiator to shorten thermal path; repair, radiation and interconnect unproven.',rad_c=91,emissivity=.90,rad_areal_kg_m2=3.85,structural_mass_credit_kg_kw=1.0,pv_kg_m2=.85,sunlight_fraction=.995,battery_kg_kw=.15,thermal_aux_fraction=.0,computer_and_shield_kg_kw=4.9,electric_loss_fraction=.09),
    Arm('C5_hot_compute','Higher-temperature electronics: target may fail chip lifetime and warranty; requires hardware test.',rad_c=110,emissivity=.90,rad_areal_kg_m2=3.85,structural_mass_credit_kg_kw=1.0,pv_kg_m2=.85,sunlight_fraction=.995,battery_kg_kw=.15,thermal_aux_fraction=.0,junction_c=127,computer_and_shield_kg_kw=4.9,electric_loss_fraction=.09),
    Arm('C6_truly_light_bus','Very light distributed structures plus PV film; high deployability, stiffness/MMOD risk.',rad_c=91,emissivity=.90,rad_areal_kg_m2=2.2,structural_mass_credit_kg_kw=1.0,pv_kg_m2=.85,sunlight_fraction=.995,battery_kg_kw=.15,thermal_aux_fraction=.0,computer_and_shield_kg_kw=4.9,bus_and_comms_kg_kw=2.0,electric_loss_fraction=.09),
    Arm('C7_no_battery_full_sun','Null-battery fantasy in 100% illumination with eclipse/transients ignored: explicit invalid control.',rad_c=91,emissivity=.90,rad_areal_kg_m2=3.85,structural_mass_credit_kg_kw=1.0,pv_kg_m2=.85,sunlight_fraction=1.,battery_kg_kw=0,thermal_aux_fraction=.0,computer_and_shield_kg_kw=4.9,electric_loss_fraction=.09),
    Arm('C8_high_power_solar','High-output arrays (300W/m2) without mass reduction; more hardening/degradation tests.',rad_c=86,emissivity=.90,rad_areal_kg_m2=3.85,structural_mass_credit_kg_kw=1.0,pvt_w_m2=300,sunlight_fraction=.995,battery_kg_kw=.15,thermal_aux_fraction=.0),
    Arm('C9_structural_pv_backside','Counterexample: shared PV/radiator skin must keep PV and coolant at incompatible temperatures.',rad_c=60,emissivity=.82,view_factor=.65,absorbed_w_m2=200,rad_areal_kg_m2=4.0,structural_mass_credit_kg_kw=1.0,pv_kg_m2=1.0,sunlight_fraction=.97,battery_kg_kw=1.0),
    Arm('C10_conservative','Conservative unknown radiation/deployment/aging penalty.',rad_c=75,emissivity=.80,view_factor=.7,absorbed_w_m2=125,rad_areal_kg_m2=5.8,pv_kg_m2=2.5,sunlight_fraction=.90,battery_kg_kw=4.5,computer_and_shield_kg_kw=6.,bus_and_comms_kg_kw=4.,sys_margin_fraction=.15),
]

def radiative_flux(arm:Arm)->float:
    # 'two-sided' means both faces see their effective background through the view factor.
    T=arm.rad_c+273.15
    return 2*arm.view_factor*arm.emissivity*SIGMA*(T**4-arm.background_k**4)-arm.absorbed_w_m2

def calculate(arm:Arm,power_mw:float=1.0,launch_price_usd_kg:float=500.0,mission_years:float=7.0)->dict:
    p=power_mw*1000.0 # kW of useful electronics input
    sys_kw=p*(1+arm.thermal_aux_fraction+arm.electric_loss_fraction+arm.sys_margin_fraction)
    q_kw=p*(1+arm.thermal_aux_fraction+arm.electric_loss_fraction)
    flux=radiative_flux(arm)
    if flux<=0:raise ValueError('Unphysical: net radiator cooling nonpositive')
    rad_area_m2=q_kw*1000./flux
    pv_area_m2=sys_kw*1000./(arm.pvt_w_m2*arm.sunlight_fraction)
    pv_mass_kg=pv_area_m2*arm.pv_kg_m2
    rad_mass_kg=rad_area_m2*arm.rad_areal_kg_m2
    other_kg=p*(arm.battery_kg_kw+arm.computer_and_shield_kg_kw+arm.bus_and_comms_kg_kw)
    credit_kg=min(p*arm.structural_mass_credit_kg_kw,p*arm.bus_and_comms_kg_kw)
    gross=pv_mass_kg+rad_mass_kg+other_kg-credit_kg
    packed_vol_m3=(rad_area_m2*arm.stow_rad_m+pv_area_m2*arm.stow_pv_m)*arm.packaging_ratio
    envelope_vol_m3=math.pi*(STARSHIP_LEGACY_ENVELOPE_DIAMETER_M/2)**2*STARSHIP_EXTENDED_ENVELOPE_HEIGHT_M
    rad_delta_k=arm.junction_c-arm.rad_c
    return {
      'arm':arm.name,'power_mw':power_mw,'radiative_flux_w_m2':round(flux,1),
      'pv_area_m2':round(pv_area_m2,1),'rad_area_m2':round(rad_area_m2,1),
      'pv_mass_t':round(pv_mass_kg/1000,2),'radiator_mass_t':round(rad_mass_kg/1000,2),
      'total_mass_t':round(gross/1000,2),'mass_kg_kw':round(gross/p,2),
      'starship_100t_launches_mass_floor':math.ceil(gross/STARSHIP_DESIGN_LEO_KG),
      'packed_volume_m3_screen':round(packed_vol_m3,1),
      'legacy_envelope_m3_screen':round(envelope_vol_m3,1),
      'starship_8x22m_loads_volume_floor':math.ceil(packed_vol_m3/envelope_vol_m3),
      'annual_launch_only_usd_kw':round((gross*launch_price_usd_kg)/(mission_years*p),1),
      'delta_junction_radiator_k':round(rad_delta_k,2),
      'thermal_margin_screen': 'FAIL: T_j<=T_rad' if rad_delta_k<=0 else 'NOT QUALIFIED: dT budget and hotspot closure unverified',
      'validation':'CONCEPT ONLY / no deployed structure, thermal-vacuum or hardware evidence',
    }

def main()->None:
   here=Path(__file__).resolve().parent
   rows=[calculate(a,1) for a in ARMS]
   rows4=[calculate(a,4) for a in ARMS]
   with (here/'SCREEN_1MW.csv').open('w',newline='') as f:
      writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()));writer.writeheader();writer.writerows(rows)
   with (here/'SCREEN_4MW.csv').open('w',newline='') as f:
      writer=csv.DictWriter(f,fieldnames=list(rows4[0].keys()));writer.writeheader();writer.writerows(rows4)
   base=rows[0];valid=[r for r in rows if r['arm'] not in ('C5_hot_compute','C7_no_battery_full_sun')]
   result={
       'purpose':'First-order triage not a multi-physics flight simulator',
       'conventional':base,
       'best_mass_with_assumptions':min(valid,key=lambda r:r['mass_kg_kw']),
       'spacex_public_75kw_per_ton_mass_kg_kw':round(SPACEX_CLAIMED_KG_PER_KW,2),
       'spacex_metric_comparability':'NOT CONFIRMED: peak vs sustained and bus scope may differ',
       'warn':'All arms are physically unqualified. Parametric hypothetical mass improvements are not discoveries.',
       'inputs':{a.name: vars(a) for a in ARMS},'one_mw':rows,'four_mw':rows4}
   (here/'RESULTS.json').write_text(json.dumps(result,indent=2))
   print('1MW C0',base['mass_kg_kw'],'kg/kW')
   for z in rows:
      print(z['arm'],z['mass_kg_kw'],'kg/kW',z['pv_area_m2'],'PV m2',z['rad_area_m2'],'radiator m2')
   print('Best (not flight-validated)',result['best_mass_with_assumptions']['arm'])
if __name__=='__main__':main()

def adversarial_corner_sweep()->dict:
    """NOT probabilities: cartesian assumption corners where optimistic design survives."""
    from itertools import product
    base=next(a for a in ARMS if a.name=='C6_truly_light_bus')
    data=[]
    for pv_dens,rad_dens,rad_c,sun_frac,margin in product(
        [.85,1.2,1.6,2.0],[2.2,3.5,5.0],[75,85,91],[.95,.98,.995],[.10,.15]):
        a=replace(base,pv_kg_m2=pv_dens,rad_areal_kg_m2=rad_dens,rad_c=rad_c,sunlight_fraction=sun_frac,sys_margin_fraction=margin)
        x=calculate(a,1)
        data.append({**x,'pv_density':pv_dens,'rad_density':rad_dens,'rad_c':rad_c,'sun_fraction':sun_frac,'system_margin':margin})
    m=[r['mass_kg_kw'] for r in data]
    result={
      'grid_cases':len(data),'not_a_probability':'All equally enumerated sensitivity corners, NOT an estimated probability distribution',
      'kg_per_kw_range':[round(min(m),2),round(max(m),2)],
      'kg_per_kw_median_grid':round(sorted(m)[len(m)//2],2),
      'cases_below_spacex_claim_metric':sum(x<SPACEX_CLAIMED_KG_PER_KW for x in m),
      'cases_below_conventional_screen':sum(x<calculate(ARMS[0],1)['mass_kg_kw'] for x in m),
      'starship_metric_scope_unverified':True,
    }
    here=Path(__file__).resolve().parent
    with (here/'SENSITIVITY_CORNERS.csv').open('w',newline='') as f:
      w=csv.DictWriter(f,fieldnames=list(data[0].keys()));w.writeheader();w.writerows(data)
    (here/'SENSITIVITY_SUMMARY.json').write_text(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
   print('ADVERSARIAL SENSITIVITY',adversarial_corner_sweep())
