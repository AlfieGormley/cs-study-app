---
id: logic-canonical-minterms
title: Minterms and canonical sums
level: basic
minutes: 3
sourceLesson: logic-boolean-algebra
summary: A minterm selects exactly one input row.
---

## Canonical forms

Any Boolean function can be written straight from its truth table in two standard ways.

### Sum of products (SOP) and minterms

A **minterm** is an AND of every variable, each either plain or complemented, that is 1 for exactly one row. Number the rows by reading the inputs as a binary number (A as the most significant bit), with this example row:

```formula
A=1, B=0, C=1
where
A: Boolean input bit
B: Boolean input bit
C: Boolean input bit
In words: The ordered input bits are one, zero, one: binary row five.
```

Reading the three bits as binary 101 gives row five:

```formula
m_5 = A·B′·C
m_5 = 1·1·1 = 1   for A = 1, B = 0, C = 1
where
m_5: minterm number 5: the product term that is 1 on row 5 (inputs 101) and 0 on every other row
A, B, C: the inputs, each 0 or 1
B′: NOT B: here B is 0, so B′ is 1
·: AND: 1 only when both sides are 1
In words: use each variable plain where the row has a 1 and complemented where it has a 0, so the term is 1 on that one row only.
```

The **canonical SOP** ORs together the minterms of every row where the output is 1. The majority function above is 1 on rows 011, 101, 110 and 111, which are rows 3, 5, 6 and 7:

```formula
Maj = Σm(3, 5, 6, 7)
Maj = m_3 + m_5 + m_6 + m_7
where
Maj: the majority function of A, B and C
Σm(…): shorthand for "OR together the minterms with these row numbers" (Σ, the Greek capital sigma, means "sum of")
m_3, m_5, m_6, m_7: the minterms of rows 3, 5, 6 and 7, for example m_3 = A′·B·C
+: OR: 1 when at least one side is 1
In words: the majority function is 1 exactly on rows 3, 5, 6 and 7, and this is the shorthand for the four-term SOP written out earlier.
```

## Key takeaways
- A minterm selects exactly one input row.
- Canonical SOP lists every row where the function is one.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Boolean algebra — Wikipedia](https://en.wikipedia.org/wiki/Boolean_algebra)
- [De Morgan's laws — Wikipedia](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [Canonical normal form (minterms and maxterms) — Wikipedia](https://en.wikipedia.org/wiki/Canonical_normal_form)
- [A Symbolic Analysis of Relay and Switching Circuits — Wikipedia](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits)
- [Nand2Tetris: build a computer from first principles](https://www.nand2tetris.org/)
