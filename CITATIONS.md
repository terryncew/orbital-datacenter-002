# References — verified

Every source below was checked to exist and to say what the paper claims
it says. URLs are the primary sources consulted. Where a source was found
to be misattributed or withdrawn in an earlier version, it is listed under
"Removed" with the reason — the paper does not cite it.

"Orbital 001", referenced below, is the unpublished predecessor manuscript
from the same program (defined in PAPER.md Section 1, compared in
Section 4.3). It is not a published source and is not cited as one.

## Cited sources

1. **Turyshev, S. G., "Orbital Data Centers: Spacecraft Constraints and
   Economic Viability", arXiv:2604.27197 (29 Apr 2026).**
   https://arxiv.org/abs/2604.27197
   Supports: 1 MW anchor — PV 5,640 m², radiator 2,500 m², 29.4 kg/kW for
   PV + storage + radiator; 34–59 kg/kW total; $250–$1,000/kg allowance at
   $10–40k/kW terrestrial benchmark; regimes C1/C2/C3.

2. **Turyshev, S. G., follow-up on orbital data-center operations and
   maintenance, arXiv:2608.27499 (2026).**
   https://arxiv.org/abs/2608.27499
   Supports: 393–419 standardized operations per MW-year; 5.3–9.0
   t/(MW-year) logistics. Cited as prior art challenging the hot-swap
   servicing model.

3. **Agüera y Arcas, Beals et al. (Google), "Towards a future space-based,
   highly scalable AI infrastructure system design" (Project Suncatcher),
   2025; arXiv:2511.19468; Joule, 1 Oct 2026.**
   https://services.google.com/fh/files/misc/suncatcher_paper.pdf
   Supports: 81-satellite cluster at 650 km; 4-Trillium-TPU prototype
   launched 1 Oct 2026 on Transporter-18; TPUs run ~15-minute bursts then
   cool; heat pipes + radiators tested in TVAC.
   Does NOT support: any thermal design. The paper names no bus class, no
   heat-pipe type, no facesheet material, and no TIM type. Architecture
   Arm C is a modeled reference, not the Suncatcher design.

4. **SpaceX, Starmind AI1 product page.**
   https://www.spacex.com/spacexai/starmind
   Supports (www envelope): 250 kW peak / 175 kW average / 75 kW/ton /
   30 m × 75 m. From these figures the audit derives 3,333.3 kg implied
   dry mass, 13.33 kg/kW on the peak denominator, and 19.05 kg/kW on the
   continuous-average denominator.
   Envelope instability (verified): on 24 Aug 2026 new.spacex.com served
   a smaller envelope the same day — 150 kW peak / 120 kW average /
   70 kW/ton / 20 m × 70 m, giving 2,142.9 kg and 17.86 kg/kW on the
   continuous denominator. The paper states which envelope it uses (www,
   250 kW) and the alternate.

5. **BCG (Elbert, Werle, Nasr, O'Niell), "Space-Based Data Centers: Cost
   and Outlook to 2040", 27 Aug 2026.**
   https://www.bcg.com/publications/2026/space-based-data-centers-cost-outlook
   Supports: 20-yr TCO $660–750M/MW orbital vs $230–300M/MW terrestrial;
   2.5–3× premium today, ~1.5× realistic improvement, 1.1–1.2× aggressive.
   Verified live. The paper's terrestrial benchmark ($220M/MW) sits below
   BCG's range; the ratio sensitivity (1.185× / 1.04× / 0.91× at BCG low /
   midpoint / high end) is computed from BCG's range and the executed
   Arm O figure. BCG's orbital figure is today's costs, not 002's modeled
   future costs.

6. **Gaalema, Indyk, Staley, "Reduced-Mass Orbital AI Inference via
   Integrated Solar, Compute, and Radiator Panels", arXiv:2604.07760
   (9 Apr 2026).**
   https://arxiv.org/abs/2604.07760
   Supports: integrated solar/compute/radiator panels; claims >100 kW/ton,
   16 MW / 150 t, junction ~40 °C. Arm I's basis; 002's model rejects the
   coplanar variant on view-factor/Earth-IR grounds. The paper states the
   disagreement and does not claim a refutation of the arXiv paper (a
   design study with its own assumptions).

7. **ICEF, Sandalow et al., "Space-Based Data Centers Roadmap: The Case
   for Caution", working paper, Nov 2026 (NOT peer-reviewed).**
   https://icef.go.jp/wp-content/themes/icef_new/pdf/roadmap/2026/ICEF%20Space-Based%20Data%20Centers%20Roadmap%20Nov%202026.pdf
   Supports: 10% of 2030 AI demand from orbit = 700+ Starship launches/yr
   in perpetuity; 50× satellite increase; "weights claimed by leading
   developers appear highly optimistic and beyond currently-proven
   technology"; phased deployment recommended.

8. **SpaceX, Starship Users Guide Rev 1.0 (Mar 2020).**
   https://spacex.relayto.com/e/starship-users-guide-37uiuuepbks0x/SDpUqC8k3
   Supports: 9 m outer diameter, 8 m dynamic envelope, extended volume up
   to 22 m height. The 665 m³ (standard) / 905 m³ (extended) volumes are
   computed from the guide's dimensions, not guide-quoted figures. The
   guide is a 2020 preliminary document; the volume bound is not a
   certified usable payload or interface.

9. **NASA / Redwire, ISS Roll-Out Solar Array (iROSA) / ROSA: flown
   (8 wings, ~28 kW each, composite booms).**
   https://www.nasa.gov/directorates/stmd/impact-story-roll-out-solar-arrays/
   Supports: iROSA is flown hardware. Does NOT support: a per-m² boom
   mass — the flysheet publishes none, which is why the F002-1 adders are
   labeled assumed inputs.

10. **U.S. Government Accountability Office, "Science & Tech Spotlight:
    Data Centers in Space", GAO-26-109012 (April 2026).**
    https://www.gao.gov/products/gao-26-109012
    Supports: space does not cool hardware efficiently; cooling at
    data-center scale unproven; solar arrays for large facilities would
    exceed any launched or assembled as of April 2026.

11. **SpaceX, SEC Free Writing Prospectus (filed 9 Jun 2026, Reg. No.
    333-296070), CFO interview and Musk/Dahl/Huot conversation.**
    https://www.sec.gov/Archives/edgar/data/1181412/000162828026041761/fwp_cfointerview.htm
    Supports: AI1 first design — 150 kW peak / 120 kW sustained power;
    ~110 m² deployable liquid radiator at 1,400 W/m² (both sides
    combined); pumped liquid radiator with redundant pump loops. The
    001 paper used this 150 kW envelope; this paper uses the www envelope
    and states the difference.

12. **mlq.ai / Tom's Hardware, Nov 2026: Kessel 72-GPU Rubin rack for
    SpaceX AI1 (SECONDARY REPORTING, not confirmed).**
    https://mlq.ai/news/spacex-is-designing-kessel-a-72-gpu-nvidia-rubin-rack-for-data-centers-in-space-report-says/
    Attributed as reported, not confirmed.

13. **ThermAvant Technologies, oscillating heat pipe product documentation
    and catalogue.**
    https://www.thermavant.com/oscillating-heat-pipes
    Supports: OHP heat spreaders, transporters, and heat sinks at TRL 9;
    OHP satellite radiators at TRL 7 (not 9); structural OHP panels at
    1.6 g/cm³ effective density (Al-6061/Ti construction); first flight
    2017 (ASETS-II, X-37B); >10 million on-orbit operating hours (Apr 2026).

14. **Revell, L. E. et al., "Near-future rocket launches could slow ozone
    recovery", Communications Earth & Environment (2025).**
    https://pmc.ncbi.nlm.nih.gov/articles/PMC12148926/
    Supports: ambitious scenario (2,040 launches/yr) → −0.29% annual-mean
    near-global total column ozone in 2030, Antarctic spring −3.9%;
    conservative scenario (884/yr) → −0.17%; ozone loss driven by chlorine
    from solid motors and black carbon; alumina alone has little impact on
    ozone in the quantities modeled.

15. **Barker, C., Marais, E. et al., "Radiative Forcing and Ozone
    Depletion of a Decade of Satellite Megaconstellation Missions",
    Earth's Future (2026), DOI 10.1029/2025EF007229.**
    Supports: ~870 tonnes black carbon/yr by 2029; ~20 tonnes black carbon
    per Falcon 9 launch; black carbon 540× more potent per unit mass than
    surface soot; 2.5–3 year residence. Authors are at UCL, not TU Delft.

16. **Ferreira et al., re-entry alumina modelling, Geophysical Research
    Letters (2024).**
    Supports: a 250 kg satellite at 30% aluminum with ~32% of aluminum
    oxidised yields just under 30 kg alumina — ~0.12 kg per kg of
    satellite. Cited as the realistic reference against the model's
    assigned ablation fractions.

17. **Sharma, S. P., "Impact of Spaceflight on Earth's Atmosphere:
    Climate, Ozone, and the Upper Atmosphere", NASA/TM−20240013276
    (Oct 2024).**
    https://ntrs.nasa.gov/api/citations/20240013276/downloads/NASA-TM-20240013276-V6.pdf
    Supports: launch black carbon / NOx / H₂O and re-entry alumina as
    stratospheric pollutants; launch tonnage rising 3,500 → >30,000 t/yr
    by 2040; re-entry flux 1,000 → >30,000 t/yr.

18. **Presler, A. F., Coles, C. E., Diem-Kirsop, P., & White, K. A.,
    "Liquid droplet radiator program at the NASA Lewis Research Center"
    (1985).**
    https://ntrs.nasa.gov/citations/19870035127
    Supports: the liquid droplet radiator concept (droplets sprayed,
    radiate, collected and recycled; ~100 µm droplets).

19. **JAXA SDS-4 / IHTC-17 2023 review, "Toward LEO Applications: The
    Scientific Journey of the Space Pulsating Heat Pipe".**
    https://arxiv.org/pdf/2312.11055
    Supports: flown pulsating heat pipes — JAXA SDS-4 (2012–), ISS Space
    PHP consortium, ASETS-II on X-37B (780 days), ACT pulsating heat pipes
    (ISS 2017).

20. **Advanced Cooling Technologies (ACT), honeycomb radiator panels;
    Beyond Gravity, thermo-structural radiator panels.** (Vendor
    catalogues.)
    Supports: the nearest prior art for structure + radiator + embedded
    heat pipe in one panel — ACT aluminum honeycomb sandwich panels
    serving as spacecraft structural shells and radiators with embedded
    CCHPs; Beyond Gravity panels up to 6 kW each, up to 18 m², with
    optional embedded heat pipe networks. Neither integrates an electrical
    power bus as a fourth function, and neither uses an oscillating heat
    pipe as the primary-structure load path.

## Removed — do not cite

- **"22.29 kg/kW modeled in Arm B": withdrawn.** Appears only as a
  hardcoded string in an earlier falsification script; no code computes
  it. Replaced by the assigned all-in continuous range 19.05–24.80 kg/kW.
- **Held-out replay figures (Arm D $32,126.74, Arm O $16,668.42,
  −48.12%): stale.** Executed values differ, and the replay engine is not
  in this package. Excluded from the paper.
- **"5 assumptions" in the falsify script: corrected.** Four waterfall
  steps plus end-of-life degradation in Arm G.
- **NASA TM-88908 as a liquid-droplet-radiator source (carried over from
  001): fabricated.** TM-88908 is a supersonic aircraft fan paper,
  unrelated to radiators. Replaced by reference 18 above.
- **"TU Delft, Earth's Future 2026" attribution (carried over from 001):
  wrong.** The 2026 Earth's Future paper on this topic is Barker/Marais,
  UCL (reference 15).
