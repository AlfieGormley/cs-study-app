---
id: isa-machine-cycle
title: Memory, the program counter and the instruction cycle
level: basic
minutes: 4
sourceLesson: isa-stored-program
summary: Trace fetch, advance, decode and execute, and identify the machine’s parts.
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

Because x86 instructions have variable byte lengths, starting a disassembly inside one can reinterpret its remaining bytes as another instruction or encounter an invalid encoding. Byte addresses alone do not mark intended instruction boundaries.

Real CPUs also accept **interrupts**, such as a hardware timer event. When an interrupt is eligible under the architecture’s masking and priority rules, the CPU preserves enough state to resume and transfers control to a handler. A preemptive OS can use timer interrupts to regain control from user code that never yields.

## Key takeaways
- Stored instructions change a machine’s behaviour without rewiring it.
- Fetch advances the toy PC before execution; a jump can replace it.
- Timer interrupts let a preemptive OS regain control from a user loop.

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
