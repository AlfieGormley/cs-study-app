---
id: logic-xor-basic-laws
title: XOR and the basic Boolean laws
level: basic
minutes: 4
sourceLesson: logic-boolean-algebra
summary: XOR detects unequal bits; XNOR detects equal bits.
---

### Exclusive OR

One more operation is so common it gets its own symbol. **XOR** is one when its inputs differ:

```formula
A ⊕ B
where
A: Boolean input bit
B: Boolean input bit
⊕: XOR
In words: Read this Boolean expression as (A XOR B).
```

The complete truth table is:

```
 A B | A⊕B
-----+-----
 0 0 |  0
 0 1 |  1
 1 0 |  1
 1 1 |  0
```

XOR is addition modulo 2: add the bits and keep only the remainder after dividing by 2, so 1 + 1 = 2 leaves 0. That is why it turns up in adders, parity bits, checksums and CRCs. Four facts are worth knowing by heart:

```formula
A ⊕ 0 = A
A ⊕ 1 = A′
A ⊕ A = 0
A ⊕ B = A′·B + A·B′
where
A, B: Boolean variables, each 0 or 1
⊕: XOR (exclusive OR): 1 when the two sides differ, 0 when they are equal
A′, B′: NOT A, NOT B
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: XOR with 0 changes nothing, XOR with 1 flips the bit, anything XORed with itself is 0, and XOR means "A is 0 and B is 1, or A is 1 and B is 0".
```

Its complement, **XNOR**, is 1 when the inputs are equal.

## The laws

These identities hold for every value of the variables. You can check any of them by writing out the truth table. Each law comes as a pair: an AND form and an OR form.

| Law | What it says |
|---|---|
| Identity | AND with 1, or OR with 0, changes nothing |
| Null | AND with 0 always gives 0; OR with 1 always gives 1 |
| Idempotent | combining a variable with itself gives the variable |
| Complement | a variable AND its NOT is 0; a variable OR its NOT is 1 |
| Involution | NOT twice gives back the original |
| Commutative | the order of the two sides does not matter |
| Associative | the grouping of three terms does not matter |
| Distributive | AND distributes over OR, *and* OR distributes over AND |
| Absorption | A combined with a term that contains A is just A |
| De Morgan | a NOT over a group complements each variable and swaps AND with OR |

The one-variable laws, in table order (identity, null, idempotent, complement, involution), AND form on the left and OR form on the right:

```formula
A·1 = A        A + 0 = A
A·0 = 0        A + 1 = 1
A·A = A        A + A = A
A·A′ = 0       A + A′ = 1
(A′)′ = A
where
A: a Boolean variable, 0 or 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
A′: NOT A: 1 when A is 0, and 0 when A is 1
(A′)′: NOT applied twice to A
In words: line by line, these are the identity, null, idempotent, complement and involution laws. Each one can be checked by trying A = 0 and A = 1.
```

The laws with two or three variables, in table order (commutative, associative, distributive, absorption, De Morgan):

```formula
A·B = B·A        A + B = B + A
(A·B)·C = A·(B·C)
(A + B) + C = A + (B + C)
A·(B + C) = A·B + A·C
A + B·C = (A + B)·(A + C)
A·(A + B) = A    A + A·B = A
(A·B)′ = A′ + B′
(A + B)′ = A′·B′
where
A, B, C: Boolean variables, each 0 or 1
·: AND: 1 only when both sides are 1 (the text often writes A·B as AB)
+: OR: 1 when at least one side is 1
A′, B′: NOT A, NOT B
( )′: NOT applied to the whole bracket
In words: order and grouping do not matter, each operator distributes over the other, a term is absorbed by a simpler term it contains, and De Morgan pushes a NOT inside a bracket by complementing each variable and swapping AND with OR.
```

## Key takeaways
- XOR detects unequal bits; XNOR detects equal bits.
- Identity, complement and idempotence hold for every Boolean input.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Boolean algebra — Wikipedia](https://en.wikipedia.org/wiki/Boolean_algebra)
- [De Morgan's laws — Wikipedia](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [Canonical normal form (minterms and maxterms) — Wikipedia](https://en.wikipedia.org/wiki/Canonical_normal_form)
- [A Symbolic Analysis of Relay and Switching Circuits — Wikipedia](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits)
- [Nand2Tetris: build a computer from first principles](https://www.nand2tetris.org/)
