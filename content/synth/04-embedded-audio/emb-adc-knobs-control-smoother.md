---
id: emb-adc-knobs-control-smoother
sourceLesson: emb-adc-knobs
title: "Smooth knob readings"
level: intermediate
minutes: 4
summary: "A moving average needs a history buffer and introduces delay."
---

## Smoothing: moving average and one-pole

**Moving average.** Average the last few readings:

```formula
y = (x_1 + x_2 + … + x_M) / M
where
y: the smoothed output
x_1: the newest raw reading
x_2: the reading before that
x_M: the oldest reading still in the window
M: how many readings are averaged, for example 4 or 8
…: "and so on": every reading between x_2 and x_M is included in the sum
In words: add up the last M readings and divide by M. Random noise partly cancels out; a real change shows up only gradually.
```

For uncorrelated zero-mean reading noise, averaging reduces noise variance; correlated interference may remain. Averaging M readings but the output lags the input by roughly half the window and you need a buffer holding the last M readings. Strictly, the lag is half of one less than the window: 3.5 readings for an 8-reading window, which at 1,000 readings a second is 3.5 ms.

**One-pole low-pass (exponential smoothing).** Keep one state value and move it a fixed fraction of the way towards each new reading:

```formula
y_n = y_{n−1} + a(x_n − y_{n−1})
where
y_n: the smoothed value after reading n
y_{n−1}: the smoothed value from the previous reading
x_n: the new raw reading
a: the dimensionless smoothing coefficient, greater than zero and at most one for this monotonic smoother; small values mean a slow response and one means no smoothing
n: the reading number
In words: each time a reading arrives, close the fraction a of the gap between the smoothed value and the reading. For a fixed input step and the stated coefficient range, the smoothed value approaches the target monotonically without overshooting.
```

In code this is one line, `y = y + a * (x - y)`. You can choose `a` from how quickly you want it to respond: an **exponential time constant**, the time the output takes to cover about 63% of a sudden step:

```formula
a = 1 − e^(−1 / (τr))
a = 1 − e^(−1 / (0.010 s × 1000 /s))
a = 1 − e^(−0.1) ≈ 1 − 0.9048 = 0.0952
where
a: the smoothing coefficient per reading, between 0 and 1, no unit
e: Euler's number, about 2.71828, the base of natural exponential growth and decay
τ: tau, the time constant you want, in seconds (s); here 10 ms = 0.010 s
r: the update rate, how many readings per second the filter receives, in per second (/s); here 1,000
s: second, the unit of time
≈: approximately equal to (rounded)
In words: work out how many readings fit in one time constant (here 10), and a is the fraction that makes the filter cover 63% of a step in that many readings. A longer time constant gives a smaller a.
```

The same calculation, plus a check of how far the filter gets towards a step from 0 to 1:

```python
import math
rate = 1000.0          # control reads/s
tau = 0.010            # 10 ms
# Select coefficient for a 10 ms response.
a = 1 - math.exp(-1 / (tau * rate))
print(f"a = {a:.4f}")
y = 0.0
# Retain y between readings of the unit
# step.
for n in range(1, 31):
    y += a * (1.0 - y)  # step to 1.0
    # Inspect one, two and three time
    # constants.
    if n in (10, 20, 30):
        print(n, f"{y:.3f}")
```

```output
a = 0.0952
10 0.632
20 0.865
30 0.950
```

Why 63%? Each reading leaves a fraction (1 − a) of the remaining gap, so after k readings the fraction of a step covered is:

```formula
covered = 1 − (1 − a)^k
covered = 1 − (1 − 0.0952)^10
covered ≈ 1 − 0.368 ≈ 0.632
where
covered: the fraction of a sudden step the output has travelled, from 0 (none) to 1 (all of it)
a: the smoothing coefficient, here 0.0952
k: the number of readings since the step; here 10, one time constant at 1,000 readings per second
≈: approximately equal to
In words: after one time constant the filter has covered about 63% of any step, after two about 86%, after three about 95%. In exact arithmetic with a coefficient strictly between zero and one, it approaches the target asymptotically; floating-point rounding can eventually stop or finish the numerical change.
```

After one time constant (10 readings, which is 10 ms) the output has covered 63.2% of a step; after three, 95%. With the stated exponential coefficient the response matches those exponential sample times even for short time constants, but updates remain a discrete staircase and a non-integer time constant need not coincide with a reading. This is the same filter as the one-pole low-pass in DSP, running at control rate. The fetched libDaisy `AnalogControl` source also uses a one-state smoother and a default slew setting of 0.002 s. Its coefficient rule is different from the time-constant coefficient rule above; do not treat that slew setting as the exact time constant of this example.

## Key takeaways
- A moving average needs a history buffer and introduces delay.
- A one-pole smoother retains state; its coefficient depends on update rate and time constant.

## Further reading
- [Getting started: ADCs — Electro-Smith](https://docs.daisy.audio/tutorials/_a4_Getting-Started-ADCs/)
- [Teensy 4.1 analog pins — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Coding schemes used with data converters (SBAA042) — Texas Instruments](https://www.ti.com/lit/an/sbaa042/sbaa042.pdf)
- [Analog-to-digital converter — Wikipedia](https://en.wikipedia.org/wiki/Analog-to-digital_converter)
- [Introduction to Digital Filters (one-pole filters) — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/)
- [AnalogControl implementation — libDaisy](https://raw.githubusercontent.com/electro-smith/libDaisy/master/src/hid/ctrl.cpp)
