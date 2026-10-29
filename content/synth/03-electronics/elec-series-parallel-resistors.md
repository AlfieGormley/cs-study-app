---
id: elec-series-parallel-resistors
sourceLesson: elec-dividers
title: "Combining series and parallel resistors"
level: basic
minutes: 2
summary: "Series resistances add; parallel branches share a voltage."
---

How resistors connect matters as much as their values. Trace which terminals share a connection before predicting the current.

## Series adds obstacles in one path
Components in a series circuit share one current path. The same current passes through each component; it is not used up along the way. Their voltage drops add to the supply voltage in this simple DC loop.

For resistors, series resistance adds. A 1 kΩ resistor followed by 2.2 kΩ behaves like 3.2 kΩ in the ideal model. Across the same supply, adding a positive series resistance reduces current.

## Parallel adds another path
Components in a parallel circuit connect across the same two nodes, so they have the same voltage. Each branch carries its own current, and those currents add at the supply. Adding a positive resistive branch increases total current from an ideal fixed-voltage supply; it does not reduce the voltage across the existing branch.

For positive finite resistors, the combined resistance is below the smallest branch. Two equal 10 kΩ resistors in parallel behave like 5 kΩ. A much larger parallel resistance has less effect: 1 MΩ across 10 kΩ gives about 9.9 kΩ because the added branch draws little extra current.

Conductance means how easily a path passes current: it is the reciprocal of resistance. Conductances add in parallel. For two resistors the useful calculation is:

```formula reference
R_total = (R1 R2) / (R1 + R2)
where
R_total: equivalent resistance of the parallel pair, in ohms (Ω)
R1: first positive branch resistance, in ohms
R2: second positive branch resistance, in ohms
In words: Two resistors connected across the same nodes provide more current paths, so their combined resistance is smaller than either one.
```

This reasoning assumes fixed, ohmic resistors and a supply that holds its voltage. A real supply can sag or enter current limit if the added branch demands too much current.

> [!analogy] Real-world analogy: One doorway or another route
> People moving through two narrow doorways in a row face both restrictions. Opening a separate route lets more people pass overall.
>
> **How it maps:** Series resistors put restrictions along one path; a parallel branch provides an additional path for current.
>
> **Where it stops:** People can wait and choose routes. In this steady electrical model, branch currents follow the applied voltage and resistance, and charge does not accumulate at a junction.

## Key takeaways

- Series parts share current; parallel parts share voltage.
- An extra series resistor reduces current from a fixed supply; an extra parallel branch increases total current.
- Use the connection pattern to sanity-check a calculated resistance.

## Further reading

- [OpenStax: series and parallel resistors](https://openstax.org/books/university-physics-volume-2/pages/10-2-resistors-in-series-and-parallel)
