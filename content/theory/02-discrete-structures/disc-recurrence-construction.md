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
> For length at least two, inspect the first bit. A leading 0 leaves any valid suffix one character shorter. A leading 1 forces the next bit to be 0, leaving any valid suffix two characters shorter. These cases are disjoint. The one-bit strings are 0 and 1; the two-bit strings are 00, 01 and 10.

```formula essential
a(n) = a(n − 1) + a(n − 2)
a(1) = 2,  a(2) = 3
where
a(n): the number of binary strings of length n with no two adjacent 1s
n: the string length, a whole number; the recurrence applies for n ≥ 3
a(n − 1), a(n − 2): the counts for strings one and two characters shorter
In words: Valid strings start with zero or, when at least two positions remain, with one followed by zero. These disjoint cases leave valid suffixes one or two characters shorter. Base counts start the sequence.
```

The skill is finding the right **first decision** that splits the objects into disjoint cases, each a smaller instance of the same problem. It is exactly the step you take when designing a dynamic-programming solution.

The **Tower of Hanoi** uses three pegs: move one disc at a time, never placing a larger disc on a smaller one. To move n discs, move n − 1 out of the way, move the biggest, then move the n − 1 back on top.

```formula essential
T(n) = 2 × T(n − 1) + 1
T(0) = 0
where
T(n): the minimum number of single-disc moves to move a tower of n discs
n: the number of discs, a non-negative integer; the recurrence applies from 1 upwards
T(n − 1): the moves for the smaller tower, needed twice (off, then back on)
In words: Moving a larger Hanoi tower requires moving the smaller tower twice, with one move of the largest disc between them. An empty tower needs no moves.
```

A pattern in a few counts suggests a formula, but does not prove it. A proof must establish the base cases and show that the claimed pattern is preserved by the recurrence.

## Avoid overlapping cases

The first decision must split objects into disjoint cases. Otherwise a recurrence overcounts just as an overlapping sum does. Base cases matter: the same “sum of the previous two” rule can give Fibonacci numbers, Lucas numbers or another sequence. For binary strings, check lengths one, two and three by enumeration before proving a claimed formula.

## Key takeaways

- Use a first decision to split a problem into smaller disjoint instances.
- A recurrence needs its base cases; small checks suggest formulas, while induction proves them.

## Further reading

- [Recurrence relation — Wikipedia](https://en.wikipedia.org/wiki/Recurrence_relation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
