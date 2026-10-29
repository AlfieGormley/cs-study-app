---
id: elec-divider-loading
sourceLesson: elec-dividers
title: "Loading, source resistance and divider limits"
level: basic
minutes: 3
summary: "Combine a resistive load with the bottom resistor first."
---

A divider voltage can look right on paper and fall when you connect the next circuit. The added circuit draws current: it becomes part of the circuit you must analyse.

## A load changes the divider
A resistive load connected from the divider output to ground sits in parallel with the lower resistor. That combination has less resistance, so the output moves towards ground. The unloaded resistor ratio no longer describes it.

For example, two 10 kΩ resistors across 3.3 V give 1.65 V unloaded. Adding a 10 kΩ load makes the lower pair equivalent to 5 kΩ and pulls the output down to 1.10 V. These are ideal resistive examples, not measurements of a particular board.

## Source resistance tells you how easily it moves
The divider’s output resistance describes it as an ideal voltage source with a resistance in series. For a divider driven by an ideal voltage supply, its upper and lower resistors appear in parallel when finding that output resistance. This is a circuit-analysis step, not an instruction to short a real supply.

```formula reference
R_out = (R1 R2) / (R1 + R2)
where
R_out: divider output resistance with an ideal independent voltage supply, in ohms (Ω)
R1: upper divider resistance, in ohms
R2: lower divider resistance, in ohms
In words: The divider has a finite source resistance. A load much larger than this resistance changes its voltage less; a comparable load causes substantial sag.
```

Two 10 kΩ resistors have 5 kΩ output resistance. A resistive load ten times the output resistance causes about 9.1% sag; one hundred times causes about 1% sag. Choose against your allowed error, not a universal ten-times rule.

Reducing both divider resistances keeps the unloaded voltage but reduces sag for the same load. The cost is more divider standing current and power consumption. Raising both values does the opposite.

## An ADC is not just a resistor
Many ADC inputs briefly connect a sampling capacitor. A high source resistance may not charge it to the new voltage within the ADC acquisition time. The error can have either sign, depending on the capacitor’s previous charge. Check the specific ADC’s source-impedance and sampling-time guidance; a DC meter reading alone cannot confirm correct sampling.

## A divider is not a regulated power supply
A board draws significant, varying current. A high-resistance divider cannot maintain its intended voltage under that load. A dummy resistor can illustrate the sag, but it does not predict a real board’s startup behaviour. Use an appropriately specified voltage regulator for power, checking input range, output current, heat and required capacitors.

## Key takeaways

- A resistive load to ground pulls the divider output down.
- Lower source resistance improves loading error at the cost of continuous current.
- Check ADC acquisition requirements and use a regulator for board power.

## Further reading

- [TI: linear-regulator fundamentals](https://www.ti.com/video/series/power-fundamentals-linear-regulator-fundamentals.html)
- [SparkFun: voltage dividers](https://learn.sparkfun.com/tutorials/voltage-dividers/all)
- [OpenStax: series and parallel resistors](https://openstax.org/books/university-physics-volume-2/pages/10-2-resistors-in-series-and-parallel)
- [Microchip: ADC acquisition time](https://developerhelp.microchip.com/xwiki/bin/view/products/data-converters/adc-specs/acquisition-time/)
