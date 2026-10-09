---
id: isa-stored-program
title: The stored-program computer and fetch–decode–execute
level: basic
minutes: 11
summary: Why programs live in memory as numbers, what the program counter does, how the fetch–decode–execute loop works, and what an instruction set architecture actually promises.
---

A **stored-program computer** fetches instructions encoded as numbers from memory. Changing those stored instructions changes its program. This does not require instructions and data to share a memory: both Harvard and von Neumann designs can be stored-program computers.

The **von Neumann model** uses a shared memory for code and data, making it possible for a program to produce or modify instructions using memory operations. The Manchester Baby successfully ran its first program on 21 June 1948, an early demonstration of electronic stored-program computing with read/write memory. Historical claims about a single inventor or an unqualified “first computer” are omitted here because they depend on which features count.

## The parts of the machine

This simplified von Neumann machine has a few key parts:

```
 +-----------------  CPU  ----------------+
 |  PC   (address of next instruction)    |
 |  IR   (instruction being executed)     |
 |  registers r0..rN   ALU   control unit |
 +-------------------+--------------------+
                     | address / data bus
 +-------------------+--------------------+
 | memory: one array of numbered cells    |
 |  [ code ... ][ data ... ][ stack ... ] |
 +----------------------------------------+
```

- **Memory** is one big array of numbered cells. Code and data sit side by side. The bits alone do not identify their intended use; real machines can also enforce page permissions such as execute-disable.
- The **program counter** (PC) identifies an instruction address. In our toy cycle it points at the next instruction to fetch; architectural definitions vary. x86-64 calls its instruction pointer `RIP`.
- The conceptual **instruction register** (IR) holds the fetched instruction. A real pipelined core can have many instructions in flight.
- **Registers** are a small number of very fast storage slots inside the CPU. Baseline x86-64 has 16 general-purpose integer registers (Intel APX extends this to 32); AArch64 has 31 numbered general-purpose registers, with separate rules for the stack pointer and zero register.
- The **ALU** (arithmetic logic unit) does the adding, comparing and bit-twiddling.
- The **control unit** decodes each instruction and drives everything else.

## The fetch–decode–execute cycle

Ignoring interrupts, exceptions and halted states, the toy machine repeats this cycle:

1. **Fetch.** Read the instruction at address PC from memory into IR.
2. **Advance.** Move PC on to the next instruction, which starts straight after the one just fetched:

```formula
PC_next = PC + L
where
PC_next: the new value of the program counter: the address of the next instruction to fetch
PC: the program counter: the address of the instruction that was just fetched
L: the length of that instruction: always 1 memory cell in the toy machine below, always 4 bytes on ARM64, anywhere from 1 to 15 bytes on x86-64
In words: the next instruction begins right after the end of the current one, unless the current instruction is a jump that later overwrites PC.
```

3. **Decode.** Work out what the bits mean: which operation, which registers, which memory address, any constant.
4. **Execute.** Do it: an ALU operation, a memory read or write, or a change to PC (a jump).
5. Repeat.

Jumps and branches are just instructions that write a new value into PC. A loop is a branch back to an earlier address. A function call records a return address, normally the instruction after the call, and transfers control to the callee. The exact mechanism depends on the ISA.

Real CPUs also accept **interrupts**, such as a hardware timer event. When an interrupt is eligible under the architecture’s masking and priority rules, the CPU preserves enough state to resume and transfers control to a handler. A preemptive OS can use timer interrupts to regain control from user code that never yields.

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
            mem[a] = acc
        elif op == 5:
            if acc == 0:
                pc = a
        elif op == 6:
            pc = a
        else:
            raise ValueError("bad opcode")
```

This teaching interpreter assumes integer cells and valid in-range addresses. Unknown opcodes raise an error; invalid accesses can raise Python exceptions. There is no step limit, so a looping program can run forever.

Here is a program that adds up every whole number from a starting value down to 1:

```formula
total = n + (n − 1) + … + 1
total = n × (n + 1) / 2
total = 3 × 4 / 2 = 6
where
total: the sum the program leaves in memory cell 21
n: the starting value, a whole number 0 or more, stored in cell 20 (3 in the run below)
…: and so on: every whole number in between is included
In words: add n, then one less, then one less again, all the way down to 1; the shortcut n × (n + 1) / 2 gives the same answer, so starting from 3 the program should end with 6.
```

The code is at addresses 0 to 8, `n` lives at 20, the running total at 21 and the constant 1 at 22:

```
addr  value  meaning
 0     120   LOAD  20     acc = n
 1     508   JZ    8      if n == 0: halt
 2     221   ADD   21     acc = n + total
 3     421   STORE 21     total = acc
 4     120   LOAD  20
 5     322   SUB   22     acc = n - 1
 6     420   STORE 20     n = acc
 7     600   JMP   0      loop
 8     000   HALT
```

```python
prog = [120, 508, 221, 421,
        120, 322, 420, 600,
        0]
mem = prog + [0] * 11 + [3, 0, 1]
run(mem)
print(mem[21])   # 6  (3 + 2 + 1)
```

Notice what is going on. The program is a list of integers in the same `mem` list as the data. `run` cannot tell `120` the instruction from `120` the number; it only treats a cell as an instruction because PC points at it. With `n = 3`, the loop body (8 instructions) runs three times, then LOAD, JZ and HALT run once more as the program stops:

```formula
F = 8 × n + 3
F = 8 × 3 + 3 = 27
where
F: the total number of instructions fetched before the machine halts
n: the starting value in cell 20 (here 3)
8: the loop body, addresses 0 to 7, which runs once for each value n, n − 1, …, 1
3: the final LOAD, JZ (now taken, because acc is 0) and HALT
In words: every pass round the loop costs 8 fetches, and stopping costs 3 more, so starting from 3 the machine makes 27 fetches.
```

> [!warning] Code is data, both ways
> If the program did `STORE 7`, it would overwrite its own `JMP` instruction with whatever number was in `acc`. That is **self-modifying code**. It is also how many attacks work: trick a program into writing attacker-chosen bytes into memory, then trick it into jumping there.

## What an ISA promises

The **instruction set architecture** (ISA) is the contract between software and hardware. It specifies:

- the instructions and how each is encoded in bits,
- the registers and their sizes,
- how memory is addressed (byte addressing, alignment rules, endianness),
- what happens on errors, interrupts and system calls,
- the privilege levels (user mode vs kernel mode).

The ISA deliberately does *not* say how the chip is built. That is the **microarchitecture**. AMD Zen and Intel Core designs both implement x86-64 but are very different inside. Apple's M-series and AWS Graviton chips both implement ARM64. Binary compatibility also requires the instructions and extensions actually used, a compatible OS and ABI, executable format, and required libraries. An ARM64 macOS binary does not therefore run unchanged on an ARM64 Linux server.

This separation is why your old programs still run on new hardware. A CPU must preserve the ISA’s observable behaviour. Many implementations overlap instructions (pipelining), issue several per cycle (superscalar), and execute out of order. This does not promise sequential consistency between threads: the ISA’s memory-ordering rules still apply. The next module covers how.

## Von Neumann, Harvard and the bottleneck

Because code and data share one memory and one path to the CPU, fetching instructions and loading data compete for the same memory bus. John Backus called this the **von Neumann bottleneck** in 1977. Main-memory latency and bandwidth can limit execution; caches and prefetching can reduce that pressure. A universal claim about the fraction of chip area occupied by caches is omitted because it requires measurements of a specified chip.

The alternative is the **Harvard architecture**: separate memories (and buses) for instructions and data. Many microcontrollers and DSPs work this way; on an AVR (the chip in classic Arduinos) the program sits in flash memory and data in SRAM.

A common modern general-purpose arrangement is called **modified Harvard** (the exact cache hierarchy is chip-specific):

| Level | Code and data |
|---|---|
| L1 cache | split: L1i and L1d |
| L2, L3 | unified |
| Main memory | one address space |

The split L1 lets the CPU fetch instructions and load data in the same cycle. Programmers still see one address space, while instructions and data can use separate cache paths.

## Where this matters in practice

### JIT compilers

A JavaScript engine like V8 or the JVM's HotSpot writes machine code into memory at run time and then jumps to it. That is the stored-program idea at full power. Two practical wrinkles:

- **Write xor execute (W^X).** A common policy prohibits a virtual mapping from being writable and executable simultaneously. JITs can switch permissions; simultaneous RW and RX aliases satisfy that mapping-level rule but do not prevent writable access to executable backing memory. Stronger policies may forbid those aliases. Apple’s JIT APIs use `MAP_JIT`, thread-specific write protection and, depending on the configuration, entitlements and callback allowlists; follow the current platform documentation.
- **Instruction visibility.** Generated code needs the platform’s cache-maintenance and instruction-synchronization protocol. On AArch64, use a supported cache-clear API; required maintenance depends on CPU features. Publishing or replacing code across threads also requires coordination with executing threads. x86 hardware coherence does not make arbitrary concurrent code modification safe. On Apple platforms, follow Apple’s instruction-cache invalidation guidance.

### Emulators and interpreters

The Python `run` loop resembles a simple instruction interpreter: fetch an opcode, dispatch, repeat. Faster implementations can differ substantially. For example, QEMU’s TCG backend translates blocks of guest instructions into host code instead of interpreting every guest instruction through this Python-style loop.

## Pitfalls and misconceptions

- **"The CPU knows what's code."** Bytes do not identify their intended high-level use, although execute permissions can restrict which pages may supply instructions. Starting inside an x86 instruction can produce a different decoding or an invalid opcode.
- **"One instruction per clock tick."** Not on a modern CPU. Instruction latency and throughput vary by instruction, dependencies, memory behaviour and microarchitecture. Multiple instructions can be in progress simultaneously.
- **"The ISA is the chip."** The ISA is an interface. Chips implementing the same ISA can have different performance and power characteristics; measure the relevant workload.

## Key takeaways
- A stored-program computer fetches instructions encoded in memory; sharing that memory with data is a further design choice.
- The toy cycle is fetch, advance, decode, execute. Real CPUs also handle exceptions, interrupts and overlapping execution.
- The ISA is the contract (instructions, registers, encoding, memory model); the microarchitecture is how a particular chip fulfils it.
- Shared code and data memory creates the von Neumann bottleneck; many modern general-purpose CPUs use split L1 caches (modified Harvard) and deeper cache hierarchies.
- Code-as-data makes possible JITs, loaders and emulators, and also code-injection attacks, which is why W^X exists.

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
