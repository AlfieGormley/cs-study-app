---
id: logic-algebra-demorgan
title: Absorption, duality and De Morgan
level: basic
minutes: 3
sourceLesson: logic-boolean-algebra
summary: OR distributes over AND in Boolean algebra.
---

Two of these surprise people who know ordinary algebra.

**OR distributes over AND.** In arithmetic, 1 + 2 × 3 is 7 but (1 + 2) × (1 + 3) is 12, so the rule fails. In Boolean algebra it holds. Expand the right-hand side, then use idempotence and absorption:

```formula
(A + B)·(A + C)
  = A·A + A·C + A·B + B·C
  = A + A·C + A·B + B·C
  = A + B·C
where
A, B, C: Boolean variables, each 0 or 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: multiply out the brackets as usual; A·A is just A (idempotence), and A swallows A·C and A·B (absorption), leaving A + B·C.
```

**Absorption**: A + A·B is just A. If A is 1 the whole thing is 1; if A is 0 then A·B is 0 too. The A·B term adds nothing.

A close cousin of absorption is worth memorising. Check it by trying both values of A:

```formula
A + A′·B = A + B
1 + 0·B = 1 = 1 + B     for A = 1
0 + 1·B = B = 0 + B     for A = 0
where
A, B: Boolean variables, each 0 or 1
A′: NOT A: 1 when A is 0, and 0 when A is 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: if A is 1 both sides are 1; if A is 0 both sides reduce to B. So "A, or (not A and B)" is the same as "A or B".
```

### Duality

Notice that each law comes in a mirrored pair. Swap AND with OR and 0 with 1 in any law and you get another valid law. This is the **duality principle**, and it halves the number of rules you need to remember.

## De Morgan's theorem

De Morgan's laws are the most-used tool in logic design. They tell you how to push a NOT inside a bracket:

```formula
(A·B)′ = A′ + B′
(A + B)′ = A′·B′
(A·B·C)′ = A′ + B′ + C′
where
A, B, C: Boolean variables, each 0 or 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
A′, B′, C′: NOT A, NOT B, NOT C
( )′: NOT applied to the whole bracket
In words: "not (A and B)" is the same as "not A, or not B", and "not (A or B)" is "not A and not B". To push a NOT through a group, complement each variable and swap AND with OR. The third line shows it works for any number of terms.
```

Proof by truth table:

```
 A B | (AB)'  A'+B' | (A+B)'  A'B'
-----+--------------+--------------
 0 0 |   1      1   |   1      1
 0 1 |   1      1   |   0      0
 1 0 |   1      1   |   0      0
 1 1 |   0      0   |   0      0
```

Programmers use this daily. `if not (logged_in and is_admin)` is the same test as `if not logged_in or not is_admin`. In hardware it matters even more, because simple inverting multi-input gates in conventional complementary CMOS include NAND and NOR (in the CMOS units), and De Morgan is how you convert between AND/OR designs and NAND/NOR ones.

## Key takeaways
- OR distributes over AND in Boolean algebra.
- De Morgan complements each input and swaps AND with OR.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Boolean algebra — Wikipedia](https://en.wikipedia.org/wiki/Boolean_algebra)
- [De Morgan's laws — Wikipedia](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [Canonical normal form (minterms and maxterms) — Wikipedia](https://en.wikipedia.org/wiki/Canonical_normal_form)
- [A Symbolic Analysis of Relay and Switching Circuits — Wikipedia](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits)
- [Nand2Tetris: build a computer from first principles](https://www.nand2tetris.org/)
