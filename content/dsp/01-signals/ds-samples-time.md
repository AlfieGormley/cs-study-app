---
id: ds-samples-time
title: Samples on a time axis
level: basic
minutes: 3
summary: Read a sample record’s timing and distinguish its last timestamp from its duration.
---

A **signal** records how a quantity changes. A sensor might measure temperature over time; a synthetic test might contain plain numbers with no physical unit. **Digital signal processing (DSP)** changes or analyses such sequences of values. A **sample** is one value. A **sample index** counts positions, starting at zero here; it is not itself a time in seconds.

A record such as `[2, 4, 1, 3]` contains four samples. Its third value has index 2 because counting starts at zero. The values alone do not say whether the measurements are a second apart or a millisecond apart.

## From count to seconds

For **uniform sampling**, consecutive values are separated by the same **sample period**. The **sample rate** counts samples per second. A higher rate means shorter gaps. This course assumes an exact constant rate unless stated otherwise.

At 4 samples per second, four samples starting at zero have timestamps 0, 0.25, 0.5 and 0.75 seconds. Interpreting the same values at twice the rate halves every gap and makes the record pass twice as quickly. Keep the rate, start time and physical units with the data.

> [!analogy] Real-world analogy: Regular snapshots
> Imagine taking a photograph every quarter of a second.
>
> **How it maps:** Each photograph is a sample; its position in the stack is its index. The schedule supplies its time.
>
> **Where it stops:** A sample need not be an image, and equally spaced measurements do not guarantee that fast motion between them can be recovered.

## Duration versus timestamp span

For a non-empty record, this course calls the number of sample periods represented by the record its **record duration**. The last period ends one interval after the final timestamp. The **timestamp span** measures only the gap between the first and last sample. State which one an application needs.

Those four samples represent a one-second record interval, although the last timestamp is 0.75 seconds. Four sample periods fill that interval; the recorded instants have only three gaps. Adding a sample at exactly one second would start the next interval rather than fill a missing slot in the first.

This **half-open interval** includes its start and excludes its end. A one-sample record has one period of duration and zero timestamp span. An empty record has no first or last timestamp.

The reference relationships below collect the timing rules. They assume a non-empty, uniformly sampled record whose first timestamp is zero.

```formula reference
T_s = 1 / F_s
t_n = n / F_s
D = N / F_s
S = (N − 1) / F_s
where
T_s: sample period, in seconds (s)
F_s: sample rate, in samples per second
t_n: timestamp of sample n relative to the first sample, in seconds (s)
n: integer sample index from zero through N − 1
N: positive number of samples in the record
D: record duration, in seconds (s)
S: first-to-last timestamp span, in seconds (s)
s: second, the unit of time
In words: A sample’s position counts the gaps since the start. Record duration counts one period per sample; timestamp span counts one fewer gap. Increasing the sample rate shortens both for the same stored record.
```

Timing metadata does not reveal everything that happened between measurements. Irregular measurements need their actual timestamps rather than one assumed rate.

## Key takeaways
- A sample index is a position; the sample rate converts it to time.
- Record duration counts sample periods, while timestamp span counts gaps.
- Keep timing and physical units alongside a numerical array.

## Further reading
- [Steven W. Smith: signal values and sample indices](https://www.dspguide.com/CH2.PDF)
