---
id: comp-jit-tradeoffs
title: "Startup, code memory and JIT platform permissions"
level: advanced
minutes: 3
sourceLesson: comp-vms-jit
summary: "Choose startup or warmed-up benchmarking according to the workload you care about."
---

The earlier JIT units explained profiling and recovery. Deployment adds other constraints: time before the first result, compilation memory, generated-code memory and permission to create executable code. These costs are specific to a runtime, build, platform and workload rather than a universal ranking of language implementations.

## Trade-offs

| | AOT | JIT |
|---|---|---|
| Start-up | Avoids runtime compilation | May incur compilation/warm-up |
| Peak speed | Very good | Very good, uses profiles |
| Memory | Depends on artifact/runtime | Compiler and code cache add costs |
| Code memory | Usually writes code before execution | Must safely write generated code |

W^X ("write XOR execute") is a memory-protection policy: a page of memory may be writable or executable, but never both for that mapping at once. Implementations may use permission switching or controlled writable and executable aliases; the exact protection model is platform specific.

- **Warm-up.** Steady-state benchmarks separate warm-up from measurement; startup-focused benchmarks must include it. A short-lived command-line tool may finish before any code gets hot, which is why Java added ahead-of-time options and class-data sharing.
- **Security.** JIT code must be written and then executed. Platforms may enforce W^X policies that separate writing from executing generated code. JITs use platform-specific mechanisms; Apple provides MAP_JIT and associated permissions/protection APIs. JIT bugs are also a rich source of browser exploits, which is why browsers offer JIT-less modes.
- **Platform rules.** JIT availability on iOS depends on entitlements and distribution conditions. Apple permits authorized alternative browser engines for EU users to access JIT facilities; do not assume every third-party app has that permission.

## Pitfalls

- **"Interpreted languages are slow."** Performance depends on language semantics, implementation and workload. Compare complete implementations on the workload you actually need.
- **Shape variation can affect inline caches.** Different construction paths can produce different shapes. A small number may use a polymorphic inline cache; seeing two shapes alone does not imply megamorphism.
- **Measuring cold code.** A single short measurement may emphasize startup rather than steady-state optimized execution; both can be legitimate goals.
- **Unbounded compilation.** A JIT that compiles everything eagerly wastes memory and start-up time on code that runs once.

## Key takeaways
- Choose startup or warmed-up benchmarking according to the workload you care about.
- JIT code writing and execution must obey platform permissions and memory-protection rules.

## Further reading
- [A virtual machine — Crafting Interpreters](https://craftinginterpreters.com/a-virtual-machine.html)
- [Adaptive bytecode specialisation — PEP 659](https://peps.python.org/pep-0659/)
- [CPython copy-and-patch JIT — PEP 744](https://peps.python.org/pep-0744/)
- [CPython 3.14 release notes](https://docs.python.org/3/whatsnew/3.14.html)
- [Maglev’s compiler design — V8](https://v8.dev/blog/maglev)
- [Sparkplug baseline compiler — V8](https://v8.dev/blog/sparkplug)
- [Fast properties and inline caches — V8](https://v8.dev/blog/fast-properties)
- [The implementation of Lua 5.0](https://www.lua.org/doc/jucs05.pdf)
- [HotSpot implementation glossary](https://openjdk.org/groups/hotspot/docs/HotSpotGlossary.html)
- [PyPy architecture and meta-tracing](https://doc.pypy.org/architecture.html)
- [Apple browser-engine distribution requirements](https://developer.apple.com/support/alternative-browser-engines/)
