---
id: sort-binary-search
title: Binary search done right
level: intermediate
minutes: 15
summary: Writing binary search from an invariant so it is correct first time, lower_bound and upper_bound, the classic overflow and infinite-loop bugs, rotated arrays and binary search on the answer.
---

Binary search is the payoff for sorting. Throughout this lesson, n is the number of elements in the sorted array, and costs use Big O notation (O(log n) grows with the base-2 logarithm of n: how many times n can be halved before reaching 1). In a sorted array of a billion items, it finds any key in at most 30 middle-element probes. The Python code may perform both equality and order tests per probe. The idea fits in a sentence: compare with the middle element and discard the half that cannot contain the answer.

And yet it is notoriously easy to get wrong. Jon Bentley reported that when he asked professional programmers to write it, around 90% of their versions had bugs. The fix is not to memorise a template, but to write every binary search from an explicit **invariant**.

## Why it is fast

Each step halves the range. The search ends when one or zero elements remain, so the question is how many halvings that takes:

```formula
r_k ≈ n / 2^k
n / 2^k = 1  ⇒  k = log_2(n)
log_2(10^9) ≈ 29.9
where
r_k: how many elements are still in range after k steps
n: the number of elements in the sorted array; a billion (10^9) in the last line
k: the number of steps (probes) taken so far
2^k: 2 multiplied by itself k times
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n, which is how many halvings take n down to 1
⇒: "which happens when"
≈: approximately equal to
In words: halving a billion items about 30 times leaves one, so binary search needs about 30 probes.
```

| n | max comparisons |
|---|---|
| 1,000 | 10 |
| 1,000,000 | 20 |
| 1,000,000,000 | 30 |

Exactly:

```formula
c_max = ⌊log_2(n)⌋ + 1
c_max = ⌊log_2(1000)⌋ + 1 = 9 + 1 = 10
where
c_max: the most three-way comparisons (less, equal or greater) a successful search can need
n: the number of elements; here 1,000
log_2(n): the base-2 logarithm of n; log_2(1000) ≈ 9.97
⌊ ⌋: the floor: round down to a whole number
In words: binary search over n elements never needs more than one probe per halving plus one, which is 10 for a thousand elements and 30 for a billion.
```

That is where the table comes from. The decision-tree argument from lesson 4 shows no comparison-based search can do better in the worst case.

## Think in invariants

Write down what is true about `lo` and `hi` before every iteration, and make sure each update keeps it true. The loop condition and the return value then follow.

### Version 1: find any index of x (closed interval)

Here `a` is the sorted array, n its length, x the value we are looking for, and `lo` and `hi` the indices bounding the part of the array still in play.

**Invariant:** if x is in the array, it is in `a[lo..hi]` (inclusive).

```python
def search(a, x):
    lo, hi = 0, len(a) - 1
    while lo <= hi:      # range non-empty
        mid = (lo + hi) // 2
        if a[mid] == x:
            return mid
        if a[mid] < x:
            lo = mid + 1  # x right of mid
        else:
            hi = mid - 1  # x is left of mid
    return -1
```

Every choice follows from the invariant. The range `[lo, hi]` is empty when `lo > hi`, so loop while `lo <= hi`. When `a[mid] < x`, mid itself is ruled out, so `lo = mid + 1`, not `mid`.

### Version 2: lower_bound (half-open interval)

Finding *some* match is often not enough. You want the **first** position where x could go: the **binary-search lower bound** (often called lower_bound), the index of the first element ≥ x. This is what Python's `bisect_left` and C++'s `std::lower_bound` return.

**Invariant:** everything in `a[0..lo)` is < x, and everything in `a[hi..n)` is ≥ x. The answer is in `[lo, hi]`.

```python
def lower_bound(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1   # a[mid] < x
        else:
            hi = mid       # a[mid] >= x
    return lo
```

When the loop ends, `lo == hi`, so everything before it is < x and everything from it on is ≥ x. That is the answer by definition. Note `hi = len(a)`, not `len(a) - 1`: the answer can be "after everything".

Trace: find lower_bound of 8 in `[1, 3, 5, 7, 9, 11, 13]`.

```
lo hi mid a[mid]
0  7  3   7    7 < 8   -> lo = 4
4  7  5   11   11 >= 8 -> hi = 5
4  5  4   9    9 >= 8  -> hi = 4
lo == hi == 4: insert 8 at index 4
```

The **binary-search upper bound** (upper_bound: the first element > x, `bisect_right`) is identical except the test becomes `a[mid] <= x`.

```
a = [1, 3, 3, 3, 5, 8]
lower_bound(a, 3) = 1
upper_bound(a, 3) = 4
count of 3s = 4 - 1 = 3
lower_bound(a, 4) = upper_bound(a, 4) = 4
```

lower_bound and upper_bound together answer most real questions: does x exist (`lo < n and a[lo] == x`), how many copies, where to insert while keeping order, and range queries ("all orders between 10:00 and 11:00" is `[lower_bound(10:00), lower_bound(11:00))`).

## The classic pitfalls

### 1. Midpoint overflow

```java
int mid = (lo + hi) / 2;        // bug
int mid = lo + (hi - lo) / 2;   // fix
int mid = (lo + hi) >>> 1;      // Java
```

A 32-bit signed `int` can hold values only up to about 2.1 billion. Two large indices can add up to more than that:

```formula
s_max = 2^31 − 1 = 2147483647
lo + hi = 1.1 × 10^9 + 1.2 × 10^9
lo + hi = 2.3 × 10^9 > s_max
lo + (hi − lo) / 2 ≤ hi
where
s_max: the largest value a 32-bit signed integer can hold
lo: the low index of the search range; here 1.1 billion
hi: the high index of the search range; here 1.2 billion
2^31: 2 multiplied by itself 31 times
10^9: ten to the power 9, a billion
≤: less than or equal to
>: greater than
In words: once both indices are above about a billion, their sum exceeds the largest int and wraps to a negative number; the safe form only ever adds half the gap to lo, so it never exceeds hi.
```

So `lo + hi` overflows once the array has more than about 2³⁰ (a billion) elements, producing a negative index. In 2006 Joshua Bloch revealed that this bug had sat in Java's `Arrays.binarySearch` for about nine years, and in the version in Programming Pearls for two decades. Python's integers do not overflow, but C, C++, Java, Go and Rust code must use the safe form.

### 2. Infinite loops

If you ever write `lo = mid`, check what happens when `hi = lo + 1`. Then `mid = (lo + hi) // 2 = lo`, so `lo = mid` changes nothing and the loop spins forever:

```formula
m = ⌊(lo + hi) / 2⌋
m = ⌊(4 + 5) / 2⌋ = ⌊4.5⌋ = 4
where
m: the midpoint index, mid in the code
lo: the low end of the range; here 4
hi: the high end of the range; here 5, one more than lo
⌊ ⌋: the floor: round down to a whole number (Python's // does this)
In words: with two elements left, the rounded-down midpoint is lo itself, so setting lo to it makes no progress.
```

```
lo=4, hi=5 -> mid=4 -> lo = mid = 4
lo=4, hi=5 -> mid=4 -> ... forever
```

The fixes: make every branch move strictly past mid (`lo = mid + 1`), or round the midpoint up (`mid = (lo + hi + 1) // 2`) when the branch is `lo = mid`, or loop while `hi - lo > 1` (see the square root example below).

### 3. Mixing interval conventions

Most bugs come from mixing closed `[lo, hi]` and half-open `[lo, hi)` conventions: `hi = len(a)` with `while lo <= hi` reads past the end; `hi = len(a) - 1` with `hi = mid` can never return n. Pick one convention per function and derive every line from it.

### 4. Unsorted or wrongly sorted input

Binary search on data that is not sorted by the same ordering silently returns nonsense, not an error. Sorting by `key=str.lower` and then searching with raw strings is a classic mismatch.

> [!tip] Test the edges
> Every binary search should be tested on: an empty array, one element, x smaller than everything, x larger than everything, x absent but in the middle, and many duplicates. Off-by-one bugs hide in exactly those cases.

## Searching a rotated sorted array

A sorted array rotated at an unknown point, like `[15, 18, 22, 3, 6, 9, 12]`, is not sorted, but **at least one half around any mid is sorted**. Check which half is sorted and whether x lies inside its range.

```python
def search_rotated(a, x):  # distinct keys
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == x:
            return mid
        if a[lo] <= a[mid]:  # left sorted
            if a[lo] <= x < a[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:  # right half sorted
            if a[mid] < x <= a[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```

This is still O(log n), but only for **distinct** keys. With duplicates, `[2, 2, 2, 3, 2]` makes it impossible to tell which half is sorted when `a[lo] == a[mid] == a[hi]`, and the worst case becomes O(n).

The same idea finds the **rotation point** (the minimum): if `a[mid] > a[hi]`, the drop is to the right of mid; otherwise it is at mid or to its left.

## Binary search on the answer

The most powerful generalisation: you do not need an array at all. You need a **monotone predicate**: a yes/no test that is false up to some point and true from then on.

```
cap:     10 11 12 13 14 15 16 ...
ok?:      F  F  F  F  F  T  T ...
                         ^ find this
```

Binary search finds the first true in about log₂ of the number of candidates evaluations of the predicate:

```formula
e ≤ ⌈log_2(H − L + 1)⌉
e ≤ ⌈log_2(55 − 10 + 1)⌉ = ⌈5.52⌉ = 6
where
e: the number of times the predicate is evaluated
L: the smallest candidate answer; 10 in the example below
H: the largest candidate answer; 55 in the example below
log_2: the base-2 logarithm
⌈ ⌉: the ceiling: round up to the next whole number
≤: less than or equal to
In words: each evaluation halves the candidate range, so 46 candidates need at most 6 checks.
```

**Example.** Packages with weights `[1, 2, ..., 10]` must be shipped in order within 5 days. What is the minimum ship capacity that works?

- A ship capacity below 10 cannot carry the heaviest package; 55 (the total) does it in one day. So the answer is in `[10, 55]`.
- "Can we ship with capacity c?" is monotone: if c works, any larger c works. It is checked greedily in O(n).

```python
def can_ship(w, days, cap):
    if days < 1:
        return False
    need, load = 1, 0
    for x in w:
        if x > cap:
            return False
        if load + x > cap:
            need += 1   # start a new day
            load = 0
        load += x
    return need <= days

def min_capacity(w, days):
    if days < 1 or not w:
        raise ValueError("weights and days")
    if any(type(x) is not int or x <= 0
           for x in w):
        raise ValueError(
            "positive int weights"
        )
    lo, hi = max(w), sum(w)
    while lo < hi:
        mid = (lo + hi) // 2
        if can_ship(w, days, mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

```
lo  hi  mid  ok?
10  55  32   yes -> hi = 32
10  32  21   yes -> hi = 21
10  21  15   yes -> hi = 15
10  15  12   no  -> lo = 13
13  15  14   no  -> lo = 15
answer: 15
```

Five checks of O(n) each, instead of trying all 46 capacities. In general:

```formula
T = O(n × log(S))
where
T: the total running time of min_capacity
n: the number of packages; each feasibility check walks all of them once
S: the total weight of all packages, which bounds the range of capacities to search (55 here)
log: the logarithm (base 2 here; the base only changes a constant)
O: Big O: grows at most this fast, up to a constant factor
In words: about log(S) feasibility checks, each costing one pass over the n packages.
```

The same pattern handles largest minimum separation of routers when feasibility is monotone and efficiently checkable. A job-scheduling decision can be monotone yet computationally hard. **Content gap:** learning-rate divergence is omitted as an example because general training dynamics do not supply a reliably monotone predicate.

**Integer square root** is another instance, using the `hi - lo > 1` style:

```python
def isqrt(n):
    if type(n) is not int or n < 0:
        raise ValueError(
            "nonnegative integer"
        )
    lo, hi = 0, n + 1   # lo*lo <= n < hi*hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid
    return lo
```

For **real-valued** answers, use a suitable tolerance and an iteration limit, and stop when the computed midpoint equals an endpoint. A fixed 100 halvings does not cover every possible binary64 interval, especially across large exponent ranges or near subnormal values.

## Binary search in the wild

- **`git bisect`** narrows commit ancestry using good/bad tests. On a linear, monotone history with no skipped commits, 1,000 candidates take about 10 tests; merge graphs, flaky tests and fixes/reintroductions complicate that model.
- **B-tree pages** in databases (PostgreSQL, InnoDB) binary search the sorted keys inside each page.
- **Timsort's galloping** (lesson 6) is an exponential search: probe 1, 3, 7, 15 ... until overshooting, then binary search. That is the right tool when the answer is probably near the start or the range is unbounded.
- **Standard libraries:** Python's `bisect`, C++'s `lower_bound`, `upper_bound` and `equal_range`, Java's `Arrays.binarySearch` (returns `-(insertion point) - 1` when absent), and Go's `sort.Search`, which is binary search on a predicate.

## Key takeaways
- Binary search takes about log₂ n steps: 30 for a billion items.
- Write it from an invariant, choose one interval convention ([lo, hi] or [lo, hi)) and derive the loop condition and updates from it.
- lower_bound (first ≥ x) and upper_bound (first > x) answer existence, counts, insertion points and range queries.
- Watch for midpoint overflow in fixed-width languages, `lo = mid` infinite loops and unsorted input.
- Rotated arrays: one half is always sorted (O(log n) for distinct keys only).
- Binary search on the answer works for any monotone predicate, turning "find the minimum that works" into O(log range) checks.

## Further reading
- [Nearly all binary searches and mergesorts are broken — Google Research blog](https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/)
- [Binary search — Wikipedia](https://en.wikipedia.org/wiki/Binary_search)
- [bisect — Python docs](https://docs.python.org/3/library/bisect.html)
- [Binary search — cp-algorithms](https://cp-algorithms.com/num_methods/binary_search.html)
