---
id: comp-pipeline
title: The compiler pipeline
level: basic
minutes: 9
summary: What compilers and interpreters actually do, the stages from source text to running code, and the tiny expression language Calc that the rest of this module builds.
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

That split is the reason the middle exists at all. With M languages and N machines, writing a compiler for every pair takes M × N compilers. With a shared **intermediate representation** (IR), you write M front ends and N back ends: M + N. This explains the modular architecture of **LLVM**, although runtimes, ABIs and language-specific work remain: Clang (C/C++), rustc, Swift and Julia all emit LLVM IR, and LLVM's back ends turn that into x86-64, ARM64, RISC-V, WebAssembly and more.

## Meet Calc, our running example

To make every stage concrete, this module builds a compiler for **Calc**, a language of integer arithmetic with local names:

```
2 * (3 + 4)
let x = 5 in x * x - 1
let a = 3 in let b = a * a in b - a
```

- Integers, `+ - * /`, unary minus and brackets.
- `/` is floor division, like Python's `//`.
- `let NAME = e1 in e2` evaluates `e1`, binds it to `NAME`, then evaluates `e2`. The name is only visible inside `e2`.
- Later lessons add ^ (power), accepting nonnegative integer exponents; negative exponents raise ArithmeticError, and 0^0 is 1. This keeps successful results integral.

Small as it is, Calc needs a lexer, a parser that respects precedence, a scope-aware checker, an optimiser and a code generator. The lessons present teaching excerpts; some depend on helper classes and wrapper code shown elsewhere or omitted. This review records which assembled examples were executed, rather than claiming every excerpt is standalone.

## Tracing one expression end to end

Follow `2 * (3 + 4)` through each stage.

### 1. Lexing

The lexer groups characters into **tokens** and throws away spaces:

```
NUM '2'  *  (  NUM '3'  +  NUM '4'  )  EOF
```

It knows nothing about precedence or brackets matching. It only knows what a number looks like.

### 2. Parsing

The parser checks that the tokens form a valid sentence of the grammar and builds a tree that captures the structure. The brackets disappear: their job was to shape the tree.

```diagram
      *
     / \
    2   +
       / \
      3   4
```

In Python this is an **AST** (abstract syntax tree) made of small objects:

```
BinOp('*', Num(2),
      BinOp('+', Num(3), Num(4)))
```

### 3. Semantic analysis

In this pipeline the checker walks the tree, looking for errors the grammar does not encode: using an undefined name, dividing by a constant zero, or (in typed languages) adding a string to an integer. `2 * (3 + 4)` is clean.

### 4. IR and optimisation

The tree is flattened into **three-address code**, where each instruction has at most one operator:

```
t1 = 3 + 4
t2 = 2 * t1
ret t2
```

An optimiser notices that both operations have constant inputs and **folds** them at compile time:

```
ret 14
```

### 5. Code generation

Without optimisation, our back end emits bytecode for a small stack machine:

```
PUSH 2
PUSH 3
PUSH 4
ADD        stack: [2, 7]
MUL        stack: [14]
```

A native back end would instead emit machine instructions and decide which CPU registers hold which values.

> [!tip] Real compilers do the same
> Run `python3 -c "import dis; dis.dis('2 * (3 + 4)')"`. CPython 3.14 includes a LOAD_SMALL_INT loading14, with surrounding bookkeeping/return instructions: its compiler folded the constant, exactly as above. Older versions print `LOAD_CONST 14`.

## Compilers, interpreters and everything between

"Compiled versus interpreted" is a spectrum, not a binary.

| Strategy | Example | Trade-off |
|---|---|---|
| Tree-walking | Early Ruby (MRI) | Simple, slow |
| Bytecode VM | CPython, Lua | Portable, moderate |
| JIT | V8, HotSpot, PyPy | Fast, complex |
| Ahead-of-time | GCC, Go, Rust | Fast start, big build |

Most production systems mix strategies. `javac` compiles Java to bytecode ahead of time; the HotSpot JVM then interprets that bytecode and JIT-compiles the hot parts. V8 parses JavaScript, generates bytecode for its Ignition interpreter, and compiles hot functions with Sparkplug, Maglev and TurboFan. Lesson 7 covers this.

A compiler that translates between languages at a similar level is often called a **transpiler**: TypeScript's `tsc` emits JavaScript, and Babel rewrites modern JavaScript into older JavaScript.

## Passes, and why there are so many

Each step through the program is a **pass**. Limited memory motivated some early single-pass designs; other compilers used multiple passes. Declaration rules are language choices. Modern optimising compilers run dozens of passes over the IR. Exact pass counts depend on compiler version, options and program; no universal count is supplied here.

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
- **"The optimiser makes code optimal."** It makes code *better*. Truly optimal code generation is undecidable in general.
- **"Parsing is the hard part."** For expression languages it is well understood. The hard engineering is in optimisation, code generation, error messages and speed of compilation.

## Key takeaways
- A compiler translates representations; an interpreter executes them. Compile-time evaluation and JIT compilation can combine these activities. Real systems usually mix the two.
- The pipeline is lex, parse, check, IR plus optimisation, then code generation.
- A shared IR turns M × N language-machine pairs into M + N pieces, which is how LLVM supports many languages and targets.
- Each stage catches different errors; some errors cannot be found until runtime.
- Calc, our running example, goes `2 * (3 + 4)` to tokens, to a tree, to IR, and to bytecode or simply `14`.

## Further reading
- [A Map of the Territory — Crafting Interpreters](https://craftinginterpreters.com/a-map-of-the-territory.html)
- [Compiler — Wikipedia](https://en.wikipedia.org/wiki/Compiler)
- [Intermediate representation — Wikipedia](https://en.wikipedia.org/wiki/Intermediate_representation)
- [Compiler Explorer (see real compiler output)](https://godbolt.org/)
- [dis: Python bytecode disassembler — Python docs](https://docs.python.org/3/library/dis.html)
- [Primary verification source 1](https://llvm.org/docs/LangRef.html)
- [Primary verification source 2](https://llvm.org/docs/Passes.html)
