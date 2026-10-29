---
id: elec-unloaded-divider
sourceLesson: elec-dividers
title: "Understanding an unloaded voltage divider"
level: basic
minutes: 2
summary: "The output is the bottom resistor’s share of the input."
---

A voltage divider uses two series resistors to make a fraction of a supply voltage. It is useful for a signal or reference feeding an input that draws very little current.

```diagram
 Vin ──┐
       R1
       ├──── Vout
       R2
 GND ──┘
```

## The lower resistor sets the output’s share
The same current flows through both resistors when the output is unloaded. The larger resistor therefore has the larger voltage drop. The output is measured from the junction to ground, so it is the voltage across the lower resistor.

Equal resistors divide the supply in half: two 10 kΩ parts across 3.3 V give 1.65 V unloaded. Making the upper resistor larger moves the junction towards ground; making the lower resistor larger moves it towards the supply.

```formula reference
Vout = Vin R2 / (R1 + R2)
where
Vout: unloaded junction voltage relative to ground, in volts (V)
Vin: voltage across the whole divider, in volts
R1: upper resistor from the supply to the junction, in ohms (Ω)
R2: lower resistor from the junction to ground, in ohms
In words: The output is the supply voltage multiplied by the lower resistor’s share of the total resistance. This assumes no current is drawn from the junction.
```

## Same ratio, different ability to drive a load
A pair of 1 kΩ resistors and a pair of 100 kΩ resistors both halve the voltage when unloaded. The smaller pair draws more continuous current from the supply but is less disturbed by a load. The larger pair wastes less power but its voltage is easier to pull down.

The ratio alone cannot tell you whether a real circuit will work. The next lesson adds the load; do not use an unloaded divider calculation as proof that it can power another board.

## Key takeaways

- The output is the lower resistor’s share of the supply.
- Changing both resistances by the same factor preserves the unloaded ratio.
- Resistance scale still determines current consumption and loading error.

## Further reading

- [SparkFun: voltage dividers](https://learn.sparkfun.com/tutorials/voltage-dividers/all)
- [OpenStax: series and parallel resistors](https://openstax.org/books/university-physics-volume-2/pages/10-2-resistors-in-series-and-parallel)
