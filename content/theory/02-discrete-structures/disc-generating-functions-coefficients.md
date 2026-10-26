---
id: disc-generating-functions-coefficients
title: "Generating functions and Catalan coefficients"
level: intermediate
minutes: 3
summary: "A generating function stores a sequence in coefficients; multiplying convolves the sequences."
sourceLesson: disc-inclusion-recurrences
---

## Generating functions

A **generating function** stores a sequence a₀, a₁, a₂, … as the coefficients of a power series:

```formula essential
A(x) = a_0 + a_1 × x + a_2 × x^2 + …
where
A(x): the generating function of the sequence
a_0, a_1, a_2: the terms of the sequence being stored (counts, for example)
x: a placeholder variable; x^n marks position n
…: and so on, one term for every position
In words: A generating function stores sequence terms as coefficients. The power marks the size; the coefficient gives its count.
```

Here the variable is a formal placeholder, not an input to evaluate. **Multiplying generating functions convolves their coefficient sequences**: to count objects of a target size, consider every split of that size across the two factors, multiply the counts for each split, then add.

The building block is the geometric series:

```formula reference
1 / (1 − x) = 1 + x + x^2 + x^3 + …
where
x: the placeholder variable (as a real number the series only adds up when x is between −1 and 1, but formal counting never evaluates it)
x^2, x^3: x multiplied by itself 2 and 3 times
…: and so on forever
In words: Every coefficient of this series is one: it represents one way to choose each non-negative number of identical items. It is used formally without evaluating the placeholder.
```

Generating functions can derive dynamic-programming recurrences or closed forms.

Fibonacci’s recurrence can be translated into an equation between formal series, then solved algebraically. The source gives the derivation; coefficient meaning is the key idea here.

> [!note] Catalan numbers
> The Catalan numbers 1, 1, 2, 5, 14, 42, … count balanced bracket strings by number of pairs. They also count ordered rooted binary-tree shapes by nodes, distinguishing left and right children. Their recursive structure explains the counting rule below.

A nonempty balanced bracket string splits uniquely into its first opening bracket, the balanced string inside its matching closing bracket, and the balanced string after it. Count all possible splits of the remaining pairs, multiplying the inside and after counts for each split and then adding. The empty string contributes one way.

> [!analogy] Real-world analogy: Boxes labelled by size
> Imagine one box for each possible size, with a card in it recording how many objects have that size.
>
> **How it maps:** A power marks the box’s size and its coefficient is the count. Combining two collections considers every pair of sizes adding to the target.
>
> **Where it stops:** The formal variable is bookkeeping, not a physical quantity to evaluate or a box you must build.

## Key takeaways

- A generating function stores a sequence in coefficients; multiplying convolves the sequences.
- Formal series support counting without evaluating the placeholder, and Catalan numbers count recursive bracket structures.

## Further reading

- [Generating function — Wikipedia](https://en.wikipedia.org/wiki/Generating_function)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [Catalan number — Wikipedia](https://en.wikipedia.org/wiki/Catalan_number)
