---
id: comp-dispatch-specialisation
title: "Dispatch strategies and adaptive CPython bytecode"
level: advanced
minutes: 3
sourceLesson: comp-vms-jit
summary: "Computed goto and tail-calling handlers change dispatch; their benefit is workload dependent."
---

## Opcode dispatch: switch, computed goto, tail calls

In a C VM, the loop is usually a big `switch (opcode)`. The compiler may implement this with a shared indirect jump, a decision tree or other code. Opcode dispatch cost depends on the resulting code and branch predictor. **Computed goto** (a GCC/Clang extension) puts a separate `goto *labels[next_op]` at the end of each handler. Separate per-handler jumps can help a predictor exploit patterns like "after `LOAD` usually comes `MUL`". CPython uses computed gotos when the C compiler supports them. Python 3.14 adds an optional build where each opcode handler is a small C function that **tail-calls** the next; with Clang 19 or newer, the Python 3.14 release notes report a preliminary 3–5% geometric-mean improvement on pyperformance over the Clang-19 baseline, depending on platform and architecture.

## Stack versus register VMs

| VM | Model | Example |
|---|---|---|
| CPython, JVM | Stack | `LOAD a; LOAD b; ADD` |
| .NET CIL, Wasm | Stack | same idea |
| Lua 5, Dalvik | Register | `ADD r2, r0, r1` |

Register VMs have "virtual registers", which are slots in the current frame. Register instructions often encode more operands, while a given computation may need fewer dispatches. Instruction widths, bytecode size and speed depend on the encoding and program. The Lua 5.0 designers reported that switching from a stack VM to a register VM made Lua noticeably faster. Stack bytecode is more compact and simpler to generate, which suits code shipped over a network, like JVM class files and WebAssembly.

## What CPython actually does

CPython is a stack VM, and you can see its bytecode with `dis`. Since 3.11 (PEP 659) it is also a **specialising adaptive interpreter**: after an instruction has run a few times, CPython rewrites it in place into a version specialised for the types it saw. On CPython 3.14:

```python
def f(a, b):
    return a * b + 1
```

```
first run      BINARY_OP 5 (*)
after ints     BINARY_OP_MULTIPLY_INT
after floats   BINARY_OP_MULTIPLY_FLOAT
```

The middle line comes from calling `f(3, 4)` 1,000 times and then `dis.dis(f, adaptive=True)`. The specialised instruction skips the generic "what types are these?" lookup and goes straight to integer multiplication, after a cheap check that both operands really are `int`s. When that check fails, as it did once we called `f(3.0, 4.0)` many times, the instruction **de-specialises** and later re-specialises for floats. That is speculation and deoptimisation, in miniature, without leaving the interpreter.

## Key takeaways
- Computed goto and tail-calling handlers change dispatch; their benefit is workload dependent.
- CPython specialises selected bytecodes and can adapt when operand types change.

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
