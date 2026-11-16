# Reusable Thermal-Structural Spines for Orbital Computing — plain-English summary

## The question

Can you cool a data center in space cheaply enough to beat building it on
Earth? The cooling problem is the whole game: a chip in orbit has nowhere
to dump its heat except by radiating it into the cold dark, and every
kilogram of radiator, solar panel, and structure has to be launched.

## The embarrassing correction first

The study started with a seductive number. An independent screen said a
"truly light" thin-film design could run a data center at **11.93 kg per
kW** — lighter than SpaceX's published AI1 figure of 13.33 kg/kW, which
looked like a breakthrough.

It was wrong. When the audit put back the parts the screen had left out —
the booms and wiring that hold the panels up, a realistic temperature drop
from chip to radiator, the fact that panels shadow each other, and the
launch strongback — the number climbed step by step: 15.20, 15.71, 16.34,
then **19.44 kg/kW**. That is 63% heavier than claimed. As a full system,
with solar panels aging over 20 years, it is 20.66 kg/kW. And when the
assumptions were varied across 216 combinations, only 25 of them stayed
below 13.33. The breakthrough was an accounting omission, not a design.
The paper keeps the failed design in the open instead of deleting it,
because that is the point: the correction is a result, not an embarrassment
to hide.

## What survived

Throwing out the light bus forced a better idea. Instead of rebuilding the
whole satellite every time the chips get old, keep the expensive parts in
orbit for 20 years — the solar arrays, the radiators, the optical spine —
and swap only the compute blades, dry-clamped in place like cartridges.
That is Arm O, the reusable spine. It cuts 20-year cost by 37% against a
conventional orbital design and by 33% against the modeled SpaceX AI1
reference, and it cuts re-entry alumina by 95% because so much less mass
comes down.

## Earth still wins

Here is the part the paper does not soften: Arm O still costs **1.24
times as much as a terrestrial data center** — $273 million per megawatt
over 20 years against $220 million on Earth, at $500 per kilogram of
launch. And making launch free does not fix it: at $0/kg, Arm O is still
1.17 times Earth. The gap is not the rocket. It is space hardware,
servicing, radiation spares, and insurance. For orbit to win at general AI
work, launch would have to fall below $200/kg *and* space hardware costs
would have to fall by almost half, at the same time.

There is one conditional exception. If 18% of the machine's time can be
sold for work that can only be done in orbit — watching Earth, radar,
secure relay — at an assumed $4,850 per kW-year, the rest of the bill lands
roughly at Earth's level. That price is assumed, not observed. Nobody has
paid it yet.

## What is not proven

Nothing here has flown. No prototype has been built, no vacuum test has
passed. The decisive test is a small coupon in a vacuum chamber: clamp a
compute blade to the spine, pull it off, clamp it again twenty times, and
measure whether heat still flows. If it does not, the whole reusable-spine
case collapses and the study says so in advance. The paper also refuses
the easy environmental story: orbit saves land, water, and grid power, but
it adds black carbon and alumina to the stratosphere, where their effects
are unmeasured. No environmental advantage is claimed.

Read the full paper in `PAPER.md`. Every number in it can be regenerated
from the code with one command: `python3 simulation/run_reproduction.py`.
