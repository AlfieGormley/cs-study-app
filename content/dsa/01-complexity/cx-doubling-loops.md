---
id: cx-doubling-loops
sourceLesson: cx-analysing-code
title: Doubling and growing inner loops
level: intermediate
minutes: 4
summary: Recognise logarithmic loops and sum a geometric series of inner-loop lengths.
---

Here n is the positive input size. Do not multiply the largest possible inner count by every outer pass without checking how the inner length changes.

## Logarithmic loops

A loop whose variable is **multiplied or divided** by a constant each step runs a logarithmic number of times.

```python
# For n = 17, i finishes at 32.
i = 1
while i < n:
    i *= 2
```

`i` takes the values 1, 2, 4, 8, ..., stopping once it reaches n. Count the steps:

```formula
i = 2^k
2^k ≥ n
k = ⌈log_2(n)⌉
k = ⌈log_2(16)⌉ = 4
k = ⌈log_2(17)⌉ = ⌈4.09⌉ = 5
where
i: the loop variable, which doubles every pass, so after k passes it equals 2^k
k: the number of loop iterations; the loop stops at the first k with 2^k ≥ n
n: the input size, the value the loop counts up to
log_2(n): the base-2 logarithm of n, the power you raise 2 to in order to get n
⌈x⌉: ceiling: round x up to the next whole number
≥: greater than or equal to
In words: doubling from 1 reaches n after about log_2(n) steps, rounded up.
```

For a bound of 16, the loop has four passes through 1, 2, 4 and 8; a bound of 17 requires a fifth pass.

The same logarithmic growth holds for halving (`n //= 2`) or another fixed factor. Tripling uses a base-three logarithm, but fixed log bases differ only by a constant factor. Here n is the positive input bound. This is the shape behind binary search and balanced trees.

A loop that stops at a square root is different again:

```python
# For n = 9, i finishes at 4.
i = 1
while i * i <= n:
    i += 1
```

This loop stops when the square of its variable passes the bound, so its iteration count follows the square root. A bound of a million gives about a thousand iterations. Here is that count, followed by the independent-loop product:

## Mixed loops and two classic traps

```formula
K(n) = ⌊√(n)⌋
K(1000000) = 1000
W(n) = n⌈log_2(n)⌉
where
K(n): the square-root loop’s iteration count
W(n): the number of doublings in the nested example below
n: the positive whole-number loop bound
√: the nonnegative square root
⌊ ⌋: floor: round down
⌈ ⌉: ceiling: round up
log_2: the base-2 logarithm
In words: The first loop counts up to the square root; restarting a doubling loop on every outer pass multiplies its count by the input size.
```

A linear outer loop around an independently restarted logarithmic inner loop has Θ(n log n) work, where n is its bound:

```python
for i in range(n):        # n times
    # Restart the doubling for every i.
    j = 1
    while j < n:          # log n times
        j *= 2
```

Now the trap. What about an outer loop that **doubles** with an inner loop that runs `i` times?

```python
i = 1
while i < n:
    # Inner lengths are 1, 2, 4, 8, ...
    for j in range(i):
        work()
    i *= 2
```

Multiplying the logarithmic outer count by the maximum inner length would overestimate it. The actual inner lengths double from one through the last power of two below the bound. Adding them gives a **geometric series**, dominated by its last term:

```formula
W = 1 + 2 + 4 + … + 2^k
W = 2^{k+1} − 1
2^k < n,  so  W < 2n
n = 100:  W = 1 + … + 64 = 127
where
W: the total number of work() calls
k: the number of the last outer pass; on that pass i = 2^k, the largest power of 2 below n
n: the input size
…: "and so on"
In words: each power of 2 is one more than the sum of all the smaller ones, so the whole sum is just under twice the last term, and the last term is less than n.
```

So the whole thing is **Θ(n)**. Always sum the actual counts.

## Key takeaways
- Multiplying a loop variable by a fixed factor gives logarithmic iteration counts.
- Resetting an inner loop makes each outer pass pay its cost again.
- Growing inner lengths can form a geometric series whose largest term dominates.

## Further reading
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
