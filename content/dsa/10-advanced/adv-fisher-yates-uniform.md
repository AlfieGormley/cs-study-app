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
def shuffle(a):
    for i in range(len(a) - 1, 0, -1):
        # Choose among the positions not yet
        # fixed.
        j = random.randint(0, i)
        # Fix one position of the shuffled
        # array.
        a[i], a[j] = a[j], a[i]
```

Think of it as drawing cards from a hat: the last position gets any of the items, the one before it any of the items left, and so on. Count the equally likely runs:

```formula
N_runs = n(n − 1) × … × 1 = n!
N_runs = 3 × 2 × 1 = 6 = 3!
where
N_runs: the number of different, equally likely sequences of random draws
n: the number of items in the array, 3 in the second line
n!: n factorial, the product of every whole number from 1 to n; also the number of permutations (orderings) of n items
…: and so on down to 1
In words: the draws can play out in exactly as many ways as there are orderings, one run per ordering, so every ordering is equally likely.
```

For three items there are 6 runs and 6 orderings, each with probability 1/6. It takes O(n) time (proportional to n) and works in place. This is the version Durstenfeld published in 1964 and Knuth gives as Algorithm P; Python's `random.shuffle` uses it.

## Key takeaways

- Draw from the remaining prefix, including the current position.
- Each permutation corresponds to one equally likely sequence of draws.

## Further reading
- [Skip list — Wikipedia](https://en.wikipedia.org/wiki/Skip_list)
- [Treap — Wikipedia](https://en.wikipedia.org/wiki/Treap)
- [Treap (Cartesian tree) — cp-algorithms](https://cp-algorithms.com/data_structures/treap.html)
- [Reservoir sampling — Wikipedia](https://en.wikipedia.org/wiki/Reservoir_sampling)
- [Fisher–Yates shuffle — Wikipedia](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle)
