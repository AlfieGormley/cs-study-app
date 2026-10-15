---
id: comp-vm-execution
title: "From recursive tree evaluation to a bytecode VM"
level: advanced
minutes: 3
sourceLesson: comp-vms-jit
summary: "Slot-based bytecode avoids repeated string-name lookup in this teaching VM."
---

The target-selection unit ended with machine code. Many of the world's most used languages do not ship machine code at all. JavaScript arrives as source text; Java ships bytecode; CPython compiles Python source when needed, including on an import without a usable cached bytecode file. Each is *executed* by a runtime that decides, while the program runs, how much compiling is worth doing.

This lesson follows that spectrum with Calc: a tree-walking interpreter, a bytecode VM, and a tiny JIT. Then it looks at how production runtimes such as V8 and HotSpot go much further.

## The tree-walking interpreter

The simplest way to run a program is to walk its AST, as `evaluate` from the earlier semantic-analysis units does:

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
            # Preserve left-to-right
            # evaluation.
            b = evaluate(right, env)
            return ARITH[op](a, b)
        case Let(name, value, body):
            v = evaluate(value, env)
            # Shadow locally without
            # changing env.
            inner = {**env, name: v}
            return evaluate(body, inner)
```

It is easy to write and easy to debug, which is why *Crafting Interpreters* starts with one and early Ruby (before YARV in 1.9) was one. This implementation has potential overheads, although other tree walkers can use resolved slots, iterative traversal or specialized nodes:

- **Pointer chasing.** Nodes are scattered across the heap, so each step risks a cache miss.
- **Recursion.** Every node costs a function call, with its frame setup and return.
- **Repeated decisions.** Each visit re-tests which kind of node this is, and names are looked up in a dictionary by string every time.

## Bytecode virtual machines

A bytecode VM can reduce these costs by compiling the tree once into an instruction sequence, then running that array in a loop. Calc's compiler from the stack-code-generation unit produces stack bytecode with variables already resolved to numbered slots. The VM is a **dispatch loop**:

```python
def run_vm(code, nslots):
    stack = []
    slots = [0] * nslots
    pc = 0
    while True:
        # Fetch, then advance to the next
        # opcode.
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
            # Stack top is the right
            # operand.
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

## Key takeaways
- Slot-based bytecode avoids repeated string-name lookup in this teaching VM.
- Pop the right operand before the left and preserve source evaluation order.

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
