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

```formula essential
Y = S′·A + S·B
where
Y: the mux output
A, B: the two data inputs, each 0 or 1
S: the select input: 0 picks A, 1 picks B
S′: NOT S
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: A low select passes the first data input; a high select passes the second. The unselected input cannot change the settled output.
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

A four-way mux uses a two-bit binary selection code: 00 picks input zero, 01 picks input one, 10 picks input two and 11 picks input three.

> [!analogy] Real-world analogy: Choosing a television input
> A television's source button chooses which connected device appears on the screen.
>
> **How it maps:** The source choice is the mux select; the connected sources are data inputs; the selected source feeds the output.
>
> **Where it stops:** A mux selects electrical data under timing constraints. It does not decode a television programme, and switching inputs need not be free of transients.

Each extra select bit doubles the number of inputs the mux can choose between. Three select bits identify eight inputs; five identify thirty-two. These bits name an input rather than hold the data being selected.

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

Each output is one minterm of the select bits: it recognises one particular input code. Only that output is high in this enabled, active-high model.

Mux data inputs need not be independent external signals. Suppose one selection should output a remaining input bit, another should output its complement, and the other selections should output constants. Wiring those four choices into the mux implements that truth table. This is another way to build a Boolean function by splitting it into cases.

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
