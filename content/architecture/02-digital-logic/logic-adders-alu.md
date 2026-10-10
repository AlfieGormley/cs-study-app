---
id: logic-adders-alu
title: Combinational circuits, adders and the ALU
level: intermediate
minutes: 19
summary: Multiplexers and decoders, the half and full adder, why ripple-carry is slow and how carry-lookahead and prefix adders fix it, subtraction in two's complement, and how an ALU produces its result and N, Z, C, V flags.
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
2^k: 2 multiplied by itself k times
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

```formula
S = A ⊕ B
C_out = A·B
S = 1 ⊕ 1 = 0   for A = B = 1
C_out = 1·1 = 1   for A = B = 1
where
S: the sum bit (the "sum" column)
C_out: the carry bit (the "carry" column), worth 2 in the next column up
A, B: the two bits being added
⊕: XOR: 1 when the two bits differ
·: AND: 1 only when both bits are 1
In words: the sum bit is 1 when exactly one input is 1, and the carry is 1 only when both are, so 1 + 1 gives sum 0, carry 1: binary 10, which is 2.
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

```formula
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
In words: the sum bit is 1 when an odd number of the three inputs are 1. A carry out happens if both A and B are 1, or if exactly one of them is and a carry comes in. The last line is the same carry written as the majority function from lesson 1.
```

The second and third lines are the same function: the second just factors the majority to reuse the XOR that the sum already computes. For example, with A = 1, B = 0 and a carry in of 1:

```formula
S = 1 ⊕ 0 ⊕ 1 = 0
C_out = 1·0 + 1·(1 ⊕ 0) = 0 + 1 = 1
where
S: the sum bit
C_out: the carry out
⊕: XOR: 1 when the two sides differ
·: AND
+: OR
In words: 1 + 0 + 1 is 2, binary 10, so the sum bit is 0 and the carry out is 1, matching the 1 0 1 row of the table.
```

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

If each carry stage costs about two gate delays (an AND then an OR), the carry chain's delay grows in proportion to the width, about **2n gate delays** for n bits:

```formula
t_ripple ≈ 2 × n × t_gate
t_ripple ≈ 2 × 64 × t_gate = 128 × t_gate
where
t_ripple: the worst-case delay of the ripple-carry chain
n: the adder width in bits, here 64
t_gate: the delay of one gate (an AND or an OR), in this simplified model where every gate is equally fast
2: two gate delays per bit: an AND then an OR on the carry path
≈: approximately equal to
In words: in the simplified model, a 64-bit ripple adder's carry passes through about 128 gates in the worst case, and doubling the width doubles the delay.
```

Whether that fits a clock target depends on actual cells and interconnect; high-performance designs commonly use lookahead, prefix, carry-select or hybrid structures.

## Carry-lookahead: compute carries in parallel

The insight is that each bit position can say, *before* knowing its carry in, what it will do with one:

- **Generate signal**: this column produces a carry regardless of its carry in (both bits are 1).
- **Propagate signal**: this column passes a carry in through to its carry out (exactly one bit is 1).

Written as equations, with the carry rule that follows from them:

```formula
G_i = A_i·B_i
P_i = A_i ⊕ B_i
C_{i+1} = G_i + P_i·C_i
where
i: the bit position, counting from 0 at the least significant bit
A_i, B_i: bit i of the two numbers being added
G_i: generate for bit i (Gi in the text): 1 when this column makes a carry by itself
P_i: propagate for bit i (Pi in the text): 1 when this column passes an incoming carry on
C_i: the carry into bit i; C_0 is the adder's carry in
C_{i+1}: the carry out of bit i, which is the carry into bit i + 1
⊕: XOR: 1 when the two bits differ
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: a carry leaves column i if the column generates one, or if it propagates a carry that arrived from below.
```

Now unroll the recurrence: substitute each carry into the next, so every carry depends only on the G and P signals and the original carry in:

```formula
C_1 = G_0 + P_0·C_0
C_2 = G_1 + P_1·G_0 + P_1·P_0·C_0
C_3 = G_2 + P_2·G_1 + P_2·P_1·G_0
    + P_2·P_1·P_0·C_0
C_4 = G_3 + P_3·G_2 + P_3·P_2·G_1
    + P_3·P_2·P_1·G_0
    + P_3·P_2·P_1·P_0·C_0
where
C_0: the adder's carry in
C_1, C_2, C_3, C_4: the carries into bits 1, 2 and 3, and the carry out of bit 3 (the adder's carry out)
G_0, G_1, G_2, G_3: generate signals of bits 0 to 3: G_i = A_i·B_i
P_0, P_1, P_2, P_3: propagate signals of bits 0 to 3: P_i = A_i ⊕ B_i
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: each term is one way for a carry to arrive: generated at some bit and then propagated by every bit above it, or the original carry in propagated by every bit.
```

For example, add A = 1011 (11) and B = 0110 (6) with no carry in, writing every 4-bit value with bit 3 on the left:

```formula
G = 1011 · 0110 = 0010
P = 1011 ⊕ 0110 = 1101
P_3·P_2·G_1 = 1·1·1 = 1
C_4 = 1
where
G: the four generate bits G_3 G_2 G_1 G_0, from ANDing A and B bit by bit
P: the four propagate bits P_3 P_2 P_1 P_0, from XORing A and B bit by bit
P_3, P_2: the propagate bits of bits 3 and 2
G_1: the generate bit of bit 1
C_4: the carry out of the 4-bit adder
·: AND, bit by bit
⊕: XOR, bit by bit
In words: only one term of the C_4 equation is 1: the carry is generated at bit 1 and rides through bits 2 and 3. Check: 11 + 6 = 17, which is binary 1 0001, so the carry out is indeed 1.
```

Each carry is a two-level sum of products of G and P. In an ideal unit-delay model with arbitrary required fan-in and one-level G/P generation, this gives about three levels. Real XORs, wide gates, fan-out and wiring do not share one universal delay. Read `C2` in words: "a carry arrives at bit 2 if bit 1 generates one, or bit 1 propagates one that bit 0 generated, or both propagate the original carry in."

The cost is that the terms get wider and more numerous as you go. As width grows, the expanded gates and interconnect become costly, so designers build **hierarchical** lookahead: 4-bit blocks each produce a block-level G and P, and a second lookahead unit combines those.

## Prefix adders: lookahead taken to its conclusion

Generate and propagate pairs for neighbouring spans of bits combine with an associative operator:

```formula
(G, P) ∘ (G′, P′) = (G + P·G′, P·P′)
where
G, P: the generate and propagate signals of the more significant span of bits
G′, P′: the generate and propagate signals of the adjacent less significant span. Here the prime means "the other span", not NOT
∘: the prefix combine operator: it merges two adjacent spans into one span covering both
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the combined span generates a carry if the upper part generates one, or the upper part propagates one that the lower part generated; it propagates only if both parts propagate.
```

Because the operator is associative (the grouping does not matter), the carries for all positions are a **parallel prefix** computation (like a prefix sum), which can be done in a tree whose depth grows with the logarithm of the width:

```formula
L = log_2(n)
L = log_2(64) = 6
where
L: the number of prefix-tree levels (Kogge–Stone)
n: the adder width in bits
log_2: logarithm base 2: how many times you must double 1 to reach n, since 2^6 = 64
In words: each level doubles the span each carry covers, so 64 bits need 6 levels instead of a 64-stage ripple, and doubling the width adds just one level.
```

The classic designs trade depth against area and wiring:

| Adder | Levels for 64 bits | Trade-off |
|---|---|---|
| Ripple-carry | 64 carry stages | Simple linear chain |
| Kogge–Stone | 6 prefix levels | Shallow tree, substantial wiring |
| Brent–Kung | 11 | Fewer cells, deeper |
| Han–Carlson | 7 | A hybrid |

These are standard topology-level comparisons, excluding input generate/propagate and final-sum logic. Cell delay, fan-out, routing and design variants determine actual speed and area.

## Subtraction with the same adder

In two's complement, negating a number means inverting every bit and adding one. So subtraction is addition of the inverted bits plus one:

```formula
−B = B′ + 1
A − B = A + B′ + 1
0101 − 0011 = 0101 + 1100 + 1
            = 1 0010 → 0010
where
A, B: n-bit numbers in two's complement
B′: B with every bit inverted (bitwise NOT)
+, −: ordinary binary addition and subtraction here, not OR
→: keep only the low 4 bits (the leading 1 is the carry out, dropped)
In words: to compute A − B, add A to the inverted B and add one more. The example is 5 − 3: 0101 + 1100 + 1 is 1 0010, and the low four bits 0010 are 2.
```

The adder already has a carry input. Put an XOR on each B input controlled by a `sub` signal, and feed `sub` into c0 (the adder's carry in) as well:

```formula
B_i ⊕ 1 = B_i′
B_i ⊕ 0 = B_i
where
B_i: bit i of the B input
B_i′: NOT B_i
⊕: XOR: 1 when the two sides differ
In words: XOR with sub = 1 inverts each B bit; XOR with sub = 0 passes it unchanged.
```

One circuit now adds and subtracts.

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

`b*` is b XOR sub: b itself when adding, NOT b when subtracting. Put n slices side by side, chain the carries, and you have an n-bit ALU that can AND, OR, add and subtract. Real ALUs add XOR, shifts (via a **barrel shifter**, a tree of muxes whose depth is the base-2 logarithm of the width: 6 levels for 64 bits), comparisons and more.

### The flags

Our teaching ALU reports N/Z/C/V-style status flags. Architectures such as ARM use these; other ISAs, including base RISC-V, use different comparison mechanisms without such an architectural flag register:

| Flag | Meaning | Computed as |
|---|---|---|
| N | Negative | MSB of result |
| Z | Zero | NOR of all result bits |
| C | Carry | carry out of MSB |
| V | Signed overflow | carry into MSB ⊕ carry out of MSB |

For an n-bit result, the four flags are:

```formula
N = r_{n−1}
Z = (r_{n−1} + … + r_1 + r_0)′
C = c_n
V = c_{n−1} ⊕ c_n
where
n: the width in bits; bits are numbered 0 (least significant) to n − 1 (the MSB, the sign bit)
r_0, r_1, r_{n−1}: bits of the result
…: the bits in between
c_n: the carry out of the MSB
c_{n−1}: the carry into the MSB
N, Z, C, V: the negative, zero, carry and overflow flags, each 0 or 1
+: OR
( )′: NOT of the whole bracket, so OR then NOT is a NOR
⊕: XOR: 1 when the two sides differ
In words: N copies the sign bit, Z is 1 only when every result bit is 0, C is the carry out of the top bit, and V is 1 when the carry into the top bit differs from the carry out of it.
```

The **V** rule deserves a moment. Signed overflow happens when two numbers of the same sign produce a result of the other sign, such as 7 + 1 in 4 bits giving `1000`, which is -8. That happens exactly when the carry into the sign bit differs from the carry out of it: in 0111 + 0001, a carry of 1 enters bit 3 but none leaves it, so V = 1 XOR 0 = 1.

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

A compare instruction (`cmp` on x86 and ARM) is a subtraction that keeps only the flags. After computing A − B:

```formula
A = B       if Z = 1
A <_u B     if C = 0
A <_s B     if N ≠ V
where
A, B: the two operands being compared
Z: the zero flag: 1 when A − B is 0
C: the carry flag, using the ARM convention: the adder's real carry out of A + B′ + 1. C = 0 means a borrow occurred, so A was smaller as an unsigned number. (x86 inverts this: its CF = 1 means a borrow.)
<_u: less than, treating both as unsigned numbers
<_s: less than, treating both as signed two's-complement numbers
N: the negative flag (sign bit of A − B)
V: the signed overflow flag
≠: is not equal to
In words: equal if the difference is zero; unsigned-less if the subtraction borrowed; signed-less if the sign flag and overflow flag disagree. N alone is wrong when the subtraction overflowed, because overflow flips the sign bit.
```

> [!warning] The carry flag's meaning after subtraction differs by ISA
> ARM sets C = 1 when there is **no** borrow (it reports the adder's real carry out of `A + B' + 1`), as the Python above does. x86 sets CF = 1 when there **is** a borrow. Same hardware idea, inverted convention. Read the manual before trusting a branch condition.

## Beyond addition

- **Multiplication** is many additions. Hardware multipliers generate all partial products at once and sum them with trees of **carry-save adders**, which add three numbers into two without propagating carries, so only one real carry-propagate add is needed at the end.
- **Division** commonly uses iterative hardware, but algorithms, latency, throughput and operand dependence vary by processor.

> [!note] Evidence gap
> Universal modern-CPU multiplication/division cycle counts are omitted because no target processor, instruction or measurement was supplied.

## Key takeaways
- Muxes select, decoders produce a one-hot output per input code. Both are built from minterms.
- A full adder's sum bit is the XOR of its three inputs, and its carry out is the majority of them.
- Ripple-carry delay grows linearly with width (about two gate delays per bit). Carry-lookahead and prefix adders compute carries from generate/propagate signals in a number of levels that grows with the logarithm of the width (6 levels for 64 bits).
- Subtraction is A plus the inverted B plus one: XOR the B inputs with `sub` and feed `sub` into the carry in.
- The ALU computes N, Z, C and V. Signed overflow is the XOR of the carries into and out of the MSB; signed less-than is "N differs from V".

## Further reading
- [Adder (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Adder_(electronics))
- [Carry-lookahead adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-lookahead_adder)
- [Kogge–Stone adder — Wikipedia](https://en.wikipedia.org/wiki/Kogge%E2%80%93Stone_adder)
- [Arithmetic logic unit — Wikipedia](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Multiplexer — Wikipedia](https://en.wikipedia.org/wiki/Multiplexer)
- [Carry-save adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-save_adder)
