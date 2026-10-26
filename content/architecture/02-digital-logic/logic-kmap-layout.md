---
id: logic-kmap-layout
title: K-map layout and valid groups
level: intermediate
minutes: 4
sourceLesson: logic-karnaugh-maps
summary: Gray ordering makes one-bit changes adjacent, including wrap-around.
---

A **Karnaugh map** (K-map) rearranges a truth table so that input rows differing in one bit sit next to each other. If the output is high for both values of that bit, the bit is irrelevant within that group and can disappear from its product term.

## The key idea: adjacency

Combine a pair that differs in one input and that input drops out. Double a valid group again and another changing input drops out. In a four-input map, a pair leaves three fixed inputs, a four-cell group leaves two, and an eight-cell group leaves one. Grouping does not discard cases: the larger group covers exactly the combined cases.

The point is to find shared behaviour, then choose a small set of groups covering every required high output.

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

The map has **wrap-round** adjacency in both directions. The left column is adjacent to the right column, and the top row to the bottom row. So cells 0, 2, 8 and 10 (the four corners) form a valid group.

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
