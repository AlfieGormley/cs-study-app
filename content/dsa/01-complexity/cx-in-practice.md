---
id: cx-in-practice
title: Complexity in practice
level: advanced
minutes: 13
summary: What Big-O leaves out and when it matters, from constant factors and CPU caches to what input sizes are feasible in a second, adversarial inputs, galactic algorithms and how to choose between algorithms.
---

Asymptotic analysis is a model. It is an excellent one, and for large enough inputs it predicts the winner. But it deliberately throws away information: constant factors, the memory hierarchy, the language runtime, and what your inputs actually look like. Experts know both the model and where it leaks.

This lesson is about using complexity as an engineering tool rather than an exam answer.

## What fits in one second

The most practical skill is estimating from the input size n which complexity you can afford. For the arithmetic exercise below, **assume 10^8 counted operations per second** and unit leading constants. This is a hypothetical model, not measured throughput or a guarantee for any language. The estimate is one division:

```formula
t = W(n) / r
where
t: the estimated running time, in seconds (s)
W(n): the number of operations the algorithm does on input size n, read off its complexity with the constant taken as 1 (for example n^2 for a quadratic algorithm)
n: the input size
r: the assumed speed, 10^8 (a hundred million) operations per second
In words: divide the operation count by the speed; anything that comes out near 1 second or less fits the budget.
```

In the table, n! is n factorial (n × (n − 1) × … × 1), 2^n is 2 multiplied by itself n times, and log n is the base-2 logarithm of n:

| Largest n (about 1 s) | Affordable complexity |
|---|---|
| 10 to 11 | O(n!) |
| 20 to 25 | O(2^n) |
| ~500 | O(n^3) |
| ~5,000 to 10,000 | O(n^2) |
| ~10^6 | O(n log n) |
| ~10^8 | O(n) |
| large n, subject to constants and storage | O(log n), O(1) |

The table comes straight from the arithmetic:

```formula
11! ≈ 4 × 10^7
2^25 ≈ 3.4 × 10^7
500^3 = 1.25 × 10^8
(10^4)^2 = 10^8
10^6 × log_2(10^6) ≈ 2 × 10^7
where
11!: 11 factorial, 11 × 10 × … × 1 = 39,916,800
2^25: 2 multiplied by itself 25 times, 33,554,432
500^3: 500 × 500 × 500
log_2(10^6): the base-2 logarithm of a million, about 19.9
≈: approximately equal to
In words: at each table row's largest n, the operation count comes out at about 10^7 to 10^8, which is about a second or less at 10^8 operations per second.
```

Read it backwards too. If a problem says n is up to 200,000, a quadratic algorithm needs about 200,000 × 200,000 = 4 × 10^10 operations, 400 seconds at the assumed rate (minutes rather than a second), so you need O(n log n) or better. If n is at most 20, exponential brute force over subsets may be the simplest correct answer.

> [!note] Content gap: cross-language timings
> A reproducible benchmark for the claimed universal Python-to-compiled speed ratio is absent, so that ratio is omitted. Interpreter version, operation type, data and hardware matter. Native built-ins or vectorisation can reduce interpreter overhead; measure the actual workload.

## Constant factors

Big-O hides constants, but the computer doesn't. Two algorithms in the same class can differ by 10x, and an asymptotically worse one can win for all inputs you'll ever see.

The standard example is sorting small arrays. Insertion sort is Θ(n^2), but its inner loop is tiny, branch-predictable and works entirely in cache. For small n it beats merge sort and quicksort, so real libraries use **hybrid sorts**:

- **Timsort-style natural merge sorts** extend short runs with binary insertion sort, then merge them. Thresholds differ by implementation; modern CPython uses a Powersort merge policy, so a single threshold/policy should not be attributed to both Python and Java.
- **Introsort** (C++ `std::sort` in common implementations) runs quicksort, switches to heapsort if the recursion gets too deep (guaranteeing O(n log n) worst case), and leaves small partitions (16 elements in libstdc++) for a final insertion sort pass.

The general lesson: the crossover point is found by measurement, not theory.

## The memory hierarchy

The RAM model treats memory accesses uniformly, but real machines have caches, main memory and storage with different access costs.

> [!note] Content gap: hardware latency measurements
> The repository contains no reproducible measurement setup for the original latency table. Exact nanosecond and microsecond figures are omitted; consult the target hardware documentation and benchmark its access patterns. Cache-line size is hardware-specific (64 bytes is common on x86; ARM implementations vary).

So **access patterns** matter enormously:

- **Arrays vs linked lists.** Summing an array and summing a linked list are both Θ(n). But the array is contiguous: a 64-byte cache line holds eight 8-byte values and the prefetcher streams the rest. A linked list's nodes can be scattered across memory, and each `next` pointer must be loaded before the following address is known, so ordinary demand loads form a dependency chain and are harder to overlap. The list is often several times slower, and much worse when nodes are scattered.
- **Traversal order.** C stores 2D arrays row by row. For an N by N array of 8-byte values, both loops below are Θ(N^2), touching all N × N elements once:

```c
/* row order: sequential */
for (i = 0; i < N; i++)
    for (j = 0; j < N; j++)
        sum += a[i][j];

/* column order: N*8-byte jumps */
for (j = 0; j < N; j++)
    for (i = 0; i < N; i++)
        sum += a[i][j];
```

For large N (so the matrix doesn't fit in cache), the column-order loop touches a new cache line on almost every access and can be several times slower, sometimes by an order of magnitude.

This is why B-trees, with hundreds of keys per node, beat binary search trees for databases and file systems: they need far fewer memory or disk accesses for the same Θ(log n) search. Cache-aware and **cache-oblivious** algorithms are designed around counting cache misses instead of instructions.

## Galactic algorithms

Some algorithms have the best known asymptotic complexity but are never used, because their constants are astronomical. They're nicknamed **galactic algorithms**: they would only win on inputs larger than anything that fits on Earth.

- **Matrix multiplication.** For n by n matrices, the naive algorithm is Θ(n^3) and Strassen's is about Θ(n^2.807). Theoretical algorithms descending from Coppersmith–Winograd have pushed the exponent below 2.372, but they are useless in practice. Even Strassen is used only above a size threshold, if at all; optimised BLAS libraries mostly rely on carefully blocked Θ(n^3) code that uses the cache brilliantly.
- **Integer multiplication.** For n-digit numbers, Harvey and van der Hoeven's 2019 algorithm runs in O(n log n), believed optimal, but only beats existing methods for astronomically large numbers. Practical libraries such as GMP switch between schoolbook, Karatsuba, Toom–Cook variants and FFT-based multiplication at tuned size thresholds.

The opposite trap also exists: assuming a fancy algorithm is needed when the simple one, with a good constant, is fast enough.

## Worst case and adversaries

Average-case performance is fine when inputs are benign. When an attacker controls the input, they will find your worst case.

- **Hash flooding.** Hash tables give O(1) average lookups, but if many keys collide, operations degrade to O(n) for a table of n keys, and inserting n colliding keys becomes Θ(n^2): about n × n / 2 comparisons. In 2011, researchers showed that many web frameworks could be knocked over by a single POST request whose parameter names all collided. Languages responded by randomising their hash functions per process. Python has randomised `str` hashing by default since 3.3 and uses SipHash since 3.4.
- **Regular expression backtracking.** Many regex engines use backtracking, which is exponential on some patterns and inputs. In July 2019 a single badly behaved regular expression exhausted CPU across Cloudflare's network and caused a global outage. RE2 and Rust's `regex` provide bounded search complexity for supported patterns. Rust documents O(mn) for individual searches (pattern size m, haystack size n), while repeated-match iterators can reach O(mn²). A fixed-pattern single search is linear in n.
- **Quicksort on sorted input.** A first- or last-element pivot can turn sorted distinct input into Θ(n²). Randomisation gives an expected bound; introsort's heapsort fallback provides the worst-case bound.

If an input could be hostile, choose algorithms with good **worst-case** bounds, or randomise.

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
2^k: 2 multiplied by itself k times
ratio: the measured T(2n) / T(n)
log_2: the base-2 logarithm: log_2(x) is the power you raise 2 to in order to get x
≈: approximately equal to
In words: if doubling the input roughly quadruples the time, the time grows like n squared.
```

A ratio of 4 means k = 2: quadratic. A ratio of 2 means linear; slightly above 2 suggests n log n; 8 means cubic. The method assumes the time is close to a single power of n over the range measured; constant start-up costs or a change in cache behaviour between sizes can distort the ratios. This catches the "it's O(n) on paper but quadratic in practice" bugs from hidden costs (lesson 3).

Measure carefully: warm up first (JIT compilers, caches), repeat runs and take the minimum or median, and use realistic data. In Python, the `timeit` module handles the repetition for you, and a profiler (such as `cProfile`) tells you where the time actually goes.

## Choosing between algorithms

A practical checklist:

1. **How big is n, really?** Today and in a few years. If n will never exceed 1,000, an O(n^2) algorithm doing 1,000 × 1,000 = a million cheap steps is probably fine.
2. **Typical or worst case?** Is the input adversarial or user-controlled? Do you have latency requirements (tail latency) or just throughput?
3. **Memory.** Will the faster algorithm's extra space fit? (Lesson 4.)
4. **Constants and hardware.** Contiguous arrays and sequential access are fast; pointer chasing is slow.
5. **Simplicity.** Simpler code has fewer bugs and is easier to change. Use the simplest algorithm that is fast enough for the largest n you expect.
6. **Use the library.** Standard library sorts, hash maps and heaps are heavily tuned. Beating them is rarely worth the effort.
7. **Measure.** Knuth's line, "premature optimization is the root of all evil", continues: "yet we should not pass up our opportunities in that critical 3%". Profile to find that 3%.

> [!example] A realistic decision
> You need the top 10 scores from n = 50 million records. Sorting is O(n log n). A size-10 heap scan is O(n log 10), effectively O(n), and uses tiny memory. Quickselect is O(n) average. At n = 5 × 10^7, the heap scan is simple, streaming (no need to hold all records) and fast, making it a suitable starting point to benchmark, even though sorting would also "work".

## Key takeaways
- A hypothetical 10^8-operation budget illustrates growth-rate differences; real time budgets require workload-specific measurements.
- Constant factors decide small inputs. Real sorts are hybrids that fall back to insertion sort for small pieces.
- Memory access dominates: cache misses and dependent loads can be expensive relative to sequential access. Sequential, contiguous access can beat pointer-chasing by large factors at the same Big-O.
- Galactic algorithms have the best asymptotic bounds but are never practical.
- When inputs can be hostile, worst-case bounds matter: hash flooding, regex backtracking and bad quicksort pivots are real outages.
- Estimate exponents with a doubling experiment, profile before optimising, and pick the simplest algorithm that is fast enough.

## Further reading
- [Latency numbers every programmer should know (gist)](https://gist.github.com/jboner/2841832)
- [Locality of reference — Wikipedia](https://en.wikipedia.org/wiki/Locality_of_reference)
- [Galactic algorithm — Wikipedia](https://en.wikipedia.org/wiki/Galactic_algorithm)
- [Introsort — Wikipedia](https://en.wikipedia.org/wiki/Introsort)
- [Timsort — Wikipedia](https://en.wikipedia.org/wiki/Timsort)
- [Time complexity guide — USACO Guide](https://usaco.guide/bronze/time-comp)
- [timeit — Python docs](https://docs.python.org/3/library/timeit.html)
