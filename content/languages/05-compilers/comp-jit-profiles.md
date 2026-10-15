---
id: comp-jit-profiles
title: "Profiling tiers, object shapes and inline caches"
level: advanced
minutes: 3
sourceLesson: comp-vms-jit
summary: "Tiering spends greater compilation effort on frequently executed code."
---

The toy JIT already separated compile cost from execution cost. Production runtimes make that choice repeatedly using profiles, then specialise operations whose common cases they can guard. The tier names below describe V8’s published 2023 design, rather than promising that every build follows exactly the same path.

## How production JITs win

Native JITs can specialize using runtime observations in both static and dynamic languages. Ahead-of-time compilers can also use profile-guided optimization.

## 1. Profiling and tiers

For workloads with uneven execution frequency, runtimes can start cheaply and **tier up** only for hot code, using counters of calls and loop iterations.

```
V8 tiers documented in its 2023 overview
 source -> Ignition    interpreter
        -> Sparkplug   fast baseline JIT
        -> Maglev      mid-tier optimiser
        -> TurboFan    full optimiser

HotSpot (Java)
 bytecode -> interpreter    (tier 0)
          -> C1             (tiers 1-3)
          -> C2, optimising (tier 4)
```

**Sparkplug** (2021) translates bytecode straight to machine code with limited local optimization, removing dispatch overhead. **Maglev** (Chrome M117, 2023) is an SSA-based optimiser that, according to the V8 team, compiles roughly 10× slower than Sparkplug and 10× faster than TurboFan. HotSpot's C1 compiles quickly, and at tiers 2 and 3 also records profiles; C2 uses those profiles for aggressive optimisation. **Graal** is a JIT for the JVM written in Java that can replace C2.

## 2. Inline caches and hidden classes

In JavaScript, `p.x` could mean anything: `p` might have any set of properties. V8 gives objects with the same layout a shared **hidden class** (a "map" or "shape") that records where each property lives. Each `p.x` site then keeps an **inline cache**: "last time, `p` had shape S and `x` was at offset 12". Next time, one comparison of the shape replaces a dictionary lookup. A site that only ever sees one shape can use a **monomorphic inline cache**. A **polymorphic inline cache** can hold several cases; a site that sees many can become megamorphic, using more general lookup or stub-cache mechanisms whose cost depends on the engine and workload.

## Key takeaways
- Tiering spends greater compilation effort on frequently executed code.
- Property access sites can guard object layouts and reuse cached handlers.

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
