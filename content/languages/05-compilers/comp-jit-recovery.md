---
id: comp-jit-recovery
title: "Speculation, OSR and tracing JITs"
level: advanced
minutes: 3
sourceLesson: comp-vms-jit
summary: "Guards protect speculative assumptions; deoptimisation restores a less specialised execution state."
---

A profile predicts a common case; it does not make that case universally true. Native optimisers therefore need a safe path when observations change. The discussion below separates recovering from a failed assumption, switching a currently running frame, and choosing a trace as the compilation unit.

## 3. Speculation and deoptimisation

The optimiser uses profiles for **speculative optimisation**: "this `+` has only ever seen small integers, so emit a single machine `add`, plus a guard." For example, V8 can **deoptimise** when a guard fails (an overflow, or a string): it reconstructs interpreter-compatible frames from optimised machine state and continues in a less specialised execution tier. Exact destinations depend on the runtime and its policy. This lets the JIT generate specialised code for a guarded common case while preserving the language’s general behaviour. Repeated deoptimizations can change optimization policy; thresholds and recovery behavior depend on the engine.

## 4. On-stack replacement

A function called once but containing a loop of a billion iterations may never reach a call-count compilation threshold. **On-stack replacement** (OSR) switches a *running* frame from interpreter to optimised code in the middle of the loop. Both V8 and HotSpot do this.

## Tracing JITs

**PyPy** and **LuaJIT** compile *traces* rather than functions: they record the exact path taken through a hot loop, including across calls, and compile that straight-line path with guards wherever execution could leave that path. This can suit repetitive loop paths; performance still depends on guards, exits and the workload. PyPy is a *meta-tracing* JIT: it traces the interpreter (written in RPython) running your program, allowing a reusable JIT framework rather than a separately hand-written Python-specific optimizing JIT; PyPy still has Python parsing and bytecode compilation. CPython's own experimental JIT (PEP 744, in 3.13) uses **copy-and-patch**: it stitches together precompiled machine-code templates for each micro-op, which is cheap to build and maintain. The 3.14 macOS and Windows installers include it, off by default (`PYTHON_JIT=1` enables it), and the docs describe its effect as anywhere from about 10% slower to 20% faster.

## Key takeaways
- Guards protect speculative assumptions; deoptimisation restores a less specialised execution state.
- OSR can optimise a currently running hot loop; tracing records paths instead of whole functions.

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
