---
id: comp-optimisation-order
title: "Pass ordering, fixed points and reassociation"
level: advanced
minutes: 3
sourceLesson: comp-ir-ssa
summary: "A transformation can create a pattern only an earlier pass understands."
---

The preceding units introduced the four passes and their contracts. Here show is a deterministic display helper and simplify applies the stated integer identities with aliases. Their implementations are omitted scaffolding; the round-by-round trace illustrates how the passes interact, rather than claiming that this fence alone is a runnable compiler.

## Pass ordering and the fixed point

Each pass can expose work for the others, so `optimise` runs them repeatedly until nothing changes:

```python
PASSES = (const_fold, simplify, cse, dce)

def optimise(code, result):
    while True:
        # A stable display means no IR
        # change.
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

Our passes also have blind spots. `let t = x * 2 in t + t - t` stays as three instructions, because seeing that `(t + t) - t` is `t` needs **reassociation**, which we have not written. Reassociation regroups a chain of operations so that terms can cancel:

```formula
(t + t) − t = t + (t − t)
t + (t − t) = t + 0 = t
where
t: any Calc integer value
In words: for integers, regrouping lets t − t cancel to 0, and t + 0 is just t.
```

The regrouping step is always valid for Calc's unbounded integers, but not for floating point, as the next unit’s floating-point example shows.

## Key takeaways
- A transformation can create a pattern only an earlier pass understands.
- Repeated stable passes reach a fixed point here; reassociation is a separate capability.

## Further reading
- [LLVM language reference](https://llvm.org/docs/LangRef.html#phi-instruction)
- [LLVM analysis and transform passes](https://llvm.org/docs/Passes.html)
- [SSA construction — Cytron and colleagues](https://www.cs.utexas.edu/~pingali/CS380C/2010/papers/ssaCytron.pdf)
- [blog.llvm.org — what-every-c-programmer-should-know.html](https://blog.llvm.org/2011/05/what-every-c-programmer-should-know.html)
- [Finding compiler bugs with Csmith](https://users.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf)
