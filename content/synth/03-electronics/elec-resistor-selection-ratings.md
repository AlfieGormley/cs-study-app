---
id: elec-resistor-selection-ratings
sourceLesson: elec-components
title: "Preferred resistor values and ratings"
level: intermediate
minutes: 2
summary: "Choose an actual preferred value, then recalculate the result."
---

Choosing a resistor means choosing an available value and checking whether the real part can do the job safely. A nominal calculation is the starting point.

## Choose from the table, then check the circuit
Preferred resistor values are published in E-series tables. E12 has twelve values in each tenfold range: 10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68 and 82. E24 provides more choices. These series are traditionally associated with 10% and 5% tolerances, but the actual part’s specification determines its tolerance.

The values are approximately evenly spaced in percentage terms. Use the published table rather than generating production values from an approximate geometric formula.

Choose in the direction that suits the circuit. For a resistor limiting nominal LED current, rounding resistance upward reduces current. For a divider or filter, a larger value is not automatically better: check the new ratio or response.

## Nominal value is not an exact value
Component tolerance is the allowed initial departure from the marked resistance. A 10 kΩ ±5% resistor may be 9.5–10.5 kΩ under its specified measurement conditions. Temperature and ageing can add further changes.

For a divider, two resistor errors can reinforce each other: a smaller upper resistor and larger lower resistor raise the output. More precise parts reduce this uncertainty, but do not fix loading or supply variation.

## Check heat and conditions
A resistor dissipation rating specifies the continuous heat allowed under stated thermal conditions. A nominal 0.25 W label does not guarantee that the resistor stays cool, or that the full rating applies at every temperature and mounting arrangement.

Check the circuit using the selected value and tolerance. For an LED resistor, the highest supply, lowest LED forward voltage and lowest allowed resistance give the highest estimated current. Check the corresponding resistor heat, LED limits, GPIO per-pin and total-current limits, and the resistor’s derating curve. A rule such as using half the wattage rating can be a starting margin, but it does not replace those checks.

## Key takeaways

- Select an actual preferred value and reassess the circuit’s behaviour.
- Tolerance and loading are different sources of error.
- Heat, voltage and operating conditions still matter at low supply voltages.

## Further reading

- [Vishay: preferred-value table, IEC 60063](https://www.vishay.com/docs/28372/e-series.pdf)
- [Vishay: resistor colour code](https://www.vishay.com/docs/49411/resistor_color_code_calculator.pdf)
- [OpenStax: electrical energy and power](https://openstax.org/books/university-physics-volume-2/pages/9-5-electrical-energy-and-power)
- [Vishay MRS16/MRS25: thermal conditions and derating](https://www.vishay.com/docs/28724/mrs16m25.pdf)
