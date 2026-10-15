---
id: logic-alu-bit-simulation
title: Simulate an ALU one bit at a time
level: intermediate
minutes: 3
sourceLesson: logic-adders-alu
summary: Trace a runnable ALU model and distinguish carry from signed overflow.
---

The previous unit defined the flags and comparison rules. This model implements the four-bit teaching ALU with individual bit operations, making the carry path visible. The width parameter selects how many low input bits the model uses; it does not simulate transistor voltages, physical propagation delay or a specific processor ISA.

Here is the whole thing in Python, bit by bit, as the hardware would do it:

```python
def full_add(a, b, cin):
    # XOR keeps the low bit of the sum.
    s = a ^ b ^ cin
    # Generate or propagate carry-in.
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
        # Isolate the current bit column.
        ai = (a >> i) & 1
        # Complement B for subtraction.
        bi = ((b >> i) & 1) ^ sub
        if op == "and":
            r = ai & bi
        elif op == "or":
            r = ai | bi
        else:          # add or sub
            # Save the incoming carry.
            c_msb = carry
            r, carry = full_add(
                ai, bi, carry)
        # Store the result bit.
        result |= r << i
    # The final column supplies N, C and V.
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

The first line adds seven and one. The unsigned answer eight fits, so carry is clear; the signed four-bit interpretation overflows, so overflow is set. The second line subtracts five from three and produces negative two, binary `1110` in two’s complement. Carry is clear here because a **borrow** occurred: three is smaller than five as an unsigned value.


## Key takeaways
- Each loop iteration computes one result bit and advances the carry.
- The final carry and the carry entering the sign bit distinguish unsigned and signed overflow.
- AND/OR flag behaviour here is a teaching choice, not a universal ISA rule.

## Further reading
- [MIT — Arithmetic structures](https://web.mit.edu/6.111/www/f2017/handouts/L08.pdf)
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Adder (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Adder_(electronics))
- [Carry-lookahead adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-lookahead_adder)
- [Kogge–Stone adder — Wikipedia](https://en.wikipedia.org/wiki/Kogge%E2%80%93Stone_adder)
- [Arithmetic logic unit — Wikipedia](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Multiplexer — Wikipedia](https://en.wikipedia.org/wiki/Multiplexer)
- [Carry-save adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-save_adder)
