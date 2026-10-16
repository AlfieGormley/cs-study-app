---
id: elec-unloaded-divider
sourceLesson: elec-dividers
title: "Deriving an unloaded voltage divider"
level: basic
minutes: 2
summary: "The output is the bottom resistor’s share of the input."
---

The output is the bottom resistor’s share of the input.

## The voltage divider
Two resistors in series across a supply split the voltage in proportion to their resistances. The output is taken from the junction:

```diagram
 Vin ──┐
       R1
       ├──── Vout
       R2
 GND ──┘
```

The formula comes straight from the two laws in the voltage and current units. The resistors are in series, so one current flows through both, set by their total. Ohm's law on R2 alone then gives the voltage across it:

```formula
I = Vin / (R1 + R2)
Vout = I × R2
Vout = Vin R2 / (R1 + R2)
where
I: the current flowing down through both resistors, in amperes (A)
Vin: the input (supply) voltage across the whole divider, in volts (V)
Vout: the output voltage, measured from the junction to ground, in volts
R1: the top resistor, between Vin and the output, in ohms (Ω)
R2: the bottom resistor, between the output and ground, in ohms
In words: the output is the input voltage scaled by the bottom resistor's share of the total resistance. This holds only when nothing draws current from the output.
```

Two examples:

```formula
Vout = 3.3 V × 10 kΩ / (10 kΩ + 10 kΩ)
Vout = 3.3 V × 0.5 = 1.65 V
Vout = 5 V × 10 kΩ / (20 kΩ + 10 kΩ)
Vout = 5 V × 1/3 ≈ 1.67 V
where
Vout: the divider's unloaded output, in volts (V)
V: volts, the unit of voltage
kΩ: kilohms; 1 kΩ = 1000 ohms
≈: approximately equal to (rounded)
In words: two equal resistors halve the voltage. With 20 kΩ on top and 10 kΩ below, the bottom resistor is a third of the total, so you get a third of the 5 V.
```

The ratio sets the output, not the individual resistance values. 1 kΩ/1 kΩ and 100 kΩ/100 kΩ both halve the voltage when unloaded.

The individual resistance values still matter in two ways. They set the divider standing current (and so the wasted power), and they determine how badly the output sags when something draws current from it.

## Key takeaways

- The output is the bottom resistor’s share of the input.
- An unloaded ratio says nothing about how well a divider drives a load.

## Further reading

- [SparkFun: voltage dividers](https://learn.sparkfun.com/tutorials/voltage-dividers/all)
- [OpenStax: series and parallel resistors](https://openstax.org/books/university-physics-volume-2/pages/10-2-resistors-in-series-and-parallel)
