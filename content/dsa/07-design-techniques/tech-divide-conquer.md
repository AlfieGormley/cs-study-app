---
id: tech-divide-conquer
title: Divide and conquer
level: intermediate
minutes: 14
summary: Split a problem into independent halves, solve them recursively and combine the answers; with the master theorem, merge sort, fast exponentiation, Karatsuba multiplication and the closest pair of points.
---

**Divide and conquer** is recursion with a plan. You divide the input into smaller subproblems, solve them recursively, and combine their answers. Balanced pieces often give efficient recurrences, but unequal splits also count as divide and conquer.

The payoff comes from the cutting. Halving an input of a million items takes only about 20 levels to reach size 1, so even if every level does linear work, the n log₂n work expression is around 20 million, compared with n² = one trillion. These growth expressions are not exact instruction counts or timings.

## The three steps

1. **Divide** the input into a subproblems, each about n/b in size.
2. **Conquer** each subproblem recursively (with a base case for tiny inputs).
3. **Combine** the sub-answers into the answer for the whole.

The cleanest examples have **independent** subproblems that can be solved separately. Repeated equivalent subproblems can waste work; caching them leads toward dynamic programming. Independence alone neither guarantees balanced splits nor eliminates all coordination costs in parallel implementations.

## Analysing it: recurrences

The cost of a divide-and-conquer algorithm is a **recurrence**:

```
T(n) = a·T(n/b) + f(n)

a     = number of subproblems
n/b   = size of each subproblem
f(n)  = cost of dividing + combining
```

Draw the recursion tree. Level k has aᵏ nodes, each of size n/bᵏ. Whether the total is dominated by the root, the leaves or spread evenly depends on how fast aᵏ grows compared with how fast the per-node work shrinks.

### The master theorem (simplified)

For fixed a ≥ 1, b > 1, d ≥ 0, a constant-cost base case and f(n) = Θ(nᵈ), compare d with log_b a. Ignore rounding of subproblem sizes in this simplified form:

| Case | Result | Who dominates |
|---|---|---|
| d > log_b a | Θ(nᵈ) | Root's combine |
| d = log_b a | Θ(nᵈ log n) | Every level equal |
| d < log_b a | Θ(n^(log_b a)) | The leaves |

| Algorithm | Recurrence | Cost |
|---|---|---|
| Binary search | T(n/2) + O(1) | O(log n) |
| Merge sort | 2T(n/2) + O(n) | O(n log n) |
| Fast power | T(n/2) + O(1) | O(log n) |
| Karatsuba | 3T(n/2) + O(n) | O(n^1.585) |
| Closest pair | 2T(n/2) + O(n) | O(n log n) |

## Two familiar examples

### Binary search

Compare the target with the middle element and discard the half that can't contain it. One subproblem of half the size, constant combine: a = 1, b = 2, d = 0. Since log₂1 = 0 = d, the cost is O(n⁰ log n) = O(log n). For a billion sorted items, that is at most 30 midpoint probes. A three-way comparator can classify a probe in one comparison; separate equality and ordering tests may perform more.

Binary search is the degenerate case where "combine" is free and one half is thrown away entirely. Some people call this *decrease and conquer*.

### Merge sort

Split the list in half, sort each half, and merge the two sorted halves in linear time.

```python
def merge_sort(xs):
    if len(xs) <= 1:
        return xs
    mid = len(xs) // 2
    left = merge_sort(xs[:mid])
    right = merge_sort(xs[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]
```

```
level 0:  [ 8 3 5 1 ]          n work
level 1:  [ 8 3 ]  [ 5 1 ]     n work
level 2:  [8] [3]  [5] [1]     n work
          log2 n levels  =>  O(n log n)
```

Here a = 2, b = 2, d = 1 and log₂2 = 1 = d, so every level does equal work: O(n log n). The `<=` keeps it **stable** (equal keys stay in their original order). The price is O(n) extra memory for merging.

## Fast exponentiation

For a non-negative integer exponent n, straightforward powering uses O(n) multiplications. The bounds here count arithmetic operations; large-integer bit costs are additional. Divide and conquer notices that

```
x^n = (x^(n/2))^2        if n is even
x^n = (x^(n//2))^2 · x   if n is odd
```

```python
def power(x, n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n == 0:
        return 1
    half = power(x, n // 2)   # once!
    if n % 2 == 0:
        return half * half
    return half * half * x
```

Each call halves n, so there are about log₂n calls and O(log n) multiplications. x¹⁰⁰⁰⁰⁰⁰ needs roughly 20 squarings instead of 999,999 multiplications.

> [!warning] Compute the half once
> Writing `return power(x, n // 2) * power(x, n // 2)` makes two recursive calls: T(n) = 2T(n/2) + O(1) = O(n). You've rebuilt the slow algorithm with extra overhead.

The iterative version reads the bits of n from least significant upwards: square x at every step and multiply it into the result when the bit is 1.

```python
def power_iter(x, n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    result = 1
    while n > 0:
        if n & 1:
            result *= x
        x *= x
        n >>= 1
    return result
```

With a modulus applied after every multiplication, this is **modular exponentiation**, the workhorse of RSA and Diffie–Hellman. Python’s built-in `pow(base, exp, mod)` performs efficient modular powering; CPython 3.14 uses binary powering and a sliding-window method depending on exponent size. It is not literally this loop. Fixed-size matrix powering can compute Fibonacci numbers using O(log n) matrix multiplications, with growing integer bit costs.

## Karatsuba multiplication

Schoolbook multiplication of two n-digit numbers multiplies every digit by every other digit: O(n²). In 1960 Anatoly Karatsuba found a faster way.

Split each number in half around 10ᵐ:

```
x = a·10^m + b
y = c·10^m + d
xy = ac·10^2m + (ad + bc)·10^m + bd
```

That looks like four half-size multiplications (ac, ad, bc, bd), which gives T(n) = 4T(n/2) + O(n) = O(n²): no gain. The trick is that the middle term can be had with **one** extra multiplication:

```
ad + bc = (a + b)(c + d) − ac − bd
```

So three multiplications suffice: T(n) = 3T(n/2) + O(n) = O(n^log₂3) ≈ O(n^1.585).

> [!example] 1234 × 5678
> m = 2, so a = 12, b = 34, c = 56, d = 78.
> - ac = 12 × 56 = 672
> - bd = 34 × 78 = 2652
> - (a+b)(c+d) = 46 × 134 = 6164
> - middle = 6164 − 672 − 2652 = 2840
>
> Result: 672·10⁴ + 2840·10² + 2652 = 6,720,000 + 284,000 + 2,652 = **7,006,652**.

The algebra above uses decimal blocks for readability. This implementation splits at powers of two, avoiding decimal string conversion and its input-size limit. Its recurrence counts bit operations on linearly sized additions/splits.

```python
def karatsuba(x, y):
    if (type(x) is not int
            or type(y) is not int):
        raise TypeError("integer operands")
    sign = -1 if (x < 0) != (y < 0) else 1
    def mul(x, y):
        if x < 16 or y < 16:
            return x * y
        m = max(x.bit_length(),
                y.bit_length()) // 2
        base = 1 << m
        a, b = divmod(x, base)
        c, d = divmod(y, base)
        ac, bd = mul(a, c), mul(b, d)
        mid = mul(a + b, c + d) - ac - bd
        return ((ac << (2*m))
                + (mid << m) + bd)
    return sign * mul(abs(x), abs(y))
```

In practice the additions and subtractions make Karatsuba slower than schoolbook for small numbers. In CPython 3.14, ordinary multiplication uses Karatsuba only when both operands exceed 70 internal digits; the squaring cutoff is 140. Internal digits have 15 or 30 bits depending on the build (`sys.int_info.bits_per_digit`). Libraries such as GMP go further with Toom–Cook and FFT-based methods for very large numbers. The same "fewer multiplications" idea gives **Strassen's** matrix multiplication: 7 half-size products instead of 8, O(n^(log₂7)), with log₂7 ≈ 2.80735.

## Closest pair of points

Given n points in the plane, find the two closest. Brute force checks all n(n−1)/2 pairs: O(n²). Divide and conquer does it in O(n log n).

1. Sort the points by x once. Split them with a vertical line at the median x.
2. Recursively find the closest distance on each side: δ_L and δ_R. Let δ = min(δ_L, δ_R).
3. The only pairs left to check are those that **straddle** the line. Both points must lie within δ of it, in a strip of width 2δ.

```
         |<- δ ->|<- δ ->|
   .     |   .   |       |    .
     .   |       |  .    |
  .      |  .    |   .   |  .
         |     strip     |
           mid line
```

4. Maintain y order through the recursion; extract the strip in that order. Compare each point with the next **7** points.

Why only 7? Any point closer than δ must lie in a δ × 2δ rectangle above it. Split that rectangle into eight δ/2 × δ/2 squares: assign boundary points to their recursive half and apply the four-square packing argument within each half. Two points of the same half in one such square would be closer than δ, contradicting that half’s distance bound. So at most one point per square, eight in total including the point itself. The combine step is O(n), provided you keep a y-sorted list rather than re-sorting the strip at every level (which would give O(n log² n)).

The implementation returns the minimum distance (infinity for fewer than two points). Coordinates must be finite real numbers with meaningful subtraction; `hypot` uses floating-point arithmetic, so exact geometric predicates would need a different numeric representation. Hash-based partitioning assumes expected constant-time tuple lookup.

```python
from math import hypot

def dist(p, q):
    return hypot(p[0] - q[0], p[1] - q[1])

def brute_force(points):
    return min((dist(p, q)
                for i, p
                in enumerate(points)
                for q in points[i+1:]),
               default=float("inf"))

def closest(points):
    points = [tuple(p) for p in points]
    if len(set(points)) != len(points):
        return 0.0
    py = sorted(points, key=lambda p: p[1])
    return _closest(sorted(points), py)

def _closest(px, py):    # distinct points
    n = len(px)
    if n <= 3:
        return brute_force(px)
    mid = n // 2
    mx = px[mid][0]
    lx, rx = px[:mid], px[mid:]
    lset = set(lx)
    ly = [p for p in py if p in lset]
    ry = [p for p in py if p not in lset]
    d = min(_closest(lx, ly),
            _closest(rx, ry))
    strip = [p for p in py
             if abs(p[0] - mx) < d]
    for i, p in enumerate(strip):
        for q in strip[i+1:i+8]:
            d = min(d, dist(p, q))
    return d
```

## In the real world

- **Hybrid cut-offs.** Recursion has overhead, so practical implementations switch to a simple algorithm below a threshold. Timsort (Python's `sorted`) uses insertion sort on short runs; CPython multiplies small integers the schoolbook way.
- **Parallelism.** Independent subproblems can run on different cores. Java’s fork/join framework can execute recursive divide-and-conquer tasks. MapReduce also separates local processing and aggregation, but a MapReduce job need not be a recursive divide-and-conquer algorithm.
- **External sorting.** Databases sort data bigger than RAM by sorting chunks that fit in memory and merging them: merge sort's structure.
- **Memory.** Merge sort needs O(n) extra space; quicksort is divide and conquer with all the work in the *divide* step (partitioning) and a trivial combine, using in-place partitioning; recursive stack space is additional.

## Pitfalls

- **Overlapping subproblems.** If the pieces share sub-pieces (naive Fibonacci), divide and conquer repeats work exponentially. That's a job for DP.
- **Unbalanced splits.** Quicksort with a bad pivot splits n into n − 1 and 0: T(n) = T(n−1) + O(n) = O(n²).
- **An expensive combine.** The combine step decides the complexity. Re-sorting inside the recursion, or copying large slices, can quietly add a log factor or worse.

## Key takeaways
- Divide, conquer, combine: independent, balanced subproblems often make the method especially efficient.
- For T(n) = aT(n/b) + Θ(nᵈ) under the stated assumptions, compare d with log_b a; more general recurrences need other analysis.
- Fast exponentiation needs only O(log n) multiplications, as long as you compute the half once.
- Karatsuba trades a multiplication for some additions: 3 subproblems instead of 4, O(n^1.585).
- Closest pair is O(n log n) because only a constant number of strip neighbours need checking.

## Further reading
- [Divide-and-conquer algorithm — Wikipedia](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm)
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Karatsuba algorithm — Wikipedia](https://en.wikipedia.org/wiki/Karatsuba_algorithm)
- [Closest pair of points problem — Wikipedia](https://en.wikipedia.org/wiki/Closest_pair_of_points_problem)
- [Exponentiation by squaring — Wikipedia](https://en.wikipedia.org/wiki/Exponentiation_by_squaring)
- [Jeff Erickson, Algorithms, chapter 1: Recursion (PDF)](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
