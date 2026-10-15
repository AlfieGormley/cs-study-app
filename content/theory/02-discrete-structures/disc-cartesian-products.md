---
id: disc-cartesian-products
title: "Cartesian products and relational rows"
level: basic
minutes: 3
summary: "A Cartesian product contains every ordered combination of input elements."
sourceLesson: disc-sets-functions
---

The **Cartesian product** A × B is the set of all ordered pairs whose first part comes from A and whose second part comes from B. Every element of A is paired with every element of B, so the sizes multiply:

```formula
A × B = { (a, b) : a ∈ A and b ∈ B }
|A × B| = |A| × |B|
{1, 2} × {x, y}
  = {(1,x), (1,y), (2,x), (2,y)}
|{1, 2} × {x, y}| = 2 × 2 = 4
where
A, B: sets; the cardinality multiplication shown here counts finite sets
a: an element of A
b: an element of B
x, y: the two elements of the example's second set
×: between sets, the Cartesian product; between numbers, ordinary multiplication
( , ): an ordered pair: order matters, so (1, x) and (x, 1) are different
∈: is an element of
| |: the cardinality: the number of elements
{ : }: the set of all things of the form before the colon that satisfy the condition after it
In words: the Cartesian product pairs every element of A with every element of B, so a 2-element set times a 2-element set gives 4 pairs.
```

A relational table is the same idea with more columns. Each column draws its values from a set of allowed values (its domain), and the table holds a set of rows chosen from all the combinations:

```formula
T ⊆ D_1 × D_2 × … × D_k
where
T: the set of rows in the table, each row a k-tuple (a list of k values in column order)
D_1, D_2, D_k: the domains: the sets of allowed values for column 1, column 2 and column k
k: the number of columns
×: Cartesian product
…: and so on, one factor per column
⊆: is a subset of
In words: a relation (in the database sense) is a set of rows chosen from all possible combinations of column values.
```

If either input set is empty, there are no ordered pairs, so the Cartesian product is empty.

Real SQL tables go a little beyond this model: they can hold duplicate rows. An SQL CROSS JOIN combines every input-row occurrence with every occurrence on the other side, retaining duplicate multiplicities.

## Key takeaways

- A Cartesian product contains every ordered combination of input elements.
- A mathematical relation selects rows from a Cartesian product; SQL preserves row multiplicities.

## Further reading

- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
