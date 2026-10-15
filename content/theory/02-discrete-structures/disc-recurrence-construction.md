---
id: disc-recurrence-construction
title: "Constructing recurrences and checking base cases"
level: intermediate
minutes: 3
summary: "Use a first decision to split a problem into smaller disjoint instances."
sourceLesson: disc-inclusion-recurrences
---

## Recurrences

A **recurrence** defines each term of a sequence from earlier terms, plus base cases. Setting one up is often easier than finding a formula directly, because it mirrors how you'd *build* the objects.

### Setting up a recurrence

> [!example] Binary strings with no two adjacent 1s
> Count the binary strings of a given length that never contain "11". Look at the first character. If it's 0, the rest is any valid string one character shorter. If it's 1, the next must be 0, and then any valid string two characters shorter follows. The two cases don't overlap, so the count is the sum of the two shorter counts.

```formula
a(n) = a(n − 1) + a(n − 2)
a(1) = 2,  a(2) = 3
a(3) = 3 + 2 = 5,  a(4) = 5 + 3 = 8
where
a(n): the number of binary strings of length n with no two adjacent 1s
n: the string length, a whole number; the recurrence applies for n ≥ 3
a(n − 1), a(n − 2): the counts for strings one and two characters shorter
In words: valid strings starting with 0, plus valid strings starting with 10. The values 2, 3, 5, 8, 13, … are the Fibonacci numbers.
```

The skill is finding the right **first decision** that splits the objects into disjoint cases, each a smaller instance of the same problem. It is exactly the step you take when designing a dynamic-programming solution.

The **Tower of Hanoi** uses three pegs: move one disc at a time, never placing a larger disc on a smaller one. To move n discs, move n − 1 out of the way, move the biggest, then move the n − 1 back on top.

```formula
T(n) = 2 × T(n − 1) + 1,   T(0) = 0
T(1), T(2), … = 1, 3, 7, 15, 31, …
T(n) = 2^n − 1
2 × (2^{n−1} − 1) + 1 = 2^n − 1
where
T(n): the minimum number of single-disc moves to move a tower of n discs
n: the number of discs, a non-negative integer; the recurrence applies from 1 upwards
T(n − 1): the moves for the smaller tower, needed twice (off, then back on)
2^n: n copies of 2 multiplied together
…: and so on
In words: the first line is the recurrence, the second its first few values, the third a guessed closed form, and the fourth checks the guess: putting 2^{n−1} − 1 into the right-hand side gives back 2^n − 1.
```

Guessing a formula from small values and proving it by induction is a perfectly good method. For 10 discs it gives 2¹⁰ − 1 = 1,023 moves.

## Avoid overlapping cases

The first decision must split objects into disjoint cases. Otherwise a recurrence overcounts just as an overlapping sum does. Base cases matter: the same “sum of the previous two” rule can give Fibonacci numbers, Lucas numbers or another sequence. For binary strings, check lengths one, two and three by enumeration before proving a claimed formula.

## Key takeaways

- Use a first decision to split a problem into smaller disjoint instances.
- A recurrence needs its base cases; small checks suggest formulas, while induction proves them.

## Further reading

- [Recurrence relation — Wikipedia](https://en.wikipedia.org/wiki/Recurrence_relation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
