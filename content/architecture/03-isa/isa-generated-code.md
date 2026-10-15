---
id: isa-generated-code
title: JIT code, permissions and instruction visibility
level: basic
minutes: 3
sourceLesson: isa-stored-program
summary: Explain why generated machine code needs permission, cache and thread coordination.
---

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
- Generating bytes and executing them requires both permissions and instruction visibility.
- Mapping-level W^X can permit writable and executable aliases of the same backing memory.
- Cross-thread code publication needs the platform’s coordination protocol.

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
