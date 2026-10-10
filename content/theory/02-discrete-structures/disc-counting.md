---
id: disc-counting
title: "Counting: permutations, combinations and pigeonhole"
level: intermediate
minutes: 18
summary: The sum and product rules, permutations and combinations, repetition and stars and bars, the binomial theorem, and the pigeonhole principle behind hash collisions and impossible compressors.
---

Counting sounds like primary school, but it is how you estimate brute-force search spaces, password strength, the number of test cases, the probability of a collision and the size of the output of an algorithm. Most errors come from one of two mistakes: counting the same thing twice, or not being clear whether **order matters**.

The good news is that nearly every problem reduces to a handful of rules, applied carefully.

## The two basic rules

**Product rule.** If a task is a sequence of steps, and the number of choices at each step doesn't depend on what you chose earlier, multiply the counts.

**Sum rule.** If a task can be done in one of several *disjoint* ways (no outcome belongs to two of them), add the counts.

```formula
N_seq = a × b
N_alt = a + b
where
N_seq: the number of ways to do step one and then step two (product rule)
N_alt: the number of ways to do the task one way or the other, when no outcome is counted by both ways (sum rule)
a: the number of choices in the first step, or the number of outcomes of the first way
b: the number of choices in the second step (the same whatever the first choice was), or the number of outcomes of the second way
In words: "and then" multiplies, "or" (with no overlap) adds. Both extend to any number of steps or ways.
```

Three everyday examples: a 4-digit PIN, a PIN with no repeated digit, and a lower-case password of length 1 to 3.

```formula
N_PIN = 10 × 10 × 10 × 10 = 10^4
N_PIN = 10,000
N_dist = 10 × 9 × 8 × 7 = 5,040
N_pw = 26 + 26^2 + 26^3
N_pw = 26 + 676 + 17,576 = 18,278
where
N_PIN: the number of 4-digit PINs when any digit 0–9 may appear in any position, repeats allowed
N_dist: the number of 4-digit PINs with no repeated digit: 10 choices, then 9 left, then 8, then 7
N_pw: the number of passwords of length 1, 2 or 3 made from the 26 letters a–z
10^4: 4 copies of 10 multiplied together (one factor of 10 per position)
26^2, 26^3: 26 × 26 and 26 × 26 × 26: the counts of 2-letter and 3-letter passwords
In words: the PIN counts are the product rule (the second with shrinking choices); the password count is the sum rule over the three disjoint lengths, then the product rule inside each length.
```

> [!example] How big is a brute-force search?
> An 8-character password over 62 symbols (a–z, A–Z, 0–9) has 62⁸ ≈ 2.18 × 10¹⁴ possibilities. At an assumed 10¹⁰ guesses per second, exhausting the space takes about 6 hours; this is arithmetic, not a measured hardware benchmark. Add 4 characters and it becomes 62¹² ≈ 3.2 × 10²¹, around 10,000 years. For independently and uniformly chosen symbols, adding length multiplies the search space exponentially. Human-chosen passwords need a different model.

## Permutations: order matters

A **permutation** is an ordering. To put n distinct items in order there are n choices for the first place, n − 1 for the second, and so on down to 1. That product has its own name and symbol, the **factorial**:

```formula
n! = n × (n − 1) × … × 2 × 1
5! = 5 × 4 × 3 × 2 × 1 = 120
where
n: the number of distinct items being put in order, a whole number 0 or more
!: factorial: multiply every whole number from n down to 1. By convention 0! = 1 (there is exactly one way to order nothing)
…: and so on: the pattern continues through every whole number in between
In words: n factorial is the number of different orderings of n distinct things. Five items can be lined up in 120 ways.
```

Often you only fill k places from n items (no item used twice). You stop the product after k factors, which is the same as dividing n! by the (n − k)! orderings of the items you didn't use:

```formula
P(n, k) = n! / (n − k)!
P(n, k) = n × (n − 1) × … × (n − k + 1)
P(8, 3) = 8 × 7 × 6 = 336
where
P(n, k): the number of permutations of k items from n: ordered selections with no item used twice
n: the number of distinct items available
k: how many places are filled, from 0 up to n
!: factorial: the product of every whole number from that number down to 1, with 0! = 1
…: the pattern continues; the second line has exactly k factors
In words: n choices for the first place, one fewer for each later place, k places in total. Choosing a gold, silver and bronze winner from 8 runners gives 336 possible podiums.
```

Factorials grow very fast. 10! is about 3.6 million and 20! is about 2.4 × 10¹⁸. However large a fixed base you pick, the factorial eventually overtakes its powers:

```formula
n! > c^n   for all n ≥ n_0
where
n!: n factorial, the product of every whole number from n down to 1
c: any fixed number greater than 1, for example 2 or 1000
c^n: n copies of c multiplied together (exponential growth)
n_0: a threshold that depends on c; past it the inequality always holds. For c = 2, n_0 = 4 (4! = 24 > 16)
≥: greater than or equal to
In words: factorial growth beats every exponential in the end, because each new factor n keeps getting bigger while c stays fixed.
```

That is why brute-forcing the travelling salesman problem (trying every ordering of cities) quickly becomes impractical as the number of cities grows (the cutoff depends on the implementation and hardware).

It is also where the lower bound for comparison sorting comes from. A sort that only compares items must be able to tell all n! orderings of its input apart, and each yes/no comparison at best halves the possibilities, so it needs about log₂(n!) comparisons in the worst case:

```formula
log_2(n!) ≈ n × log_2(n)
log_2(20!) ≈ 61.1
20 × log_2(20) ≈ 86.4
where
n: the number of items being sorted
n!: n factorial, the number of possible orderings of n distinct items
log_2: logarithm base 2: log_2(x) is the power you raise 2 to in order to get x, i.e. how many halvings take x down to 1
≈: approximately equal to; here it means the ratio of the two sides tends to 1 as n grows
In words: the number of comparisons needed grows like n log n. The approximation is rough for small n (at n = 20 the two sides are 61 and 86, a ratio of about 0.71), but the ratio creeps towards 1 as n grows.
```

## Combinations: order doesn't matter

A **combination** is a subset: a choice of items where order is irrelevant. The number of k-element subsets of an n-element set is the **binomial coefficient**. Count the ordered selections, then divide out the overcounting: each unordered group of k items appears k! times among the ordered ones.

```formula
C(n, k) = n! / (k! × (n − k)!)
C(n, k) = P(n, k) / k!
C(8, 3) = 336 / 6 = 56
where
C(n, k): the binomial coefficient, read "n choose k": the number of ways to choose k items from n distinct items when order doesn't matter. Books also write it as n over k in tall brackets
P(n, k): the number of ordered selections of k items from n (no repeats), n! / (n − k)!
n: the number of distinct items available
k: how many are chosen, from 0 up to n
!: factorial: the product of every whole number from that number down to 1, with 0! = 1
In words: choosing a team of 3 from 8 people: there are 336 ordered ways to pick 3, and each team turns up 3! = 6 times among them, so there are 56 teams.
```

This "count ordered, then divide out the overcounting" move is one of the most useful in counting.

Three facts about binomial coefficients, each with a one-line counting argument:

- **Symmetry.** Choosing who's in is the same as choosing who's out.
- **Pascal's rule.** Pick one particular item: either it is in the subset or it isn't, and those two cases are disjoint.
- **Sum of a row.** Adding the counts for every possible subset size gives the total number of subsets, and each item is independently in or out.

```formula
C(n, k) = C(n, n − k)
C(n, k) = C(n − 1, k − 1) + C(n − 1, k)
C(n, 0) + C(n, 1) + … + C(n, n) = 2^n
C(5, 2) = C(5, 3) = 10
C(5, 2) = C(4, 1) + C(4, 2) = 4 + 6
1 + 5 + 10 + 10 + 5 + 1 = 32 = 2^5
where
C(n, k): the number of ways to choose k items from n when order doesn't matter ("n choose k")
n: the number of distinct items, at least 1 for Pascal's rule
k: the size of the subset, from 0 to n (for Pascal's rule, 1 to n − 1 so both terms make sense)
…: and so on, through every subset size from 0 to n
2^n: n copies of 2 multiplied together: each of the n items is either in or out
In words: line 1 is symmetry, line 2 is Pascal's rule, line 3 is the row sum. The last three lines check each fact with n = 5.
```

Pascal's rule is exactly how each number in Pascal's triangle is the sum of the two above it:

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

Binomial coefficients get their name from expanding a power of a two-term sum such as x + y. Expanding (x + y)ⁿ means picking either x or y from each of the n brackets and multiplying; the number of ways to pick x exactly k times is C(n, k).

```formula
(x + y)^n = Σ C(n, k) × x^k × y^{n−k}
(x + y)^3 = x^3 + 3 × x^2 × y
          + 3 × x × y^2 + y^3
where
x, y: any two numbers (or algebraic quantities that commute)
n: the power, a whole number 0 or more
k: the number of brackets from which x is picked, running from 0 to n
C(n, k): the number of ways to choose those k brackets ("n choose k")
Σ: sigma, "sum of": add up the term after it for every whole number k from 0 to n
x^k, y^{n−k}: k copies of x multiplied together, y multiplied by itself n − k times
In words: the coefficient of the term with k copies of x is the number of ways to choose which k brackets supply them. For n = 3 the coefficients are 1, 3, 3, 1, the fourth row of Pascal's triangle.
```

Substituting 1 for both x and y makes the left side 2ⁿ and the right side the sum of the row, which recovers the row-sum fact above.

### Lattice paths

How many shortest paths are there on a grid from (0, 0) to (4, 3), moving only right (R) or up (U)? Every path is a string of 4 Rs and 3 Us, and choosing which 3 of the 7 positions are Us fixes it:

```formula
N_path = C(7, 3) = (7 × 6 × 5) / 3!
N_path = 210 / 6 = 35
where
N_path: the number of shortest grid paths from (0, 0) to (4, 3)
C(7, 3): the number of ways to choose 3 of the 7 moves to be up-moves ("7 choose 3")
!: factorial: 3! = 3 × 2 × 1 = 6
In words: a path is fixed by deciding which 3 of its 7 moves go up, so there are 35 paths.
```

Many dynamic-programming problems ("unique paths") are this binomial coefficient in disguise.

## Repetition allowed

In this table, n is the number of distinct items (or kinds of item) available, at least 1, and k is how many you pick, 0 or more. nᵏ means k copies of n multiplied together.

| Order? | Repeats? | Count |
|---|---|---|
| Yes | No | P(n, k) |
| Yes | Yes | nᵏ |
| No | No | C(n, k) |
| No | Yes | C(n+k−1, k) |

The no-repeat formulas assume you pick no more than n items; otherwise the count is zero. The last row, **multisets** (collections where an item may appear more than once), is counted with **stars and bars**. Distributing k identical items into n distinct bins is the same as arranging k stars and n − 1 bars in a line, where the bars separate the bins:

```
10 identical jobs, 4 workers:
**|****||****   -> 2, 4, 0, 4
```

Every such line is fixed by choosing which positions hold bars:

```formula
M(n, k) = C(n + k − 1, n − 1)
        = C(n + k − 1, k)
M(4, 10) = C(13, 3) = 286
where
M(n, k): the number of ways to put k identical items into n distinct bins (bins may stay empty), which is also the number of multisets of size k from n kinds
n: the number of bins (kinds), at least 1
k: the number of identical items, 0 or more
C(a, b): "a choose b", the number of ways to choose b positions out of a
In words: lay out k stars and n − 1 bars, 13 symbols for 10 jobs and 4 workers, and choose which 3 positions are bars: 286 ways. The two forms are equal by symmetry.
```

If every worker must get at least one job, hand one to each first, then distribute the remaining 6 freely: 6 stars and 3 bars, so C(9, 3) = 84 ways.

### Arrangements with repeated letters

The number of distinct arrangements of a word with repeated letters is the **multinomial coefficient**: arrange all the letters as if they were distinct, then divide by the orderings of each group of identical letters, which don't change the word.

```formula
N_arr = n! / (n_1! × n_2! × … × n_m!)
N_arr = 6! / (3! × 2! × 1!)
N_arr = 720 / 12 = 60
where
N_arr: the number of distinct arrangements of the letters
n: the total number of letters (here 6, for BANANA)
n_1, n_2, …, n_m: how many times each of the m different letters appears (here A 3 times, N twice, B once); they add up to n
m: the number of different letters (here 3)
!: factorial: the product of every whole number from that number down to 1
…: and so on, one factor per different letter
In words: BANANA's 720 labelled orderings collapse in groups of 3! × 2! = 12, leaving 60 different words.
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

**If there are more pigeons than holes, some hole has at least two pigeons.** More generally, if you spread items over boxes, some box must hold at least the average, rounded up:

```formula
L_max ≥ ⌈N / k⌉
⌈1,000,000 / 4,096⌉ = ⌈244.14⌉ = 245
where
L_max: the number of items in the fullest box
N: the number of items
k: the number of boxes, at least 1
⌈ ⌉: ceiling: round up to the nearest whole number, so ⌈244.14⌉ = 245 and ⌈3⌉ = 3
≥: is at least
In words: the boxes can't all be below average, and a box holds a whole number of items, so the fullest box holds at least the average rounded up.
```

The bound is the best possible: spreading the items as evenly as you can gives a fullest box of exactly ⌈N/k⌉. It sounds trivial, but it proves things that are otherwise surprising:

- Among 13 people, two share a birth month.
- Hash 1,000,000 keys into 4,096 buckets and some bucket receives at least 245 keys (the example in the formula), however good the hash function.
- In a group of at least two people with mutual friendships and no self-friendships, two have the same number of friends within the group. In a group of 10, the possible friend counts are 0 to 9, but 0 and 9 can't both occur (someone with 9 friends is friends with everyone), so 10 people share at most 9 different counts.

### No compressor shrinks every file

A lossless compressor must be injective (different inputs give different outputs), or decompression would be ambiguous. Count the files of exactly n bits against all the strictly shorter ones:

```formula
2^0 + 2^1 + … + 2^{n−1} = 2^n − 1
where
n: the length of the input files, in bits
2^n: the number of different files of exactly n bits (each bit is 0 or 1)
2^0, 2^1, …: the numbers of files of length 0, 1, … bits; the sum runs up to length n − 1
…: and so on, one term for each length
In words: there is exactly one fewer bit string shorter than n bits than there are strings of exactly n bits. For n = 3: 1 + 2 + 4 = 7 shorter strings, against 8 strings of 3 bits.
```

So no injective compressor can map all 2ⁿ inputs to shorter outputs. A compressor defined on all finite bit strings that shrinks some inputs must expand others (an identity encoding need not expand anything); format framing and block overhead are concrete reasons gzip or zstd output may grow. The counting argument proves that some growth is unavoidable for such a total shrinking compressor; it does not require a particular header design.

### The birthday problem

Pigeonhole is also the root of the **birthday problem**, which asks the harder question of when a collision becomes *likely* rather than *certain*. In the model of independent, uniformly distributed birthdays over 365 possible days, certainty needs 366 people, but 23 already give a better than 50% chance. For hashes, the same model gives:

```formula
N_coll ≈ 2^{b/2}
N_coll ≈ 2^32 ≈ 4.3 × 10^9   for b = 64
where
N_coll: the number of hashed items at which a collision (two items with the same hash) becomes reasonably likely
b: the number of bits in each hash output, so there are 2^b possible outputs
≈: roughly; collisions can also happen earlier
In words: with independent, uniformly distributed b-bit hash outputs, collisions become substantially likely around the square root of the number of possible outputs, not near the total. A 64-bit hash runs into them after a few billion items.
```

That probability calculation is covered in the probability module.

## Common traps

- **Order or not?** "Choose a committee" is a combination; "choose a president, secretary and treasurer" is a permutation. A committee of 3 with a chair can be counted two ways (first block below), and both must agree.
- **Overcounting symmetric arrangements.** Seating people round a table where rotations count as the same: each seating appears once per seat it could be rotated to (second block below).
- **"At least one".** Count the complement: all possibilities minus those with none (third block below). Trying to count "exactly one digit, plus exactly two, plus …" directly is slower and error-prone, and "pick a position for the digit, then fill the rest" overcounts.
- **Disjointness in the sum rule.** If the cases overlap you need inclusion–exclusion, which is the next lesson.

```formula
3 × C(10, 3) = 3 × 120 = 360
10 × C(9, 2) = 10 × 36 = 360
where
C(10, 3): "10 choose 3": the number of 3-person committees from 10 people, 120
C(9, 2): "9 choose 2": the number of ways to pick the 2 ordinary members from the 9 people left once the chair is chosen, 36
In words: choose the committee then which of its 3 is chair, or choose the chair first then 2 more: both give 360.
```

```formula
R(n) = n! / n = (n − 1)!
R(6) = 5! = 120
where
R(n): the number of ways to seat n distinct people round a table when rotations of a seating count as the same
n: the number of people (and seats)
!: factorial: the product of every whole number from that number down to 1
In words: the n! straight-line orderings fall into groups of n rotations, so divide by n. For n ≥ 3, if mirror images also count as the same, halve it again (60 for 6 people).
```

```formula
N_1 = 36^6 − 26^6
N_1 = 2,176,782,336 − 308,915,776
N_1 = 1,867,866,560
where
N_1: the number of 6-character passwords over a–z and 0–9 (36 symbols) with at least one digit
36^6: all 6-character strings over the 36 symbols
26^6: the strings with no digit at all, letters only
In words: everything minus the all-letter passwords leaves exactly those with at least one digit.
```

## Key takeaways
- Product rule for sequences of choices, sum rule for disjoint cases; nearly everything builds on these two.
- Permutations count ordered selections; combinations count unordered ones, which is the ordered count divided by the number of orderings of each selection.
- Stars and bars counts identical items into distinct bins; multinomial coefficients handle words with repeated letters.
- Pigeonhole: items spread over boxes force some box to hold at least the average rounded up, which is why hash collisions and incompressible files must exist.
- Count the complement for "at least one", and always check a small case by brute force.

## Further reading
- [Combination — Wikipedia](https://en.wikipedia.org/wiki/Combination)
- [Permutation — Wikipedia](https://en.wikipedia.org/wiki/Permutation)
- [Stars and bars — Wikipedia](https://en.wikipedia.org/wiki/Stars_and_bars_(combinatorics))
- [Pigeonhole principle — Wikipedia](https://en.wikipedia.org/wiki/Pigeonhole_principle)
- [itertools — Python docs](https://docs.python.org/3/library/itertools.html)
- [Mathematics for Computer Science, Part III: Counting (MIT)](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
