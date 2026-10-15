---
id: sys-finding-memory-bugs
title: Find bugs on the paths you exercise
level: intermediate
minutes: 3
sourceLesson: sys-memory-bugs
summary: Combine warnings, review, valid regression tests, malformed inputs and sanitizer-enabled fuzzing.
---

## Finding these bugs

You will not find memory bugs reliably by reading code alone. The standard toolkit:

| Tool | How it works | Cost |
|---|---|---|
| AddressSanitizer | Instrumented accesses checked against shadow memory | Depends on the program |
| Valgrind Memcheck | Dynamic binary instrumentation | Depends on the program |
| Fuzzing | Generates varied test inputs | Depends on budget |
| Static analysis | Reasons about code without running it | False positives |

**AddressSanitizer** (`-fsanitize=address` in Clang/GCC) uses poisoned regions and delayed reuse to detect many invalid accesses. It can report errors such as `heap-use-after-free`. What it catches depends on instrumentation, allocation layout and execution: it does not check every object boundary, every uninitialised value or every possible input. Intra-object overwrites and accesses after storage is reused may go undetected.

**Fuzzers** such as libFuzzer and AFL++ use feedback to explore inputs. Combining fuzzing with sanitizers helps expose faults on executed paths; neither proves absence of bugs. OSS-Fuzz provides continuous fuzzing for eligible open-source projects. Valid regression tests remain useful alongside malformed-input tests.

> [!tip] A C/C++ testing baseline
> Enable useful warnings, test with ASan/UBSan where supported, and fuzz untrusted-input parsers. Review unbounded string operations; the unbounded `gets()` function was removed from C11. A clean run under sanitizers is evidence about those executions, not proof of memory safety.

> [!note] Content omitted after review
> A universal current vulnerability percentage, a ranking of the most productive testing method, and fixed costs for sanitizers are omitted because this review did not establish representative measurements. Historical Chromium figures describe only its stated sample.

## Key takeaways
- Combine warnings, review, valid regression tests, malformed inputs and sanitizer-enabled fuzzing.
- AddressSanitizer detects many executed invalid accesses but does not check every boundary or every input.
- A clean run is evidence about that execution; it does not prove absence of memory bugs.

## Further reading
- [AddressSanitizer — Clang](https://clang.llvm.org/docs/AddressSanitizer.html)
- [UndefinedBehaviorSanitizer — Clang](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html)
- [OSS-Fuzz — Google](https://google.github.io/oss-fuzz/)
