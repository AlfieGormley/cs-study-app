---
id: logic-mux-decoder
title: Multiplexers and decoders
level: intermediate
minutes: 4
sourceLesson: logic-adders-alu
summary: A mux chooses one input; a decoder selects one output.
---

A **combinational circuit** is one whose outputs depend only on its current inputs. There is no memory: change the inputs, wait for the gates to settle, and the outputs follow. Everything in lessons 1 to 3 was combinational.

This lesson builds the combinational blocks that every processor contains: multiplexers, decoders, adders and the **arithmetic logic unit** (ALU). Addition is central to operations such as integer arithmetic and address generation. Whether an adder lies on a particular critical path depends on the implementation.

## Multiplexers: choosing a signal

A **multiplexer** (mux) is a hardware `if`. A 2-to-1 mux passes input A when the select S is 0, and B when S is 1:

```formula
Y = S′·A + S·B
Y = 1·A + 0·B = A   for S = 0
where
Y: the mux output
A, B: the two data inputs, each 0 or 1
S: the select input: 0 picks A, 1 picks B
S′: NOT S
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: when S is 0 only the A·S′ term can be 1, so Y copies A; when S is 1 only the S·B term can be 1, so Y copies B.
```

```
      +-----+
A ----|0    |
      | MUX |---- Y
B ----|1    |
      +-----+
         |
         S
```

A 4-to-1 mux uses two select bits and four AND terms, one for each value of the select bits:

```formula
Y = S_1′·S_0′·I_0 + S_1′·S_0·I_1
  + S_1·S_0′·I_2 + S_1·S_0·I_3
where
Y: the mux output
I_0, I_1, I_2, I_3: the four data inputs
S_1, S_0: the two select bits (S1 and S0 in the text), S_1 the more significant; together they form the binary number of the input to pass
S_1′, S_0′: NOT S_1, NOT S_0
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: each data input is ANDed with the one combination of select bits that names it, so S_1 = 1, S_0 = 0 (binary 2) passes I_2.
```

In general, each extra select bit doubles the number of inputs the mux can choose between:

```formula
N_inputs = 2^k
N_inputs = 2^3 = 8   for k = 3
where
N_inputs: the number of data inputs the mux chooses between
k: the number of select lines
2^k: k copies of 2 multiplied together
In words: each extra select line doubles the number of inputs, so an 8-to-1 mux needs 3 select lines and a 32-to-1 mux needs 5.
```

Muxes are everywhere in a CPU: choosing whether the ALU's second operand is a register or an immediate, choosing which result is written back, choosing the next PC. In the datapath lesson you will see that most of a processor's "control" is just driving mux selects.

## Decoders: one-hot from binary

The active-high binary decoder model here maps a binary input to one output per possible input value (2 input bits give 4 outputs, 3 give 8, 5 give 32), exactly one of which is 1 when enabled. Active-low and enabled variants also exist. A 2-to-4 decoder:

```
 S1 S0 | Y3 Y2 Y1 Y0
-------+-------------
  0  0 |  0  0  0  1
  0  1 |  0  0  1  0
  1  0 |  0  1  0  0
  1  1 |  1  0  0  0
```

Each output is one minterm of the select bits:

```formula
Y_0 = S_1′·S_0′      Y_1 = S_1′·S_0
Y_2 = S_1·S_0′       Y_3 = S_1·S_0
where
Y_0, Y_1, Y_2, Y_3: the four decoder outputs (Y0 to Y3 in the table)
S_1, S_0: the two input bits, S_1 the more significant
S_1′, S_0′: NOT S_1, NOT S_0
·: AND: 1 only when both sides are 1
In words: output number k is 1 only when the input bits spell k in binary; for example Y_2 is 1 only for S_1 = 1, S_0 = 0.
```

Decoders select which memory row or register to write, and which instruction class an opcode belongs to. A **binary encoder** does the reverse, and a **priority encoder** reports the active input with the highest assigned priority. That may be the highest- or lowest-numbered input; interrupt controllers may use programmable priorities.

## Key takeaways
- A mux chooses one input; a decoder selects one output.
- Mux data inputs can encode a Boolean function.

## Further reading
- [MIT — Arithmetic structures](https://web.mit.edu/6.111/www/f2017/handouts/L08.pdf)
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Adder (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Adder_(electronics))
- [Carry-lookahead adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-lookahead_adder)
- [Kogge–Stone adder — Wikipedia](https://en.wikipedia.org/wiki/Kogge%E2%80%93Stone_adder)
- [Arithmetic logic unit — Wikipedia](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Multiplexer — Wikipedia](https://en.wikipedia.org/wiki/Multiplexer)
- [Carry-save adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-save_adder)
