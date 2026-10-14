---
id: snd-decibel-gain
title: Decibels and gain multipliers
level: intermediate
minutes: 5
summary: Choose amplitude or power decibels and convert a chain of gains to a sample multiplier.
sourceLesson: snd-levels
---

A synth that's too quiet is annoying. One that clips is broken: harsh, aliasing distortion every time a chord gets loud. Managing level is a constant job, from the first oscillator to the final converter, and decibels are the language for it.



## Why decibels

Level ratios in audio span an enormous range. The loudest signal a 24-bit converter handles is millions of times larger in amplitude than its quietest. Ratios like that are unreadable as plain numbers, and our perception of loudness is roughly logarithmic anyway, so audio uses a logarithmic unit: the **decibel** (dB).

A decibel is always a **ratio** to something. There are two formulas, and mixing them up is the most common mistake. For quantities that measure power or energy:

```formula
L = 10 × log_10(P_2 / P_1)
L = 10 × log_10(2) ≈ +3.01 dB
where
L: the level change, in decibels (dB); positive means louder
log_10: the base-10 logarithm, which answers "10 to what power gives this number?" (log_10(100) = 2)
P_1: the reference power (any unit, such as watts, W)
P_2: the power being compared, in the same unit as P_1; here twice P_1
dB: decibels, tenths of a bel
≈: approximately equal to (rounded)
In words: ten times the logarithm of the power ratio gives decibels, so doubling the power is about +3 dB.
```

For amplitudes (sample values, voltages, sound pressures):

```formula
L = 20 × log_10(A_2 / A_1)
L = 20 × log_10(2) ≈ +6.02 dB
where
L: the level change, in decibels (dB)
log_10: the base-10 logarithm
A_1: the reference amplitude (a sample value, or volts, V)
A_2: the amplitude being compared, in the same unit; here twice A_1
dB: decibels
≈: approximately equal to (rounded)
In words: twenty times the logarithm of the amplitude ratio gives decibels, so doubling an amplitude is about +6 dB.
```

Why the different factors? Power is proportional to amplitude squared, and the logarithm of a square is twice the logarithm:

```formula
P ∝ A^2
10 × log_10(A_2^2 / A_1^2)
= 20 × log_10(A_2 / A_1)
where
P: power
A: amplitude
∝: "is proportional to": doubling the right side doubles the left
A_2^2 / A_1^2: the power ratio written with amplitudes, because powers go as amplitude squared
log_10: the base-10 logarithm; log_10(x^2) = 2 × log_10(x)
In words: the power formula applied to squared amplitudes is the amplitude formula, so both give the same decibels for the same change.
```

Both formulas give the **same** dB value for the same change; you just use the one matching the quantity you have. Samples, voltages and pressures are **amplitudes**, so in synth code you'll nearly always use **20·log10**.

Going back from decibels to a multiplier undoes the logarithm:

```formula
g = 10^(L / 20)
g = 10^(−6 / 20) ≈ 0.501
where
g: the amplitude multiplier (gain factor) to apply to the samples; no unit
L: the level change, in decibels (dB); here −6 dB
10^x: 10 raised to the power x, the inverse of log_10
≈: approximately equal to (rounded)
In words: divide the decibels by 20 and raise 10 to that power; −6 dB means multiply the samples by about 0.5.
```

The same two conversions in Python:

```python
import math

def amp_db(ratio):
    # Samples are amplitudes, not powers.
    return 20 * math.log10(ratio)

def db_amp(db):
    # Undo the amplitude decibel formula.
    return 10 ** (db / 20)

for r in (2, 0.5, 10, 0.1, 1.4142):
    d = amp_db(r)
    print(f"x{r:<6} -> {d:+6.2f} dB")
for db in (-3, -6, -12, -20):
    print(f"{db:+} dB -> x{db_amp(db):.3f}")
```

```text
x2      ->  +6.02 dB
x0.5    ->  -6.02 dB
x10     -> +20.00 dB
x0.1    -> -20.00 dB
x1.4142 ->  +3.01 dB
-3 dB -> x0.708
-6 dB -> x0.501
-12 dB -> x0.251
-20 dB -> x0.100
```

Memorise a few: **doubling an amplitude adds about 6 dB**, **×10 adds 20 dB**, and **×1.414 (the square root of 2) adds about 3 dB**. In power terms, doubling power is +3 dB. Gains in dB **add** where the ratios multiply:

```formula
L = L_1 + L_2
L = −6 + (−12) = −18 dB
g = 10^(−18 / 20) ≈ 0.126
where
L: the total gain of two stages in a row, in decibels (dB)
L_1: the first stage's gain, in dB; here −6
L_2: the second stage's gain, in dB; here −12
g: the total amplitude multiplier
10^x: 10 raised to the power x
dB: decibels
≈: approximately equal to (rounded)
In words: chaining a −6 dB stage and a −12 dB stage gives −18 dB, the same as multiplying 0.501 by 0.251 to get about 0.126.
```

## Key takeaways

- Use twenty times the log for amplitude ratios and ten times the log for power ratios.
- Doubling amplitude adds about 6 dB; doubling power adds about 3 dB.
- Serial gains add in decibels and multiply as linear factors.

## Further reading

- [Decibel — Wikipedia](https://en.wikipedia.org/wiki/Decibel)
