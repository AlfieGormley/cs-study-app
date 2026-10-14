---
id: cx-measuring-algorithms
sourceLesson: cx-in-practice
title: Measuring and choosing an algorithm
level: advanced
minutes: 4
summary: Use doubling ratios and realistic constraints to choose a suitable implementation.
---

Here n is the input size. Measurement complements operation counting by exposing hidden costs and practical crossover points.

## Measuring: the doubling experiment

You can estimate the exponent of an algorithm empirically. Time it at n, 2n, 4n and look at the ratios. These numbers are illustrative, not recorded measurements:

| n | time | ratio |
|---|---|---|
| 1,000 | 0.05 s | |
| 2,000 | 0.20 s | 4.0 |
| 4,000 | 0.81 s | 4.05 |
| 8,000 | 3.30 s | 4.07 |

Why does the ratio reveal the exponent? If the running time is roughly a power of n, doubling n multiplies it by 2 to that power, and the constant cancels:

```formula
T(n) ≈ c × n^k
T(2 × n) / T(n) ≈ (2 × n)^k / n^k = 2^k
k ≈ log_2(ratio)
k ≈ log_2(4.07) ≈ 2.02
where
T(n): the measured running time at input size n, in seconds (s)
c: an unknown constant (machine speed, language, implementation), which cancels in the ratio
n: the input size
k: the exponent being estimated
2^k: k copies of 2 multiplied together
ratio: the measured T(2n) / T(n)
log_2: the base-2 logarithm: log_2(x) is the power you raise 2 to in order to get x
≈: approximately equal to
In words: if doubling the input roughly quadruples the time, the time grows like n squared.
```

A ratio of 4 means k = 2: quadratic. A ratio of 2 means linear; slightly above 2 suggests n log n; 8 means cubic. The method assumes the time is close to a single power of n over the range measured; constant start-up costs or a change in cache behaviour between sizes can distort the ratios. This catches the "it's O(n) on paper but quadratic in practice" bugs from hidden costs (the code-analysis lessons).

Measure carefully: warm up first (JIT compilers, caches), repeat runs and take the minimum or median, and use realistic data. In Python, the `timeit` module handles the repetition for you, and a profiler (such as `cProfile`) tells you where the time actually goes.

## Choosing between algorithms

A practical checklist:

1. **How big is n, really?** Today and in a few years. If n will never exceed 1,000, an O(n^2) algorithm doing 1,000 × 1,000 = a million cheap steps is probably fine.
2. **Typical or worst case?** Is the input adversarial or user-controlled? Do you have latency requirements (tail latency) or just throughput?
3. **Memory.** Will the faster algorithm's extra space fit? (The space-complexity lessons.)
4. **Constants and hardware.** Contiguous arrays and sequential access are fast; pointer chasing is slow.
5. **Simplicity.** Simpler code has fewer bugs and is easier to change. Use the simplest algorithm that is fast enough for the largest n you expect.
6. **Use the library.** Standard library sorts, hash maps and heaps are heavily tuned. Beating them is rarely worth the effort.
7. **Measure.** Knuth's line, "premature optimization is the root of all evil", continues: "yet we should not pass up our opportunities in that critical 3%". Profile to find that 3%.

> [!example] A realistic decision
> You need the top 10 scores from n = 50 million records. Sorting is O(n log n). A size-10 heap scan is O(n log 10), effectively O(n), and uses tiny memory. Quickselect is O(n) average. At n = 5 × 10^7, the heap scan is simple, streaming (no need to hold all records) and fast, making it a suitable starting point to benchmark, even though sorting would also "work".

## Key takeaways
- Doubling experiments suggest growth only over the range and conditions measured.
- Profile realistic data to find which operations dominate.
- Choose the simplest approach that meets the input, memory and latency constraints.

## Further reading
- [timeit — Python docs](https://docs.python.org/3/library/timeit.html)
