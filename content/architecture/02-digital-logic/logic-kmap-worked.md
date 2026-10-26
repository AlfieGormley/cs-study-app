---
id: logic-kmap-worked
title: Read three- and four-variable K-maps
level: intermediate
minutes: 4
sourceLesson: logic-karnaugh-maps
summary: Wrap-around groups can replace several smaller groups.
---

## Worked example: three variables

The three-input function is high on rows 0, 2, 4, 5 and 6, and low elsewhere. Read row numbers from the binary input order A, B, C.

Fill in the map:

```
          BC
  A      00  01  11  10
       +---+---+---+---+
   0   | 1 | 0 | 0 | 1 |
       +---+---+---+---+
   1   | 1 | 1 | 0 | 1 |
       +---+---+---+---+
```

- **Group 1**: the four cells in columns 00 and 10 (m0, m2, m4, m6). They wrap round the edge. A changes, B changes, C is 0 throughout. Term: NOT C.
- **Group 2**: the pair m4, m5 in row 1, columns 00 and 01. A = 1, B = 0, C changes. Term: A AND NOT B.

```formula essential
F = C′ + A·B′
where
F: the minimised function
A, B, C: the inputs, each 0 or 1
C′, B′: NOT C, NOT B
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: F is 1 whenever C is 0 (group 1), or when A is 1 and B is 0 (group 2). Check row 5 (101): C′ = 0 but A·B′ = 1, so F = 1, as required.
```

The canonical sum of products needed five 3-literal minterms. A direct AND/OR implementation needs complements B' and C', a two-input AND and a two-input OR; shared complements or a different gate mapping can change that count.

> [!warning] Don't stop at the obvious pairs
> A beginner might group m0 with m2 and m4 with m6 separately. One smaller pair requires A low and C low; the other requires A high and C low.

Both terms share NOT C and together cover every value of A, so the single term NOT C covers the same cells. Always look for the wrap-round.

## Worked example: four variables

The four-input function is high on rows 0, 1, 2, 5, 8, 9 and 10, and low elsewhere. Read row numbers from the binary input order A, B, C, D.

```
          CD
  AB     00  01  11  10
       +---+---+---+---+
  00   | 1 | 1 | 0 | 1 |
  01   | 0 | 1 | 0 | 0 |
  11   | 0 | 0 | 0 | 0 |
  10   | 1 | 1 | 0 | 1 |
       +---+---+---+---+
```

- Rows 00 and 10 are adjacent (wrap-round). Columns 00 and 01 in those rows give m0, m1, m8, m9: B = 0, C = 0. Term:  (NOT B AND NOT C) .
- The four corners m0, m2, m8, m10: B = 0, D = 0. Term:  (NOT B AND NOT D) .
- That leaves m5 (row 01, column 01). Its best partner is m1 directly above it: A = 0, C = 0, D = 1. Term:  (NOT A AND NOT C AND D) .

```formula essential
F = B′·C′ + B′·D′ + A′·C′·D
where
F: the minimised function
A, B, C, D: the inputs, each 0 or 1
A′, B′, C′, D′: NOT A, NOT B, NOT C, NOT D
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: three groups (a wrap-round block of four, the four corners and one pair) cover all seven 1s, giving three short terms instead of seven 4-literal minterms.
```

## Key takeaways
- Wrap-around groups can replace several smaller groups.
- Read constant variables from each group to construct its term.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Karnaugh map — Wikipedia](https://en.wikipedia.org/wiki/Karnaugh_map)
- [Quine–McCluskey algorithm — Wikipedia](https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm)
- [Espresso heuristic logic minimizer — Wikipedia](https://en.wikipedia.org/wiki/Espresso_heuristic_logic_minimizer)
- [Hazard (logic) — Wikipedia](https://en.wikipedia.org/wiki/Hazard_(logic))
- [Don't-care term — Wikipedia](https://en.wikipedia.org/wiki/Don%27t-care_term)
- [Gray code — Wikipedia](https://en.wikipedia.org/wiki/Gray_code)
