import unittest
from dataclasses import replace
from tournament import ARMS,calculate,radiative_flux,STARSHIP_DESIGN_LEO_KG
class Physics(unittest.TestCase):
 def test_area_scales_linear_with_power(self):
  a=calculate(ARMS[0],1); b=calculate(ARMS[0],4)
  self.assertAlmostEqual(b['rad_area_m2']/a['rad_area_m2'],4,delta=.02)
 def test_radiation_grows_with_temp(self):
  a=ARMS[0]; self.assertGreater(radiative_flux(replace(a,rad_c=95)),radiative_flux(a))
 def test_thermo_penalty_sun_irradiation(self):
  a=ARMS[0]; self.assertLess(radiative_flux(replace(a,absorbed_w_m2=200)),radiative_flux(a))
 def test_stowed_volume_gross_bound(self):
  for arm in ARMS:
   r=calculate(arm,1);self.assertGreater(r['starship_100t_launches_mass_floor'],0)
 def test_pv_power_fraction_monotonic(self):
  a=ARMS[0]; x=calculate(a,1); y=calculate(replace(a,sunlight_fraction=.5),1)
  self.assertGreater(y['pv_mass_t'],x['pv_mass_t'])
 def test_mass_credit_capped_to_bus_mass(self):
  a=ARMS[0]; x=calculate(replace(a,structural_mass_credit_kg_kw=20),1); y=calculate(replace(a,structural_mass_credit_kg_kw=a.bus_and_comms_kg_kw),1)
  self.assertAlmostEqual(x['total_mass_t'],y['total_mass_t'])
 def test_unphysical_flux_rejected(self):
  a=ARMS[0];
  with self.assertRaises(ValueError): calculate(replace(a,rad_c=-250,absorbed_w_m2=500),1)
 def test_increasing_mass_increases_launch_floor(self):
  a=ARMS[0]; x=calculate(a,1);y=calculate(replace(a,computer_and_shield_kg_kw=100),1)
  self.assertGreater(y['total_mass_t'],x['total_mass_t'])
if __name__=='__main__':unittest.main()
