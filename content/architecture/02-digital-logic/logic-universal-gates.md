---
id: logic-universal-gates
title: Standard gates and NAND universality
level: basic
minutes: 5
sourceLesson: logic-gates-cmos
summary: NAND alone or NOR alone can implement any Boolean function.
---

Boolean algebra is the maths. A **logic gate** is a physical device that computes one Boolean operation on voltages. Wire gates together and you can compute any Boolean function. Add memory (sequential-logic lessons) and you can build a computer.

Many modern processors build gates from billions of **CMOS** transistors. Apple's M1, for example, has about 16 billion. This lesson starts with the gates as black boxes, then opens them up to see the transistors, because this conventional construction explains why a NAND can use fewer devices than an AND, why wide NOR gates can be costly, and how switching power depends on clock speed.

## The standard gates

Seven gates cover nearly everything. The schematic notation below labels each gate by name:

```
A --+-----+          A --+-----+
    | AND |-- Y          | OR  |-- Y
B --+-----+          B --+-----+

A --[NOT]o-- Y       A --+------+
                         | NAND |o-- Y
                     B --+------+
```

A small circle (`o`) on an output means "inverted". So NAND is AND followed by NOT, and NOR is OR followed by NOT.

```
 A B | AND OR NAND NOR XOR XNOR
-----+--------------------------
 0 0 |  0   0   1   1   0   1
 0 1 |  0   1   1   0   1   0
 1 0 |  0   1   1   0   1   0
 1 1 |  1   1   0   0   0   1
```

NOT (the **inverter**) has one input. A **buffer** is a gate whose output equals its input; it computes nothing, but it boosts a weak signal so it can drive a long wire or many other gates.

## Universal gates

A set of gates is **functionally complete** if it can build every Boolean function. AND, OR and NOT together are complete: the canonical sum of products from Boolean-algebra lessons needs only those three.

Remarkably, **NAND on its own is complete**. So is NOR. Here is how NAND replaces the others:

```formula
A′ = NAND(A, A)
A·B = NAND(NAND(A, B), NAND(A, B))
A + B = NAND(NAND(A, A), NAND(B, B))
A + B = (A′·B′)′
where
A, B: Boolean inputs, each 0 or 1
NAND(X, Y): the NAND gate (NOT-AND) applied to inputs X and Y: 0 only when both inputs are 1, otherwise 1
A′, B′: NOT A, NOT B: the complement
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
( )′: NOT applied to the whole bracket
In words: a NAND with both inputs tied together is an inverter; NAND followed by that inverter is AND; and NAND of the two inverted inputs is OR. The last line shows why: by De Morgan, NOT(NOT A AND NOT B) is A OR B.
```

XOR takes four NAND gates. Wiring diagrams of this get cluttered fast, so here it is as a **netlist**, a list of gates and the named wires between them, which is how real design tools describe circuits:

```
n1 = NAND(A,  B)
n2 = NAND(A,  n1)
n3 = NAND(B,  n1)
Y  = NAND(n2, n3)    # Y is A XOR B
```

Check one row by substituting A = 1 and B = 0, one gate at a time:

```formula
n1 = NAND(1, 0) = 1
n2 = NAND(1, 1) = 0
n3 = NAND(0, 1) = 1
Y = NAND(0, 1) = 1
where
n1, n2, n3: the internal wires named in the netlist
Y: the circuit's output
NAND( , ): the NAND gate: 0 only when both inputs are 1, otherwise 1
In words: with A = 1 and B = 0 the output is 1, which is what A XOR B should give, since the inputs differ.
```

### Two-level logic in NAND-NAND

The practical payoff: any sum of products converts directly to two layers of NAND. Take the function A·B + C·D ("A and B, or C and D"):

```
A --+------+
    | NAND |o--+
B --+------+   |   +------+
               +---| NAND |o-- Y
C --+------+   +---|      |
    | NAND |o--+   +------+
D --+------+
```

Why it works, using De Morgan on the output gate:

```formula
Y = NAND(NAND(A, B), NAND(C, D))
Y = ((A·B)′·(C·D)′)′
Y = (A·B)′′ + (C·D)′′
Y = A·B + C·D
where
Y: the circuit's output
A, B, C, D: the four inputs, each 0 or 1
NAND(X, Y): NOT (X AND Y): 0 only when both inputs are 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
( )′: NOT applied to the whole bracket
( )′′: NOT applied twice, which cancels out
In words: the outer NAND turns into an OR of its inverted inputs, and those inversions cancel the inner NANDs' inversions, leaving AND-OR.
```

So draw the AND-OR circuit, replace every gate with NAND, and the function is unchanged. The inversion bubbles cancel in pairs.

## Key takeaways
- NAND alone or NOR alone can implement any Boolean function.
- NAND–NAND networks implement sum-of-products logic.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/cmos/notes.html)
- [Logic gate — Wikipedia](https://en.wikipedia.org/wiki/Logic_gate)
- [CMOS — Wikipedia](https://en.wikipedia.org/wiki/CMOS)
- [NAND logic — Wikipedia](https://en.wikipedia.org/wiki/NAND_logic)
- [Functional completeness — Wikipedia](https://en.wikipedia.org/wiki/Functional_completeness)
- [Processor power dissipation — Wikipedia](https://en.wikipedia.org/wiki/Processor_power_dissipation)
- [Nand2Tetris: build a computer from NAND gates](https://www.nand2tetris.org/)
