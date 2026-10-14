---
id: cx-amortised-potential
sourceLesson: cx-amortised-analysis
title: Potential as stored work
level: advanced
minutes: 4
summary: Use changes in a potential function to prove an amortised bound.
---

A potential function tracks stored credit for the whole structure rather than individual elements. This unit applies it to the doubling array.

## Method 3: the potential method

Instead of credit on individual elements, define a single **potential function** Φ (the Greek capital letter phi) on the whole data structure, like stored energy. The amortised cost of an operation is its real cost plus the change in potential it causes:

```formula
a_i = c_i + Φ_i − Φ_{i−1}
where
a_i: the amortised cost of the i-th operation
c_i: the actual cost of the i-th operation
Φ_i: the potential of the data structure after the i-th operation, a number you define
Φ_{i−1}: the potential just before the i-th operation
i: which operation in the sequence (1st, 2nd, …)
In words: an operation's amortised cost is what it really cost plus how much potential it stored (or minus how much it released).
```

Summing over a sequence, the Φ terms form a **telescoping sum**: each intermediate Φ appears once with a plus and once with a minus, so they cancel:

```formula
Σ_{i=1}^{n} a_i
  = Σ_{i=1}^{n} c_i + Φ_n − Φ_0
where
Σ_{i=1}^{n}: capital sigma, "sum of": add up the expression for every operation i from 1 to n
a_i: the amortised cost of operation i
c_i: the actual cost of operation i
Φ_n: the potential after the last operation
Φ_0: the potential at the start
n: the number of operations
i: which operation
In words: the total amortised cost equals the total real cost plus the net potential stored over the whole sequence.
```

So if Φ starts at 0 and is never negative, the total actual cost is at most the total amortised cost. The art is choosing a Φ that rises during cheap operations and drops sharply when an expensive one happens.

For the dynamic array, use

```formula
Φ = 2s − c
Φ_0 = 0
s ≥ c/2, so Φ ≥ 0
where
Φ: phi, the potential of the array, in cost units
s: the size: how many elements are stored
c: the capacity: how many slots are allocated
Φ_0: the initial potential
≥: greater than or equal to
In words: the potential is zero when the array is exactly half full and rises by 2 with every element added after that.
```

Start with an empty array of capacity zero. After the first append, it is at least half full, so potential stays nonnegative:

**Append without resize:** size rises by one while capacity stays fixed. Actual cost is one unit, potential rises by two, and their sum is three.

```formula
s_new = s + 1
c_new = c
a = 1 + 2 = 3
where
s, s_new: the stored item count before and after the append
c, c_new: capacity before and after, in slots
a: the amortised cost, in element-write/copy units
In words: A cheap append stores two units of potential in addition to its one-unit write.
```

**Append with resize:** the array is full, so its size equals its capacity. It doubles capacity, copies all existing elements and writes one new element:

```formula
Φ_before = 2k − k = k
Φ_after = 2 × (k + 1) − 2k = 2
a = (k + 1) + 2 − k = 3
k = 8: a = 9 + 2 − 8 = 3
where
Φ_before: the potential just before the append, when the array is full (size k, capacity k)
Φ_after: the potential just after, with size k + 1 and capacity 2k
k: the capacity (and size) at the moment the array is full
a: the amortised cost of this append: actual cost k + 1 plus the change in potential, Φ_after − Φ_before = 2 − k
In words: the copy costs k, but the potential drops by about k at the same moment, so the amortised cost is still 3.
```

For capacity eight, actual cost is nine units; potential falls from eight to two, leaving amortised cost three, as the substitution below shows. Every append has amortised cost at most three; the very first append from zero to one capacity costs only two. Cheap appends build the potential that pays for copying.

## Key takeaways
- Amortised cost includes actual cost and the change in stored potential.
- Intermediate potential terms cancel when costs are summed.
- The starting and final potential determine whether the amortised total bounds the actual total.

## Further reading
- [Potential method — Wikipedia](https://en.wikipedia.org/wiki/Potential_method)
- [Erickson: Amortized Analysis](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/09-amortize.pdf)
