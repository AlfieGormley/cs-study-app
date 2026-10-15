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

Count its runs against the possible orderings:

```formula
N_runs = n^n
N_perm = n!
N_runs = 3^3 = 27
N_perm = 3! = 6
27 / 6 = 4.5
where
N_runs: the number of equally likely sequences of random draws
N_perm: the number of possible orderings (permutations)
n: the number of items, 3 in the example
n^n: n copies of n multiplied together, because each of n steps picks from all n positions
n!: n factorial, 1 × 2 × … × n
In words: 27 equally likely runs cannot be shared evenly among 6 orderings, so some orderings must come up more often.
```

Counting them: three permutations appear 5 times in 27 and three appear 4 times, so some come out with probability 5/27 ≈ 18.5 % instead of 1/6 ≈ 16.7 %.

> [!warning] Unpredictability matters
> A fair permutation algorithm does not make a predictable generator secure. Use an operating-system-backed generator such as `secrets.SystemRandom` when choices must be unpredictable.
>
> Content gap: the specific historical poker incident is omitted because a reliable primary account establishing the exact loop and seed was not verified in this audit.

Two more pitfalls:

- Sorting with a random comparator, such as JavaScript's `arr.sort(() => Math.random() - 0.5)`, gives biased, implementation-dependent results, because the sort assumes comparisons are consistent. Sorting by a random key drawn once per element is unbiased (ignoring ties), but O(n log n) for n elements.
- Too little randomness: a generator can only produce as many shuffles as it has possible seeds, as below.

```formula
52! ≈ 8 × 10^67
log_2(52!) ≈ 225.6
2^32 ≈ 4.3 × 10^9
where
52!: 52 factorial, the number of orders of a 52-card deck
log_2(52!): the base-2 logarithm of 52!: the number of bits needed to give every order its own state
2^32: the number of different seeds a 32-bit seed allows
≈: approximately equal to
In words: a deck has about 8 × 10^67 orders, needing about 226 bits of state, but a 32-bit seed can start only about 4.3 billion different shuffles.
```

  So a generator seeded with 32 bits can reach at most about 4 billion of the deck's orders, a vanishingly small fraction.

## Pitfalls

- Off-by-one ranges: `randint(0, i)` is inclusive in Python, `randrange(i)` is not. Drawing `j` with `randrange(i)` in Fisher–Yates, so position `i` can never keep its own item, is Sattolo's algorithm: it produces only single-cycle permutations, uniformly within that restricted class, rather than uniformly over all permutations.
- Ignoring the high-probability fine print: expected O(log n), for n keys, is extremely reliable at scale, but individual operations vary. Systems needing hard per-operation bounds use deterministic trees.
- Predictable seeds: if attackers can predict your priorities or independent random draws, they can build bad inputs for skip lists and treaps after all.

## Key takeaways

- Swapping with any array position creates unequal permutation counts.
- Unbiased algorithms still require enough unpredictable randomness for security-sensitive uses.

## Further reading
- [Skip list — Wikipedia](https://en.wikipedia.org/wiki/Skip_list)
- [Treap — Wikipedia](https://en.wikipedia.org/wiki/Treap)
- [Treap (Cartesian tree) — cp-algorithms](https://cp-algorithms.com/data_structures/treap.html)
- [Reservoir sampling — Wikipedia](https://en.wikipedia.org/wiki/Reservoir_sampling)
- [Fisher–Yates shuffle — Wikipedia](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle)
