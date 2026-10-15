---
id: comp-toy-jit
title: "A source-generating JIT and its break-even cost"
level: advanced
minutes: 4
sourceLesson: comp-vms-jit
summary: "The toy JIT emits Python source and delegates compilation to CPython, rather than emitting native code."
---

## A toy JIT for Calc

A **just-in-time (JIT) compiler** generates code at runtime for a program it is already running. Production JITs such as V8 and HotSpot emit native machine code; just-in-time describes compilation timing rather than requiring one particular target. We can get the flavour with less risk by emitting *Python source* and letting CPython's compiler turn it into bytecode:

```python
def py(node, slot):
    match node:
        case Num(value):
            return repr(value)
        case Var():
            # Slots keep shadowed source
            # names apart.
            return f"s{slot[id(node)]}"
        case Neg(e):
            return f"(-{py(e, slot)})"
        case BinOp(op, l, r):
            a, b = py(l, slot), py(r, slot)
            if op == "^":
                return f"power({a}, {b})"
            # Calc slash means Python floor
            # division.
            if op == "/":
                op = "//"
            return f"({a} {op} {b})"
        case Let(_, value, body):
            s = f"s{slot[id(node)]}"
            v = py(value, slot)
            b = py(body, slot)
            # Evaluate binding first; return
            # body.
            return f"({s} := {v}, {b})[1]"

def jit(tree):
    chk = check(tree)
    if chk.errors:
        raise SyntaxError(chk.errors[0])
    src = "lambda: " + py(tree, chk.slot)
    code = compile(src, "<calc>", "eval")
    # Return a callable; execution happens
    # later.
    return eval(code, {"power": power})
```

`let` becomes an assignment expression inside a tuple, using the checker's slot numbers as variable names (`s0`, `s1`) so shadowed names never collide. `jit(parse("let x = 5 in x * x - 1"))` builds `lambda: (s0 := 5, ((s0 * s0) - 1))[1]`, and calling it returns 24. When comparing execution paths, account for check rejecting literal-zero division before either bytecode or JIT execution.

Benchmark the complete implementations on a stated workload and runtime before claiming a speedup. Flattening and slot resolution can reduce interpreter work; the toy JIT hands execution over to CPython bytecode, removing our Python-level dispatch loop. CPython instructions here are bytecode instructions, not native CPU instructions.
The cost: compiling through jit can cost more than interpreting a short program once, because it invokes CPython's whole compiler. It pays off only if per-run savings repay that cost; the number of runs depends on both costs. That trade-off, compile time against run time, is the central problem of every JIT, and it can be written down:

```formula
n_even = C / (t_i − t_c)
where
n_even: the break-even number of runs: after this many, compiling has paid for itself
C: the one-off cost of compiling, in microseconds (µs)
t_i: the time for one interpreted run, in µs
t_c: the time for one run of the compiled code, in µs
µs: microseconds, millionths of a second
In words: divide the one-off compile cost by the time each compiled run saves; run the code more often than that and compiling wins.
```

For illustration only (these are made-up numbers, not measurements of Calc): if compiling costs 900 µs, an interpreted run takes 5 µs and a compiled run 0.5 µs, each run saves 4.5 µs and compiling pays for itself after 900 / 4.5 = 200 runs. This break-even formula requires compiled execution to be faster than interpreted execution and a positive compile cost. At an exact integer break-even the costs tie; strictly fewer total microseconds needs a larger run count. The model assumes every run saves the same amount and ignores memory use; real JITs estimate it with counters rather than computing it exactly.

## Key takeaways
- The toy JIT emits Python source and delegates compilation to CPython, rather than emitting native code.
- Use unique slots for shadowed bindings and compare compile cost against positive per-run savings.

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
