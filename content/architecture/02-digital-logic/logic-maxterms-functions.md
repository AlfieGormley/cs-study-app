---
id: logic-maxterms-functions
title: Maxterms and counting functions
level: basic
minutes: 3
sourceLesson: logic-boolean-algebra
summary: A maxterm is zero on exactly one row.
---

### Product of sums (POS) and maxterms

A **maxterm** is an OR of every variable that is 0 for exactly one row: complement the variables that are 1 in that row. For example, take A low, B high and C low.

Its binary code is 010, so it is row two:

```formula essential
M_2 = A + B′ + C
where
M_2: maxterm number 2: the sum term that is 0 on row 2 (inputs 010) and 1 on every other row
A, B, C: the inputs, each 0 or 1; on row 2, A = 0, B = 1 and C = 0
B′: NOT B: here B is 1, so B′ is 0
+: OR: 1 when at least one side is 1
In words: Each part is low on the selected row, so the OR is low there. Changing any input makes at least one part high.
```

The **canonical POS** ANDs together the maxterms of every row where the output is 0. The majority function is 0 on rows 0, 1, 2 and 4:

```formula essential
Maj = ΠM(0, 1, 2, 4)
Maj = (A + B + C)·(A + B + C′)
      ·(A + B′ + C)·(A′ + B + C)
where
Maj: the majority function of A, B and C
ΠM(…): shorthand for "AND together the maxterms with these row numbers" (Π, the Greek capital pi, means "product of")
A, B, C: the inputs, each 0 or 1
A′, B′, C′: NOT A, NOT B, NOT C
+: OR: 1 when at least one side is 1
·: AND: 1 only when both sides are 1
In words: each bracket is 0 on exactly one of the rows where the majority is 0, so the AND of all four is 0 on those rows and 1 everywhere else.
```

SOP lists where the function is 1; POS lists where it is 0. The index sets are complements of each other: {3, 5, 6, 7} and {0, 1, 2, 4} together make every row from 0 to 7. Both describe the same function, and neither is usually minimal; they are a starting point.

### Counting functions

Each row of a truth table can independently output 0 or 1, so the number of different functions grows extremely fast with the number of inputs.

A lookup table stores one output bit for each input combination. Choosing those stored bits independently lets the same hardware implement any Boolean function of its inputs. Adding an input doubles the table size and creates many more possible functions.

## Key takeaways
- A maxterm is zero on exactly one row.
- Canonical POS lists zero rows; each output row is a free binary choice.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Boolean algebra — Wikipedia](https://en.wikipedia.org/wiki/Boolean_algebra)
- [De Morgan's laws — Wikipedia](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [Canonical normal form (minterms and maxterms) — Wikipedia](https://en.wikipedia.org/wiki/Canonical_normal_form)
- [A Symbolic Analysis of Relay and Switching Circuits — Wikipedia](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits)
- [Nand2Tetris: build a computer from first principles](https://www.nand2tetris.org/)
