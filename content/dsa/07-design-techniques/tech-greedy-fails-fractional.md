---
id: tech-greedy-fails-fractional
title: Why fractional knapsack is greedy
level: advanced
minutes: 2
sourceLesson: tech-greedy-fails
summary: Exchange equal weights of material to favour higher value-to-weight ratio.
---

## Fractional versus 0/1 knapsack

A knapsack holds a maximum total weight, its capacity W. The examples use positive integer weights, non-negative integer values and non-negative integer capacity. Items may be omitted; maximise the value carried.

### Fractional: greedy works

If you can take **part** of an item, sort by **value per unit weight** and take as much as possible of the best ratio first. The code uses exact rational arithmetic so near-equal ratios are not misordered by floating-point rounding.

```python
from fractions import Fraction

def fractional(items, cap):   # (w, v)
    items = list(items)
    if (type(cap) is not int or cap < 0
            or any(type(w) is not int
                   or w <= 0
                   or type(v) is not int
                   or v < 0
                   for w, v in items)):
        raise ValueError("item domain")
    total = Fraction(0)
    by_ratio = sorted(
        items,
        # Compare value densities without
        # rounding.
        key=lambda x: Fraction(x[1], x[0]),
        reverse=True)
    for w, v in by_ratio:
        # Take a fraction if the whole item
        # cannot fit.
        take = min(w, cap)
        total += Fraction(v * take, w)
        cap -= take
        if cap == 0:
            break
    return total
```

Exchange argument: if an optimal load holds some lower-ratio item while higher-ratio material is left behind, swap equal weights. Value goes up or stays the same. So filling by ratio is optimal. For n items, sorting takes O(n log n) ratio comparisons; exact rational arithmetic has additional operand-bit costs.

## Key takeaways
- Exchange equal weights of material to favour higher value-to-weight ratio.
- Exact rational sorting avoids ratio ties being misordered by floating-point rounding.

## Further reading
- [Greedy algorithms — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/04-greedy.pdf)
- [Dynamic programming — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
