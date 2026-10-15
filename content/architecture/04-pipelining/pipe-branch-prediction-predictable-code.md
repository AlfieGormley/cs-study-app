---
id: pipe-branch-prediction-predictable-code
sourceLesson: pipe-branch-prediction
title: Write and inspect predictable code
level: intermediate
minutes: 3
summary: Explain sorted-data behaviour and evaluate branchless source without assuming a speedup.
---

A predictor learns machine-level branches, while a compiler can transform source control flow. The following C fragments are illustrative loop bodies with explicit types and valid-array assumptions. Their numerical results can be checked, but they establish no timing advantage for any particular phone or processor.

## Writing code that predicts well

### Data-dependent branches

Illustrative C loop body: assume `data` is a valid array of `uint8_t`, `n` is its length (`size_t`), and `sum` is `uint64_t` initially zero. Include `<stdint.h>` and `<stddef.h>`. Unsigned accumulation is defined modulo 2^64:

```c
// Filter bytes using an unsigned total.
for (size_t i = 0; i < n; i++)
    if (data[i] >= 128)
        sum += data[i];
```

If byte values are independently uniform over 0–255 and unpredictable from available history, the condition is a fair coin flip. If a machine branch remains, history prediction has expected accuracy 50%. Sorting the same values produces long runs of false then true conditions, which simple predictors learn. This can reduce misprediction cost, but supplies no guaranteed speedup: inspect the generated code and exclude or amortise sorting cost. The compiler may remove the branch in both versions.

### Branchless code

For an unpredictable branch, consider a branchless implementation and measure it. A conditional move (x86 `cmov`, ARM `csel`) selects a value without a jump:

```c
// Select a contribution; lowering varies.
sum += (data[i] >= 128) ? data[i] : 0;
```

A compiler can use a conditional move, arithmetic selection or vectorisation; it may also retain a branch. The source form does not promise a particular lowering, which is why naive benchmarks of this effect are often misleading.

> [!tip] Branchless is not always faster
> Branchless selection can introduce data dependencies or work on both alternatives, whereas a predicted branch permits speculative execution. Either source form may compile to the same machine code. Compare generated code and measure the actual workload; on supported Linux systems, `perf stat -e branches,branch-misses` provides useful counters, subject to hardware availability and permissions.

### Other habits

- Keep hot loops simple, with predictable trip counts.
- In interpreters, "threaded" dispatch (a separate indirect jump per opcode handler) can give a PC-indexed indirect predictor more context than one central `switch`, if the compiler preserves separate dispatch sites. This does not guarantee a speedup.
- Sort or partition data by the condition you'll branch on, if changing order preserves semantics and repeated processing amortises the rearrangement cost.

## Key takeaways
- A source condition can become a branch, conditional select or vector code.
- Sorting may improve a remaining branch’s predictability but has its own cost and semantic constraints.
- Inspect generated code and measure the actual workload before claiming a speedup.

## Further reading
- [GCC: branch expectation built-in](https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html)
- [Linux perf tutorial](https://perfwiki.github.io/main/tutorial/)
- [Spectre: original research paper](https://spectreattack.com/spectre.pdf)
