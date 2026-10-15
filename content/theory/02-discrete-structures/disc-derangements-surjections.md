---
id: disc-derangements-surjections
title: "Derangements and onto assignments"
level: intermediate
minutes: 4
summary: "Derangements exclude every fixed point by inclusion–exclusion."
sourceLesson: disc-inclusion-recurrences
---

### Derangements

A **derangement** is a permutation where nothing stays in its original place: every guest leaves with someone else's coat, or every reviewer gets someone else's pull request.

Let Aᵢ be the permutations that fix item i (leave it in its original position). Fixing any particular k items leaves (n − k)! permutations of the rest, and there are C(n, k) ways to choose which k. Inclusion–exclusion over "at least one fixed point" gives:

```formula
D(n) = n! − C(n, 1) × (n − 1)!
     + C(n, 2) × (n − 2)! − …
D(n) = n! × (1 − 1/1! + 1/2! − … ± 1/n!)
D(4) = 24 × (1 − 1 + 1/2 − 1/6 + 1/24)
D(4) = 24 − 24 + 12 − 4 + 1 = 9
where
D(n): the number of derangements of n items: orderings with no item in its original position
n: the number of items, 0 or more
k: the number of items forced to stay in their original positions in one term, from 0 to n
C(n, k): "n choose k", the number of ways to pick which k items stay put
!: factorial: the product of every whole number from that number down to 1, with 0! = 1
…: and so on, one term for each k up to n
±: the sign of the last term: + when n is even, − when n is odd
In words: start from all n! orderings, subtract those fixing some item, add back those fixing two, and so on. Since C(n, k) × (n − k)! = n! / k!, each term is n! divided by k!, which gives the bracketed form.
```

The bracket is the start of the series for e⁻¹ (1 divided by Euler's number e ≈ 2.718), which gives a shortcut:

```formula
D(n) = ⌊n! / e + 1/2⌋   for n ≥ 1
D(4) = ⌊24 / 2.718 + 0.5⌋ = ⌊9.33⌋ = 9
D(n) / n! → 1 / e ≈ 0.368
where
D(n): the number of derangements of n items
n!: n factorial, the number of all orderings of n items
e: Euler's number, about 2.71828, the base of natural logarithms
⌊ ⌋: floor: round down to a whole number. Adding 1/2 first turns this into rounding to the nearest whole number
→: tends to, as n grows larger and larger
≈: approximately equal to
In words: the number of derangements is n! / e rounded to the nearest whole number, and the chance that a random ordering moves every item approaches about 36.8%.
```

The values run 0, 1, 2, 9, 44, 265, … for 1 to 6 items. The limit is approached quickly, but small cases differ substantially: for 1 item the probability is 0, and for 2 items it is 1/2.

### Counting onto functions

How many ways can you assign 5 distinct jobs to 3 servers so every server gets at least one? There are 3⁵ assignments in all. Subtract those missing a given server, add back those missing two:

```formula
S = 3^5 − C(3, 1) × 2^5 + C(3, 2) × 1^5
S = 243 − 3 × 32 + 3 × 1
S = 243 − 96 + 3 = 150
where
S: the number of assignments of 5 distinct jobs to 3 servers that leave no server idle (onto, or surjective, functions)
3^5: all assignments: each of the 5 jobs independently picks one of 3 servers
C(3, 1) × 2^5: choose 1 server to leave idle (3 ways), then send all 5 jobs to the other 2
C(3, 2) × 1^5: choose 2 servers to leave idle (3 ways), then all jobs go to the last one
C(a, b): "a choose b", the number of ways to choose b items from a
In words: 150 of the 243 assignments use every server. Assignments missing two servers were subtracted twice, so they are added back once.
```

The same pattern counts onto functions from an m-element set to an n-element set: add or subtract, for each number j of excluded targets, C(n, j) × (n − j)ᵐ, with the sign + for even j and − for odd j.

Inclusion–exclusion is the go-to method whenever the condition is "every X is covered" or "no X is bad": count the complement events, which are often easier, and alternate.

## Key takeaways

- Derangements exclude every fixed point by inclusion–exclusion.
- Onto assignments exclude missed targets and restore overlaps with alternating signs.

## Further reading

- [Derangement — Wikipedia](https://en.wikipedia.org/wiki/Derangement)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
