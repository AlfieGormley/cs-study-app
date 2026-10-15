---
id: comp-ssa-phi
title: "Single assignment, merge values and phi nodes"
level: advanced
minutes: 5
sourceLesson: comp-ir-ssa
summary: "SSA names have one static definition even when their defining block executes repeatedly."
---

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

## Branches and phi functions

Calc has no `if`, but real languages do, and that is where SSA needs a new idea. Code is split into **basic blocks** (straight-line sequences with one entry and one exit), linked into a **control-flow graph**:

```
        entry: if c
         /           \
 then: y1 = g(x)   else: y2 = h(x)
         \           /
   end: y3 = phi(y1, y2)
        ret y3 + 1
```

At `end`, `y` could be either version. A **phi function** (φ, the Greek letter phi) selects the value according to which edge control arrived along:

```formula
y_3 = φ(y_1, y_2)
where
y_3: the new SSA name for y in the merge block `end`
y_1: the version of y computed in the `then` block
y_2: the version of y computed in the `else` block
φ: the phi function: not a calculation, but a choice: it yields y_1 if control arrived from `then` and y_2 if it arrived from `else`
In words: at a merge point, y_3 is whichever version of y was produced on the path the program actually took.
```

LLVM requires an incoming value for each predecessor block; repeated edges from one predecessor repeat the same value. The edge-based intuition still explains which incoming value is selected. For example, if `c` is 0 the program takes the `else` branch, so y_3 is y_2, the result of `h(x)`. LLVM phi instructions must precede non-phi instructions at the start of their block. They also handle loop-carried values: a loop header can merge an entry value with the next iteration’s value. A merge may be trivial, including a single predecessor, before simplification. Here is real LLVM IR from `clang -O1` for that C function (lightly trimmed: attributes removed, long lines wrapped):

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

Where do phis go? Cytron's algorithm uses **iterated dominance frontiers** of definition blocks: the blocks where one path from the assignment meets a path that bypasses it. In practice, front ends like Clang emit simple loads and stores to stack slots, and LLVM's `mem2reg` pass promotes them to SSA registers and inserts the phis. Phi nodes are IR operations. Lowering can introduce edge-specific parallel copies, requiring cycle resolution and sometimes splitting critical edges; coalescing can eliminate copies.

## A name is static, execution is dynamic

SSA means one definition in the program text, not one execution. A loop-body definition may execute on every iteration. A phi at the loop header selects the initial value on entry and the next value on the back edge. Facts available only on one path remain conditional; only unconditional facts about a value may be substituted at every use.

## Key takeaways
- SSA names have one static definition even when their defining block executes repeatedly.
- Phi operands select values by incoming control-flow edge rather than evaluating both paths.

## Further reading
- [LLVM language reference](https://llvm.org/docs/LangRef.html#phi-instruction)
- [LLVM analysis and transform passes](https://llvm.org/docs/Passes.html)
- [SSA construction — Cytron and colleagues](https://www.cs.utexas.edu/~pingali/CS380C/2010/papers/ssaCytron.pdf)
- [blog.llvm.org — what-every-c-programmer-should-know.html](https://blog.llvm.org/2011/05/what-every-c-programmer-should-know.html)
- [Finding compiler bugs with Csmith](https://users.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf)
