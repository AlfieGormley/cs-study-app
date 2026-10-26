---
id: prob-quicksort-runtime-checks
title: Check quicksort runtime and production safeguards
level: advanced
minutes: 3
sourceLesson: prob-algorithms
summary: A sampled comparison count is one draw, rather than proof of the mean.
---

A measured quicksort execution is one draw from a runtime distribution. Repeating it can check an expected-comparison prediction, but one fast run cannot establish either the mean or a worst-case guarantee.

## Count the work actually performed

```python
import random

def qs(a):
    # Distinct keys with a total order.
    # Count actual pivot comparisons.
    if len(a) <= 1:
        return 0
    # Every element can be the next pivot.
    i = random.randrange(len(a))
    p = a[i]
    lo, hi = [], []
    for j, x in enumerate(a):
        # Skip the pivot itself.
        if j == i:
            continue
        if x < p:
            lo.append(x)
        else:
            hi.append(x)
    # Count this partition and both sides.
    return (len(a) - 1) + qs(lo) + qs(hi)

print(qs(list(range(1000))))
# One run; the mean is about 10,986.
```

This function counts pivot comparisons; it does not return the sorted array. It assumes distinct keys with a total order. Every partition compares its pivot once with each other element, then adds the two recursive counts.

For 1,000 distinct keys and fresh independent uniform pivots, the theoretical mean is about 10,986 comparisons. Individual runs vary. Check many independent runs if estimating the mean, and distinguish comparison counts from elapsed time, which also includes allocation, recursion and machine effects.

## Understand what randomisation changes

On sorted distinct input, always choosing the first element repeatedly creates the most unbalanced partition. Uniform random pivots remove that systematic dependence on input order in expectation. They do not prevent a sequence of extreme pivots by chance.

The teaching implementation can still have quadratic work and deep recursion. Equal keys also all enter one side in this two-way partition, so the distinct-key guarantee does not apply to them. An adaptive adversary or predictable random choices changes the assumptions too.

Production sorts can use duplicate-aware partitioning, depth limits and a fallback algorithm such as heapsort to provide stronger safeguards. Evaluate the actual library contract and implementation rather than assuming it is this teaching function.

## Key takeaways
- A single run checks behaviour, not an expectation or bound.
- Random pivots improve expected behaviour on fixed distinct-key inputs.
- Duplicate handling and fallback strategies address risks outside that expectation.

## Further reading
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
