---
id: df-moving-average
title: Smooth a stream with a moving average
level: basic
minutes: 4
summary: Build a causal moving average and distinguish smoothing, startup effects and delay.
---

A **moving average** gives equal weight to a fixed number of neighbouring samples. It can reduce rapid fluctuations when the useful quantity changes slowly. For a live sensor stream, choose present and past samples so the operation is causal. A centred average on a saved recording is a different timing choice because it also uses future samples.

## A three-sample average

This causal version includes the present reading and two older ones. It starts with zero history, and its divisor stays three even during startup.

```formula
y[n] = (x[n] + x[n − 1] + x[n − 2]) / 3
where
y: the smoothed output sequence, in the same units as the input
x: the input sequence; samples before index zero are zero
n: the integer sample index, starting at zero
3: the number of equally weighted samples in this average, including zero history during startup
In words: add the current reading and the two previous readings, then divide by three.
```

Suppose a sensor suddenly changes from zero to 6 and stays there. The first outputs are 2, 4 and 6. The filter needs three nonzero input samples to fill its window. This **startup transient** follows from the declared zero history; it is not a calculation error.

A program that instead divides the first sum by one and the second by two outputs 6 immediately. That may be a useful boundary policy, but it is not the same fixed-coefficient LTI filter at the beginning of the record. Initialising past samples to the first reading also changes the initial state.

> [!analogy] Real-world analogy: a three-day spending average
> A daily dashboard averages today's spending with the previous two days. One expensive day affects three successive dashboard entries.
>
> **How it maps:** The sliding set of days maps to the filter's sample window; equal shares map to equal coefficients. A sharp event spreads across several outputs.
>
> **Where it stops:** Days without records are often omitted in a dashboard. This filter explicitly fills missing earlier history with zeros and keeps its divisor fixed.

## Smoothness has a timing cost

The three coefficients are symmetric, so this filter has a linear phase response and a group delay of one sample wherever its frequency response is nonzero. Group delay describes how the phase changes across a small frequency interval. It does not mean every output sample is simply the input shifted by one place: smoothing changes amplitudes and shapes, and response sign changes can add phase jumps.

At 100 samples per second, one sample is 0.01 seconds. An abrupt event spreads across three output samples. For an alarm, that spreading can matter more than how quiet the line looks on a plot. A longer average generally smooths more rapid variation and spreads a change over more samples.

Complete Python example: NumPy is imported as `np`, and `convolve` includes the tail after the four input samples. The first four outputs are the causal outputs while readings arrive; the remaining two come from feeding zero input afterwards.

```python
import numpy as np

x = [6.0, 6.0, 6.0, 6.0]
h = np.ones(3) / 3
y = np.convolve(x, h, mode="full")
print(y.tolist())
# [2.0, 4.0, 6.0, 6.0, 4.0, 2.0]
```

## Key takeaways
- A causal moving average uses present and past readings.
- Zero history and a fixed divisor create a predictable startup transient.
- Smoothing changes amplitudes and timing; choose the window for the task.

## Further reading
- [Smith: moving average filters, Chapter 15](https://www.dspguide.com/CH15.PDF)
- [Julius O. Smith: symmetric linear-phase filters](https://www.dsprelated.com/freebooks/filters/Symmetric_Linear_Phase_Filters.html)
