---
id: tech-divide-conquer
title: Divide and conquer
level: intermediate
minutes: 14
summary: Split a problem into independent halves, solve them recursively and combine the answers; with the master theorem, merge sort, fast exponentiation, Karatsuba multiplication and the closest pair of points.
---

**Divide and conquer** is recursion with a plan. You divide the input into smaller subproblems, solve them recursively, and combine their answers. Balanced pieces often give efficient recurrences, but unequal splits also count as divide and conquer.

The payoff comes from the cutting. Halving an input of a million items takes only about 20 levels to reach size 1, so even if every level does work proportional to the input size, the total stays small. Compare that with an algorithm that pairs every item with every other item:

```formula
L = log_2(n) = log_2(1,000,000) ≈ 20
W_dc = n × L ≈ 1,000,000 × 20
W_dc ≈ 20,000,000
W_sq = n^2 = 1,000,000^2
W_sq = 1,000,000,000,000
where
n: the number of input items, here one million
L: the number of halving levels needed to get from n items down to 1
log_2(n): the base-2 logarithm of n, the number of times you can halve n before reaching 1; log_2(1,000,000) ≈ 19.93
W_dc: the rough work, in basic steps, of a divide-and-conquer algorithm that does about n steps on each level
W_sq: the rough work, in basic steps, of a quadratic algorithm that compares every item with every other item
n^2: n squared, n × n
≈: approximately equal to
In words: about 20 levels of a million steps each is about 20 million steps, against a trillion for the all-pairs approach: 50,000 times less work.
```

These growth expressions are scale estimates, not exact instruction counts or timings.

## The three steps

1. **Divide** the input into some number of smaller subproblems, each a fixed fraction of the original size.
2. **Conquer** each subproblem recursively (with a base case for tiny inputs).
3. **Combine** the sub-answers into the answer for the whole.

The cleanest examples have **independent** subproblems that can be solved separately. Repeated equivalent subproblems can waste work; caching them leads toward dynamic programming. Independence alone neither guarantees balanced splits nor eliminates all coordination costs in parallel implementations.

## Analysing it: recurrences

The cost of a divide-and-conquer algorithm is a **recurrence**: an equation that gives the running time on an input in terms of the running time on smaller inputs.

```formula
T(n) = a × T(n / b) + f(n)
where
T(n): the running time on an input of size n, in basic steps
n: the input size (number of items, digits or points)
a: the number of subproblems each call creates; a fixed number of at least 1
b: the factor by which the input shrinks; each subproblem has size n / b; a fixed number greater than 1
T(n / b): the running time of one subproblem
f(n): the work one call does itself, outside its recursive calls: dividing the input and combining the answers
In words: one call costs the cost of its a smaller calls, plus the work it does itself to split and to combine.
```

For merge sort, a = 2 (two halves), b = 2 (each half is n / 2) and f(n) is the linear merge.

Draw the recursion tree to see where the time goes:

```formula
N_k = a^k
s_k = n / b^k
where
N_k: the number of calls (nodes) on level k of the recursion tree
s_k: the input size of each call on level k
k: the level number, 0 at the root (the first call)
a: the number of subproblems per call
b: the shrink factor per level
n: the original input size
a^k: a multiplied by itself k times
b^k: b multiplied by itself k times
In words: going down one level multiplies the number of calls by a and divides each call's input size by b.
```

Whether the total is dominated by the root, the leaves or spread evenly depends on how fast the number of calls grows compared with how fast the per-call work shrinks.

### The master theorem (simplified)

The **master theorem** answers that race in one step for recurrences of this shape. It applies when a and b are fixed numbers, the base case costs a constant, and the work outside the recursion is a power of n. This simplified form ignores the rounding of subproblem sizes to whole numbers:

```formula
f(n) = Θ(n^d)
c = log_b(a)
T(n) = Θ(n^d)            if d > c
T(n) = Θ(n^d × log n)    if d = c
T(n) = Θ(n^c)            if d < c
where
T(n): the running time on an input of size n
n: the input size
f(n): the work one call does outside its recursive calls
d: the exponent of that work; a fixed number of at least 0 (d = 1 means linear work, d = 0 constant work)
n^d: n raised to the power d
a: the number of subproblems per call, at least 1
b: the factor by which each subproblem shrinks, greater than 1
c: the critical exponent: the number of leaves of the recursion tree grows like n^c
log_b(a): the logarithm of a to base b, the power you must raise b to in order to get a; for example log_2(4) = 2
log: logarithm; in Big-O and Big-Theta the base only changes a constant factor
Θ: Big-Theta, "grows at exactly this rate, up to constant factors"
In words: if the root's own work grows faster than the number of leaves, the root wins; if they match, every level costs the same and you pay that once per level, log n times; if the leaves grow faster, the leaves win.
```

| Case | Who dominates |
|---|---|
| combine exponent bigger | the root's combine |
| exponents equal | every level equally |
| leaf exponent bigger | the leaves |

For example, merge sort has a = 2, b = 2 and d = 1. The critical exponent is log₂2 = 1, which equals d, so it is the middle case: Θ(n log n). More general recurrences (uneven splits, work like n log n) need other tools, such as the full master theorem or the Akra–Bazzi method.

In this table, n is the input size and T is the running time; each recurrence is written with the master-theorem shape above:

| Algorithm | Recurrence | Cost |
|---|---|---|
| Binary search | T(n/2) + O(1) | O(log n) |
| Merge sort | 2T(n/2) + O(n) | O(n log n) |
| Fast power | T(n/2) + O(1) | O(log n) |
| Karatsuba | 3T(n/2) + O(n) | O(n^1.585) |
| Closest pair | 2T(n/2) + O(n) | O(n log n) |

## Two familiar examples

### Binary search

Compare the target with the middle element and discard the half that can't contain it. That is one subproblem of half the size, with a constant amount of work per call:

```formula
T(n) = T(n / 2) + O(1)
a = 1,  b = 2,  d = 0
c = log_2(1) = 0 = d
T(n) = Θ(n^0 × log n) = Θ(log n)
where
T(n): the worst-case running time of binary search on n sorted items
n: the number of items still in the search range
O(1): a constant amount of work (one probe and comparison), however large n is
a: the number of subproblems per call; 1, because one half is thrown away
b: the shrink factor; 2, because the range halves
d: the exponent of the per-call work; 0, because n^0 = 1 is constant
c: the critical exponent, log_2(a)
log_2(1): the base-2 logarithm of 1, which is 0 because 2^0 = 1
n^0: n to the power 0, which is 1
log: logarithm (the base only changes a constant)
Θ: Big-Theta, grows at exactly this rate up to constant factors
In words: d equals the critical exponent, so this is the "every level equal" case: a constant amount of work on each of about log n levels.
```

For a billion sorted items, log₂(1,000,000,000) ≈ 29.9, so that is at most 30 midpoint probes. A three-way comparator can classify a probe in one comparison; separate equality and ordering tests may perform more.

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
          3 levels, all 4 items each
```

Each level does linear work in total (every item is merged once per level), and there are about log₂n + 1 levels:

```formula
T(n) = 2 × T(n / 2) + Θ(n)
a = 2,  b = 2,  d = 1
c = log_2(2) = 1 = d
T(n) = Θ(n^1 × log n) = Θ(n × log n)
where
T(n): the running time of merge sort on n items
n: the number of items to sort
Θ(n): work proportional to n, here the merge, which touches every item once
a: the number of subproblems per call; 2 halves
b: the shrink factor; 2, because each half has n / 2 items
d: the exponent of the merge work; 1, because it is linear (n^1 = n)
c: the critical exponent, log_2(a)
log_2(2): the base-2 logarithm of 2, which is 1
log: logarithm (the base only changes a constant)
Θ: Big-Theta, grows at exactly this rate up to constant factors
In words: d equals the critical exponent, so every level does the same n work, and there are about log n levels.
```

For a million items that is roughly 1,000,000 × 20 = 20 million element moves, a scale estimate rather than an exact count. The `<=` keeps it **stable** (equal keys stay in their original order). The price is O(n) extra memory for merging.

## Fast exponentiation

To raise a number x to a non-negative whole-number power n, straightforward powering multiplies by x one time after another, which is O(n) multiplications. The bounds here count arithmetic operations; large-integer bit costs are additional. Divide and conquer notices that a power splits into two equal halves:

```formula
x^n = (x^{n/2})^2        if n mod 2 = 0
x^n = (x^{⌊n/2⌋})^2 × x  if n mod 2 = 1
where
x: the base, the number being raised to a power
n: the exponent, a whole number of at least 0
x^n: x multiplied by itself n times (x^0 = 1)
mod: the remainder after division (Python's %); n mod 2 is 0 when n is even and 1 when n is odd
(…)^2: squaring: the bracketed value multiplied by itself
⌊n/2⌋: the floor of n / 2: halve n and round down to a whole number (Python's n // 2); ⌊7/2⌋ = 3
In words: to get x to the n, compute x to half of n once and square it; if n is odd, the rounding down lost one factor of x, so multiply it back in.
```

For example, x⁷ = (x³)² × x, and x³ = (x¹)² × x.

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

Each call halves n, so there are about log₂n calls, each doing at most two multiplications:

```formula
T(n) = T(n / 2) + O(1) = O(log n)
M ≈ log_2(1,000,000) ≈ 20
where
T(n): the number of multiplications `power` performs for exponent n
n: the exponent
O(1): a constant amount of work per call (at most two multiplications)
O(log n): grows in proportion to the logarithm of n
O: Big-O, "grows no faster than, up to a constant factor"
log: logarithm (base 2 here)
M: the number of squaring steps for an exponent of one million
log_2(1,000,000): the base-2 logarithm of one million, about 19.93: the number of halvings from 1,000,000 down to 1
≈: approximately equal to
In words: halving the exponent each time means x to the millionth power needs about 20 squarings (plus a few extra multiplications for odd steps) instead of 999,999 multiplications.
```

> [!warning] Compute the half once
> Writing `return power(x, n // 2) * power(x, n // 2)` makes two recursive calls instead of one. You've rebuilt the slow algorithm with extra overhead.

The recurrence shows why: two calls on half the exponent, with constant work each, is the "leaves dominate" case.

```formula
T(n) = 2 × T(n / 2) + O(1)
c = log_2(2) = 1 > d = 0
T(n) = Θ(n^1) = Θ(n)
where
T(n): the number of multiplications for exponent n
n: the exponent
O(1): constant work per call
c: the critical exponent, log_2(a) with a = 2 subproblems
log_2(2): the base-2 logarithm of 2, which is 1
d: the exponent of the per-call work; 0 for constant work
Θ: Big-Theta, grows at exactly this rate up to constant factors
In words: the call tree doubles at every level, so it ends with about n leaves, and the total is linear in n: no better than multiplying n times.
```

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

With a modulus applied after every multiplication, this is **modular exponentiation**, the workhorse of RSA and Diffie–Hellman. Taking the remainder after each step keeps the numbers small, and it gives the same final remainder:

```formula
(a × b) mod m
  = ((a mod m) × (b mod m)) mod m
3^13 mod 7 = 3
where
a: one number being multiplied
b: the other number being multiplied
m: the modulus, a positive whole number
mod: the remainder after dividing by m (Python's %); 17 mod 7 = 3
3^13: 3 raised to the power 13, which is 1,594,323
In words: you can reduce each factor to its remainder before multiplying and still get the right remainder at the end, so the intermediate numbers never grow beyond m².
```

Python’s built-in `pow(base, exp, mod)` performs efficient modular powering; CPython 3.14 uses binary powering and a sliding-window method depending on exponent size. It is not literally this loop. Fixed-size matrix powering can compute the nth Fibonacci number using O(log n) matrix multiplications, with growing integer bit costs.

## Karatsuba multiplication

Schoolbook multiplication of two n-digit numbers multiplies every digit by every other digit: O(n²). In 1960 Anatoly Karatsuba found a faster way.

Split each number into a high half and a low half around a power of ten:

```formula
x = a × 10^m + b
y = c × 10^m + d
x × y = a × c × 10^{2 × m}
      + (a × d + b × c) × 10^m
      + b × d
where
x: the first number to multiply, with n digits
y: the second number to multiply, with n digits
m: the split point, about half the number of digits (n / 2)
10^m: 10 raised to the power m, a 1 followed by m zeros
10^{2 × m}: 10 raised to the power 2 × m
a: the high half of x (its leading digits)
b: the low half of x (its last m digits)
c: the high half of y
d: the low half of y
In words: each number is "high half shifted left by m digits, plus low half", so their product is three pieces: high × high shifted by 2m digits, the two cross products shifted by m digits, and low × low.
```

That looks like four half-size multiplications (a × c, a × d, b × c and b × d), which gives no gain:

```formula
T(n) = 4 × T(n / 2) + O(n)
c_crit = log_2(4) = 2 > 1
T(n) = Θ(n^2)
where
T(n): the number of digit operations to multiply two n-digit numbers
n: the number of digits in each number
O(n): linear work for the additions and shifts
c_crit: the critical exponent of the master theorem, log_2 of the number of subproblems; it is compared with 1, the exponent of the linear O(n) work
log_2(4): the base-2 logarithm of 4, which is 2 because 2^2 = 4
Θ: Big-Theta, grows at exactly this rate up to constant factors
n^2: n squared, the cost of schoolbook multiplication
In words: four half-size products are exactly as expensive as multiplying every digit by every digit.
```

The trick is that the middle term can be had with **one** extra multiplication:

```formula
a × d + b × c
  = (a + b) × (c + d) − a × c − b × d
where
a: the high half of x
b: the low half of x
c: the high half of y
d: the low half of y
In words: multiply the two half-sums together once, then subtract the high and low products you already computed; what is left is exactly the two cross terms.
```

So three multiplications suffice:

```formula
T(n) = 3 × T(n / 2) + O(n)
c_crit = log_2(3) ≈ 1.585 > 1
T(n) = Θ(n^{log_2(3)}) ≈ Θ(n^{1.585})
where
T(n): the number of digit operations to multiply two n-digit numbers
n: the number of digits in each number
O(n): linear work for the additions, subtractions and shifts
c_crit: the critical exponent, log_2 of the number of subproblems; it is compared with 1, the exponent of the linear O(n) work
log_2(3): the base-2 logarithm of 3, about 1.585: the power you raise 2 to in order to get 3
≈: approximately equal to
Θ: Big-Theta, grows at exactly this rate up to constant factors
In words: three half-size products put the algorithm in the "leaves dominate" case, with about n^1.585 work instead of n^2.
```

For 1000-digit numbers that is roughly 1000^1.585 ≈ 57,000 digit products instead of 1000² = 1,000,000. A worked example on 1234 × 5678:

```formula
m = 2: a = 12, b = 34, c = 56, d = 78
a × c = 12 × 56 = 672
b × d = 34 × 78 = 2652
(a + b) × (c + d) = 46 × 134 = 6164
p_mid = 6164 − 672 − 2652 = 2840
x × y = 672 × 10^4 + 2840 × 10^2 + 2652
x × y = 6,720,000 + 284,000 + 2,652
x × y = 7,006,652
where
m: the split point in digits; 2 for 4-digit numbers
a: the high half of x, here 12
b: the low half of x, here 34
c: the high half of y, here 56
d: the low half of y, here 78
p_mid: the middle coefficient, a × d + b × c, found from one multiplication and two subtractions
x: the first number, 1234
y: the second number, 5678
In words: three two-digit multiplications (672, 2652 and 6164) and some subtractions and shifts give 1234 × 5678 = 7,006,652.
```

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

In practice the additions and subtractions make Karatsuba slower than schoolbook for small numbers. In CPython 3.14, ordinary multiplication uses Karatsuba only when both operands exceed 70 internal digits; the squaring cutoff is 140. Internal digits have 15 or 30 bits depending on the build (`sys.int_info.bits_per_digit`). Libraries such as GMP go further with Toom–Cook and FFT-based methods for very large numbers. The same "fewer multiplications" idea gives **Strassen's** matrix multiplication: 7 half-size products instead of 8.

```formula
T(n) = 7 × T(n / 2) + O(n^2)
c = log_2(7) ≈ 2.807 > 2
T(n) = Θ(n^{log_2(7)}) ≈ Θ(n^{2.807})
where
T(n): the number of arithmetic operations to multiply two n × n matrices
n: the number of rows (and columns) of each square matrix
O(n^2): the work of the 18 additions and subtractions of (n / 2) × (n / 2) blocks, each touching n^2 / 4 entries
c: the critical exponent, log_2 of the number of subproblems
log_2(7): the base-2 logarithm of 7, about 2.80735
≈: approximately equal to
Θ: Big-Theta, grows at exactly this rate up to constant factors
In words: seven half-size products put Strassen in the "leaves dominate" case, about n^2.807 work instead of the n^3 of the schoolbook method.
```

## Closest pair of points

Given n points in the plane, find the two closest. Brute force checks every pair:

```formula
P = n × (n − 1) / 2
P = 1000 × 999 / 2 = 499,500
where
P: the number of distinct pairs of points
n: the number of points; 1000 in the example line
In words: each of the n points pairs with the n − 1 others, and dividing by 2 stops each pair being counted twice; this grows like n², so brute force is O(n²).
```

Divide and conquer does it in O(n log n) time, where n is still the number of points.

1. Sort the points by x once. Split them with a vertical line at the median x.
2. Recursively find the closest distance on each side, and keep the smaller:

```formula
δ = min(δ_L, δ_R)
where
δ: delta, the smallest distance found so far, in the same units as the coordinates
δ_L: the closest-pair distance among the points left of the line
δ_R: the closest-pair distance among the points right of the line
min: the minimum function, which returns the smaller of its inputs
In words: the best answer so far is whichever half had the closer pair.
```

3. The only pairs left to check are those that **straddle** the line. Both points must lie within δ of it, in a strip of width 2δ (δ on each side).

```
         |<- δ ->|<- δ ->|
   .     |   .   |       |    .
     .   |       |  .    |
  .      |  .    |   .   |  .
         |     strip     |
           mid line
```

4. Maintain y order through the recursion; extract the strip in that order. Compare each point with the next **7** points.

Why only 7? Any point closer than δ must lie in a rectangle δ tall and 2δ wide above it. Split that rectangle into eight small squares, each δ/2 on a side: assign boundary points to their recursive half and apply the four-square packing argument within each half. The key fact is that no two points inside one small square can be δ apart or more:

```formula
s = δ / 2
g = √(s^2 + s^2) = δ / √2
g ≈ 0.707 × δ < δ
where
s: the side length of each small square
δ: delta, the smallest distance found within either half
g: the length of a small square's diagonal, the furthest apart two points inside it can be
√: the square root
≈: approximately equal to
In words: two points in the same small square are at most about 0.71 δ apart, which is closer than δ.
```

Two points of the same half in one such square would therefore be closer than δ, contradicting that half’s distance bound. So at most one point per square, eight in total including the point itself, which leaves at most 7 others to compare with.

The combine step is O(n), provided you keep a y-sorted list rather than re-sorting the strip at every level. Re-sorting costs O(n log n) per level, which would give O(n log² n) in total, where log² n means (log n) × (log n).

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
- **Unbalanced splits.** Quicksort with a bad pivot splits n items into n − 1 and 0. The recursion is then n levels deep instead of log n:

```formula
T(n) = T(n − 1) + O(n)
T(n) ≈ n + (n − 1) + … + 1
T(n) = n × (n + 1) / 2 = O(n^2)
where
T(n): the running time of quicksort on n items
n: the number of items in the current call
O(n): linear partitioning work in one call
…: and so on, one less each time
≈: approximately equal to (ignoring constant factors)
O: Big-O, grows no faster than this, up to a constant factor
n^2: n squared
In words: peeling off one item per level costs n, then n − 1, and so on, which adds up to about n²/2 steps.
```

- **An expensive combine.** The combine step decides the complexity. Re-sorting inside the recursion, or copying large slices, can quietly add a log factor or worse.

## Key takeaways
- Divide, conquer, combine: independent, balanced subproblems often make the method especially efficient.
- For recurrences of the master-theorem shape, compare the exponent of the combine work with the critical exponent log_b(a); more general recurrences need other analysis.
- Fast exponentiation needs only O(log n) multiplications, as long as you compute the half once.
- Karatsuba trades a multiplication for some additions: 3 subproblems instead of 4, about n^1.585 digit operations for n-digit numbers instead of n².
- Closest pair is O(n log n) because only a constant number of strip neighbours need checking.

## Further reading
- [Divide-and-conquer algorithm — Wikipedia](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm)
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Karatsuba algorithm — Wikipedia](https://en.wikipedia.org/wiki/Karatsuba_algorithm)
- [Closest pair of points problem — Wikipedia](https://en.wikipedia.org/wiki/Closest_pair_of_points_problem)
- [Exponentiation by squaring — Wikipedia](https://en.wikipedia.org/wiki/Exponentiation_by_squaring)
- [Jeff Erickson, Algorithms, chapter 1: Recursion (PDF)](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
