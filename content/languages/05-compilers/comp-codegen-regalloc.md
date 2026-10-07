---
id: comp-codegen-regalloc
title: Code generation and register allocation
level: advanced
minutes: 15
summary: How a back end turns IR into instructions for a stack machine or a real CPU, choosing instructions, mapping unlimited temporaries onto a handful of registers with liveness analysis, linear scan and graph colouring, and spilling when they run out.
---

After optimisation, the program is a list of simple instructions over an unlimited supply of temporaries. Real hardware has neither unlimited temporaries nor our instruction set. The **back end** closes the gap with three jobs:

1. **Instruction selection.** Which machine instructions implement each IR operation?
2. **Register allocation.** Which of the CPU's few registers holds each value, and what goes to memory when they run out?
3. **Instruction scheduling.** In what order should instructions run so the pipeline stays busy?

This lesson covers the first two, and a simple teaching back end: a stack machine.

## Target 1: a stack machine

The abstract operand-stack instruction set does not name hardware registers. Its interpreter or JIT implementation may still allocate registers. Every instruction takes its operands from the top of an operand stack and pushes its result. The JVM, CPython, WebAssembly and .NET's CIL all use this model for their bytecode.

Code generation is a **post-order** tree walk: emit code for the children, then the operator.

```python
def compile_bc(tree):
    chk = check(tree)
    if chk.errors:
        raise SyntaxError(chk.errors[0])
    code = []
    def gen(node):
        match node:
            case Num(value):
                code.append(("PUSH", value))
            case Var():
                s = chk.slot[id(node)]
                code.append(("LOAD", s))
            case Neg(operand):
                gen(operand)
                code.append(("NEG", None))
            case BinOp(op, left, right):
                gen(left)
                gen(right)
                code.append(
                    (OPCODE[op], None))
            case Let(_, value, body):
                gen(value)
                s = chk.slot[id(node)]
                code.append(("STORE", s))
                gen(body)
    gen(tree)
    code.append(("RET", None))
    return code, chk.scopes.nslots
```

The slot numbers come from the checker in lesson 4. `let x = 5 in x * x - 1` becomes:

```
PUSH 5
STORE 0      x lives in slot 0
LOAD 0
LOAD 0
MUL
PUSH 1
SUB
RET          -> 24
```

The VM must reserve enough stack, so compilers compute the **maximum stack depth** statically. The JVM stores it in every method as `max_stack`, and CPython stores `co_stacksize`. Calc's `max_stack` just tracks each instruction's effect: `PUSH` and `LOAD` add one, binary operators remove one, `STORE` removes one.

Tree shape matters. `((1+2)+3)+4` needs a depth of 2, while `1+(2+(3+4))` needs 4, because every left operand waits on the stack while the right side is computed. The same idea, for registers, is Sethi–Ullman numbering below.

Stack code is compact and trivial to generate, which is why it is popular for portable bytecode. The bytecode records an evaluation order, but implementations can cache stack values in hardware registers or optimize the instruction sequence.

## Target 2: a register machine

Real CPUs compute in **registers**: baseline x86-64 has 16 general-purpose integer registers (APX extends this to 32), and AArch64 names 31 general-purpose X registers, with SP handled separately. Our IR has unlimited temporaries. Register allocation is the mapping, and it is one of the most important things a back end does, because keeping values in registers avoids spill loads and stores; costs depend on the processor and instruction.

### Liveness

A value is live where a future execution path can use it before redefinition. In this straight-line example, definition-to-last-use intervals summarize liveness. Two values can share a register only if they are never live at the same time. On straight-line code, liveness is a simple scan:

```python
def live_ranges(code, result, params):
    start = {p: -1 for p in params}
    end = {p: -1 for p in params}
    for i, ins in enumerate(code):
        start[ins.dest] = end[ins.dest] = i
        for a in filter(is_temp, ins.args):
            end[a] = i
    if is_temp(result):
        end[result] = len(code)
    return start, end
```

Inputs are defined at -1 (they arrive before the first instruction) and the result is used by `ret`. Take `(x + y) * (x + y) - x * 8`, after the lesson 5 optimiser:

```
 i  instruction     live after it
-1  (inputs)        x  y
 0  t1 = x + y      x  t1
 1  t3 = t1 * t1    x  t3
 2  t4 = x * 8      t3 t4
 3  t5 = t3 - t4    t5
 4  ret t5
```

At most **two** values are live at any point. `y` dies at instruction 0 and `x` at instruction 2, so their registers can be reused. In this idealized model, MaxLive is the number of freely interchangeable registers needed without spills, allowing a dying operand register to hold the result. Real targets impose additional operand, register-class and ABI constraints.

### Linear scan

**Linear scan** (Poletto and Sarkar, 1999) walks the live ranges in order of start, handing out free registers and taking them back when a range ends:

```python
def linear_scan(code, result, params, k):
    if k < 1:
        raise ValueError(
            "k must be positive")
    start, end = live_ranges(code, result,
                             params)
    free = [f"r{i}" for i in range(k)]
    active = []    # values in registers
    reg, spill = {}, []
    for v in sorted(start, key=start.get):
        if end[v] < 0:
            continue   # unused input
        # free registers whose value died
        for w in list(active):
            if end[w] <= start[v]:
                active.remove(w)
                free.append(reg[w])
        if free:
            reg[v] = free.pop(0)
            active.append(v)
            continue
        # no register: spill whichever
        # interval ends furthest ahead
        far = max(active, key=end.get)
        if end[far] > end[v]:
            reg[v] = reg.pop(far)
            active.remove(far)
            active.append(v)
            spill.append(far)
        else:
            spill.append(v)
    return reg, spill
```

`end[w] <= start[v]` lets a value that dies *at* an instruction give its register to the value that instruction defines, so `t3 = t1 * t1` can write the register `t1` was in. With `k = 2` and a simple emitter:

```
add r1, r0, r1      t1 = x + y
mul r1, r1, r1      t3 = t1 * t1
mul r0, r0, #8      t4 = x * 8
sub r1, r1, r0      t5 = t3 - t4
ret r1
```

Here `x` arrived in `r0` and `y` in `r1`. Two registers suffice, exactly MaxLive. For these interval ranges and interchangeable registers, start-order allocation finds a spill-free assignment when k is at least MaxLive. This is not a guarantee of minimum spill cost on real hardware. The original claimed 10,000-program test artifact is absent, so that result is omitted.

### Spilling

With `k = 1` there are not enough registers. This linear scan spills the interval whose end (last use) is furthest away, keeping it in a stack slot instead:

```
add r0, [sp+0], r0
mul r0, r0, r0
mul [sp+8], [sp+0], #8
sub r0, r0, [sp+8]
ret r0
```

`x` and `t4` now live in memory. This is pseudo-assembly that lets any operand be in memory; a real back end would reserve a scratch register and insert explicit loads and stores. This interval-end heuristic differs from farthest-next-use cache replacement and is not an optimal spill-cost algorithm. Spills inside a hot loop are a classic cause of slow code.

### Graph colouring

Once code has branches and loops, live ranges stop being simple intervals: a value can be live in one branch and dead in another. The classic general approach (Chaitin, 1981) builds an **interference graph** with a node per value and an edge between any two values that are live at the same time. Allocating k registers is then **k-colouring** the graph so that no edge joins two nodes of the same colour.

```
  a ── b         k = 2: impossible,
  │ ╲  │         a, b, d form a
  │  ╲ │         triangle
  c    d
```

General k-colourability for k at least 3 is NP-complete, so allocators use Chaitin's heuristic: repeatedly remove a node with fewer than k neighbours (it can always be coloured later), pushing it on a stack. If every node has k or more neighbours, choose one to spill. Then pop nodes and give each a colour its neighbours do not use. Briggs' refinement (1994) defers the spill decision, because a node with k neighbours may still be colourable if two neighbours share a colour.

**Coalescing** is the other half: if the IR says b = a, assigning compatible noninterfering values the same register removes the copy. Conservative coalescing also checks whether merging could make allocation harder. This is how phi functions from SSA mostly vanish.

| Approach | Design emphasis |
|---|---|
| Linear scan | Interval processing with low allocation overhead |
| Graph colouring | Interference graph and colouring heuristics |
| LLVM greedy | Cost-driven splitting and reassignment |

JIT compilers favour linear scan because allocation time is part of the program's run time. Ahead-of-time compilers can afford more.

## Sethi–Ullman numbering

For a single expression *tree*, Sethi and Ullman (1970) showed how to compute the minimum number of registers directly, and the evaluation order that achieves it:

```python
def sethi_ullman(node):
    match node:
        case Num() | Var():
            return 1
        case Neg(operand):
            return sethi_ullman(operand)
        case BinOp(_, left, right):
            a = sethi_ullman(left)
            b = sethi_ullman(right)
            if a == b:
                return a + 1
            return max(a, b)
```

When reordering preserves effects and exception behavior, evaluate the subtree needing more registers first; its result then occupies one register while the smaller side uses the rest. Only when both sides need the same number does the total go up by one. So `(a+b)*(c+d)` needs 3, while `a+(b+(c+d))` needs only 2, *if* the compiler evaluates `c+d` first. Evaluating strictly left to right would hold `a`, `b` and `c` while computing `c+d`: four registers. (This version counts a leaf as one register; machines with memory or immediate operands can count a right-hand leaf as zero.)

## Instruction selection

So far each IR operation became one instruction. Real instruction sets offer better choices. Here is representative optimized assembly for the C version of our example, for x86-64 (Intel syntax):

```c
int f(int x, int y) {
    return (x + y) * (x + y) - x * 8;
}
```

```
lea   eax, [rsi + rdi]
imul  eax, eax
shl   edi, 3
sub   eax, edi
ret
```

And for ARM64 (Apple silicon):

```
add  w8, w1, w0
mul  w8, w8, w8
sub  w0, w8, w0, lsl #3
ret
```

Several decisions are visible:

- **Common subexpressions.** `x + y` is computed once, as in our CSE.
- **`lea` as an adder.** x86's address-calculation instruction computes `rsi + rdi` into a fresh register without overwriting either input, unlike the traditional two-operand x86 add encoding.
- **Strength reduction.** `x * 8` becomes a shift: `shl edi, 3` on x86, and on ARM64 the shift is folded *into* the subtraction (`w0, lsl #3`), removing the separate multiply instruction; this does not imply zero execution cost.
- **Calling convention.** On x86-64 Linux (System V ABI), the first six eligible scalar integer arguments arrive in `rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9` and the result returns in `rax`. On ARM64 arguments arrive in `x0` to `x7` (`w0`, `w1` are their 32-bit halves) and the result goes in `x0`. The allocator works around these fixed registers.

Selecting instructions is often framed as **tree tiling**: each machine instruction is a "tile" that covers a pattern of IR nodes (`lea` covers `a + b*8 + c`), and the selector covers the tree with the cheapest set of tiles. LLVM's SelectionDAG and GlobalISel, and GCC's machine descriptions, are pattern-matching engines for exactly this. At -O0, compilers still allocate registers, but commonly retain stack locations and extra loads for debugging. Exact assembly depends on compiler, target and options. The C example assumes inputs whose signed arithmetic is defined.

> [!example] Floor versus truncation
> C's `x / 2` on signed `int` rounds towards zero, so Clang emits a shift *plus* a correction for negative numbers (`shr`, `add`, `sar` on x86). Calc's `/` is floor division, which is exactly what an arithmetic right shift computes, so a Calc value known to fit the signed machine word could use sar. Arbitrarily large Calc integers require more machinery. Language semantics shape the machine code.

Calling conventions also split registers into **caller-saved** (the callee may overwrite them, so the caller must save any live values before a call) and **callee-saved** (a function that uses them must restore them: `rbx`, `rbp` and `r12` to `r15` on x86-64 System V). An allocator may choose callee-saved registers for values live across calls, balancing their save/restore cost against other options.

## Pitfalls

- **Register pressure from optimisation.** CSE and loop-invariant code motion keep values alive longer; too much of it causes spills that cost more than the recomputation saved.
- **Ignoring the ABI.** A value that must survive a call cannot sit in a caller-saved register unless it is saved around the call.
- **Benchmarking unoptimised builds.** -O0 prioritizes compilation and debugging over optimization; measure the build configuration relevant to your goal when comparing algorithms.
- **Assuming fewer instructions means faster.** Latency and throughput depend on the exact instruction and microarchitecture. Instruction selection uses target costs, not instruction count alone.

## Key takeaways
- Stack-machine code is a post-order walk of the tree; the compiler records the maximum stack depth so the VM can reserve it.
- Register allocation maps unlimited temporaries onto a few registers; two values may share one only if their live ranges do not overlap.
- Linear scan efficiently processes intervals; its spill-free interval result does not guarantee optimal spill costs. Graph-based allocators model interference explicitly.
- When registers run out, values are spilled to the stack; choosing which value to spill is the key heuristic.
- Instruction selection exploits the target: `lea`, shifted operands and strength reduction, all constrained by the calling convention.

## Further reading
- [Register allocation — Wikipedia](https://en.wikipedia.org/wiki/Register_allocation)
- [Linear Scan Register Allocation — Poletto and Sarkar (1999)](https://web.cs.ucla.edu/~palsberg/course/cs132/linearscan.pdf)
- [Sethi–Ullman algorithm — Wikipedia](https://en.wikipedia.org/wiki/Sethi%E2%80%93Ullman_algorithm)
- [x86 calling conventions — Wikipedia](https://en.wikipedia.org/wiki/X86_calling_conventions)
- [Compiler Explorer](https://godbolt.org/)
- [A Map of the Territory — Crafting Interpreters](https://craftinginterpreters.com/a-map-of-the-territory.html)
- [Primary verification source 1](https://llvm.org/docs/CodeGenerator.html)
- [Primary verification source 3](https://www.intel.com/content/www/us/en/developer/articles/technical/advanced-performance-extensions-apx.html)
- [Primary verification source 4](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
