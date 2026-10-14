---
id: cx-aggregate-appends
sourceLesson: cx-amortised-analysis
title: Dynamic arrays and total append cost
level: advanced
minutes: 5
summary: Bound the total writes and copies over a sequence of dynamic-array appends.
---

Some operations are usually cheap but occasionally very expensive. Appending to a Python list is the standard example: almost every `append` writes one slot, but now and then the list runs out of room and copies every element to a bigger block of memory.

Here n is the number of elements in the list (or the number of operations in a sequence). If you judged each operation by its worst case, you'd call `append` O(n), and a loop of n appends O(n^2), with quadratic growth. O(n²) is a valid but unnecessarily loose upper bound; the tight bound (Θ, Big-Theta) for n appends from an empty list is Θ(n). **Amortised analysis** gives the right answer by bounding the total cost of a *sequence* of operations, then dividing by the length of the sequence.

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

Count the cost of appending nine items, starting from capacity 1, as one unit per element written or copied:

| Append # | Copies | Write | Capacity after |
|---|---|---|---|
| 1 | 0 | 1 | 1 |
| 2 | 1 | 1 | 2 |
| 3 | 2 | 1 | 4 |
| 4 | 0 | 1 | 4 |
| 5 | 4 | 1 | 8 |
| 6-8 | 0 | 3 | 8 |
| 9 | 8 | 1 | 16 |

Total copies: 1 + 2 + 4 + 8 = 15. Total writes: 9. Total cost 24 for 9 appends, 24 / 9 ≈ 2.67 per append, under 3. This lesson uses aggregate analysis to prove that this always holds; the following lessons give accounting and potential proofs.

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
copies = 2^{k+1} − 1 < 2n
T(n) = n + copies < 3n
a = T(n) / n < 3
n = 9, k = 3
copies = 2^4 − 1 = 15
T(9) = 24 < 3 × 9 = 27
where
copies: the total number of element copies over all resizes
k: the number of the last resize, so 2^k is the largest power of 2 below n
n: the number of appends
T(n): the total cost of n appends: n writes plus all the copies
a: the amortised cost per append
…: "and so on"
In words: the copies add up to less than 2n and the writes to exactly n, so n appends cost less than 3n in total and less than 3 each on average.
```

Check against the nine-append table: four copy rounds total 15 copies, plus nine writes. The aggregate card confirms that the 24-unit total stays below the 27-unit bound. Thus the amortised cost is at most three units: **O(1)**, independent of sequence length.

Aggregate analysis is the simplest method, but it gives every operation the same amortised cost. When a data structure supports several operations with different costs, the next two methods are more flexible.

## Key takeaways
- Amortised analysis bounds whole operation sequences without assuming probabilities.
- A doubling array performs a geometric series of copies.
- Bounding total sequence cost can give constant amortised append cost despite an expensive individual resize.

## Further reading
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
- [Dynamic array — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_array)
- [Erickson: Amortized Analysis](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/09-amortize.pdf)
