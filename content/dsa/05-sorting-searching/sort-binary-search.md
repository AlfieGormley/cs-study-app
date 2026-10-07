---
id: sort-binary-search
title: Binary search done right
level: intermediate
minutes: 15
summary: Writing binary search from an invariant so it is correct first time, lower and upper bound, the classic overflow and infinite-loop bugs, rotated arrays and binary search on the answer.
---

Binary search is the payoff for sorting. In a sorted array of a billion items, it finds any key in at most 30 middle-element probes. The Python code may perform both equality and order tests per probe. The idea fits in a sentence: compare with the middle element and discard the half that cannot contain the answer.

And yet it is notoriously easy to get wrong. Jon Bentley reported that when he asked professional programmers to write it, around 90% of their versions had bugs. The fix is not to memorise a template, but to write every binary search from an explicit **invariant**.

## Why it is fast

Each step halves the range. Starting from n elements, after k steps about n / 2ᵏ remain. The search ends when one or zero remain, so it takes about log₂ n steps.

| n | max comparisons |
|---|---|
| 1,000 | 10 |
| 1,000,000 | 20 |
| 1,000,000,000 | 30 |

Exactly, a successful search over n elements needs at most ⌊log₂ n⌋ + 1 three-way comparisons. The decision-tree argument from lesson 4 shows no comparison-based search can do better in the worst case.

## Think in invariants

Write down what is true about `lo` and `hi` before every iteration, and make sure each update keeps it true. The loop condition and the return value then follow.

### Version 1: find any index of x (closed interval)

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

### Version 2: lower bound (half-open interval)

Finding *some* match is often not enough. You want the **first** position where x could go: the **lower bound**, the index of the first element ≥ x. This is what Python's `bisect_left` and C++'s `std::lower_bound` return.

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

Trace: find the lower bound of 8 in `[1, 3, 5, 7, 9, 11, 13]`.

```
lo hi mid a[mid]
0  7  3   7    7 < 8   -> lo = 4
4  7  5   11   11 >= 8 -> hi = 5
4  5  4   9    9 >= 8  -> hi = 4
lo == hi == 4: insert 8 at index 4
```

**Upper bound** (first element > x, `bisect_right`) is identical except the test becomes `a[mid] <= x`.

```
a = [1, 3, 3, 3, 5, 8]
lower_bound(a, 3) = 1
upper_bound(a, 3) = 4
count of 3s = 4 - 1 = 3
lower_bound(a, 4) = upper_bound(a, 4) = 4
```

Lower and upper bound together answer most real questions: does x exist (`lo < n and a[lo] == x`), how many copies, where to insert while keeping order, and range queries ("all orders between 10:00 and 11:00" is `[lower_bound(10:00), lower_bound(11:00))`).

## The classic pitfalls

### 1. Midpoint overflow

```java
int mid = (lo + hi) / 2;        // bug
int mid = lo + (hi - lo) / 2;   // fix
int mid = (lo + hi) >>> 1;      // Java
```

With 32-bit ints, `lo + hi` overflows once the array has more than about 2³⁰ (a billion) elements, producing a negative index. In 2006 Joshua Bloch revealed that this bug had sat in Java's `Arrays.binarySearch` for about nine years, and in the version in Programming Pearls for two decades. Python's integers do not overflow, but C, C++, Java, Go and Rust code must use the safe form.

### 2. Infinite loops

If you ever write `lo = mid`, check what happens when `hi = lo + 1`. Then `mid = (lo + hi) // 2 = lo`, so `lo = mid` changes nothing and the loop spins forever.

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

Binary search finds the first true in O(log(range)) evaluations of the predicate.

**Example.** Packages with weights `[1, 2, ..., 10]` must be shipped in order within 5 days. What is the smallest ship capacity that works?

- Capacity below 10 cannot carry the heaviest package; 55 (the total) does it in one day. So the answer is in `[10, 55]`.
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

Five checks of O(n) each, instead of trying all 46 capacities. Total cost: O(n log(sum)). The same pattern handles largest minimum separation of routers when feasibility is monotone and efficiently checkable. A job-scheduling decision can be monotone yet computationally hard. **Content gap:** learning-rate divergence is omitted as an example because general training dynamics do not supply a reliably monotone predicate.

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
- Lower bound (first ≥ x) and upper bound (first > x) answer existence, counts, insertion points and range queries.
- Watch for midpoint overflow in fixed-width languages, `lo = mid` infinite loops and unsorted input.
- Rotated arrays: one half is always sorted (O(log n) for distinct keys only).
- Binary search on the answer works for any monotone predicate, turning "find the minimum that works" into O(log range) checks.

## Further reading
- [Nearly all binary searches and mergesorts are broken — Google Research blog](https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/)
- [Binary search — Wikipedia](https://en.wikipedia.org/wiki/Binary_search)
- [bisect — Python docs](https://docs.python.org/3/library/bisect.html)
- [Binary search — cp-algorithms](https://cp-algorithms.com/num_methods/binary_search.html)
