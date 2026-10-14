---
id: cx-memory-tradeoffs
sourceLesson: cx-space-complexity
title: Memory trade-offs and real storage
level: intermediate
minutes: 4
summary: Choose a representation and balance extra memory against speed.
---

Here n is the input size. The earlier lessons established how to count extra storage; now use that count to choose an algorithm and representation.

## Time-space trade-offs

Here n is the input item count. Many speed-ups work by spending memory:

- **Hashing for lookups.** Checking for duplicates with a set takes expected O(n) time and O(n) space. Sorting in place, then scanning neighbours, takes O(n log n) time with little extra space.
- **Precomputation.** A prefix-sum array (n extra numbers) answers "sum of `xs[a:b]`" in O(1) instead of O(b − a), the length of the range (formula below).
- **Lookup tables.** Counting set bits in a byte with a 256-entry table instead of looping over bits.

The prefix-sum trick stores running totals once, then answers any range sum with one subtraction:

```formula
P[0] = 0
P[i + 1] = P[i] + xs[i]
sum(xs[a:b]) = P[b] − P[a]
sum(xs[1:4]) = P[4] − P[1]
sum(xs[1:4]) = 9 − 3 = 6
where
P: the prefix-sum array, n + 1 numbers; P[i] is the total of the first i items
xs: the original list of n numbers; xs[i] is the item at position i (counting from 0)
xs[a:b]: the items from position a up to but not including position b
sum: the total of the items in the range
i: a position in the list, from 0 to n − 1
a, b: the start and end positions of the range asked about
n: the number of items in xs
In words: the total of a range is "everything up to b" minus "everything up to a", so each query is one subtraction, at the cost of storing n + 1 extra numbers.
```

For input `[3, 1, 4, 1, 5]`, the running totals are `[0, 3, 4, 8, 9, 14]`. The card’s substitution adds the middle three values, giving 6:

## Constants matter for memory

Asymptotic notation hides constant factors, but with memory, those constants decide whether something fits. For a typical 64-bit CPython build (check `sys.getsizeof` on the actual build):

- A small `int` object is 28 bytes (`sys.getsizeof(1)`).
- A list stores an 8-byte pointer per element, plus the objects themselves.

So a list of 10 million distinct small integers costs:

```formula
M_list = N × (8 B + 28 B)
M_list = 10^7 × 36 B = 3.6 × 10^8 B ≈ 360 MB
M_array = N × 8 B = 8 × 10^7 B ≈ 80 MB
where
M_list: the memory used by the Python list and its int objects, in bytes (B)
M_array: the memory used by a packed array of 8-byte integers, in bytes (B)
N: the number of integers stored, here 10 million = 10^7
B: bytes; one byte is 8 bits
MB: megabytes; 1 MB = 10^6 bytes
≈: approximately equal to
In words: each list element costs an 8-byte pointer plus a 28-byte int object, four and a half times the 8 bytes a packed array needs.
```

That is roughly 80 MB of pointers plus about 280 MB of int objects. A NumPy `int64` array or the standard `array` module stores the same numbers as raw 8-byte values: about 80 MB. Both are "O(n)", but the packed data fits below a 256 MB budget, while the list does not. Runtime overhead and temporary conversion buffers still need headroom.

> [!example] An interview-style check
> "Find whether any two numbers in this list of n numbers sum to a target." Hash set: expected O(n) time, O(n) space. Sort then two pointers: O(n log n) time, O(1) extra if you may sort in place. Neither is "better"; it depends on whether memory or time is the constraint, and whether you may modify the input.

## Key takeaways
- Hashing and precomputation can save time by storing additional data.
- Recomputation, streaming and in-place algorithms can reduce extra memory.
- Object overhead and representation decide whether real data fits a memory limit.

## Further reading
- [Space complexity — Wikipedia](https://en.wikipedia.org/wiki/Space_complexity)
