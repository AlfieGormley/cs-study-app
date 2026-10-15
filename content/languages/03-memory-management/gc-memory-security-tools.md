---
id: gc-memory-security-tools
title: "Memory safety and diagnostic tools"
level: basic
minutes: 3
sourceLesson: gc-manual-memory
summary: "Reusing a freed object's slot can turn a dangling function pointer into attacker-controlled execution, subject to allocator behaviour and defences"
---

Memory corruption can cross a security boundary rather than merely crash. Tools help find exercised failures, while language and library contracts determine which operations are valid.

## Why these are security holes

These bugs are not just crashes. Consider a use-after-free:

1. The program frees an object that contains a function pointer, but keeps a dangling pointer to it.
2. An attacker triggers an allocation of the same size with contents they control (say, a string from a network packet). The allocator reuses the freed slot.
3. The program calls through its dangling pointer, reading the attacker's bytes as a function address.

If the slot is reused as assumed and control-flow defenses do not stop the call through the corrupted pointer, this can enable arbitrary code execution. Overflows and double frees can be turned into similar primitives.

Chromium’s published analysis reported roughly 70% of its high-severity security bugs as memory-safety issues, with use-after-free a major category. Treat this as the historical dataset described by the source, not a measured current rate across all products. A separate universal Microsoft annual percentage is omitted here because this review has not established its applicable period and dataset. This is why governments and large companies now push new code towards **memory-safe languages**: Java, Go, Python, C#, Swift and Rust.

> [!note] What "memory safe" means
> A memory-safe language guarantees you cannot read or write memory you do not own: no dangling pointers, no out-of-bounds access, no double free. GC languages achieve it by never freeing reachable memory and bounds-checking arrays. Rust combines static ownership checks with runtime checks such as bounds checks and library synchronization; unsafe code and native interfaces remain obligations in all these systems.

## Finding the bugs

- **AddressSanitizer** (`-fsanitize=address` in Clang and GCC) instruments relevant memory accesses in compiled code; uninstrumented code and other coverage limitations remain. It reports heap-use-after-free, buffer overflows and double frees with stack traces, with a typical slowdown of about 2x, so you can run your test suite under it.
- **Valgrind Memcheck** runs an unmodified binary on a simulated CPU. No recompilation, but programs run roughly 20 to 30 times slower.
- **LeakSanitizer** and Valgrind's `--leak-check=yes` report blocks still allocated at exit with no pointer to them.
- **Fuzzers** (libFuzzer, AFL) combined with sanitizers find the inputs that trigger these bugs.

These find bugs in the code paths you exercise. They cannot prove their absence. Sound safe-language implementations instead enforce a class of validity rules for supported operations; unsafe code, native interfaces and implementation bugs remain obligations.

## Key takeaways
- Reusing a freed object's slot can turn a dangling function pointer into attacker-controlled execution, subject to allocator behaviour and defences.
- AddressSanitizer instruments compiled code; Memcheck can analyse a supported existing binary without rebuilding it.
- Passing sanitizer tests proves neither complete path coverage nor absence of all memory errors; quoted slowdown factors are documentation estimates.

## Further reading
- [Memory safety — Chromium security](https://www.chromium.org/Home/chromium-security/memory-safety/)
- [AddressSanitizer — Clang documentation](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Valgrind quick start guide](https://valgrind.org/docs/manual/quick-start.html)
- [CWE-416: Use After Free — MITRE](https://cwe.mitre.org/data/definitions/416.html)
- [Resource acquisition is initialization — Wikipedia](https://en.wikipedia.org/wiki/Resource_acquisition_is_initialization)
- [Region-based memory management — Wikipedia](https://en.wikipedia.org/wiki/Region-based_memory_management)
- [Primary verification source 1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Primary verification source 5](https://eel.is/c++draft/unique.ptr.single)
