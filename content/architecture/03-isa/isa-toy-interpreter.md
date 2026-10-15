---
id: isa-toy-interpreter
title: Build a tiny instruction interpreter
level: basic
minutes: 3
sourceLesson: isa-stored-program
summary: Decode decimal instructions and follow the accumulator interpreter.
---

## A small computer in Python

The clearest way to understand the cycle is to build one. This toy machine has one register, an **accumulator** (`acc`), and memory cells holding integers. Each instruction is a single decimal number: the hundreds digit says which operation to do, and the last two digits give the memory address it works on.

```formula
ir = op × 100 + a
op = ⌊ir / 100⌋
a = ir mod 100
ir = 2 × 100 + 21 = 221
where
ir: the whole instruction as stored in one memory cell, a whole number from 0 to 699 in this machine
op: the opcode: a number from 0 to 6 that says which operation to do (see the table below)
a: the address operand: which memory cell, 0 to 99, the instruction reads, writes or jumps to
⌊ ⌋: floor: round down to a whole number, so ⌊221 / 100⌋ = 2
mod: modulo: the remainder after whole-number division, so 221 mod 100 = 21
100: the machine works in decimal and gives the address two digits (00 to 99), so multiplying the opcode by 100 shifts it past them
In words: the hundreds digit is the operation and the last two digits are the address, so 221 means "ADD the value in cell 21 to the accumulator".
```

Decoding is the reverse: Python's `divmod(ir, 100)` returns the floor and the remainder together. In the table, `m[a]` means the memory cell at address `a`, written in the same Python style as the code below:

| op | Meaning |
|---|---|
| 0 | HALT |
| 1 | `acc = m[a]` (LOAD) |
| 2 | `acc += m[a]` (ADD) |
| 3 | `acc -= m[a]` (SUB) |
| 4 | `m[a] = acc` (STORE) |
| 5 | `if acc == 0`: jump to `a` (JZ, jump if zero) |
| 6 | jump to `a` (JMP, jump) |

```python
def run(mem):
    pc, acc = 0, 0
    while True:
        ir = mem[pc]             # fetch
        # Default to the following cell.
        pc += 1
        op, a = divmod(ir, 100)  # decode
        if op == 0:              # execute
            return
        elif op == 1:
            acc = mem[a]
        elif op == 2:
            acc += mem[a]
        elif op == 3:
            acc -= mem[a]
        elif op == 4:
            # STORE can also overwrite code.
            mem[a] = acc
        elif op == 5:
            if acc == 0:
                # Branch replaces next PC.
                pc = a
        elif op == 6:
            pc = a
        else:
            raise ValueError("bad opcode")
```

This teaching interpreter assumes integer cells and valid in-range addresses. Unknown opcodes raise an error; invalid accesses can raise Python exceptions. There is no step limit, so a looping program can run forever.

## Key takeaways
- The opcode selects an operation and the address selects a memory cell.
- The accumulator collects arithmetic results.
- This teaching interpreter needs valid addresses and has no execution limit.

## Further reading
- [Von Neumann architecture — Wikipedia](https://en.wikipedia.org/wiki/Von_Neumann_architecture)
- [Instruction cycle — Wikipedia](https://en.wikipedia.org/wiki/Instruction_cycle)
- [Manchester Baby — Wikipedia](https://en.wikipedia.org/wiki/Manchester_Baby)
- [Modified Harvard architecture — Wikipedia](https://en.wikipedia.org/wiki/Modified_Harvard_architecture)
- [Little man computer — Wikipedia](https://en.wikipedia.org/wiki/Little_man_computer)
- [Self-modifying code — Wikipedia](https://en.wikipedia.org/wiki/Self-modifying_code)

### Primary references for this review
- [Manchester’s account of the Baby](https://curation.cs.manchester.ac.uk/computer50/www.computer50.org/mark1/new.baby.html)
- [Intel APX register extension](https://www.intel.com/content/www/us/en/developer/articles/technical/advanced-performance-extensions-apx.html)
- [Arm: implementing cache maintenance](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/caches-self-modifying-code-implementing-clear-cache)
- [Arm: code updates across threads](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/caches-self-modifying-code-working-with-threads)
- [Apple: porting JIT compilers](https://developer.apple.com/documentation/apple-silicon/porting-just-in-time-compilers-to-apple-silicon)
- [QEMU translation internals](https://www.qemu.org/docs/master/devel/tcg.html)
