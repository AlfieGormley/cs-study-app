---
id: cx-writing-recurrences
sourceLesson: cx-recurrences
title: Writing recurrences from code
level: advanced
minutes: 4
summary: Separate recursive subproblem costs from each call’s own work.
---

Loops can be analysed by counting. Recursive algorithms, especially **divide and conquer** (split the problem, solve the pieces recursively, combine), need a different tool. Their running time is naturally described by a **recurrence**: an equation that defines T(n), the running time on an input of size n, in terms of T on smaller inputs.

This lesson is about writing those recurrences and solving them quickly. Throughout, n is the input size, O, Ω and Θ are the upper, lower and tight bounds from the asymptotic-notation lessons, and logarithms use base two unless another base is written.

## From code to recurrence

Every recursive function's cost splits into the calls it makes and the work it does itself:

```formula
T(n) = r T(m) + w(n)
where
T(n): the running time on an input of size n, in basic steps
r: how many recursive calls one call makes
T(m): the running time of one recursive call
m: the input size each recursive call gets, smaller than n
w(n): the work one call does outside its recursive calls (splitting, comparing, merging)
n: the input size of the current call
In words: the cost of a call is the cost of all the calls it makes, plus the work it does itself.
```

```python
# a is sorted; lo and hi are inclusive.
def bsearch(a, t, lo, hi):
    if lo > hi:
        # Empty range: target is absent.
        return -1
    mid = (lo + hi) // 2
    if a[mid] == t:
        return mid
    if a[mid] < t:
        # Narrow indices without copying a.
        return bsearch(a, t, mid + 1, hi)
    return bsearch(a, t, lo, mid - 1)
```

Binary search makes one recursive call on half the range, plus a constant amount of work (O(1)). Merge sort calls itself on two halves and merges in linear time:

```formula
T_bs(n) = T_bs(n / 2) + O(1)
T_ms(n) = 2T_ms(n / 2) + Θ(n)
where
T_bs(n): the running time of binary search on a range of n items
T_ms(n): the running time of merge sort on n items
n: the input size
O(1): at most a constant amount of work, however large n is
Θ(n): work proportional to n (the merge step touches every item once)
In words: binary search does a constant amount of work and then searches one half; merge sort sorts both halves and then does a linear merge.
```

Some common recurrence/solution pairs follow. Each pair uses T for its own cost function with a fixed positive base case:

```formula
T(n) = T(n/2) + 1
T(n) = Θ(log(n))
T(n) = T(n/2) + n
T(n) = Θ(n)
T(n) = 2T(n/2) + 1
T(n) = Θ(n)
T(n) = 2T(n/2) + n
T(n) = Θ(n log(n))
T(n) = T(n − 1) + 1
T(n) = Θ(n)
T(n) = T(n − 1) + n
T(n) = Θ(n^2)
T(n) = 2T(n − 1) + 1
T(n) = Θ(2^n)
where
T(n): the cost in each independent pair, in basic steps
n: the current input size
log: the base-2 logarithm
Θ: a tight growth bound
In words: The first four pairs are half-size recursion; the last three reduce size by one. Their ordering matches the examples below.
```

| Pair | Example | Growth |
|---|---|---|
| 1 | Binary search | logarithmic |
| 2 | Halving then scanning | linear |
| 3 | Tree traversal | linear |
| 4 | Merge sort | linear times log |
| 5 | Linear recursion | linear |
| 6 | Selection sort | quadratic |
| 7 | Towers of Hanoi | exponential |

The following recurrence lessons derive these bounds. The **base case** costs a fixed amount when input is too small to split, so it is usually left implicit. Rounding fractional input sizes up or down does not change these asymptotic answers.

## Key takeaways
- A recurrence adds recursive subproblem costs to the work outside those calls.
- The number and size of recursive calls determine its shape.
- Base cases and rounding matter for exact counts even when they leave the eventual growth unchanged.

## Further reading
- [Divide-and-conquer algorithm — Wikipedia](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm)
- [Algorithms by Jeff Erickson, chapter 1: Recursion](https://jeffe.cs.illinois.edu/teaching/algorithms/)
