from pathlib import Path
import json
p=Path('content/architecture/03-isa/isa-stored-program.md');s=p.read_text()
a=s.index('The first electronic'); b=s.index('## The parts')
s=s[:a]+'''A **stored-program computer** fetches instructions encoded as numbers from memory. Changing those stored instructions changes its program. This does not require instructions and data to share a memory: both Harvard and von Neumann designs can be stored-program computers.

The **von Neumann model** uses a shared memory for code and data, making it possible for a program to produce or modify instructions using memory operations. The Manchester Baby successfully ran its first program on 21 June 1948, an early demonstration of electronic stored-program computing with read/write memory. Historical claims about a single inventor or an unqualified “first computer” are omitted here because they depend on which features count.

'''+s[b:]
s=s.replace('A von Neumann machine has a few essential parts:', 'This simplified von Neumann machine has a few essential parts:')
s=s.replace('Code and data sit side by side, and nothing in the bits says which is which.', 'Code and data sit side by side. The bits alone do not identify their intended use; real machines can also enforce page permissions such as execute-disable.')
s=s.replace('The **program counter** (PC) holds the address of the next instruction. On x86-64 it is called `RIP` (instruction pointer).', 'The **program counter** (PC) identifies an instruction address. In our toy cycle it points at the next instruction to fetch; architectural definitions vary. x86-64 calls its instruction pointer `RIP`.')
s=s.replace('The **instruction register** (IR) holds the instruction currently being worked on.', 'The conceptual **instruction register** (IR) holds the fetched instruction. A real pipelined core can have many instructions in flight.')
s=s.replace('x86-64 has 16 general-purpose integer registers; ARM64 has 31.', 'Baseline x86-64 has 16 general-purpose integer registers (Intel APX extends this to 32); AArch64 has 31 numbered general-purpose registers, with separate rules for the stack pointer and zero register.')
s=s.replace('The CPU does one thing forever:', 'Ignoring interrupts, exceptions and halted states, the toy machine repeats this cycle:')
s=s.replace('A function call saves the current PC somewhere and then jumps.', 'A function call records a return address, normally the instruction after the call, and transfers control to the callee. The exact mechanism depends on the ISA.')
a=s.index('Between instructions,');b=s.index('The clearest way',a)
s=s[:a]+'''Real CPUs also accept **interrupts**, such as a hardware timer event. When an interrupt is eligible under the architecture’s masking and priority rules, the CPU preserves enough state to resume and transfers control to a handler. A preemptive OS can use timer interrupts to regain control from user code that never yields.

## A small computer in Python

'''+s[b:]
s=s.replace('elif op == 5 and acc == 0:\n            pc = a','elif op == 5:\n            if acc == 0:\n                pc = a')
s=s.replace('elif op == 6:\n            pc = a','elif op == 6:\n            pc = a\n        else:\n            raise ValueError("unknown opcode")')
s=s.replace('Here is a program that adds', 'This teaching interpreter assumes integer cells and valid in-range addresses. Unknown opcodes raise an error; invalid accesses can raise Python exceptions. There is no step limit, so a looping program can run forever.\n\nHere is a program, for a nonnegative integer `n`, that adds')
s=s.replace('A binary compiled for the ISA runs on all of them; only the speed differs.', 'Binary compatibility also requires the instructions and extensions actually used, a compatible OS and ABI, executable format, and required libraries. An ARM64 macOS binary does not therefore run unchanged on an ARM64 Linux server.')
s=s.replace('It also means a modern CPU only has to look *as if* it executes one instruction at a time, in order. Inside, it overlaps dozens of instructions (pipelining), runs several per cycle (superscalar), and executes them out of order.', 'A CPU must preserve the ISA’s observable behaviour. Many implementations overlap instructions (pipelining), issue several per cycle (superscalar), and execute out of order. This does not promise sequential consistency between threads: the ISA’s memory-ordering rules still apply.')
s=s.replace('CPUs have long been far faster than memory, so most of a modern chip\'s area goes on caches to hide it.', 'Main-memory latency and bandwidth can limit execution; caches and prefetching can reduce that pressure. A universal claim about the fraction of chip area occupied by caches is omitted because it requires measurements of a specified chip.')
s=s.replace('Modern general-purpose CPUs are a hybrid, often called **modified Harvard**:', 'A common modern general-purpose arrangement is called **modified Harvard** (the exact cache hierarchy is chip-specific):')
s=s.replace('which keeps the stored-program model.', 'while instructions and data can use separate cache paths.')
a=s.index('- **Write xor execute');b=s.index('## Pitfalls',a)
s=s[:a]+'''- **Write xor execute (W^X).** A common policy prohibits a virtual mapping from being writable and executable simultaneously. JITs can switch permissions; simultaneous RW and RX aliases satisfy that mapping-level rule but do not prevent writable access to executable backing memory. Stronger policies may forbid those aliases. Apple’s JIT APIs use `MAP_JIT`, thread-specific write protection and, depending on the configuration, entitlements and callback allowlists; follow the current platform documentation.
- **Instruction visibility.** Generated code needs the platform’s cache-maintenance and instruction-synchronization protocol. On AArch64, use a supported cache-clear API; required maintenance depends on CPU features. Publishing or replacing code across threads also requires coordination with executing threads. x86 hardware coherence does not make arbitrary concurrent code modification safe. On Apple platforms, follow Apple’s instruction-cache invalidation guidance.

### Emulators and interpreters

The Python `run` loop resembles a simple instruction interpreter: fetch an opcode, dispatch, repeat. Faster implementations can differ substantially. For example, QEMU’s TCG backend translates blocks of guest instructions into host code instead of interpreting every guest instruction through this Python-style loop.

'''+s[b:]
s=s.replace('It does not. Bytes are code only when PC points at them. Disassembling from the wrong starting byte on x86 gives plausible-looking nonsense.', 'Bytes do not identify their intended high-level use, although execute permissions can restrict which pages may supply instructions. Starting inside an x86 instruction can produce a different decoding or an invalid opcode.')
s=s.replace('Some instructions take dozens of cycles (division, a cache miss can cost hundreds), and a wide core can retire four or more simple ones per cycle.', 'Instruction latency and throughput vary by instruction, dependencies, memory behaviour and microarchitecture. Multiple instructions can be in progress simultaneously.')
s=s.replace('Two chips with the same ISA can differ tenfold in speed and power.', 'Chips implementing the same ISA can have different performance and power characteristics; measure the relevant workload.')
s=s.replace('A stored-program computer keeps instructions in the same memory as data, as numbers; the PC decides which bytes get executed.', 'A stored-program computer fetches instructions encoded in memory; sharing that memory with data is a further design choice.')
s=s.replace('The CPU loops: fetch the instruction at PC, advance PC, decode, execute. Jumps simply write PC.', 'The toy cycle is fetch, advance, decode, execute. Real CPUs also handle exceptions, interrupts and overlapping execution.')
s += '''\n### Primary references for this review\n- [Manchester’s account of the Baby](https://curation.cs.manchester.ac.uk/computer50/www.computer50.org/mark1/new.baby.html)\n- [Intel APX register extension](https://www.intel.com/content/www/us/en/developer/articles/technical/advanced-performance-extensions-apx.html)\n- [Arm: implementing cache maintenance](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/caches-self-modifying-code-implementing-clear-cache)\n- [Arm: code updates across threads](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/caches-self-modifying-code-working-with-threads)\n- [Apple: porting JIT compilers](https://developer.apple.com/documentation/apple-silicon/porting-just-in-time-compilers-to-apple-silicon)\n- [QEMU translation internals](https://www.qemu.org/docs/master/devel/tcg.html)\n'''
p.write_text(s)
p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[0]['options'][1]['text']='Instructions are encoded in memory and fetched from there for execution'
q[0]['options'][1]['explanation']='Correct. Program instructions live in memory. Sharing the same store with data is an additional property of a von Neumann design.'
q[0]['options'][3]['explanation']='Disk storage is not the defining feature. Ordinary CPUs fetch instructions through their memory system; a loader or demand paging can bring executable bytes from a file into memory.'
q[0]['workedExample']='Stored-program means instructions are encoded in memory for the machine to fetch. A Harvard design can also be stored-program despite separating instruction and data memories. The shared code/data memory in the lesson is a von Neumann design choice.'
q[1]['prompt']='In the lesson’s simple fetch–decode–execute model, what does JMP 40 do?'
q[1]['options'][3]['explanation']='A jump changes the next instruction address. Real implementations can incur fetch delays, but pausing until a location is ready is not the meaning of JMP.'
q[2]['prompt']+=' Assume both machines support the binary’s required extensions and have compatible Linux ABIs and libraries.'
q[2]['options'][0]['explanation']='Correct under the stated compatibility assumptions: the processors implement the instruction semantics the program requires, with different internal implementations.'
q[2]['options'][1]['explanation']='Ordinary native loading does not translate these instructions. Dynamic translation can be used in other contexts, including emulating a CPU with the same ISA.'
q[2]['options'][2]['explanation']='Sharing an ISA does not mean sharing an internal core design; Zen and Core are different microarchitectures.'
q[2]['workedExample']='The binary needs compatible instruction semantics plus its OS ABI, loader and libraries. Given those assumptions, different pipeline and cache designs can execute it. ISA compatibility does not promise identical timings, CPU identification values or every nondeterministic result.'
q[5]['options'][1]['explanation']='Code and data can inhabit the same process virtual address space, although mappings have different permissions. Split caches do not require separate programmer-visible spaces.'
q[5]['options'][3]['explanation']='Modern cores overlap instructions while preserving architectural behaviour. Their memory model still determines what concurrent threads can observe.'
q[5]['workedExample']='For the typical arrangement described: separate L1 instruction/data caches and one process address space are true. Separate code/data DRAM and strictly one-at-a-time execution are false. Cache sizes and lower cache arrangements vary by chip.'
q[6]['prompt']='A JIT writes valid native ARM64 instructions to a buffer with appropriate executable permissions. On one ARM64 server it sometimes executes instructions previously held in that buffer. Which missing step best explains this?'
q[6]['options'][0]['explanation']='Byte order must match the target, but the prompt supplies valid native instructions. Stale instructions point instead to instruction visibility.'
q[6]['options'][2]['text']='The JIT omitted the required instruction-cache maintenance and synchronization before executing updated code'
q[6]['options'][2]['explanation']='Correct. Use the platform’s cache-clear API and code-publication protocol. Which explicit maintenance operations are needed depends on the CPU; sharing code across threads requires additional coordination.'
q[6]['workedExample']='Stores and instruction fetches can see different cached contents. A platform cache-clear API arranges the required visibility and instruction synchronization. For multiple threads, coordinate publication and execution as well. Neither a blanket “all ARM caches are incoherent” nor “x86 code updates always work” is a reliable rule.'
q[7]['options'][0]['explanation']='Native preemption does not depend on compiler-inserted calls. Some runtimes insert checks for their own scheduling, garbage collection or other purposes.'
q[7]['options'][1]['explanation']='Correct when the timer interrupt is enabled and eligible. Interrupt handling transfers control to the kernel, which can invoke its scheduler.'
q[7]['options'][2]['explanation']='A correctly configured preemptive OS can regain control using interrupts without the program voluntarily yielding.'
q[7]['options'][3]['explanation']='An ordinary branch to itself does not automatically fault. The hardware timer supplies the preemption event; general-purpose loop detection is not required.'
q[7]['workedExample']='The loop never voluntarily enters the kernel. An enabled hardware timer interrupt becomes eligible under the CPU’s masking and priority rules. Interrupt entry preserves a return point and transfers control to a handler; the scheduler can then arrange to run another task. This is a conceptual sequence, not a promise of zero interrupt latency.'
q[8]['prompt']='For this question, the policy is specifically: no single virtual mapping may be writable and executable at once. Which designs meet that mapping-level W^X rule? Select all that apply.'
q[8]['options'][1]['explanation']='RWX violates the specified policy. It enables execution of bytes written there, although exploiting a bug also requires a way to redirect control flow.'
q[8]['options'][2]['explanation']='Each mapping meets this narrow rule, but the writable alias can still change executable backing memory. A stronger policy may prohibit such simultaneous aliases.'
q[8]['options'][3]['explanation']='RWX violates the specified policy. Combining writable executable memory with a suitable write and control-flow primitive can enable code injection.'
q[8]['workedExample']='RW then RX complies with the stated mapping-level rule; RWX mappings do not. Separate RW and RX aliases also meet this narrow rule, but are weaker than a policy forbidding simultaneous writable access to executable backing memory. Hiding an alias is not a security guarantee.'
q[9]['prompt']='In a hypothetical model a 3 GHz core needs one 4-byte instruction and 8 data bytes from DRAM per cycle, with no caches or reuse. Assume one 64-bit DDR4-3200 data channel has a theoretical peak of 25.6 GB/s and assume 80 ns access latency. Which statement is correct?'
q[9]['options'][1]['text']='Demand is 36 GB/s, exceeding the channel peak; 80 ns is 240 cycles, which matters for dependent accesses'
q[9]['options'][1]['explanation']='Correct: 12 bytes × 3 billion cycles/s = 36 GB/s; 80 ns × 3 cycles/ns = 240 cycles. Peak bandwidth also excludes real protocol and access-pattern losses.'
q[9]['options'][2]['explanation']='A second channel can increase peak bandwidth, but does not by itself eliminate access latency, dependencies or protocol overhead.'
q[9]['options'][3]['explanation']='Independent requests can overlap, but dependency chains can expose latency. The bandwidth shortfall already prevents the stated sustained demand on one channel.'
q[9]['workedExample']='12 B/cycle × 3 × 10^9 cycles/s = 36 GB/s. A 64-bit channel transferring 3.2 × 10^9 times/s has a theoretical data peak of 25.6 GB/s. The assumed 80 ns latency equals 240 cycles. Overlap can hide some latency, but dependencies and finite bandwidth still constrain throughput; it is not true that every instruction necessarily waits a full DRAM latency.'
q[10]['prompt']='A disassembler starts inside a multi-byte x86-64 instruction, without knowing the intended instruction boundaries. What can happen?'
q[10]['options'][0]['explanation']='x86 does not require a fixed instruction alignment. Decoding can start at any byte, though some resulting encodings are invalid.'
q[10]['options'][1]['explanation']='Starting within a variable-length instruction can reinterpret its remaining bytes; this is not a guaranteed shifted copy of the original stream.'
q[10]['options'][2]['text']='It can decode different, plausible-looking instructions, or encounter an invalid encoding'
q[10]['options'][2]['explanation']='Correct. The starting offset affects decoding. The new stream can later meet the original instruction boundaries again.'
q[10]['options'][3]['explanation']='Instructions are not padded to a fixed length. NOPs can be placed for alignment or patching, but an arbitrary interior byte need not decode as NOP.'
q[10]['workedExample']='x86 instructions have variable length, up to 15 bytes. Starting inside one can reinterpret its tail as a new opcode, producing different instructions or an invalid encoding. Decoding may later resynchronize. Starting one byte after a function entry is not necessarily wrong: its first instruction could be one byte long.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print('Applied stored-program lesson and 11-question review corrections')
