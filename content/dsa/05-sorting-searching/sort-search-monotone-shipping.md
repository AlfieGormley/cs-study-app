---
id: sort-search-monotone-shipping
title: Monotone feasibility and shipping capacity
level: intermediate
minutes: 4
sourceLesson: sort-binary-search
summary: Feasibility must be monotone and cheap enough to evaluate.
---

This unit builds on the preceding search units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

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
        # A full ship starts the next
        # ordered day.
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
        # Feasible capacity may still be too
        # large.
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
T = O(n log(S))
where
T: the total running time of min_capacity
n: the number of packages; each feasibility check walks all of them once
S: the total weight of all packages, which bounds the range of capacities to search (55 here)
log: the logarithm (base 2 here; the base only changes a constant)
O: Big O: grows at most this fast, up to a constant factor
In words: about log(S) feasibility checks, each costing one pass over the n packages.
```

The same pattern handles largest minimum separation of routers when feasibility is monotone and efficiently checkable. A job-scheduling decision can be monotone yet computationally hard. **Content gap:** learning-rate divergence is omitted as an example because general training dynamics do not supply a reliably monotone predicate.

## Key takeaways
- Feasibility must be monotone and cheap enough to evaluate.
- Shipping capacity uses a greedy ordered pass inside each binary-search check.

## Further reading
- [Insertion-bound searches — Python bisect](https://docs.python.org/3/library/bisect.html)
