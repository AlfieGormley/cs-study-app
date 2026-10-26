---
id: logic-half-full-adders
title: Half adders and full adders
level: intermediate
minutes: 3
sourceLesson: logic-adders-alu
summary: A half adder combines two bits; a full adder includes carry-in.
---

## The half adder

Add two single bits. There are four cases:

```
 A B | carry sum
-----+-----------
 0 0 |   0    0
 0 1 |   0    1
 1 0 |   0    1
 1 1 |   1    0     (1+1 = 10 binary)
```

Read the columns:

```formula essential
S = A ⊕ B
C_out = A·B
where
S: the sum bit (the "sum" column)
C_out: the carry bit (the "carry" column), worth 2 in the next column up
A, B: the two bits being added
⊕: XOR: 1 when the two bits differ
·: AND: 1 only when both bits are 1
In words: Different inputs make the sum high. Two high inputs instead make the sum low and carry high, representing binary ten.
```

One XOR and one AND. It is called a *half* adder because it cannot accept a carry from a previous column.

## The full adder

To add multi-bit numbers, each column must add three bits: A, B and the carry in from the column to its right.

```
 A B Cin | Cout S
---------+--------
 0 0  0  |  0   0
 0 0  1  |  0   1
 0 1  0  |  0   1
 0 1  1  |  1   0
 1 0  0  |  0   1
 1 0  1  |  1   0
 1 1  0  |  1   0
 1 1  1  |  1   1
```

Two equations describe it:

```formula essential
S = A ⊕ B ⊕ C_in
C_out = A·B + C_in·(A ⊕ B)
C_out = A·B + A·C_in + B·C_in
where
S: the sum bit for this column
C_out: the carry out to the next column up (Cout in the table)
A, B: the two bits being added in this column
C_in: the carry in from the column to the right (Cin in the table)
⊕: XOR: 1 when the two sides differ; a chain of XORs is 1 when an odd number of its inputs are 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the sum bit is 1 when an odd number of the three inputs are 1. A carry out happens if both A and B are 1, or if exactly one of them is and a carry comes in. The last line is the same carry written as the majority function from Boolean-algebra lessons.
```

The second and third lines are the same function: the second factors the majority to reuse the XOR that the sum already computes.

With one data input high, the other low and carry-in high, two input bits are high. The sum is zero and carry-out is one, matching the truth-table row.

## Key takeaways
- A half adder combines two bits; a full adder includes carry-in.
- The sum uses XOR and the carry implements the majority function.

## Further reading
- [MIT — Arithmetic structures](https://web.mit.edu/6.111/www/f2017/handouts/L08.pdf)
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Adder (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Adder_(electronics))
- [Carry-lookahead adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-lookahead_adder)
- [Kogge–Stone adder — Wikipedia](https://en.wikipedia.org/wiki/Kogge%E2%80%93Stone_adder)
- [Arithmetic logic unit — Wikipedia](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Multiplexer — Wikipedia](https://en.wikipedia.org/wiki/Multiplexer)
- [Carry-save adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-save_adder)
