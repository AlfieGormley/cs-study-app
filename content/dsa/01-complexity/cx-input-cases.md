---
id: cx-input-cases
sourceLesson: cx-analysing-code
title: Best, average and worst cases
level: intermediate
minutes: 3
summary: State which inputs or random choices a performance claim describes.
---

Here n is the number of input items. Case analysis describes which inputs or random choices are being counted.

## Best, average and worst case

The same algorithm can take very different time on different inputs of the same size. Linear search shows this:

```python
def find(xs, target):
    # enumerate gives positions and values.
    for i, x in enumerate(xs):
        if x == target:
            return i
    # -1 signals that the target is absent.
    return -1
```

- **Best case:** target is first. 1 comparison, Θ(1).
- **Worst case:** target is last or absent. n comparisons, Θ(n).
- **Average case:** if the target is present and equally likely to be at any position, average the comparison counts over all n positions:

```formula
E = (1 + 2 + … + n) / n
E = (n × (n + 1) / 2) / n
E = (n + 1) / 2 = Θ(n)
where
E: the expected (average) number of comparisons
n: the number of items in the list
…: "and so on" up to n
Θ(n): Big-Theta of n: grows in proportion to n
In words: on average you look through about half the list, which is still linear.
```

For a list of 1,001 items that is 501 comparisons on average.

Which one should you report?

- **Worst case** is the default. It's a guarantee, it's usually easiest to analyse, and adversarial inputs exist (users and attackers will find your slow path).
- **Average case** describes typical behaviour, but it depends on an assumption about the input distribution, which may be wrong for your data.
- **Best case** is rarely useful on its own. Any algorithm can be given a fast best case by checking for one special input.

A related term is **expected time** for **randomised** algorithms. For distinct keys with uniformly random pivots, randomised quicksort is expected Θ(n log n) on every fixed input, because the randomness is in the algorithm, not the input. For distinct keys, quicksort with a first- or last-element pivot is average Θ(n log n) over uniformly random permutations but Θ(n²) on sorted input, which real data often is.

> [!example] Early exits
> An early return can improve best or average time. Whether it changes the worst case depends on whether any inputs still force the original expensive path. Ask which inputs attain the maximum after adding the check.

## Key takeaways
- Different inputs of the same size can follow different paths.
- An average-case claim needs an input distribution.
- Expected time for a randomised algorithm averages its random choices under a stated input model.

## Further reading
- [Best, worst and average case — Wikipedia](https://en.wikipedia.org/wiki/Best,_worst_and_average_case)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
