---
id: elec-series-parallel-resistors
sourceLesson: elec-dividers
title: "Combining series and parallel resistors"
level: basic
minutes: 3
summary: "Series resistances add; parallel branches share a voltage."
---

A common analogue knob on a microcontroller synth uses a potentiometer as a voltage divider. The board reads its wiper voltage with an ADC and turns it into a number; encoders and other controls work differently. To wire knobs correctly, and to understand why some readings come out wrong, you need series and parallel resistance and the divider formula.

## Series: one path, resistances add
Components in **series** (a series circuit) share a single current path. The same current flows through each one, and their voltages add up to the total. Because the current has to push through every resistor in turn, their resistances simply add:

```formula
R_total = R1 + R2 + R3 + ...
where
R_total: the single resistance that behaves the same as the whole chain, in ohms (Ω)
R1: the first resistor in the chain, in ohms
R2: the second resistor, in ohms
R3: the third resistor, in ohms
...: and so on, for as many resistors as are in the chain
Ω: ohms, the unit of resistance
In words: resistors in series add up. The total is always larger than the largest one.
```

For example, a 1 kΩ and a 2.2 kΩ in series:

```formula
R_total = R1 + R2
R_total = 1 kΩ + 2.2 kΩ = 3.2 kΩ
where
R_total: the combined resistance, in ohms (Ω)
R1: the first resistor, here 1 kΩ
R2: the second resistor, here 2.2 kΩ
kΩ: kilohms; 1 kΩ = 1000 ohms (Ω)
In words: the pair behaves exactly like one 3.2 kΩ resistor.
```

## Parallel: several paths, conductances add
Components in **parallel** (a parallel circuit) connect across the same two connection points, so they all have the **same voltage**. The currents split between the branches and add up to the total. Each extra branch is another path for current, so the combination conducts *more* easily than any branch alone.

The easy way to add them is by **conductance**, which is one divided by resistance (how easily current flows). Conductances in parallel add:

```formula
1 / R_total = 1 / R1 + 1 / R2 + ...
where
R_total: the single resistance that behaves the same as all the branches together, in ohms (Ω)
R1: the first branch's resistance, in ohms
R2: the second branch's resistance, in ohms
...: and so on, one term per branch
Ω: ohms, the unit of resistance
In words: add up one-over-resistance for every branch, then take one over the answer. Each branch adds a path, so the total always comes out smaller than the smallest branch.
```

For exactly two resistors this rearranges into a handier "product over sum" form. The symbol ∥ is shorthand for "in parallel with":

```formula
R1 ∥ R2 = (R1 R2) / (R1 + R2)
where
R1 ∥ R2: the combined resistance of R1 and R2 in parallel, in ohms (Ω)
∥: "in parallel with"
R1: the first resistor, in ohms
R2: the second resistor, in ohms
Ω: ohms, the unit of resistance
In words: for two resistors in parallel, multiply them, then divide by their sum.
```

Three facts are worth memorising:

- Two equal positive resistors in parallel give half the value: two 10 kΩ parts combine to 5 kΩ.
- The parallel total is always **smaller than the smallest** branch.
- A much larger resistor in parallel barely changes anything:

```formula
10 kΩ ∥ 1 MΩ = (10 kΩ × 1000 kΩ) / 1010 kΩ
10 kΩ ∥ 1 MΩ ≈ 9.9 kΩ
where
∥: "in parallel with"
kΩ: kilohms; 1 kΩ = 1000 ohms (Ω)
MΩ: megohms; 1 MΩ = 1000 kΩ = 1,000,000 Ω
≈: approximately equal to (rounded)
In words: putting a 1 MΩ resistor across a 10 kΩ one lowers it by only about 1%, because almost all the current takes the easier 10 kΩ path.
```

## Key takeaways

- Series resistances add; parallel branches share a voltage.
- For positive finite resistances, a parallel total is below the smallest branch.

## Further reading

- [OpenStax: series and parallel resistors](https://openstax.org/books/university-physics-volume-2/pages/10-2-resistors-in-series-and-parallel)
