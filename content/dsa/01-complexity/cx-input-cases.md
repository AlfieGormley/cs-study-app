---
id: cx-input-cases
sourceLesson: cx-analysing-code
title: Best, average and worst cases
level: intermediate
minutes: 2
summary: State which inputs or random choices a performance claim describes.
---

Inputs of the same size can follow different paths. Here n is the number of items and equality comparisons have constant cost.

```python
def find(xs, target):
    for i, x in enumerate(xs):
        if x == target:
            return i
    return -1  # Target is absent.
```

## State what is being averaged

The best case finds the target first: constant work. The worst case finds it last or fails to find it: linear work. If a present target is equally likely to occupy any position, the average search examines about half the list and is still linear.

That average depends on its assumptions. A workload that frequently requests the first item differs from one with mostly absent targets. "Average" without an input distribution is incomplete.

For a randomised algorithm, expected time can instead average over the algorithm's random choices while holding the input fixed. Quicksort with distinct keys and fresh uniformly random pivots has expected Θ(n log n) time on every fixed input of n items. A first-element pivot on sorted distinct input instead gives quadratic work. An adversary adapting to predictable random choices falls outside the fixed-input model.

## Early exits need a remaining worst case

An early return can improve some inputs dramatically. It changes worst-case growth only if every valid input avoids the previous worst path. To assess a claim, try to construct an input that still forces the full scan or unbalanced recursion.

Worst-case guarantees are useful for hostile inputs and deadlines. Average or expected bounds can also be useful, provided their assumptions fit the application. A fast best case alone gives little assurance about an actual workload.

## Key takeaways
- Best and worst case select extreme inputs of a given size.
- Average case requires an input distribution.
- Expected time can average random choices for each fixed input.

## Further reading
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
