---
id: comp-ir-ssa
title: IR, SSA and optimisation
level: advanced
minutes: 15
summary: Why compilers lower the AST to an intermediate representation, how three-address code and static single assignment make analysis easy, and how constant folding, algebraic simplification, CSE and dead-code elimination work, with illustrative optimisation passes for Calc.
---

The AST mirrors what the programmer wrote: nested, full of sugar, shaped by the grammar. The machine wants flat sequences of simple operations. In between sits the **intermediate representation** (IR), the form in which a compiler does most of its thinking.

A good IR is simple enough that each optimisation needs only a few rules, explicit enough that nothing is hidden (every temporary value has a name), and reusable across source languages and targets, while preserving language semantics and relevant target layout constraints. Lesson 1 showed why that last property matters: it lets LLVM serve dozens of languages and targets with one optimiser.

Real compilers often use several IRs at different levels. GCC lowers to GIMPLE, then RTL. rustc goes from AST to HIR, then MIR (where the borrow checker runs), then LLVM IR. Swift has SIL. MLIR is a framework for defining such levels.

## Three-address code

The classic IR is **three-address code**: each instruction has at most one operator and at most three names, two operands and a destination. Nested expressions are flattened by giving every intermediate result a **temporary**.

```python
@dataclass
class Ins:
    dest: str
    op: str      # + - * / ^ neg
    args: tuple
```

Lowering Calc's AST is one more tree walk. It returns the *operand* that holds each subexpression's value: an `int` for a constant, or a temp name such as `"t3"`.

```python
class Lowerer:
    def __init__(self, params=()):
        self.code = []
        self.n = 0
        self.used = set(params)

    def emit(self, op, *args):
        self.n += 1
        dest = f"t{self.n}"
        while dest in self.used:
            self.n += 1
            dest = f"t{self.n}"
        self.used.add(dest)
        ins = Ins(dest, op, args)
        self.code.append(ins)
        return dest

    def lower(self, node, env):
        match node:
            case Num(value):
                return value
            case Var(name):
                return env[name]
            case Neg(operand):
                a = self.lower(operand, env)
                return self.emit("neg", a)
            case BinOp(op, left, right):
                a = self.lower(left, env)
                b = self.lower(right, env)
                return self.emit(op, a, b)
            case Let(name, value, body):
                v = self.lower(value, env)
                e2 = {**env, name: v}
                return self.lower(body, e2)
```

The wrapper reserves input names before generating temporaries. In this toy IR, strings denote named operands and integers denote constants:

```python
def is_temp(value):
    return isinstance(value, str)

def to_ir(tree, params=()):
    lowerer = Lowerer(params)
    env = {p: p for p in params}
    result = lowerer.lower(tree, env)
    return lowerer.code, result
```

A let initializer may emit instructions; the binding itself only updates the environment. Source binding names disappear, while parameter names remain as inputs.

```
let a = 3 in let b = a * a in b - a

t1 = 3 * 3
t2 = t1 - 3
ret t2
```

## Static single assignment

The IR above has a property that matters enormously: every temp is assigned **exactly once**. This is **static single assignment** form (SSA), whose efficient construction was described by Cytron, Ferrante, Rosen, Wegman and Zadeck in their 1991 paper. Many production compilers use SSA-based representations: LLVM, GCC (since 4.0), HotSpot's C2, V8's TurboFan, Go and Swift.

Why it helps: if `t1` is defined once, then *wherever* you see `t1`, you know exactly which instruction produced it. There is no "which assignment to `x` reaches this line?" question, so facts about a value hold everywhere. Constant propagation becomes "if `t1 = 3 * 3`, replace every `t1` with 9". With ordinary variables you would need a data-flow analysis to know that no other assignment interferes.

Calc is SSA *by construction* because `let` never reassigns, it only introduces. Even shadowing is fine:

```
let x = 1 in let x = x + 1 in x * 10

t1 = 1 + 1
t2 = t1 * 10
ret t2
```

The two `x`s become two different operands. Converting an imperative program to SSA does exactly this renaming: `x = 1; x = x + 1` becomes `x1 = 1; x2 = x1 + 1`.

### Branches and phi functions

Calc has no `if`, but real languages do, and that is where SSA needs a new idea. Code is split into **basic blocks** (straight-line sequences with one entry and one exit), linked into a **control-flow graph** (CFG):

```
        entry: c == 0?
         /           \
 then: y1 = g(x)   else: y2 = h(x)
         \           /
   end: y3 = phi(y1, y2)
        ret y3 + 1
```

At `end`, `y` could be either version. A **phi function** (φ) selects the value according to which edge control arrived along. Here is real LLVM IR from `clang -O1` for that C function (lightly trimmed: attributes removed, long lines wrapped):

```
define i32 @f(i32 %x, i32 %c) {
entry:
  %tobool.not = icmp eq i32 %c, 0
  br i1 %tobool.not, label %if.else,
                     label %if.then
if.then:
  %call = tail call i32 @g(i32 %x)
  br label %if.end
if.else:
  %call1 = tail call i32 @h(i32 %x)
  br label %if.end
if.end:
  %y.0 = phi i32 [ %call, %if.then ],
                 [ %call1, %if.else ]
  %add = add nsw i32 %y.0, 1
  ret i32 %add
}
```

Where do phis go? Cytron's algorithm uses **iterated dominance frontiers** of definition blocks: the blocks where one path from the assignment meets a path that bypasses it. In practice, front ends like Clang emit simple loads and stores to stack slots, and LLVM's `mem2reg` pass promotes them to SSA registers and inserts the phis. Phi nodes are IR operations. Lowering can introduce edge-specific parallel copies, requiring cycle resolution and sometimes edge splitting; coalescing can eliminate copies.

## Optimisations

Calc's optimiser has four passes. Each takes `(code, result)` and returns a new pair, so they compose freely.

### 1. Constant folding and propagation

If both operands are known constants, compute the answer now and remember it for later instructions:

```python
def fold(op, a, b):
    """Compute a op b now, or None if it is
    unsafe to do at compile time."""
    if op == "/" and b == 0:
        return None   # keep runtime error
    if op == "^":
        bits = max(1, abs(a).bit_length())
        if not 0 <= b <= 64:
            return None
        if bits * b > 4096:
            return None
    return ARITH[op](a, b)
```

```python
def const_fold(code, result):
    known, out = {}, []
    for ins in code:
        args = tuple(known.get(a, a)
                     for a in ins.args)
        if any(map(is_temp, args)):
            out.append(Ins(ins.dest, ins.op,
                           args))
            continue
        if ins.op == "neg":
            v = -args[0]
        else:
            v = fold(ins.op, *args)
        if v is None:
            out.append(Ins(ins.dest, ins.op,
                           args))
        else:
            known[ins.dest] = v
    return out, known.get(result, result)
```

`fold` is where correctness lives. Folding `1 / 0` would crash the *compiler*, and the program must instead fail when it runs. And folding `2 ^ 1000000` would make the compiler build a 300,000-digit number for a value that might never be used. Compilers need explicit resource budgets. This example bounds folded powers; it is not a complete resource-limit policy for all arithmetic.

### 2. Algebraic simplification

Some operations are known without knowing both operands: `x + 0` is `x`, `x * 1` is `x`, `x - x` is 0, `x * 0` is 0. The `identity` function holds the rules, and `simplify` replaces the instruction with the shortcut, recording an alias so later uses see through it.

These rules are valid for Calc's unbounded integers. For floating point, some are not generally valid: `x * 0` is `NaN` when `x` is infinity, and `x - x` is `NaN` for `NaN`. Compilers need proofs or suitable floating-point permissions for transformations that change observable results; fast-math is one way to grant such permissions.

### 3. Common subexpression elimination

For these deterministic, pure arithmetic operations in one block, reuse an operation previously computed on the same operands. Loads and calls require additional effect and alias analysis. Because of SSA, "same operands" means the same values, guaranteed.

```python
def cse(code, result):
    seen, alias, out = {}, {}, []
    for ins in code:
        args = tuple(alias.get(a, a)
                     for a in ins.args)
        if ins.op in ("+", "*"):  # a+b=b+a
            args = tuple(sorted(args,
                                key=repr))
        key = (ins.op, args)
        if key in seen:
            alias[ins.dest] = seen[key]
        else:
            seen[key] = ins.dest
            out.append(Ins(ins.dest, ins.op,
                           args))
    return out, alias.get(result, result)
```

This is **local value numbering**. Sorting the operands of commutative operators makes `x + y` and `y + x` the same key:

```
(x + y) * (y + x)      optimised
t1 = x + y             t1 = x + y
t2 = y + x             t3 = t1 * t1
t3 = t1 * t2           ret t3
ret t3
```

### 4. Dead-code elimination

Walk backwards from the result, keeping only instructions whose value is needed:

```python
def dce(code, result):
    live, out = {result}, []
    for ins in reversed(code):
        needed = ins.dest in live
        if needed or may_trap(ins):
            out.append(ins)
            live.update(filter(is_temp,
                               ins.args))
    out.reverse()
    return out, result
```

Here is the trap predicate for Calc's defined arithmetic errors. Host resource exhaustion is outside this teaching model:

```python
def may_trap(ins):
    if ins.op not in ("/", "^"):
        return False
    b = ins.args[1]
    if is_temp(b):
        return True
    if ins.op == "/":
        return b == 0
    return b < 0
```

The may_trap check is the subtle part. It returns `True` for a division whose divisor is not a known non-zero constant, and for `^` with a possibly negative exponent. Consider `(1/0)*0`:

```
t1 = 1 / 0       optimised
t2 = t1 * 0      t1 = 1 / 0
ret t2           ret 0
```

`simplify` turns `t1 * 0` into 0, which makes `t1` unused. Without `may_trap`, DCE would delete the division and the program would quietly return 0 instead of failing. An instruction with a **side effect** (raising, writing memory, doing I/O) is never dead just because its result is unused.

> [!warning] C plays by different rules
> In C, dividing by zero and signed overflow are *undefined behaviour*. The compiler may assume they never happen, so it can delete such a division. Clang compiles `return x + 1 > x;` to "return 1", because overflow "cannot" happen. Calc defines its errors, so its optimiser must preserve them.

### Pass ordering and the fixed point

Each pass can expose work for the others, so `optimise` runs them repeatedly until nothing changes:

```python
PASSES = (const_fold, simplify, cse, dce)

def optimise(code, result):
    while True:
        before = show(code, result)
        for p in PASSES:
            code, result = p(code, result)
        if show(code, result) == before:
            return code, result
```

Watch it work, with inputs `x` and `y`:

```
let k = 2 + 3 in let a = x * k in
let b = x * 5 in a - b + y * (k - 4)
```

```
lowered         round 1
t1 = 2 + 3      fold:  k = 5,
t2 = x * t1       k - 4 = 1
t3 = x * 5      simplify: y * 1 -> y
t4 = t2 - t3    cse: t3 is t2
t5 = t1 - 4     now: t2 = x * 5
t6 = y * t5          t4 = t2 - t2
t7 = t4 + t6         t7 = t4 + y
ret t7

round 2
simplify: t2 - t2 -> 0, then 0 + y -> y
dce: t2 is unused, delete it
result: ret y
```

CSE in round 1 created `t2 - t2`, which only `simplify` can remove, so a second round was needed. Real compilers may run individual transformations to local fixed points, while using a carefully tuned outer pipeline (LLVM's `-O2` pipeline runs some passes, such as `instcombine`, several times), because compile time matters too.

Our passes also have blind spots. `let t = x * 2 in t + t - t` stays as three instructions, because seeing that `(t + t) - t` is `t` needs **reassociation**, which we have not written.

## What else real optimisers do

| Pass | Idea |
|---|---|
| Inlining | Copy a callee's body in |
| SCCP | Constants through branches |
| GVN | CSE across blocks |
| LICM | Hoist work out of loops |
| Strength red. | `x * 2` to `x << 1` |
| Vectorise | One SIMD operation on several lanes |

**Inlining** is often called the most important, because it exposes everything else: once a small function's body sits in its caller, its parameters may be constants. **SCCP** (sparse conditional constant propagation, Wegman and Zadeck) propagates constants and deletes branches that can never be taken. **GVN** (global value numbering) is CSE across basic blocks. **LICM** (loop-invariant code motion) moves computations that do not change out of loops.

## Pitfalls

- **Floating point is not real arithmetic.** In Python, `(0.1 + 0.2) + 0.3` is `0.6000000000000001` while `0.1 + (0.2 + 0.3)` is `0.6`. A compiler that reassociates floats changes results, so a transformation needs suitable permissions or a proof that observable results are preserved.
- **Compile-time blow-up.** Constant folding, inlining and loop unrolling can all make the compiler slow or huge. Every such pass needs limits, like `fold`'s exponent cap.
- **Undefined behaviour cuts both ways.** It lets C compilers optimise aggressively, and it is why "the compiler deleted my null check" is a real bug report.
- **Optimisers have bugs.** Csmith, a random C program generator from the University of Utah, found hundreds of bugs in GCC and LLVM by comparing optimised and unoptimised builds. The original claimed 40,000-program Calc test harness is absent, so that result is not retained. This lesson supplies excerpts; identity, simplify and display helpers must be supplied to assemble the complete demonstration. Audit execution coverage is recorded separately.

## Key takeaways
- An IR sits between AST and machine code: explicit, with abstractions reusable across languages and targets.
- Three-address code gives every intermediate value a name; SSA makes each name assigned exactly once, so facts about a value hold wherever it is used.
- Branches need phi functions to merge values; construction can use iterated dominance frontiers; lowering resolves their edge-dependent value selection.
- Constant folding, algebraic simplification, CSE and DCE feed each other, so pass order and repetition matter.
- Optimisations must preserve behaviour, including errors: preserve observable errors and side effects; unreachable or provably unobservable operations may be removed.

## Further reading
- [Static single-assignment form — Wikipedia](https://en.wikipedia.org/wiki/Static_single-assignment_form)
- [LLVM Language Reference Manual (phi instruction)](https://llvm.org/docs/LangRef.html#phi-instruction)
- [Efficiently Computing SSA Form and the Control Dependence Graph — Cytron et al.](https://www.cs.utexas.edu/~pingali/CS380C/2010/papers/ssaCytron.pdf)
- [Value numbering — Wikipedia](https://en.wikipedia.org/wiki/Value_numbering)
- [What Every C Programmer Should Know About Undefined Behavior — LLVM Blog](https://blog.llvm.org/2011/05/what-every-c-programmer-should-know.html)
- [Compiler Explorer](https://godbolt.org/)
- [Primary verification source 2](https://llvm.org/docs/Passes.html)
- [Primary verification source 4](https://users.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf)
