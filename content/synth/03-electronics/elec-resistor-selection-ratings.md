---
id: elec-resistor-selection-ratings
sourceLesson: elec-components
title: "Preferred resistor values and ratings"
level: intermediate
minutes: 3
summary: "Choose an actual preferred value, then recalculate the result."
---

Choose an actual preferred value, then recalculate the result.

### Preferred values
Resistors come in E-series values. E12 (for ±10%) has 12 values per decade (each tenfold range, such as 10 to 100): 10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82. E24 adds more in between. You calculate an ideal value, then choose the nearest standard value in the safe direction.

The values aren't arbitrary. The underlying ideal sequence uses a constant ratio, so neighbours are approximately evenly spaced in percentage terms. The actual preferred values use a standard table:

```formula
v_n ≈ 10 × 10^{n/12}
v_4 ≈ 10 × 10^{4/12} ≈ 21.5 → 22
where
v_n: the n-th E12 value in the 10 to 100 decade (scale by 10, 100, 1000 … for other decades)
v_4: the value at step 4
n: the step number, 0 to 11 for the twelve values
10^{n/12}: ten raised to the power n ÷ 12; each step multiplies by about 1.21
≈: approximately equal to (the standard rounds each value to two digits)
→: rounds to
In words: each E12 value is about 21% above the one before, so neighbouring tolerance ranges are intended to sit close together. The actual rounded E12 table can leave small gaps; it is not an exact coverage proof. The rounded ideal sequence does not reproduce the whole E12 table. For example, the ideal positions near 27, 33, 39 and 47 give about 26.1, 31.6, 38.3 and 46.4. Use the published preferred-value table rather than generating production values from this approximation.
```

E24 uses the same idea with 24 steps per decade (n ÷ 24), each about 10% apart.

### Tolerance and resistor dissipation rating
- **Component tolerance**: how far a real part may be from its marked value. A 10 kΩ ±5% part may be anywhere from 9.5 to 10.5 kΩ. For a divider that sets a precise level, use 1% parts.
- **Resistor dissipation rating:** the most power the part can turn into heat continuously. Common small through-hole resistors are rated around 0.25 W. Check the datasheet. Calculate the power and leave margin. Running at half the rating or less is a common conservative practice.

```formula
R_min = R_nom(1 − t)
R_max = R_nom(1 + t)
R_min = 10 kΩ × 0.95 = 9.5 kΩ
R_max = 10 kΩ × 1.05 = 10.5 kΩ
where
R_nom: the nominal (marked) resistance, here 10 kΩ
t: the tolerance as a fraction, here ±5% = 0.05
R_min: the lowest value the part may really have
R_max: the highest value the part may really have
kΩ: kilohms; 1 kΩ = 1000 ohms (Ω)
In words: a ±5% part can be up to 5% below or above its marked value.
```

For the power check, use the resistor form of the power law from the voltage and current units:

```formula
P = I^2 R
P = (0.010 A)^2 × 330 Ω = 0.033 W
where
P: the power the resistor turns into heat, in watts (W)
I: the current through it, here 10 mA = 0.010 amperes (A)
I^2: the current squared
R: the resistance, here 330 ohms (Ω)
A: amperes, the unit of current
Ω: ohms, the unit of resistance
W: watts, the unit of power
In words: 10 mA through 330 Ω makes 33 mW of heat, about an eighth of a 0.25 W rating, so a small resistor is comfortable.
```

## Key takeaways

- Choose an actual preferred value, then recalculate the result.
- Tolerance, temperature and power derating belong in the design check.

## Further reading

- [Vishay: preferred-value table, IEC 60063](https://www.vishay.com/docs/28372/e-series.pdf)
- [Vishay: resistor colour code](https://www.vishay.com/docs/49411/resistor_color_code_calculator.pdf)
- [OpenStax: electrical energy and power](https://openstax.org/books/university-physics-volume-2/pages/9-5-electrical-energy-and-power)
