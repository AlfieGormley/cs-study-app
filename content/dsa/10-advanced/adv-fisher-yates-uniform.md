---
id: adv-fisher-yates-uniform
title: The Fisher–Yates shuffle
level: advanced
minutes: 2
summary: Draw from the remaining prefix, including the current position.
sourceLesson: adv-randomised-structures
---

Here n is the number of keys or stream items, and k is the requested sample size when sampling. Random draws are assumed independent and uniform under the stated model.

## The Fisher–Yates shuffle

To shuffle an array uniformly, walk from the end. At each position `i`, swap `a[i]` with `a[j]` for `j = randint(0, i)`, which can pick `i` itself.

```python
import random

def shuffle(a):
    for i in range(len(a) - 1, 0, -1):
        # Choose among the positions not yet
        # fixed.
        j = random.randint(0, i)
        # Fix one position of the shuffled
        # array.
        a[i], a[j] = a[j], a[i]
```

At each step, choose uniformly among the items not yet placed. Once a position is filled, later steps never touch it. For any target ordering, there is exactly one sequence of choices that puts those items into their target positions, and all such sequences have equal probability. The argument applies to distinct labelled items; duplicate values can be treated as separately labelled occurrences.

It takes O(n) time for n items and works in place. Python's `random.shuffle` uses this backward-swap procedure.

> [!analogy] Real-world analogy: Drawing names from a hat
> Draw a name for the last seat, then choose among the remaining names for the next seat.
>
> **How it maps:** Fisher–Yates chooses an item from the remaining prefix and fixes one final position per step. Swapping keeps the remaining items available without shifting the array.
>
> **Where it stops:** The random draws must be independent and uniform. A predictable generator is unsuitable when the result must be secret, even if the swapping procedure is correct.

## Key takeaways

- Draw from the remaining prefix, including the current position.
- Each permutation corresponds to one equally likely sequence of draws.

## Further reading
- [Python random-number generation](https://docs.python.org/3/library/random.html)
- [CPython’s shuffle implementation](https://raw.githubusercontent.com/python/cpython/v3.14.0/Lib/random.py)
