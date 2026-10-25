---
id: ds-signal-operations
title: Gain, mixing and delay
level: basic
minutes: 5
summary: Change values and timing while stating what happens at record edges.
---

Many DSP tasks begin with simple operations: scale one record, add two records, or shift a record in time. Specify units and timing before combining arrays. Adding a temperature in degrees to an acceleration in metres per second squared has no physical meaning without an explicit model or conversion.

## Scale and mix aligned records

**Gain** multiplies every sample by a factor. A negative gain reverses polarity, swapping positive and negative values. **Mixing** here means adding aligned samples, possibly with separate gains. It does not mean interleaving two arrays or appending one after another.

```formula
y[n] = g x[n]
m[n] = a x[n] + b v[n]
0 ≤ n ≤ N − 1
where
y: scaled output signal, in the same units as x
n: integer sample index from 0 through N − 1
N: positive sample count shared by these aligned records
g: unitless gain factor
x: first input signal
m: mixed output, in the same physical units as both inputs
a: unitless gain applied to x
b: unitless gain applied to v
v: second input signal, with the same units, sample rate and time alignment as x
In words: Scale a signal by multiplying its values; mix compatible aligned signals by adding their scaled values.
```

For the unitless records `[1, -1]` and `[1, 1]`, adding corresponding values gives `[2, 0]`. Equal positive samples reinforce; opposite samples cancel. Two records each within a normalised limit of 1 can therefore sum beyond that limit. Scaling before a range-limited output provides **headroom**, a margin below the allowed peak.

Ordinary Python list `+` concatenates lists. It does not implement this sample-by-sample sum. Use a loop or numerical arrays deliberately. Equal array lengths alone do not establish that the timestamps agree.

## Delay with explicit boundaries

A **sample delay** makes an event occur later. For an integer delay, retrieve an earlier input value at each output index. This lesson treats values outside the finite input record as zero, called **zero extension**.

```formula
y[n] = x[n − d]
0 ≤ n ≤ N − 1
τ = d / F_s
τ = 2 / (100 / s) = 0.02 s
where
y: delayed output signal, in the same units as x
x: input signal, treated as zero outside its stored indices
n: integer output sample index from 0 through N − 1
N: positive number of output samples chosen to retain; the input remains zero outside its stored indices
d: non-negative integer delay, in samples, here 2
τ: delay time, in seconds (s)
F_s: sample rate, in samples per second, here 100
s: second, the unit of time
In words: A delay of two samples at one hundred samples per second moves an event twenty milliseconds later.
```

For input `[1, 2, 3]` and a two-sample delay, retaining only three output samples gives `[0, 0, 1]`. Retaining the complete delayed finite record gives `[0, 0, 1, 2, 3]`. This is a storage choice: the last two original values were cropped in the short output, not destroyed by the delay itself.

> [!analogy] Real-world analogy: A recording with a later start
> Imagine placing a recorded announcement two seconds later on a timeline.
>
> **How it maps:** A delay changes the announcement’s position. Saving only the original time window can crop the end, while extending the timeline retains it.
>
> **Where it stops:** This models a pure shift, not echoes, speed changes or the physical propagation of sound.

This complete example keeps the original output length and uses unitless samples. The conditional prevents Python negative indices from wrapping round to the list’s end.

```python
x = [1, 2, 3]
delay = 2
y = []
for n in range(len(x)):
    i = n - delay
    y.append(x[i] if 0 <= i < len(x)
             else 0)
print(y)
# [0, 0, 1]
```

Negative indices in Python are a language feature, not a model of signal history. Similarly, shifting values from the end back to the start would be a circular shift, a different boundary convention. Fractional-sample delay requires more than integer list indexing and is outside this lesson.

## Key takeaways
- Mixing adds aligned compatible samples; gains control their contributions.
- Sample addition can exceed individual input peaks.
- State the delay’s boundary convention and whether the output retains its tail.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH5.PDF)
