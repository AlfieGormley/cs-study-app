---
id: cx-amortised-analysis
title: Amortised analysis
level: advanced
minutes: 13
summary: Why appending to a dynamic array is O(1) even though some appends copy everything, and the aggregate, accounting and potential methods for proving it.
---

Some operations are usually cheap but occasionally very expensive. Appending to a Python list is the standard example: almost every `append` writes one slot, but now and then the list runs out of room and copies every element to a bigger block of memory.

Here n is the number of elements in the list (or the number of operations in a sequence). If you judged each operation by its worst case, you'd call `append` O(n), and a loop of n appends O(n^2), growing like n × n. O(n²) is a valid but unnecessarily loose upper bound; the tight bound (Θ, Big-Theta) for n appends from an empty list is Θ(n). **Amortised analysis** gives the right answer by bounding the total cost of a *sequence* of operations, then dividing by the length of the sequence.

> [!note] Amortised is not average-case
> Average-case analysis assumes a probability distribution over inputs. Amortised analysis uses **no probability at all**. It says: for *any* sequence of n operations, even one chosen by an adversary, the total cost is at most n times the amortised cost. It's a worst-case guarantee about sequences.

## The dynamic array

A dynamic array keeps its elements in a fixed-size block of memory with some spare **capacity**. Append writes into the next free slot. When the block is full, it allocates a new block of **double** the capacity, copies everything across, and frees the old one.

```
cap 4: [a b c d]           full
append e:
  alloc cap 8, copy 4
       [a b c d e _ _ _]
append f, g, h: 1 write each
append i:
  alloc cap 16, copy 8
```

Count the cost of appending n = 9 items, starting from capacity 1, as one unit per element written or copied:

| Append # | Copies | Write | Capacity after |
|---|---|---|---|
| 1 | 0 | 1 | 1 |
| 2 | 1 | 1 | 2 |
| 3 | 2 | 1 | 4 |
| 4 | 0 | 1 | 4 |
| 5 | 4 | 1 | 8 |
| 6-8 | 0 | 3 | 8 |
| 9 | 8 | 1 | 16 |

Total copies: 1 + 2 + 4 + 8 = 15. Total writes: 9. Total cost 24 for 9 appends, 24 / 9 ≈ 2.67 per append, under 3. The rest of this lesson shows three ways to prove that this always holds.

All three prove the same kind of statement. The **amortised cost** per operation is the total cost of a sequence divided by its length:

```formula
a = T(n) / n
T(9) = 15 + 9 = 24
a = 24 / 9 ≈ 2.67
where
a: the amortised cost per operation, in units (one unit per element written or copied)
T(n): the total actual cost of a sequence of n operations, in the same units
n: the number of operations in the sequence, here 9 appends
≈: approximately equal to
In words: spread the total cost evenly over all the operations; a rare expensive copy is shared out among the many cheap writes.
```

## Method 1: aggregate analysis

Bound the total cost of n operations directly, then divide.

- Writes: exactly n.
- Copies: the array resizes when its size hits 1, 2, 4, ..., up to the largest power of two below n. The copy costs are a **geometric series** (each term double the one before), whose sum is just under twice its last term:

```formula
copies = 1 + 2 + 4 + … + 2^k
copies = 2^{k+1} − 1 < 2 × n
T(n) = n + copies < 3 × n
a = T(n) / n < 3
where
copies: the total number of element copies over all resizes
k: the number of the last resize, so 2^k is the largest power of 2 below n
2^k: 2 multiplied by itself k times
2^{k+1}: 2 multiplied by itself k + 1 times
n: the number of appends
T(n): the total cost of n appends: n writes plus all the copies
a: the amortised cost per append
…: "and so on"
In words: the copies add up to less than 2n and the writes to exactly n, so n appends cost less than 3n in total and less than 3 each on average.
```

Check against the table: n = 9 gives k = 3, copies = 2^4 − 1 = 15 and total 24, below 3 × 9 = 27. So the amortised cost per append is at most 3: **O(1)**, a constant that does not grow with n.

Aggregate analysis is the simplest method, but it gives every operation the same amortised cost. When a data structure supports several operations with different costs, the next two methods are more flexible.

## Method 2: the accounting method

Charge each operation a fixed **amortised cost**, which may be more than it really costs. The overcharge is stored on elements of the structure as **amortised credit**, and expensive operations pay for themselves out of saved credit. The rule: **credit must never go negative**.

For the dynamic array, charge **3 units** per append:

1. 1 unit pays for writing the new element now.
2. 1 unit is stored on the new element, to pay for copying it at the next resize.
3. 1 unit is stored on an element from the *older half* of the array, which already spent its credit in the previous resize.

Why it works: look at the append that triggers a resize from capacity k to 2k, plus the k − 1 appends after it that fill the new array. Those k appends each bank 2 units:

```formula
banked = k × 2 = 2 × k
needed = 2 × k
banked − needed = 0 ≥ 0
where
banked: the credit saved by the k appends between two resizes, in units
needed: the cost of copying all 2k elements at the next resize, in units
k: the capacity before the earlier resize; the new capacity is 2 × k
≥: greater than or equal to
In words: the appends that fill the new half save exactly enough credit to copy the whole array next time, so the credit never goes negative.
```

```
resize 4 -> 8, then write e:
  [o o o o e _ _ _]   e banks 2
3 more appends (f, g, h):
  [o o o o e f g h]   8 banked
append i: copy 8, spending all 8
```

Since the bank never goes negative, the real total cost is at most the total charged: **3n**.

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
Φ = 2 × s − c
where
Φ: phi, the potential of the array, in cost units
s: the size: how many elements are stored
c: the capacity: how many slots are allocated
In words: the potential is zero when the array is exactly half full and rises by 2 with every element added after that.
```

Start with an empty array of capacity 0, so Φ = 0. After the first append, the array is always at least half full (s ≥ c / 2), so Φ is never negative.

**Append without resize** (size s to s + 1, capacity c unchanged): actual cost 1, Φ goes up by 2. Amortised = 1 + 2 = **3**.

**Append with resize** (size = capacity = k, capacity becomes 2k): actual cost is k copies plus 1 write.

```formula
Φ_before = 2 × k − k = k
Φ_after = 2 × (k + 1) − 2 × k = 2
a = (k + 1) + 2 − k = 3
where
Φ_before: the potential just before the append, when the array is full (size k, capacity k)
Φ_after: the potential just after, with size k + 1 and capacity 2k
k: the capacity (and size) at the moment the array is full
a: the amortised cost of this append: actual cost k + 1 plus the change in potential, Φ_after − Φ_before = 2 − k
In words: the copy costs k, but the potential drops by about k at the same moment, so the amortised cost is still 3.
```

For example, with k = 8: actual cost 9 (8 copies, 1 write), Φ falls from 8 to 2, so the amortised cost is 9 + 2 − 8 = 3. Every append has amortised cost at most 3, whatever k is (the very first append, from capacity 0 to 1, costs only 2). The potential built up by the cheap appends is precisely what pays for the copy.

## Why the growth must be geometric

Suppose instead the array grows by a **fixed amount**, say 10 slots each time. Resizes happen at sizes 10, 20, 30, ..., and each copies the whole array:

```formula
copies = 10 + 20 + 30 + … + n
copies = 10 × (1 + 2 + … + n / 10)
copies ≈ 10 × (n / 10)^2 / 2 = n^2 / 20
n = 10^6:  copies ≈ 10^12 / 20 = 5 × 10^10
where
copies: the total number of element copies over n appends
n: the number of appends (a multiple of 10 here)
n^2: n squared, n × n
…: "and so on"
≈: approximately equal to (lower-order terms dropped)
In words: the copy sizes grow in a straight line rather than doubling, so they add up to a quadratic total, about n squared over 20.
```

That is about 5 × 10^10 copies for a million appends, and the amortised cost per append is Θ(n), growing in proportion to n. Growing by a constant *factor* is what makes the series geometric and the amortised cost O(1).

The factor doesn't have to be 2. Suppose each resize multiplies the capacity by a growth factor g, starting from capacity 1. Ignoring integer rounding:

```formula
copies = 1 + g + g^2 + … + C / g
copies = (C − 1) / (g − 1)
n ≤ C < g × n
where
copies: the total number of element copies over all resizes
g: the growth factor, any fixed number greater than 1 (2 for doubling, 1.5, 1.125, …)
g^2: g × g
C: the final capacity after n appends
n: the number of appends
…: "and so on"
≤: less than or equal to
In words: each resize copies the old capacity, those capacities form a geometric series, and the series adds up to a constant multiple of the final capacity, which is itself within a factor g of n.
```

So the copying is at most about g × n / (g − 1), a constant times n. Since n ≤ C < g × n, a bound in terms of arbitrary n needs the extra factor g. The smaller estimate n / (g − 1) applies near a full final capacity. With g = 2 it gives about n copies; with g = 1.5 about 2n. Real implementations differ:

| Implementation | Growth |
|---|---|
| CPython `list` | ~1.125x + small constant |
| OpenJDK `ArrayList` single-item growth | preferred ~1.5x; implementation detail |
| C++ libstdc++ `vector` single-item growth | commonly ~2x; implementation detail |
| Rust `Vec` | amortised O(1) push; no particular growth factor guaranteed |

CPython's comment in `listobject.c` gives the capacities as 0, 4, 8, 16, 24, 32, 40, 52, 64, 76, ... A smaller factor wastes less memory on empty slots but copies more often. Any factor above 1 keeps appends O(1) amortised.

## Shrinking without thrashing

If the array also supports `pop`, you may want to free memory as it empties. The obvious rule, "halve the capacity when it becomes half full", has a nasty failure.

Suppose the array is exactly full at capacity k. Append: double to 2k (k copies). Pop: now half full, halve back to k (k copies). Append again: full, double again. Alternating push and pop at that boundary makes **every operation cost Θ(n)**, proportional to the number of elements n (which is about k).

The fix is **hysteresis**: grow when full, but shrink only when the array is a **quarter** full, and then halve. After any resize the array is half full, so at least Θ(capacity) cheap operations must happen before the next resize. Both push and pop are then O(1) amortised.

## More examples

- **Binary counter.** Incrementing a binary counter can flip many bits (`0111 -> 1000`), but over n increments bit 0 flips n times, bit 1 about n/2 times, bit 2 about n/4 times:

```formula
flips ≤ n + n/2 + n/4 + … < 2 × n
where
flips: the total number of bit flips over n increments
n: the number of increments, starting from 0
…: "and so on", halving each time
≤: less than or equal to
In words: bit j flips once every 2^j increments, and those halving counts add up to less than 2n, so each increment costs fewer than 2 flips on average.
```

So increment is O(1) amortised: a constant per operation, however large n is.
- **Queue from two stacks.** Push onto an `inbox` stack. To dequeue, pop from `outbox`; if it's empty, first move everything from `inbox` to `outbox`. A single dequeue can cost O(n), where n is the number of elements waiting, but each element is moved at most once, so every operation is O(1) amortised.
- **Hash table resizing** works just like the dynamic array: double the table when the load factor gets high, rehashing every key.
- Later modules meet more advanced cases: splay trees and union-find both have amortised bounds that worst-case analysis can't show.

## Pitfalls in production

**Amortised O(1) is not "every operation is fast".** A Python list of 100 million pointers occupies about 800 MB; the append that triggers a resize may have to copy most of that, and the call pauses until it finishes. Amortisation bounds aggregate work, but allocation and copying still affect measured throughput. For latency-sensitive systems (trading, games, audio, real-time control), one slow append can blow a deadline.

Ways to avoid spikes:

- **Preallocate** when you know the size: `reserve()` in C++, `with_capacity()` in Rust, `[None] * n` in Python.
- **Incremental resizing.** Redis's hash tables rehash gradually: they keep the old and new tables side by side and move a few buckets on each operation (and in a background timer), so no single command pays for the whole rehash.

**Amortisation can break if expensive states can be replayed.** The proofs assume each expensive operation is preceded by many cheap ones that build up credit. If a data structure is shared and old versions can be reused (some persistent or functional structures), an adversary can trigger the expensive operation on the same "full" version repeatedly. Okasaki's work on purely functional data structures handles this with lazy evaluation.

## Key takeaways
- Amortised cost bounds the total over any sequence of operations, divided by its length. It's a worst-case guarantee with no probability involved.
- Dynamic array append is O(1) amortised: total cost of n appends is under 3 × n with doubling.
- Aggregate method: sum the whole sequence. Accounting: overcharge cheap operations and bank credit. Potential: define Φ and let its changes pay for expensive steps.
- A fixed growth factor above 1 is sufficient for amortised O(1) append in this copy-on-resize model; fixed additive growth gives Θ(n) amortised cost.
- Shrink at a quarter full, not half, to avoid thrashing.
- Amortised bounds hide latency spikes. Preallocate or resize incrementally when individual operation latency matters.

## Further reading
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
- [Potential method — Wikipedia](https://en.wikipedia.org/wiki/Potential_method)
- [Accounting method — Wikipedia](https://en.wikipedia.org/wiki/Accounting_method_(computer_science))
- [Dynamic array — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_array)
- [CPython listobject.c (list growth policy)](https://github.com/python/cpython/blob/main/Objects/listobject.c)
