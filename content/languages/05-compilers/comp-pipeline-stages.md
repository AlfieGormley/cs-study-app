---
id: comp-pipeline-stages
title: "The compiler pipeline and shared IR"
level: basic
minutes: 3
sourceLesson: comp-pipeline
summary: "A front end handles source-language rules; a back end handles target-machine rules."
---

A CPU cannot run `2 * (3 + 4)`. It runs instructions like "load 3 into a register" and "multiply two registers". Something has to bridge the gap between text a human wrote and instructions a machine executes. That something is a **compiler**, an **interpreter**, or a mix of both.

A **compiler** translates a program into another language, usually a lower-level one. Translation is distinct from executing the resulting program, although compilers may evaluate constants or run compile-time code. An **interpreter** runs the program directly. The distinction is about the implementation, not the language: Python has an interpreter (CPython), a JIT compiler (PyPy) and ahead-of-time compilers (Cython, Nuitka).

## The pipeline at a glance

Almost every compiler is a chain of stages. Stages transform representations or compute facts about them; analysis and many optimization passes do not lower abstraction.

```flow
Source text: 2 * (3 + 4)
Lexer: characters → tokens
Parser: tokens → syntax tree
Semantic analysis: names, types, errors
IR + optimisation: simpler, faster code
Code generation: machine code / bytecode
Target code
```

The stages are usually grouped into three parts:

| Part | Stages | Depends on |
|---|---|---|
| Front end | lex, parse, check | Source language |
| Middle end | IR, optimisation | Mostly shared; language semantics and target costs still matter |
| Back end | codegen, reg. alloc | Target machine |

That split is the reason the middle exists at all. Suppose you must support several source languages on several machines. Writing a separate compiler for every language–machine pair *multiplies* the work; a shared **intermediate representation** (IR), a common in-between form that every front end produces and every back end consumes, only *adds* it:

```formula
C_direct = MN
C_shared = M + N
where
C_direct: the number of separate compilers needed when each one goes straight from one source language to one machine
C_shared: the number of pieces needed with a shared IR: one front end per language plus one back end per machine (the single shared optimiser is not counted)
M: the number of source languages, such as C, Rust and Swift
N: the number of target machines (CPU architectures), such as x86-64 and ARM64
In words: without a shared IR every language must be paired with every machine; with one, each language and each machine is written only once.
```

For example, 4 languages and 5 machines need 4 × 5 = 20 direct compilers, but only 4 + 5 = 9 pieces with a shared IR, and adding a sixth machine costs one new back end instead of four new compilers. The count is idealised: runtimes, ABIs (the rules for how compiled code calls functions and lays out data on a platform) and language-specific work remain. This explains the modular architecture of **LLVM**: Clang (C/C++), rustc, Swift and Julia all emit LLVM IR, and LLVM's back ends turn that into x86-64, ARM64, RISC-V, WebAssembly and more.

## Key takeaways
- A front end handles source-language rules; a back end handles target-machine rules.
- The shared-IR piece count is an architecture model, not an engineering effort estimate.

## Further reading
- [Compiler stages — Crafting Interpreters](https://craftinginterpreters.com/a-map-of-the-territory.html)
- [LLVM language reference](https://llvm.org/docs/LangRef.html)
- [LLVM analysis and transform passes](https://llvm.org/docs/Passes.html)
- [CPython bytecode reference](https://docs.python.org/3.14/library/dis.html)
