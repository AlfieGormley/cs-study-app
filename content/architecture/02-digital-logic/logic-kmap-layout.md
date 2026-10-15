---
id: logic-kmap-layout
title: K-map layout and valid groups
level: intermediate
minutes: 5
sourceLesson: logic-karnaugh-maps
summary: Gray ordering makes one-bit changes adjacent, including wrap-around.
---

In Boolean-algebra lessons we simplified the majority function by spotting this:

```formula
A′·B·C + A·B·C = B·C·(A′ + A) = B·C
where
A, B, C: Boolean inputs, each 0 or 1
A′: NOT A: 1 when A is 0, and 0 when A is 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: two terms that are identical except that one has A and the other has NOT A collapse into one term without A, because A′ + A is always 1.
```

That move, combining two terms that differ in exactly one variable, is the combination step in two-level minimisation; selecting a minimum cover is a separate problem. The hard part is seeing which terms to pair.

A **Karnaugh map** (K-map), introduced by Maurice Karnaugh at Bell Labs in 1953, rearranges the truth table into a grid where terms that differ in one variable sit **next to each other**. Simplification becomes drawing rectangles around 1s.

## The key idea: adjacency

The algebra behind every K-map group is one identity:

```formula
X·Y + X·Y′ = X·(Y + Y′) = X·1 = X
where
X: any product term shared by both terms, for example A·B′
Y: the one variable that differs between the two terms
Y′: NOT Y
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: if two terms are the same except for one variable, which is plain in one and complemented in the other, they merge into the shared part and that variable disappears.
```

Two minterms that differ in one variable merge into one term with that variable removed. Four minterms that form two such pairs merge again, removing a second variable, and so on. Each doubling of the group removes one more variable:

```formula
N_cells = 2^k
N_literals = n − k
N_literals = 4 − 2 = 2   for n = 4, k = 2
where
N_cells: the number of cells in a valid group (1, 2, 4, 8 or 16)
k: how many variables the group eliminates
2^k: k copies of 2 multiplied together
n: the number of input variables in the map
N_literals: the number of literals (variables, plain or complemented) left in the group's product term
In words: in a 4-variable map, a group of 4 cells (k = 2) leaves a 2-literal term, a pair leaves 3 literals and a group of 8 leaves just 1.
```

To make mergeable minterms adjacent, the rows and columns are labelled in **Gray code** order, where neighbours differ in exactly one bit:

```
binary order:  00  01  10  11
Gray order:    00  01  11  10
```

In binary order, 01 and 10 are neighbours but differ in two bits. In Gray order every step flips one bit, **including the wrap from 10 back to 00**.

## Laying out the map

### Three variables

Put A on the rows and BC on the columns. Each cell holds one row of the truth table; here are the minterm numbers:

```
          BC
  A      00  01  11  10
       +---+---+---+---+
   0   | 0 | 1 | 3 | 2 |
       +---+---+---+---+
   1   | 4 | 5 | 7 | 6 |
       +---+---+---+---+
```

Note that columns 3 and 2 are swapped compared with the truth table order. That is the Gray code at work.

### Four variables

AB on the rows, CD on the columns, both in Gray order:

```
          CD
  AB     00  01  11  10
       +---+---+---+---+
  00   | 0 | 1 | 3 | 2 |
  01   | 4 | 5 | 7 | 6 |
  11   |12 |13 |15 |14 |
  10   | 8 | 9 |11 |10 |
       +---+---+---+---+
```

The map has **wrap-round** adjacency in both directions, like the surface of a doughnut. The left column is adjacent to the right column, and the top row to the bottom row. So cells 0, 2, 8 and 10 (the four corners) form a valid group.

## The grouping rules

1. Group only 1s (for sum of products).
2. For maps up to four variables, each group is a rectangle with power-of-two side lengths. Its total size is 1, 2, 4, 8 or 16 cells; a full 16-cell group gives constant 1.
3. Groups may wrap round edges and may **overlap**.
4. Make each group **as large as possible**. Bigger groups mean fewer literals.
5. Use **as few groups as possible** to cover every 1.

To read a group, find the variables that **stay constant** across all its cells. A variable that is 1 throughout appears plain, one that is 0 throughout appears complemented, and one that changes is dropped.

## Key takeaways
- Gray ordering makes one-bit changes adjacent, including wrap-around.
- Power-of-two rectangles eliminate the variables that vary.

## Further reading
- [Karnaugh — original map-method paper](https://bh.hallikainen.org/uploads/karnaugh.pdf)
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Karnaugh map — Wikipedia](https://en.wikipedia.org/wiki/Karnaugh_map)
- [Quine–McCluskey algorithm — Wikipedia](https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm)
- [Espresso heuristic logic minimizer — Wikipedia](https://en.wikipedia.org/wiki/Espresso_heuristic_logic_minimizer)
- [Hazard (logic) — Wikipedia](https://en.wikipedia.org/wiki/Hazard_(logic))
- [Don't-care term — Wikipedia](https://en.wikipedia.org/wiki/Don%27t-care_term)
- [Gray code — Wikipedia](https://en.wikipedia.org/wiki/Gray_code)
