---
id: comp-vms-jit
title: Interpreters, bytecode VMs and JIT compilers
level: advanced
minutes: 16
summary: How tree-walking interpreters execute programs, how bytecode VMs and dispatch loops work, and how JIT compilers such as V8, HotSpot and PyPy use profiling, inline caches, speculation and deoptimisation to make dynamic languages fast.
---

Lesson 6 ended with machine code. Many of the world's most used languages do not ship machine code at all. JavaScript arrives as source text; Java ships bytecode; Python compiles to bytecode on import. Each is *executed* by a runtime that decides, while the program runs, how much compiling is worth doing.

This lesson follows that spectrum with Calc: a tree-walking interpreter, a bytecode VM, and a tiny JIT. Then it looks at how production runtimes such as V8 and HotSpot go much further.

## The tree-walking interpreter

The simplest way to run a program is to walk its AST, as `evaluate` from lesson 4 does:

```python
def evaluate(node, env):
    match node:
        case Num(value):
            return value
        case Var(name):
            return env[name]
        case Neg(operand):
            return -evaluate(operand, env)
        case BinOp(op, left, right):
            a = evaluate(left, env)
            b = evaluate(right, env)
            return ARITH[op](a, b)
        case Let(name, value, body):
            v = evaluate(value, env)
            inner = {**env, name: v}
            return evaluate(body, inner)
```

It is easy to write and easy to debug, which is why *Crafting Interpreters* starts with one and early Ruby (before YARV in 1.9) was one. This implementation has potential overheads, although other tree walkers can use resolved slots, iterative traversal or specialized nodes:

- **Pointer chasing.** Nodes are scattered across the heap, so each step risks a cache miss.
- **Recursion.** Every node costs a function call, with its frame setup and return.
- **Repeated decisions.** Each visit re-tests which kind of node this is, and names are looked up in a dictionary by string every time.

## Bytecode virtual machines

A bytecode VM can reduce these costs by compiling the tree once into an instruction sequence, then running that array in a loop. Calc's compiler from lesson 6 produces stack bytecode with variables already resolved to numbered slots. The VM is a **dispatch loop**:

```python
def run_vm(code, nslots):
    stack = []
    slots = [0] * nslots
    pc = 0
    while True:
        op, arg = code[pc]
        pc += 1
        if op == "PUSH":
            stack.append(arg)
        elif op == "LOAD":
            stack.append(slots[arg])
        elif op == "STORE":
            slots[arg] = stack.pop()
        elif op == "NEG":
            stack.append(-stack.pop())
        elif op == "RET":
            return stack.pop()
        else:
            b = stack.pop()
            a = stack.pop()
            f = BINOPS[op]
            stack.append(f(a, b))
```

Trace `let x = 5 in x * x - 1`:

```
pc  instruction  stack     slots
0   PUSH 5       [5]       [0]
1   STORE 0      []        [5]
2   LOAD 0       [5]       [5]
3   LOAD 0       [5, 5]    [5]
4   MUL          [25]      [5]
5   PUSH 1       [25, 1]   [5]
6   SUB          [24]      [5]
7   RET          -> 24
```

The work per instruction is now small and predictable: fetch, decode, execute. The names are gone, replaced by `slots[0]`. Production bytecode can use compact contiguous storage. This Python list instead stores references to tuples, so it is not a packed byte array.

### Dispatch: switch, computed goto, tail calls

In a C VM, the loop is usually a big `switch (opcode)`. The compiler may implement this with a shared indirect jump, a decision tree or other code. Dispatch cost depends on the resulting code and branch predictor. **Computed goto** (a GCC/Clang extension) puts a separate `goto *labels[next_op]` at the end of each handler. Separate handler dispatch sites can help a predictor exploit patterns like "after `LOAD` usually comes `MUL`". CPython uses computed gotos when the C compiler supports them. Python 3.14 adds an optional build where each opcode handler is a small C function that **tail-calls** the next; with Clang 19 or newer, the Python 3.14 release notes report a preliminary 3–5% geometric-mean improvement on pyperformance over the Clang-19 baseline, depending on platform and architecture.

### Stack versus register VMs

| VM | Model | Example |
|---|---|---|
| CPython, JVM | Stack | `LOAD a; LOAD b; ADD` |
| .NET CIL, Wasm | Stack | same idea |
| Lua 5, Dalvik | Register | `ADD r2, r0, r1` |

Register VMs have "virtual registers", which are slots in the current frame. Each instruction is larger, but you need fewer of them, and fewer instructions means fewer dispatches. The Lua 5.0 designers reported that switching from a stack VM to a register VM made Lua noticeably faster. Stack bytecode is more compact and simpler to generate, which suits code shipped over a network, like JVM class files and WebAssembly.

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

## A toy JIT for Calc

A **just-in-time (JIT) compiler** generates code at runtime for a program it is already running. Production JITs such as V8 and HotSpot emit native machine code; just-in-time describes compilation timing rather than requiring one particular target. We can get the flavour with less risk by emitting *Python source* and letting CPython's compiler turn it into bytecode:

```python
def py(node, slot):
    match node:
        case Num(value):
            return repr(value)
        case Var():
            return f"s{slot[id(node)]}"
        case Neg(e):
            return f"(-{py(e, slot)})"
        case BinOp(op, l, r):
            a, b = py(l, slot), py(r, slot)
            if op == "^":
                return f"power({a}, {b})"
            if op == "/":
                op = "//"
            return f"({a} {op} {b})"
        case Let(_, value, body):
            s = f"s{slot[id(node)]}"
            v = py(value, slot)
            b = py(body, slot)
            return f"({s} := {v}, {b})[1]"

def jit(tree):
    chk = check(tree)
    if chk.errors:
        raise SyntaxError(chk.errors[0])
    src = "lambda: " + py(tree, chk.slot)
    code = compile(src, "<calc>", "eval")
    return eval(code, {"power": power})
```

`let` becomes an assignment expression inside a tuple, using the checker's slot numbers as variable names (`s0`, `s1`) so shadowed names never collide. `jit(parse("let x = 5 in x * x - 1"))` builds `lambda: (s0 := 5, ((s0 * s0) - 1))[1]`, and calling it returns 24. The original claimed 18,000-program test artifact is absent, so that result is omitted. Comparisons must account for check rejecting literal-zero division before either bytecode or JIT execution.

No reproducible artifact accompanies the original timing table, so its microsecond values and speed ratios are omitted. Benchmark the complete implementations on a stated workload and runtime before claiming a speedup. Flattening and slot resolution can reduce interpreter work; the toy JIT delegates execution to CPython bytecode, removing our Python-level dispatch loop. CPython instructions here are bytecode instructions, not native CPU instructions.
The cost: compiling through jit can cost more than interpreting a short program once, because it invokes CPython's whole compiler. It only pays off if the program runs many times. That trade-off, compile time against run time, is the central problem of every JIT.

## How production JITs win

Native JITs can specialize using runtime observations in both static and dynamic languages. Ahead-of-time compilers can also use profile-guided optimization.

### 1. Profiling and tiers

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

### 2. Inline caches and hidden classes

In JavaScript, `p.x` could mean anything: `p` might have any set of properties. V8 gives objects with the same layout a shared **hidden class** (a "map" or "shape") that records where each property lives. Each `p.x` site then keeps an **inline cache**: "last time, `p` had shape S and `x` was at offset 12". Next time, one comparison of the shape replaces a dictionary lookup. A site that only ever sees one shape is **monomorphic** and fast; one that sees many can become megamorphic, using more general lookup or stub-cache mechanisms whose cost depends on the engine and workload.

### 3. Speculation and deoptimisation

The optimiser uses profiles to **speculate**: "this `+` has only ever seen small integers, so emit a single machine `add`, plus a guard." If the guard fails (an overflow, or a string), the code **deoptimises**: it reconstructs the interpreter's frame from the optimised machine state and continues in the interpreter. This lets the JIT generate code for the common case only, which is what makes JavaScript competitive with statically typed languages on hot loops. Repeated deoptimizations can change optimization policy; thresholds and recovery behavior depend on the engine.

### 4. On-stack replacement

A function called once but containing a loop of a billion iterations may never reach a call-count compilation threshold. **On-stack replacement** (OSR) switches a *running* frame from interpreter to optimised code in the middle of the loop. Both V8 and HotSpot do this.

### Tracing JITs

**PyPy** and **LuaJIT** compile *traces* rather than functions: they record the exact path taken through a hot loop, including across calls, and compile that straight-line path with guards wherever execution could diverge. This is excellent for loop-heavy code. PyPy is a *meta-tracing* JIT: it traces the interpreter (written in RPython) running your program, allowing a reusable JIT framework rather than a separately hand-written Python-specific optimizing JIT; PyPy still has Python parsing and bytecode compilation. CPython's own experimental JIT (PEP 744, in 3.13) uses **copy-and-patch**: it stitches together precompiled machine-code templates for each micro-op, which is cheap to build and maintain. The 3.14 macOS and Windows installers include it, off by default (`PYTHON_JIT=1` enables it), and the docs describe its effect as anywhere from about 10% slower to 20% faster.

## Trade-offs

| | AOT | JIT |
|---|---|---|
| Start-up | Avoids runtime compilation | May incur compilation/warm-up |
| Peak speed | Very good | Very good, uses profiles |
| Memory | Depends on artifact/runtime | Compiler and code cache add costs |
| Security | W^X easy | Needs writable code |

- **Warm-up.** Steady-state benchmarks separate warm-up from measurement; startup-focused benchmarks must include it. A short-lived command-line tool may finish before any code gets hot, which is why Java added ahead-of-time options and class-data sharing.
- **Security.** JIT code must be written and then executed. Platforms may enforce W^X policies that separate writing from executing generated code. JITs use platform-specific mechanisms; Apple provides MAP_JIT and associated permissions/protection APIs. JIT bugs are also a rich source of browser exploits, which is why browsers offer JIT-less modes.
- **Platform rules.** JIT availability on iOS depends on entitlements and distribution conditions. Apple permits authorized alternative browser engines for EU users to access JIT facilities; do not assume every third-party app has that permission.

## Pitfalls

- **"Interpreted languages are slow."** Performance depends on language semantics, implementation and workload. No reproducible cross-language benchmark is supplied here, so a universal speed ratio to C is omitted.
- **Shape variation can affect inline caches.** Different construction paths can produce different shapes. A small number may remain polymorphic; seeing two shapes alone does not imply megamorphism.
- **Measuring cold code.** A single short measurement may emphasize startup rather than steady-state optimized execution; both can be legitimate goals.
- **Unbounded compilation.** A JIT that compiles everything eagerly wastes memory and start-up time on code that runs once.

## Key takeaways
- Tree-walkers can be simple; bytecode VMs flatten the tree, resolve names to slots, and run a tight dispatch loop.
- Dispatch cost matters: computed goto and tail-call dispatch can help on suitable implementations; register VMs can express operations with fewer dispatches.
- CPython 3.11+ specialises instructions to the types it observes and de-specialises when they change.
- JITs trade compile time for run time, so they tier up: interpreter, baseline compiler, then optimiser for hot code.
- Profiling, inline caches, speculation with deoptimisation and on-stack replacement are what make dynamic languages fast.

## Further reading
- [A Virtual Machine — Crafting Interpreters](https://craftinginterpreters.com/a-virtual-machine.html)
- [PEP 659: Specializing Adaptive Interpreter](https://peps.python.org/pep-0659/)
- [PEP 744: JIT Compilation](https://peps.python.org/pep-0744/)
- [Maglev: V8's Fastest Optimizing JIT — V8 blog](https://v8.dev/blog/maglev)
- [JavaScript engine fundamentals: Shapes and Inline Caches — Mathias Bynens](https://mathiasbynens.be/notes/shapes-ics)
- [The Implementation of Lua 5.0 (register VM)](https://www.lua.org/doc/jucs05.pdf)
- [HotSpot Glossary of Terms — OpenJDK](https://openjdk.org/groups/hotspot/docs/HotSpotGlossary.html)
- [Primary verification source 1](https://docs.python.org/3/whatsnew/3.14.html)
- [Primary verification source 5](https://v8.dev/blog/sparkplug)
- [Primary verification source 6](https://doc.pypy.org/architecture.html)
- [Primary verification source 7](https://developer.apple.com/support/alternative-browser-engines/)
