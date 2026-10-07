---
id: cx-recurrences
title: Recurrences and the Master Theorem
level: advanced
minutes: 14
summary: Turning recursive code into recurrences, solving them with recursion trees, the three cases of the Master Theorem, where it fails, and the Akra–Bazzi generalisation for uneven splits.
---

Loops can be analysed by counting. Recursive algorithms, especially **divide and conquer** (split the problem, solve the pieces recursively, combine), need a different tool. Their running time is naturally described by a **recurrence**: an equation that defines T(n) in terms of T on smaller inputs.

This lesson is about writing those recurrences and solving them quickly.

## From code to recurrence

Write T(n) as (number of recursive calls) x T(size of each) + (work done outside the calls).

```python
def bsearch(a, t, lo, hi):
    if lo > hi:
        return -1
    mid = (lo + hi) // 2
    if a[mid] == t:
        return mid
    if a[mid] < t:
        return bsearch(a, t, mid + 1, hi)
    return bsearch(a, t, lo, mid - 1)
```

One recursive call on half the range, plus O(1) work: `T(n) = T(n/2) + O(1)`.

Merge sort calls itself on two halves and merges in linear time: `T(n) = 2T(n/2) + Θ(n)`.

Some common recurrences and their solutions:

| Recurrence | Example | Solution |
|---|---|---|
| T(n/2) + 1 | binary search | Θ(log n) |
| T(n/2) + n | halving + scan | Θ(n) |
| 2T(n/2) + 1 | tree traversal | Θ(n) |
| 2T(n/2) + n | merge sort | Θ(n log n) |
| T(n-1) + 1 | linear recursion | Θ(n) |
| T(n-1) + n | selection sort | Θ(n^2) |
| 2T(n-1) + 1 | Towers of Hanoi | Θ(2^n) |

You'll be able to derive all of them by the end of the lesson. The base case (such as `T(1) = Θ(1)`) is almost always constant, so it is usually left implicit. Floors and ceilings (`n/2` versus `ceil(n/2)`) don't change the asymptotic answer, so we ignore them too.

## The recursion tree

The most intuitive method is to draw the tree of calls and add up the work at each level. For merge sort, `T(n) = 2T(n/2) + n`:

```
level 0:        n                 = n
             /     \
level 1:   n/2     n/2            = n
          /  \     /  \
level 2: n/4 n/4  n/4 n/4         = n
          ...
level k: 2^k nodes of n/2^k       = n
          ...
leaves:  n nodes of size 1        = n
```

Each level does n work in total, and the size halves at each level, so there are `log2 n + 1` levels. Total: **Θ(n log n)**.

Now try `T(n) = 3T(n/2) + n` (the shape of Karatsuba's multiplication algorithm). Level k has `3^k` nodes, each doing `n / 2^k` work, so level k totals `n (3/2)^k`. The work *grows* by a factor of 1.5 per level. A growing geometric series is dominated by its **last** term, the leaves. There are

```
3^(log2 n) = n^(log2 3) ~ n^1.585
```

leaves, so `T(n) = Θ(n^(log2 3))` (exponent approximately 1.585).

And `T(n) = 2T(n/2) + n^2`: level k totals `2^k (n/2^k)^2 = n^2 / 2^k`. The work *shrinks* by half per level. A shrinking geometric series is dominated by its **first** term, the root: `T(n) = Θ(n^2)`.

These three behaviours are the whole idea behind the Master Theorem.

> [!tip] The three shapes
> - Work per level **shrinks** geometrically: the root dominates. T(n) = Θ(f(n)).
> - Work per level is **equal**: multiply one level by the number of levels, log n.
> - Work per level **grows** geometrically: the leaves dominate. T(n) = Θ(number of leaves).

## The Master Theorem

The Master Theorem solves recurrences of the form

```
T(n) = a T(n/b) + f(n)
a >= 1, b > 1
```

where a is the number of subproblems, n/b is the size of each, and f(n) is the work done outside the recursive calls.

The key quantity is the **critical exponent** `c = log_b a`. The tree has `a^(log_b n) = n^(log_b a)` leaves, so `n^c` is the total cost of the leaf level. Compare f(n) with `n^c`:

**Case 1: f is polynomially smaller than n^c.** If `f(n) = O(n^(c - ε))` for some `ε > 0`, the leaves dominate:

```
T(n) = Θ(n^c)
```

**Case 2: f is about the same as n^c.** If `f(n) = Θ(n^c log^k n)` for some `k >= 0`, summing the level costs introduces one more log power (levels are equal only when k = 0):

```
T(n) = Θ(n^c log^(k+1) n)
```

**Case 3: f is polynomially larger than n^c.** If `f(n) = Ω(n^(c + ε))` for some `ε > 0`, *and* the **regularity condition** `a f(n/b) <= k f(n)` holds for some constant `k < 1` and all large n, the root dominates:

```
T(n) = Θ(f(n))
```

The regularity condition says that the work really does shrink from one level to the next. It holds automatically for ordinary polynomial f; it exists to rule out pathological, wildly oscillating functions.

### The simple version

Most recurrences you'll meet have `f(n) = Θ(n^d)`. Then just compare d with `log_b a`:

| Compare | Result |
|---|---|
| d < log_b a | Θ(n^(log_b a)) |
| d = log_b a | Θ(n^d log n) |
| d > log_b a | Θ(n^d) |

Equivalently, compare `a` with `b^d`: that ratio is exactly how fast the work per level grows.

### Worked examples

| Recurrence | a, b | log_b a | f | Case | T(n) |
|---|---|---|---|---|---|
| T(n/2) + 1 | 1, 2 | 0 | 1 | 2 | log n |
| 2T(n/2) + n | 2, 2 | 1 | n | 2 | n log n |
| 3T(n/2) + n | 3, 2 | 1.585 | n | 1 | n^1.585 |
| 7T(n/2) + n^2 | 7, 2 | 2.807 | n^2 | 1 | n^2.807 |
| 4T(n/2) + n^2 | 4, 2 | 2 | n^2 | 2 | n^2 log n |
| 2T(n/2) + n^2 | 2, 2 | 1 | n^2 | 3 | n^2 |
| T(n/2) + n | 1, 2 | 0 | n | 3 | n |
| 2T(n/2) + n log n | 2, 2 | 1 | n log n | 2, k=1 | n log^2 n |

Two of these are famous. `7T(n/2) + n^2` is **Strassen's** matrix multiplication: by using 7 half-size multiplications instead of 8, it beats the naive Θ(n^3). `3T(n/2) + n` is **Karatsuba's** integer multiplication, which uses 3 half-size products instead of 4 and beats the schoolbook Θ(n^2). In both, cutting the number of subproblems lowers `log_b a`, which is the exponent that matters in case 1.

## Where the Master Theorem doesn't apply

**Subtract-and-conquer.** `T(n) = T(n - 1) + n` isn't of the form `aT(n/b)`. Unroll it instead: `n + (n-1) + ... + 1 = Θ(n^2)`. Likewise `T(n) = 2T(n - 1) + 1` doubles at every level for n levels: `2^n - 1`, Θ(2^n).

**The gap between cases.** `T(n) = 2T(n/2) + n / log n` has `log_b a = 1`. Is `f = n / log n` polynomially smaller than n? No: `n / log n` is bigger than `n^(1 - ε)` for every `ε > 0`. It isn't `Θ(n log^k n)` for `k >= 0` either. So it falls between case 1 and case 2 of the standard statement. (The answer is `Θ(n log log n)`, as Akra–Bazzi shows below. Some textbooks state an extended case 2 that allows negative k and covers this directly.)

**Uneven splits.** `T(n) = T(n/3) + T(2n/3) + n` has two subproblems of different sizes. The Master Theorem needs every subproblem to be n/b.

**Non-constant a or b.** `T(n) = sqrt(n) T(sqrt(n)) + n` needs other techniques, such as a change of variables (`n = 2^m`).

## Substitution: guess and prove

When no theorem fits, guess the answer (from a recursion tree) and prove it by induction. For merge sort, prove `T(n) <= c n log2 n` for powers of two n ≥ 2, choosing c large enough to cover T(2). Treat T(1) separately, since log2(1) = 0:

```
T(n) = 2T(n/2) + n
     <= 2 c (n/2) log2(n/2) + n
     =  c n (log2 n - 1) + n
     =  c n log2 n - c n + n
     <= c n log2 n      when c >= 1
```

> [!warning] The classic induction bug
> "Guess T(n) = O(n). Then T(n) = 2T(n/2) + n <= 2 c(n/2) + n = cn + n = O(n)." This is wrong. You must prove the *exact* form `T(n) <= cn` with the same c, and `cn + n` is not `<= cn`. Hiding constants inside O during an induction lets you "prove" anything.

## Akra–Bazzi: the general case

The **Akra–Bazzi** method handles recurrences with several subproblem sizes under regularity assumptions: nonnegative g with suitable polynomial growth, bounded positive base cases, and sufficiently small perturbations of the subproblem sizes. The smooth polynomial/logarithmic examples here satisfy these conditions:

```
T(n) = g(n) + sum of a_i T(b_i n)
with a_i > 0 and 0 < b_i < 1
```

1. Find the unique p such that `sum of a_i x b_i^p = 1`.
2. Then

```
T(n) = Θ( n^p (1 + I) )
I = integral from 1 to n
    of g(u) / u^(p+1) du
```

The intuition: p plays the role of `log_b a`. It is the exponent at which the subproblems' total "weight" exactly balances. Then you compare g with `n^p`, much like the Master Theorem, but the integral handles the in-between cases smoothly. (It also tolerates small perturbations such as floors and ceilings in the subproblem sizes.)

**Example 1: uneven split.** `T(n) = T(n/3) + T(2n/3) + n`.

- `(1/3)^p + (2/3)^p = 1` gives `p = 1`.
- `I = integral of u / u^2 = integral of 1/u = ln n`.
- `T(n) = Θ(n (1 + ln n)) = Θ(n log n)`.

The recursion tree agrees: no level does more than n work, the first `log_3 n` levels are complete and do exactly n each, and the deepest path (always taking 2/3) has `log_(3/2) n` levels. Both counts are Θ(log n).

**Example 2: median of medians.** The linear-time selection algorithm satisfies `T(n) = T(n/5) + T(7n/10) + n`.

- At `p = 1`, `1/5 + 7/10 = 0.9 < 1`, so p is less than 1 (numerically about 0.84).
- `I = integral of u^(-p)`, which is about `n^(1-p) / (1-p)`.
- `T(n) = Θ(n^p x n^(1-p)) = Θ(n)`.

The intuition: the subproblem sizes add up to only 90% of n, so the work per level shrinks geometrically and the root's linear work dominates.

**Example 3: the gap case.** `T(n) = 2T(n/2) + n / log n`. Here `p = 1`, and `I = integral of 1 / (u ln u) = ln ln n` (start the integral at 2 rather than 1 to avoid dividing by `ln 1 = 0`; the lower limit only changes constants), giving `Θ(n log log n)`.

## Key takeaways
- Write a recurrence as (number of calls) x T(subproblem size) + (work outside the calls).
- Recursion trees show the three shapes: shrinking levels (root dominates), equal levels (multiply by log n), growing levels (leaves dominate).
- Master Theorem for `aT(n/b) + f(n)`: compare f with `n^(log_b a)`. Smaller: `Θ(n^(log_b a))`. Equal: add a log factor. Larger (with regularity): `Θ(f)`.
- Strassen and Karatsuba win by reducing a, the number of subproblems.
- The Master Theorem does not cover `T(n-1)` recurrences, uneven splits, or f in the gap between cases.
- Akra–Bazzi finds p with `sum a_i b_i^p = 1` and handles uneven splits like `T(n/5) + T(7n/10) + n = Θ(n)`.

## Further reading
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Akra–Bazzi method — Wikipedia](https://en.wikipedia.org/wiki/Akra%E2%80%93Bazzi_method)
- [Divide-and-conquer algorithm — Wikipedia](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm)
- [Algorithms by Jeff Erickson, chapter 1: Recursion](https://jeffe.cs.illinois.edu/teaching/algorithms/)
- [Strassen algorithm — Wikipedia](https://en.wikipedia.org/wiki/Strassen_algorithm)
- [Karatsuba algorithm — Wikipedia](https://en.wikipedia.org/wiki/Karatsuba_algorithm)
