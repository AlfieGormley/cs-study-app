---
id: comp-execution-strategies
title: "Execution strategies, passes and diagnostics"
level: basic
minutes: 4
sourceLesson: comp-pipeline
summary: "Compilation and interpretation can coexist in one implementation."
---

## Compilers, interpreters and everything between

"Compiled versus interpreted" is a spectrum, not a binary.

| Strategy | Example | Trade-off |
|---|---|---|
| Tree-walking | Early Ruby (MRI) | Simple; per-node execution overhead |
| Bytecode VM | CPython, Lua | Portable representation; dispatch costs |
| JIT | V8, HotSpot, PyPy | Runtime compilation and optimisation costs |
| Ahead-of-time | GCC, Go, Rust | Compilation before execution; runtime costs remain |

Most production systems mix strategies. `javac` compiles Java to bytecode ahead of time; the HotSpot JVM then interprets that bytecode and JIT-compiles the hot parts. V8 parses JavaScript, generates bytecode for its Ignition interpreter, and compiles hot functions with Sparkplug, Maglev and TurboFan. The later VM and JIT units cover this.

A compiler that translates between languages at a similar level is often called a **transpiler**: TypeScript's `tsc` emits JavaScript, and Babel rewrites modern JavaScript into older JavaScript.

## Passes, and why there are so many

A traversal or transformation step is a **compiler pass**. Limited memory motivated some early single-pass designs; other compilers used multiple passes. Declaration rules are language choices. Modern optimising compilers run dozens of passes over the IR. Exact pass counts depend on compiler version, options and program; no universal count is supplied here.

Breaking the work into passes keeps each one simple and testable, but the **order** matters. Inlining a function first can expose constants for folding, which can make a branch dead, which can make a variable unused. Choosing pass order is a long-standing research problem with no single right answer.

## Errors are a feature

A compiler's other job is telling people what they got wrong. Each stage catches a different class of error:

| Stage | Catches | Calc example |
|---|---|---|
| Lexer | Illegal characters | `2 $ 3` |
| Parser | Malformed structure | `2 * (3 +` |
| Semantic | Meaningless code | `y + 1` |
| Runtime in this simple pipeline | Faults missed by the literal-only checker | `1 / (2 - 2)` |

Notice the last row. `1 / 0` can be caught at compile time because both operands are constants, but `1 / (x - 2)` depends on `x`. For an unrestricted Turing-complete language, exact prediction of every possible runtime fault is undecidable. Closed Calc has no loops or recursion: its arithmetic can in principle be evaluated in advance, subject to resource limits. Its literal-only checker simply chooses a limited analysis.

Modern tools such as Clang and rustc invest heavily in error messages: precise positions, the offending source line, and suggested fixes. That requires every token to remember where it came from, which is why our lexer records a position in each token.

## Pitfalls and misconceptions

- **"Python is interpreted, C is compiled."** These are properties of implementations. CPython compiles to bytecode first; there are C interpreters too.
- **"Interpreters do no compilation."** An interpreter may execute source-derived trees, bytecode or another representation; compilation to bytecode is common but not required.
- **"The optimiser makes code optimal."** It makes code *better*. There is no general procedure that finds a shortest equivalent program for every unrestricted program. Specific bounded instruction-selection and scheduling problems have their own solvable cases or complexity limits.
- **"Parsing is the hard part."** For expression languages it is well understood. The hard engineering is in optimisation, code generation, error messages and speed of compilation.

## Key takeaways
- Compilation and interpretation can coexist in one implementation.
- Pass order exposes opportunities; token positions support useful errors.

## Further reading
- [Compiler stages — Crafting Interpreters](https://craftinginterpreters.com/a-map-of-the-territory.html)
- [LLVM language reference](https://llvm.org/docs/LangRef.html)
- [LLVM analysis and transform passes](https://llvm.org/docs/Passes.html)
- [CPython bytecode reference](https://docs.python.org/3.14/library/dis.html)
