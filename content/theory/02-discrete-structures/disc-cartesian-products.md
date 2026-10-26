---
id: disc-cartesian-products
title: "Cartesian products and relational rows"
level: basic
minutes: 2
summary: "A Cartesian product contains every ordered combination of input elements."
sourceLesson: disc-sets-functions
---

The **Cartesian product** A × B is the set of all ordered pairs whose first part comes from A and whose second part comes from B. Every element of A is paired with every element of B, so the sizes multiply:

```formula essential
A × B = { (a, b) : a ∈ A and b ∈ B }
where
A, B: the two sets whose ordered pairs are being formed
a: an element of A
b: an element of B
×: between sets, the Cartesian product; between numbers, ordinary multiplication
( , ): an ordered pair: order matters, so (1, 2) and (2, 1) are different
∈: is an element of
{ : }: the set of all things of the form before the colon that satisfy the condition after it
In words: The Cartesian product contains every ordered pair made by choosing one element from the first set and one from the second.
```

Each column of a mathematical table draws values from its own domain, and a row records one combination in column order.

A mathematical table chooses rows from all allowed combinations of its column domains. It need not contain every combination.

If either input set is empty, there are no ordered pairs, so the Cartesian product is empty.

Real SQL tables go a little beyond this model: they can hold duplicate rows. An SQL CROSS JOIN combines every input-row occurrence with every occurrence on the other side, retaining duplicate multiplicities.

## Key takeaways

- A Cartesian product contains every ordered combination of input elements.
- A mathematical relation selects rows from a Cartesian product; SQL preserves row multiplicities.

## Further reading

- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
