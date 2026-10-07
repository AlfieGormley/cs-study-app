---
id: disc-counting
title: "Counting: permutations, combinations and pigeonhole"
level: intermediate
minutes: 14
summary: The sum and product rules, permutations and combinations, repetition and stars and bars, the binomial theorem, and the pigeonhole principle behind hash collisions and impossible compressors.
---

Counting sounds like primary school, but it is how you estimate brute-force search spaces, password strength, the number of test cases, the probability of a collision and the size of the output of an algorithm. Most errors come from one of two mistakes: counting the same thing twice, or not being clear whether **order matters**.

The good news is that nearly every problem reduces to a handful of rules, applied carefully.

## The two basic rules

**Product rule.** If a task is a sequence of steps, with a choices for the first and b for the second (whatever the first was), there are a · b ways in total.

**Sum rule.** If a task can be done in one of several *disjoint* ways, add the counts.

```
4-digit PIN, digits 0-9:
  10^4 = 10,000
PIN with no repeated digit:
  10*9*8*7 = 5,040
Password of length 1 to 3 over a-z:
  26 + 26^2 + 26^3 = 18,278
```

The PIN example is the product rule with shrinking choices. The password example is the sum rule over disjoint lengths, then the product rule within each length.

> [!example] How big is a brute-force search?
> An 8-character password over 62 symbols (a–z, A–Z, 0–9) has 62⁸ ≈ 2.18 × 10¹⁴ possibilities. At an assumed 10¹⁰ guesses per second, exhausting the space takes about 6 hours; this is arithmetic, not a measured hardware benchmark. Add 4 characters and it becomes 62¹² ≈ 3.2 × 10²¹, around 10,000 years. For independently and uniformly chosen symbols, adding length multiplies the search space exponentially. Human-chosen passwords need a different model.

## Permutations: order matters

A **permutation** is an ordering. The number of ways to order n distinct items is

```
n! = n * (n-1) * ... * 2 * 1
```

The number of ways to pick an ordered sequence of k items from n (no repeats) is

```
P(n, k) = n! / (n-k)!
        = n * (n-1) * ... * (n-k+1)
```

Choosing a gold, silver and bronze winner from 8 runners: P(8, 3) = 8 · 7 · 6 = 336.

For every fixed base c > 1, n! eventually grows faster than cⁿ: 10! is about 3.6 million, 20! is about 2.4 × 10¹⁸. That is why brute-forcing the travelling salesman problem (trying every ordering of cities) quickly becomes impractical as n grows (the cutoff depends on the implementation and hardware), and why sorting lower bounds come from log₂(n!) ≈ n log₂ n (a comparison sort must distinguish all n! orderings).

## Combinations: order doesn't matter

A **combination** is a subset. The number of k-element subsets of an n-element set is the **binomial coefficient**:

```
C(n, k) = n! / (k! (n-k)!)
        = P(n, k) / k!
```

Why divide by k!? Each unordered set of k items appears k! times among the ordered sequences. This "count ordered, then divide out the overcounting" move is one of the most useful in counting.

Choosing a team of 3 from 8 people: C(8, 3) = 336 / 6 = 56.

Useful facts:

- **Symmetry**: C(n, k) = C(n, n−k). Choosing who's in is the same as choosing who's out.
- **Pascal's rule**: C(n, k) = C(n−1, k−1) + C(n−1, k). Either a particular item is in the subset or it isn't.
- **Sum of a row**: C(n, 0) + C(n, 1) + … + C(n, n) = 2ⁿ, the total number of subsets.

```
Pascal's triangle
          1
         1 1
        1 2 1
       1 3 3 1
      1 4 6 4 1
    1 5 10 10 5 1
```

### The binomial theorem

```
(x + y)^n = sum over k of C(n,k) x^k y^(n-k)
```

Expanding (x + y)ⁿ means picking x or y from each of the n brackets; C(n, k) counts the ways to pick x exactly k times. Setting x = y = 1 recovers the 2ⁿ row sum.

### Lattice paths

How many shortest paths are there on a grid from (0, 0) to (4, 3), moving only right (R) or up (U)? Every path is a string of 4 Rs and 3 Us, and choosing which 3 of the 7 positions are Us fixes it: C(7, 3) = 35. Many dynamic-programming problems ("unique paths") are this binomial coefficient in disguise.

## Repetition allowed

| Order? | Repeats? | Count |
|---|---|---|
| Yes | No | P(n, k) |
| Yes | Yes | nᵏ |
| No | No | C(n, k) |
| No | Yes | C(n+k−1, k) |

Here n ≥ 1 and k ≥ 0; no-repeat factorial formulas assume k ≤ n (otherwise the count is zero). The last row, **multisets**, is counted with **stars and bars**. Distributing k identical items into n distinct bins is the same as arranging k stars and n − 1 bars in a line:

```
10 identical jobs, 4 workers:
**|****||****   -> 2, 4, 0, 4
positions: 10 stars + 3 bars = 13
choose bar positions: C(13, 3) = 286
```

If every worker must get at least one job, hand one to each first, then distribute the remaining 6 freely: C(6 + 3, 3) = C(9, 3) = 84.

### Arrangements with repeated letters

The number of distinct arrangements of a word with repeated letters is the **multinomial coefficient**: n! divided by the factorial of each letter's count. BANANA has 6 letters with A × 3, N × 2, B × 1:

```
6! / (3! * 2! * 1!) = 720 / 12 = 60
```

## Check by brute force

When in doubt, write the dumbest possible enumeration for a small case. Python's `itertools` and `math` make this one line each:

```python
from itertools import (permutations,
    combinations, product)
from math import comb, perm

len(list(permutations('abcd', 2)))  # 12
perm(4, 2)                          # 12
len(list(combinations('abcd', 2)))  # 6
comb(4, 2)                          # 6
len(set(permutations('BANANA')))    # 60
```

Brute force for small n, then the formula for large n, is the standard workflow for avoiding off-by-one and overcounting mistakes.

## The pigeonhole principle

**If n + 1 pigeons sit in n holes, some hole has at least two pigeons.** More generally, if N items go into k boxes, some box has at least ⌈N/k⌉ items.

It sounds trivial, but it proves things that are otherwise surprising:

- Among 13 people, two share a birth month.
- Hash 1,000,000 keys into 4,096 buckets and some bucket receives at least ⌈244.1⌉ = 245 keys, however good the hash function.
- In a group of at least two people with mutual friendships and no self-friendships, two have the same number of friends within the group (n people, possible counts 0 to n − 1, but 0 and n − 1 can't both occur).

> [!note] No compressor shrinks every file
> There are 2ⁿ files of exactly n bits but only 2ⁿ − 1 files shorter than n bits (2⁰ + 2¹ + … + 2ⁿ⁻¹). A lossless compressor must be injective, so it cannot map all 2ⁿ inputs to shorter outputs. A compressor defined on all finite bit strings that shrinks some inputs must expand others (an identity encoding need not expand anything); format framing and block overhead are concrete reasons gzip or zstd output may grow. The counting argument proves that some growth is unavoidable for such a total shrinking compressor; it does not require a particular header design.

Pigeonhole is also the root of the **birthday problem**, which asks the harder question of when a collision becomes *likely* rather than *certain*. In the model of independent, uniformly distributed birthdays over 365 possible days, certainty needs 366 people, but 23 already give a better than 50% chance. That probability calculation, and its consequence that independent uniformly distributed b-bit hash outputs have substantial collision probability around 2^(b/2) items (collisions can also occur earlier), is covered in the probability module.

## Common traps

- **Order or not?** "Choose a committee" is a combination; "choose a president, secretary and treasurer" is a permutation. A committee of 3 with a chair is either 3 · C(10, 3) or 10 · C(9, 2): both give 360.
- **Overcounting symmetric arrangements.** Seating n people round a table where rotations count as the same gives (n − 1)!, not n!. For n ≥ 3 distinct people, if mirror images also count as the same, halve it again.
- **"At least one".** Count the complement. Passwords of length 6 over a–z and 0–9 with at least one digit: 36⁶ − 26⁶ (all minus those with no digit). Trying to count "exactly one digit, plus exactly two, plus …" directly is slower and error-prone, and "pick a position for the digit, then fill the rest" overcounts.
- **Disjointness in the sum rule.** If the cases overlap you need inclusion–exclusion, which is the next lesson.

## Key takeaways
- Product rule for sequences of choices, sum rule for disjoint cases; nearly everything builds on these two.
- P(n, k) counts ordered selections; C(n, k) = P(n, k) / k! counts unordered ones.
- Stars and bars gives C(n + k − 1, k) for k identical items into n bins; multinomials handle repeated letters.
- Pigeonhole: N items in k boxes forces a box with at least ⌈N/k⌉, which is why hash collisions and incompressible files must exist.
- Count the complement for "at least one", and always check a small case by brute force.

## Further reading
- [Combination — Wikipedia](https://en.wikipedia.org/wiki/Combination)
- [Permutation — Wikipedia](https://en.wikipedia.org/wiki/Permutation)
- [Stars and bars — Wikipedia](https://en.wikipedia.org/wiki/Stars_and_bars_(combinatorics))
- [Pigeonhole principle — Wikipedia](https://en.wikipedia.org/wiki/Pigeonhole_principle)
- [itertools — Python docs](https://docs.python.org/3/library/itertools.html)
- [Mathematics for Computer Science, Part III: Counting (MIT)](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
