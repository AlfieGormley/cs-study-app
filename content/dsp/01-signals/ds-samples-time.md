---
id: ds-samples-time
title: Samples on a time axis
level: basic
minutes: 5
summary: Translate sample indices into time without losing the final interval.
---

A **signal** records how a quantity changes. A sensor might measure temperature over time; a synthetic test might contain plain numbers with no physical unit. **Digital signal processing (DSP)** changes or analyses such sequences of values. A **sample** is one value. A **sample index** counts positions, starting at zero here; it is not itself a time in seconds.

A Python list such as `[2, 4, 1, 3]` contains four samples. Writing `x[2]` in Python retrieves the third value, 1. Mathematical signal notation uses the same square brackets to identify a sequence value.

## From count to seconds

For **uniform sampling**, consecutive values are separated by the same **sample period**. The **sample rate** counts samples per second. This course assumes an exact constant rate unless stated otherwise.

```formula
T_s = 1 / F_s
t_n = n / F_s
0 ≤ n ≤ N − 1
where
T_s: sample period, in seconds (s)
F_s: sample rate, in samples per second
t_n: timestamp of sample n relative to the first sample, in seconds (s)
n: integer sample index, a unitless count
N: number of samples in the record, a positive integer count
s: second, the unit of time
In words: Divide the index by the sample rate to locate a sample in time; the first index is zero.
```

At 4 samples per second the timestamps are 0, 0.25, 0.5 and 0.75 seconds. A bare list does not store its rate: keep the rate and physical units with the data.

> [!analogy] Real-world analogy: Regular snapshots
> Imagine taking a photograph every quarter of a second.
>
> **How it maps:** Each photograph is a sample; its position in the stack is its index. The schedule supplies its time.
>
> **Where it stops:** A sample need not be an image, and equally spaced measurements do not guarantee that fast motion between them can be recovered.

## Duration versus timestamp span

For a non-empty record, this course calls the number of sample periods represented by the record its **record duration**. The last period ends one interval after the final timestamp. The **timestamp span** measures only the gap between the first and last sample. State which one an application needs.

```formula
D = N / F_s
S = (N − 1) / F_s
D = 4 / (4 / s) = 1 s
S = 3 / (4 / s) = 0.75 s
where
D: record duration, in seconds (s)
S: first-to-last timestamp span, in seconds (s)
N: positive number of samples, here 4
F_s: sample rate, here 4 samples per second
s: second, the unit of time
In words: Four sample periods occupy one second, but four timestamps have only three gaps.
```

The half-open record interval includes its start and excludes its end. A one-sample record therefore has one period of duration and zero timestamp span. An empty record has no first or last timestamp.

## Build times from integer indices

This complete example uses NumPy, a library for numerical arrays. `np.arange(4)` creates integer indices 0 through 3, excluding 4; dividing an array acts on every element. Building integer indices first avoids a floating-point step accidentally changing the number of timestamps.

```python
import numpy as np
fs = 4.0  # samples per second
n = np.arange(4)
t = n / fs
print(t.tolist())
print(len(t) / fs)
# [0.0, 0.25, 0.5, 0.75]
# 1.0 seconds of record duration
```

This establishes timing, not what happened between samples. Irregular measurements need their actual timestamps rather than one assumed rate.

## Key takeaways
- A sample index is a position; the sample rate converts it to time.
- Record duration counts sample periods, while timestamp span counts gaps.
- Keep timing and physical units alongside a numerical array.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH2.PDF)
- [NumPy: integer index arrays with arange](https://numpy.org/doc/stable/reference/generated/numpy.arange.html)
