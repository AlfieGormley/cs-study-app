---
id: logic-adders-alu
title: Combinational circuits, adders and the ALU
level: intermediate
minutes: 15
summary: Multiplexers and decoders, the half and full adder, why ripple-carry is slow and how carry-lookahead and prefix adders fix it, subtraction in two's complement, and how an ALU produces its result and N, Z, C, V flags.
---

A **combinational circuit** is one whose outputs depend only on its current inputs. There is no memory: change the inputs, wait for the gates to settle, and the outputs follow. Everything in lessons 1 to 3 was combinational.

This lesson builds the combinational blocks that every processor contains: multiplexers, decoders, adders and the **arithmetic logic unit** (ALU). Addition is central to operations such as integer arithmetic and address generation. Whether an adder lies on a particular critical path depends on the implementation.

## Multiplexers: choosing a signal

A **multiplexer** (mux) is a hardware `if`. A 2-to-1 mux passes input A when the select S is 0, and B when S is 1:

```
Y = S'·A + S·B

      +-----+
A ----|0    |
      | MUX |---- Y
B ----|1    |
      +-----+
         |
         S
```

A 4-to-1 mux uses two select bits and four AND terms: `Y = S1'S0'·I0 + S1'S0·I1 + S1S0'·I2 + S1S0·I3`. In general a 2^k-to-1 mux needs k select lines.

Muxes are everywhere in a CPU: choosing whether the ALU's second operand is a register or an immediate, choosing which result is written back, choosing the next PC. In the datapath lesson you will see that most of a processor's "control" is just driving mux selects.

## Decoders: one-hot from binary

The active-high binary decoder model here maps an n-bit input to 2^n outputs, exactly one of which is 1 when enabled. Active-low and enabled variants also exist. A 2-to-4 decoder:

```
 S1 S0 | Y3 Y2 Y1 Y0
-------+-------------
  0  0 |  0  0  0  1
  0  1 |  0  0  1  0
  1  0 |  0  1  0  0
  1  1 |  1  0  0  0
```

Each output is one minterm: `Y0 = S1'S0'`, `Y1 = S1'S0`, `Y2 = S1S0'`, `Y3 = S1S0`. Decoders select which memory row or register to write, and which instruction class an opcode belongs to. An **encoder** does the reverse, and a **priority encoder** reports the active input with the highest assigned priority. That may be the highest- or lowest-numbered input; interrupt controllers may use programmable priorities.

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

Read the columns: `sum = A ⊕ B` and `carry = A·B`. One XOR and one AND. It is called a *half* adder because it cannot accept a carry from a previous column.

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

- `S = A ⊕ B ⊕ Cin`: the sum bit is 1 when an odd number of inputs are 1.
- `Cout = AB + Cin(A ⊕ B)`: a carry out happens if both A and B are 1, or if exactly one is and a carry comes in. This is the same function as the **majority** you simplified in lesson 1, `AB + ACin + BCin`, just factored to reuse the XOR.

## Ripple-carry adder

Chain n full adders, each carry out feeding the next carry in:

```
  a3 b3     a2 b2     a1 b1     a0 b0
   | |       | |       | |       | |
 +-----+   +-----+   +-----+   +-----+
 | FA  |<--| FA  |<--| FA  |<--| FA  |<-c0
 +-----+ c3+-----+ c2+-----+ c1+-----+
  |   |      |         |         |
 c4  s3     s2        s1        s0
```

It is small (n full adders) and simple. Its weakness is that the worst-case carry dependence grows through the lower stages; a generate or kill at an intermediate bit can cut that dependence for particular inputs. The worst case is a carry that starts at bit 0 and propagates all the way, as in `0111...1 + 1`.

If each carry stage costs about two gate delays (an AND then an OR), an n-bit ripple adder has about **2n gate delays** on its carry chain. For 64 bits the simplified two-gate-per-stage model gives roughly 128 delays. Whether that fits a clock target depends on actual cells and interconnect; high-performance designs commonly use lookahead, prefix, carry-select or hybrid structures.

## Carry-lookahead: compute carries in parallel

The insight is that each bit position can say, *before* knowing its carry in, what it will do with one:

- **Generate** `Gi = Ai·Bi`: this column produces a carry regardless of its carry in.
- **Propagate** `Pi = Ai ⊕ Bi`: this column passes a carry in through to its carry out.

Then `C(i+1) = Gi + Pi·Ci`. Unroll the recurrence:

```
C1 = G0 + P0·C0
C2 = G1 + P1·G0 + P1·P0·C0
C3 = G2 + P2·G1 + P2·P1·G0
        + P2·P1·P0·C0
C4 = G3 + P3·G2 + P3·P2·G1
        + P3·P2·P1·G0
        + P3·P2·P1·P0·C0
```

Each carry is a two-level sum of products of G and P. In an ideal unit-delay model with arbitrary required fan-in and one-level G/P generation, this gives about three levels. Real XORs, wide gates, fan-out and wiring do not share one universal delay. Read `C2` in words: "a carry arrives at bit 2 if bit 1 generates one, or bit 1 propagates one that bit 0 generated, or both propagate the original carry in."

The cost is that the terms get wider and more numerous as you go. As width grows, the expanded gates and interconnect become costly, so designers build **hierarchical** lookahead: 4-bit blocks each produce a block-level G and P, and a second lookahead unit combines those.

## Prefix adders: lookahead taken to its conclusion

Generate and propagate pairs combine with an associative operator:

```
(G, P) ∘ (G', P') = (G + P·G', P·P')
```

where `(G, P)` is the more significant span. Because the operator is associative, the carries for all positions are a **parallel prefix** computation (like a prefix sum), which can be done in a tree of **log2(n) levels**. For 64 bits that is 6 levels instead of a 64-stage ripple.

The classic designs trade depth against area and wiring:

| Adder | Levels (n = 64) | Trade-off |
|---|---|---|
| Ripple-carry | 64 carry stages | Simple linear chain |
| Kogge–Stone | 6 prefix levels | Shallow tree, substantial wiring |
| Brent–Kung | 11 | Fewer cells, deeper |
| Han–Carlson | 7 | A hybrid |

These are standard topology-level comparisons, excluding input generate/propagate and final-sum logic. Cell delay, fan-out, routing and design variants determine actual speed and area.

## Subtraction with the same adder

In two's complement, `-B = B' + 1` (invert every bit, add one). So:

```
A - B = A + B' + 1
```

The adder already has a carry input. Put an XOR on each B input controlled by a `sub` signal (`Bi ⊕ 1 = Bi'`, `Bi ⊕ 0 = Bi`), and feed `sub` into c0 as well. One circuit now adds and subtracts.

## Building an ALU

An ALU computes several operations in parallel on the same operands and uses a mux to pick one. A 1-bit **ALU slice**:

```
          +-------+
 a --+----|  AND  |------+
     | +--|       |      |  +-----+
     | |  +-------+      +--|0    |
     | |  +-------+         |     |
     +----|  OR   |---------|1 MUX|-- r
     | +--|       |         |     |
     | |  +-------+      +--|2    |
     | |  +-------+      |  +-----+
     +----| FULL  |------+     |
       +--| ADDER |            op
 b* ---+  +-------+
           ^     |
          cin   cout
```

`b*` is `b ⊕ sub`. Put n slices side by side, chain the carries, and you have an n-bit ALU that can AND, OR, add and subtract. Real ALUs add XOR, shifts (via a **barrel shifter**, a log2(n)-deep tree of muxes), comparisons and more.

### The flags

Our teaching ALU reports N/Z/C/V-style status flags. Architectures such as ARM use these; other ISAs, including base RISC-V, use different comparison mechanisms without such an architectural flag register:

| Flag | Meaning | Computed as |
|---|---|---|
| N | Negative | MSB of result |
| Z | Zero | NOR of all result bits |
| C | Carry | carry out of MSB |
| V | Signed overflow | carry into MSB ⊕ carry out of MSB |

The **V** rule deserves a moment. Signed overflow happens when two numbers of the same sign produce a result of the other sign, such as 7 + 1 in 4 bits giving `1000`, which is -8. That happens exactly when the carry into the sign bit differs from the carry out of it.

Here is the whole thing in Python, bit by bit, as the hardware would do it:

```python
def full_add(a, b, cin):
    s = a ^ b ^ cin
    cout = (a & b) | (cin & (a ^ b))
    return s, cout

def alu(a, b, op, n=4):
    if n < 1 or op not in {"and", "or",
                           "add", "sub"}:
        raise ValueError("bad width or op")
    sub = int(op == "sub")
    carry = sub        # the +1 for A-B
    c_msb = 0          # carry into MSB
    result = 0
    for i in range(n):
        ai = (a >> i) & 1
        bi = ((b >> i) & 1) ^ sub
        if op == "and":
            r = ai & bi
        elif op == "or":
            r = ai | bi
        else:          # add or sub
            c_msb = carry
            r, carry = full_add(
                ai, bi, carry)
        result |= r << i
    flags = {
        "N": result >> (n - 1),
        "Z": int(result == 0),
        "C": carry,
        "V": c_msb ^ carry,
    }
    return result, flags

r, f = alu(0b0111, 0b0001, "add")
print(f"{r:04b}", f)
# 1000 {'N': 1, 'Z': 0, 'C': 0, 'V': 1}
r, f = alu(0b0011, 0b0101, "sub")
print(f"{r:04b}", f)
# 1110 {'N': 1, 'Z': 0, 'C': 0, 'V': 0}
```

Inputs are interpreted by their low n bits. This teaching implementation clears C and V for AND/OR; real ISA flag-update rules vary.

The first line is 7 + 1: the unsigned answer 8 fits (C = 0), but as signed 4-bit numbers it overflowed (V = 1). The second is 3 − 5 = −2, which is `1110` in two's complement. C = 0 here means a **borrow** occurred, because 3 < 5 unsigned.

### Comparisons come free

A compare instruction (`cmp` on x86 and ARM) is a subtraction that keeps only the flags. From `A - B`:

- `A == B` if Z = 1.
- Unsigned `A < B` if a borrow occurred.
- Signed `A < B` if N ≠ V. (N alone is wrong when the subtraction overflowed.)

> [!warning] The carry flag's meaning after subtraction differs by ISA
> ARM sets C = 1 when there is **no** borrow (it reports the adder's real carry out of `A + B' + 1`), as the Python above does. x86 sets CF = 1 when there **is** a borrow. Same hardware idea, inverted convention. Read the manual before trusting a branch condition.

## Beyond addition

- **Multiplication** is many additions. Hardware multipliers generate all partial products at once and sum them with trees of **carry-save adders**, which add three numbers into two without propagating carries, so only one real carry-propagate add is needed at the end.
- **Division** commonly uses iterative hardware, but algorithms, latency, throughput and operand dependence vary by processor.

> [!note] Evidence gap
> Universal modern-CPU multiplication/division cycle counts are omitted because no target processor, instruction or measurement was supplied.

## Key takeaways
- Muxes select, decoders produce a one-hot output per input code. Both are built from minterms.
- A full adder has `S = A ⊕ B ⊕ Cin` and `Cout = AB + Cin(A ⊕ B)`, the majority function.
- Ripple-carry delay grows linearly with width (about 2n gate delays). Carry-lookahead and prefix adders compute carries from generate/propagate signals in about log2(n) levels.
- Subtraction is `A + B' + 1`: XOR the B inputs with `sub` and feed `sub` into the carry in.
- The ALU computes N, Z, C and V. Signed overflow is carry-in ⊕ carry-out of the MSB; signed less-than is N ≠ V.

## Further reading
- [Adder (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Adder_(electronics))
- [Carry-lookahead adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-lookahead_adder)
- [Kogge–Stone adder — Wikipedia](https://en.wikipedia.org/wiki/Kogge%E2%80%93Stone_adder)
- [Arithmetic logic unit — Wikipedia](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Multiplexer — Wikipedia](https://en.wikipedia.org/wiki/Multiplexer)
- [Carry-save adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-save_adder)
