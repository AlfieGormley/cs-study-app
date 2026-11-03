---
id: adv-shuffle-bias-randomness
title: Shuffle bias, seed limits and adversaries
level: advanced
minutes: 3
summary: Swapping with any array position creates unequal permutation counts.
sourceLesson: adv-randomised-structures
---

Here n is the number of keys or stream items, and k is the requested sample size when sampling. Random draws are assumed independent and uniform under the stated model.

### The classic bug

A tempting variant swaps every position with **any** position:

```python
for i in range(n):
    j = random.randint(0, n - 1)  # wrong
    # Swap across the whole array; later
    # steps may move this item again.
    a[i], a[j] = a[j], a[i]
```

For three distinct items this loop has twenty-seven equally likely sequences of draws but only six possible orderings. Those runs cannot be divided equally among six outcomes, so the output is biased. Enumerating gives three orderings five runs each and three orderings four runs each. Random individual swaps do not imply a uniform final ordering.

> [!warning] Unpredictability matters
> A fair permutation algorithm does not make a predictable generator secure. Use an operating-system-backed generator such as `secrets.SystemRandom` when choices must be unpredictable.


Two more pitfalls:

- Sorting with a random comparator, such as JavaScript's `arr.sort(() => Math.random() - 0.5)`, gives biased, implementation-dependent results, because the sort assumes comparisons are consistent. Sorting by a random key drawn once per element is unbiased (ignoring ties), but O(n log n) for n elements.
- Too little randomness: a generator can only produce as many shuffles as it has possible seeds.

A deterministic generator started from a fixed-size seed can produce no more complete shuffle outcomes than it has possible seeds. Repeated draws do not manufacture new entropy. A correct Fisher–Yates loop cannot overcome a seed space that is too small, and a guessable seed makes prediction easier still.

## Pitfalls

- Off-by-one ranges: `randint(0, i)` is inclusive in Python, `randrange(i)` is not. Drawing `j` with `randrange(i)` in Fisher–Yates, so position `i` can never keep its own item, is Sattolo's algorithm: it produces only single-cycle permutations, uniformly within that restricted class, rather than uniformly over all permutations.
- Ignoring the high-probability fine print: expected O(log n), for n keys, is extremely reliable at scale, but individual operations vary. Systems needing hard per-operation bounds use deterministic trees.
- Predictable seeds: if attackers can predict your priorities or independent random draws, they can build bad inputs for skip lists and treaps after all.

## Key takeaways

- Swapping with any array position creates unequal permutation counts.
- Unbiased algorithms still require enough unpredictable randomness for security-sensitive uses.

## Further reading
- [Python random-number generation](https://docs.python.org/3/library/random.html)
- [CPython’s shuffle implementation](https://raw.githubusercontent.com/python/cpython/v3.14.0/Lib/random.py)
