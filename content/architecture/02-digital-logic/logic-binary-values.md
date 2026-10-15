---
id: logic-binary-values
title: Binary values and Boolean operations
level: basic
minutes: 4
sourceLesson: logic-boolean-algebra
summary: Boolean signals abstract voltage ranges into two values.
---

Boolean algebra models binary signals with values 0 and 1. Physical digital circuits use voltage ranges, have transition intervals and may encounter unknown, metastable or high-impedance states; sequential circuits also depend on stored state. The mathematics of such functions is **Boolean algebra**, named after George Boole, who described an algebra of logic in 1847 and 1854.

Claude Shannon connected this algebra to relay circuits in his MIT master's work, published in a 1938 paper. That paper shows how switching circuits can be analysed using rules analogous to the calculus of propositions. That idea is the bridge from logic to hardware: write the behaviour you want as a Boolean expression, simplify it with algebra, and the simplified expression can suggest a smaller circuit; actual area, delay and power depend on the implementation.

This unit introduces the signal values and basic operations used throughout the following units.

## Values and the three fundamental operations

A Boolean variable takes one of two values: 0 or 1 (mapped here using positive logic to low and high voltage ranges). There are three fundamental operations.

**AND** is one only when both inputs are one. Its symbolic notation is:

```formula
A·B
where
A: Boolean input bit
B: Boolean input bit
· or adjacent brackets: Boolean AND
In words: Read this Boolean expression as (A AND B).
```

Adjacent letters also denote AND. **OR** is one when at least one input is one:

```formula
A + B
where
A: Boolean input bit
B: Boolean input bit
+: Boolean OR
In words: Read this Boolean expression as (A OR B).
```

**NOT** flips a bit. Its usual notations are a bar over the input, a preceding negation sign, or a prime after the input, as the next card shows.

The symbols are borrowed from arithmetic, but they mean something different here. This card shows representative cases, using 0 and 1 directly:

```formula
0·0 = 0    0·1 = 0    1·1 = 1
0 + 0 = 0  0 + 1 = 1  1 + 1 = 1
0′ = 1     1′ = 0
where
·: AND: the result is 1 only when both sides are 1. In the text it is often left out, so AB means A·B
+: OR, not addition: the result is 1 when at least one side is 1
′: NOT, the complement: it turns 0 into 1 and 1 into 0. The text writes it as an apostrophe (A'); books often draw a bar over the letter instead
In words: AND behaves like multiplication on 0 and 1, and OR almost behaves like addition. The one surprise is that 1 + 1 = 1: OR has no carry, it just asks "is anything true?".
```

A **truth table** lists the output for every input combination. Each extra input doubles the number of combinations, so the table size grows quickly:

```formula
N_rows = 2^n
N_rows = 2^3 = 8   for n = 3
where
N_rows: the number of rows in the truth table, one per input combination
n: the number of inputs (Boolean variables)
2^n: n copies of 2 multiplied together. Each input can be 0 or 1, and every new input doubles the number of combinations
In words: a truth table for n inputs has 2^n rows, so three inputs need 8 rows and four need 16.
```

Here is the table for the three operations, with two inputs:

```
 A B | AB  A+B  A'
-----+-------------
 0 0 |  0   0    1
 0 1 |  0   1    1
 1 0 |  0   1    0
 1 1 |  1   1    0
```

**Precedence**: NOT binds tightest, then AND, then OR, just as powers come before multiplication and multiplication before addition in arithmetic. A NOT written after a bracket applies to the whole bracket:

```formula
A + B·C′ = A + (B·(C′))
(A·B)′ ≠ A′·B′
where
A, B, C: Boolean variables, each 0 or 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
C′, A′, B′: NOT C, NOT A, NOT B: the complement of that one variable
( )′: NOT applied to everything inside the bracket
≠: is not equal to (not the same function: some input gives a different output)
In words: NOT grabs only the thing directly before it, AND is done before OR, and a NOT over a whole group is very different from a NOT on each variable. With A = 1 and B = 0, (A·B)′ is 1 but A′·B′ is 0.
```

## Key takeaways
- Boolean signals abstract voltage ranges into two values.
- AND, OR and NOT have distinct truth tables and precedence.

## Further reading
- [UCC Library — Boole publications and dates](https://www.ucc.ie/en/heritage/history/people/ucc-staff/professor-george-boole/)
- [Shannon — A symbolic analysis of relay and switching circuits](https://tubes.mit.edu/6S917/_static/2025/resources/shannon38.pdf)
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Boolean algebra — Wikipedia](https://en.wikipedia.org/wiki/Boolean_algebra)
- [De Morgan's laws — Wikipedia](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [Canonical normal form (minterms and maxterms) — Wikipedia](https://en.wikipedia.org/wiki/Canonical_normal_form)
- [A Symbolic Analysis of Relay and Switching Circuits — Wikipedia](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits)
- [Nand2Tetris: build a computer from first principles](https://www.nand2tetris.org/)
