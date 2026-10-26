---
id: logic-binary-values
title: Binary values and Boolean operations
level: basic
minutes: 3
sourceLesson: logic-boolean-algebra
summary: Boolean signals abstract voltage ranges into two values.
---

Boolean algebra models binary signals with values 0 and 1. Physical digital circuits use voltage ranges, have transition intervals and may encounter unknown, metastable or high-impedance states; sequential circuits also depend on stored state. The mathematics of such functions is **Boolean algebra**, named after George Boole, who described an algebra of logic in 1847 and 1854.

Claude Shannon connected this algebra to relay circuits in his MIT master's work, published in a 1938 paper. That paper shows how switching circuits can be analysed using rules analogous to the calculus of propositions. That idea is the bridge from logic to hardware: write the behaviour you want as a Boolean expression, simplify it with algebra, and the simplified expression can suggest a smaller circuit; actual area, delay and power depend on the implementation.

This unit introduces the signal values and basic operations used throughout the following units.

## Values and the three fundamental operations

A Boolean variable takes one of two values: 0 or 1 (mapped here using positive logic to low and high voltage ranges). There are three fundamental operations.

> [!analogy] Real-world analogy: Two permissions
> An action may require both a manager's approval and a supervisor's approval, or either approval may be enough.
>
> **How it maps:** Requiring both permissions is AND; accepting either or both is OR. NOT reverses one yes/no condition.
>
> **Where it stops:** This compares settled yes/no decisions. A physical gate also has voltage limits and takes time to respond.

**AND** is one only when both inputs are one. **OR** is one when at least one input is one, including when both are one. **NOT** flips a bit. The notation is compact, but OR must not be mistaken for ordinary addition:

```formula essential
A·B      A + B      A′
where
A, B: Boolean input bits, each zero or one
A′: the complement of A
·: AND: the result is 1 only when both sides are 1. In the text it is often left out, so AB means A·B
+: OR, not addition: the result is 1 when at least one side is 1
′: NOT, the complement: it turns 0 into 1 and 1 into 0. The text writes it as an apostrophe (A'); books often draw a bar over the letter instead
In words: the three expressions mean AND of the inputs, OR of the inputs, and NOT of the first input. OR of two ones is still one: it asks whether anything is true and produces no carry.
```

A **truth table** lists the output for every input combination. Adding a new independent input creates two cases for every old row: the new input low and the new input high. Each extra input therefore doubles the table size. A complete table must cover both cases, even when their outputs happen to match.

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

```formula essential
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
