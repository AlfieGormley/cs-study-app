---
id: cx-analysing-code
title: Analysing code
level: intermediate
minutes: 12
summary: How to read the complexity off real code, including dependent and logarithmic loops, recursion, hidden library costs, and best, average and worst case.
---

You now have the notation. This lesson is about using it: looking at a piece of code and working out its time complexity quickly and correctly. Most code reduces to a handful of patterns, plus a few traps that catch even experienced engineers.

## The basic rules

1. **Cost model.** Treat fixed-size arithmetic, comparison and indexing as O(1). Python arbitrary-precision integers, long strings, user-defined comparisons and output can cost more; the counts below abstract those costs unless stated otherwise.
2. **Sequential blocks add.** O(n) followed by O(n^2) is O(n + n^2) = O(n^2).
3. **Nested loops multiply**, if the inner loop's length doesn't depend on the outer variable. n iterations of an O(m) body is O(nm).
4. **Branches take the worse side** for worst-case analysis. `if cond: O(n) else: O(1)` is O(n) in the worst case.
5. **Function calls cost whatever the function costs.** A one-line call to `sorted()` is O(n log n), not O(1).

Those cover simple code. The interesting cases are loops whose bounds change.

## Dependent nested loops

When the inner loop depends on the outer variable, you have to **sum** rather than multiply.

```python
for i in range(n):
    for j in range(i):
        work()
```

The inner loop runs 0, 1, 2, ..., n-1 times, so the total is `n(n-1)/2 = Θ(n^2)`. Halving the work does not change the class.

Three nested loops over `i < j < k` do one step per triple, which is `n(n-1)(n-2)/6`, about `n^3 / 6`: still Θ(n^3).

> [!tip] A quick sanity check
> For nested loops, ask "roughly how many times does the innermost line run, as a fraction of the full box?" If it's a constant fraction (a half, a sixth), the class is the same as the full product.

## Logarithmic loops

A loop whose variable is **multiplied or divided** by a constant each step runs a logarithmic number of times.

```python
i = 1
while i < n:
    i *= 2
```

`i` takes the values 1, 2, 4, 8, ..., stopping once it reaches n. After k steps `i = 2^k`, so it stops when `2^k >= n`, i.e. after `ceil(log2 n)` steps. For n = 16 that's 4 iterations (1, 2, 4, 8); for n = 17 it's 5.

The same holds for halving (`n //= 2`), and for any constant factor: multiplying by 3 gives `log3 n` steps, still Θ(log n). This is the shape behind binary search and balanced trees.

A loop that stops at a square root is different again:

```python
i = 1
while i * i <= n:
    i += 1
```

This runs about `sqrt(n)` times.

## Mixed loops and two classic traps

A linear outer loop around a logarithmic inner loop gives `n log n`:

```python
for i in range(n):        # n times
    j = 1
    while j < n:          # log n times
        j *= 2
```

Now the trap. What about an outer loop that **doubles** with an inner loop that runs `i` times?

```python
i = 1
while i < n:
    for j in range(i):
        work()
    i *= 2
```

It looks like "log n outer times n inner", so `n log n`. But the inner loop runs `1 + 2 + 4 + ... ` up to below n. A geometric series is dominated by its last term, and

```
1 + 2 + 4 + ... + 2^k = 2^(k+1) - 1
```

which is less than `2n`. So the whole thing is **Θ(n)**. Always sum the actual counts.

The second trap is the **harmonic** loop:

```python
for i in range(1, n + 1):
    for j in range(0, n, i):
        work()
```

The inner loop runs about `n / i` times. Total: `n/1 + n/2 + n/3 + ... + n/n = n x H(n)`, where H(n) is the harmonic number, about `ln n`. So this is **Θ(n log n)**, not n^2. It appears in sieves (such as the Sieve of Eratosthenes, which is even tighter at `n log log n`) and in some graph and number theory problems.

| Pattern | Count |
|---|---|
| inner to i | n^2 / 2 |
| i *= 2 | log n |
| i*i <= n | sqrt n |
| doubling outer, inner to i | < 2n |
| inner step i | n ln n |

## Recursion

For recursive code, count **how many calls** happen and **how much work each does** outside the recursive calls.

Linear recursion makes one call per level:

```python
def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)
```

Θ(n) calls and multiplications in the unit-cost model. Actual Python integer multiplications become more expensive as n! grows.

Branching recursion is where things explode. Naive Fibonacci makes two calls per level:

```python
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

Draw the **recursion tree**:

```
                 f5
           /            \
         f4              f3
       /    \          /    \
     f3      f2      f2      f1
    /  \    /  \    /  \
   f2  f1  f1  f0  f1  f0
  /  \
 f1  f0
```

(Here `f5` means `fib(5)`.) `fib(5)` makes 15 calls. In general the number of calls is `2F(n+1) - 1`, where `F` is the Fibonacci sequence itself. That grows like `φ^n`, with φ (the golden ratio) about 1.618. `fib(30)` makes about 2.7 million calls; `fib(50)` would make about 4 x 10^10.

The waste is visible in the tree: `fib(3)` is computed twice, `fib(2)` three times. Caching results (**memoisation**, covered with dynamic programming later) reduces this to n distinct calls: Θ(n).

Divide-and-conquer recursion (halving the problem) needs the tools in lesson 6, but a rough guide:

- One call on half the input, O(1) extra work: Θ(log n) (binary search).
- Two calls on halves, O(n) extra work: Θ(n log n) (merge sort).

## Hidden costs

Many "one-line" operations aren't O(1). In Python (CPython):

| Operation | Cost |
|---|---|
| `x in some_list` | O(n) |
| `x in some_set` | O(1) average |
| `lst.append(x)` | O(1) amortised |
| `lst.insert(0, x)` | O(n) |
| `lst.pop(0)` | O(n) |
| `lst[a:b]` | O(b - a) copy |
| `sorted(lst)` | O(n log n) |
| `len(lst)` | O(1) |

This turns innocent-looking code quadratic:

```python
def unique(items):
    seen = []
    out = []
    for x in items:
        if x not in seen:   # O(n) scan
            seen.append(x)
            out.append(x)
    return out
```

The membership test scans `seen`, so the function is Θ(n^2) when most items are distinct. Changing `seen` to a `set` makes it Θ(n) on average. The algorithm didn't change; the data structure did.

> [!warning] Slicing in recursion
> `binary_search(arr[mid:], target)` looks logarithmic, but each slice copies up to half the array. The total copying is `n/2 + n/4 + ...`, about n, so the "O(log n)" search is actually O(n). Pass indices (`lo`, `hi`) instead of slices.

## Best, average and worst case

The same algorithm can take very different time on different inputs of the same size. Linear search shows this:

```python
def find(xs, target):
    for i, x in enumerate(xs):
        if x == target:
            return i
    return -1
```

- **Best case:** target is first. 1 comparison, Θ(1).
- **Worst case:** target is last or absent. n comparisons, Θ(n).
- **Average case:** if the target is present and equally likely to be at any position, the expected number of comparisons is `(1 + 2 + ... + n) / n = (n + 1) / 2`, still Θ(n).

Which one should you report?

- **Worst case** is the default. It's a guarantee, it's usually easiest to analyse, and adversarial inputs exist (users and attackers will find your slow path).
- **Average case** describes typical behaviour, but it depends on an assumption about the input distribution, which may be wrong for your data.
- **Best case** is rarely useful on its own. Any algorithm can be given a fast best case by checking for one special input.

A related term is **expected** time for **randomised** algorithms. For distinct keys with uniformly random pivots, randomised quicksort is expected Θ(n log n) on every fixed input, because the randomness is in the algorithm, not the input. For distinct keys, quicksort with a first- or last-element pivot is average Θ(n log n) over uniformly random permutations but Θ(n²) on sorted input, which real data often is.

> [!example] Early exits
> An early return can improve best or average time. Whether it changes the worst case depends on whether any inputs still force the original expensive path. Ask which inputs attain the maximum after adding the check.

## Key takeaways
- Sequential code adds, nested loops multiply, dependent loops need an actual sum.
- Multiplying or dividing the loop variable by a constant gives Θ(log n) iterations.
- A geometric series is dominated by its largest term: doubling outer loops often give Θ(n), not n log n.
- The harmonic loop `n/1 + n/2 + ... + n/n` is Θ(n log n).
- For recursion, count calls times work per call. Two calls per level with little shrinkage is exponential.
- Library calls have costs: `in` on a list, `pop(0)` and slicing are all O(n).
- Report worst case by default; average case depends on assumptions about input.

## Further reading
- [TimeComplexity — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- [Best, worst and average case — Wikipedia](https://en.wikipedia.org/wiki/Best,_worst_and_average_case)
- [Harmonic series — Wikipedia](https://en.wikipedia.org/wiki/Harmonic_series_(mathematics))
- [Memoization — Wikipedia](https://en.wikipedia.org/wiki/Memoization)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
