---
id: comp-calc-trace
title: "Trace Calc from text to bytecode"
level: basic
minutes: 4
sourceLesson: comp-pipeline
summary: "Calc uses integer floor division and nonnegative integer powers."
---

## Meet Calc, our running example

To make every stage concrete, this module builds a compiler for **Calc**, a language of integer arithmetic with local names:

```
2 * (3 + 4)
let x = 5 in x * x - 1
let a = 3 in let b = a * a in b - a
```

- Integers, `+ - * /`, unary minus and brackets.
- `/` is floor division, like Python's `//`: it divides and then rounds *down*, so `7 / 2` is 3 and `-7 / 2` is -4.
- `let NAME = e1 in e2` evaluates `e1`, binds it to `NAME`, then evaluates `e2`. The name is only visible inside `e2`.
- Later lessons add `^` (power, so `2 ^ 3` evaluates to 8), accepting nonnegative integer exponents; negative exponents raise `ArithmeticError`, and `0 ^ 0` is 1. This keeps successful results integral.

Small as it is, Calc needs a lexer, a parser that respects precedence, a scope-aware checker, an optimiser and a code generator. The lessons present teaching excerpts; some depend on helper classes and wrapper code shown elsewhere or omitted. This review records which assembled examples were executed, rather than claiming every excerpt is standalone.

## Tracing one expression end to end

Follow `2 * (3 + 4)` through each stage.

## 1. Lexing

The lexer groups characters into **tokens** and throws away spaces:

```
NUM '2'  *  (  NUM '3'  +  NUM '4'  )  EOF
```

It knows nothing about precedence or brackets matching. It only knows what a number looks like.

## 2. Parsing

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

## 3. Semantic analysis

In this pipeline the checker walks the tree, looking for errors the grammar does not encode: using an undefined name, dividing by a constant zero, or (in typed languages) adding a string to an integer. `2 * (3 + 4)` is clean. This teaching checker tests only whether a divisor is a literal zero node. It does not evaluate a compound divisor such as `2 - 2`; later optimisation may expose more constants.

## 4. IR and optimisation

The tree is flattened into **three-address code**, where each instruction has at most one operator:

```
t1 = 3 + 4
t2 = 2 * t1
ret t2
```

An optimiser notices that both operations have constant inputs and computes them at compile time, which is called **constant folding**:

```
ret 14
```

## 5. Code generation

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
> Run `python3 -c "import dis; dis.dis('2 * (3 + 4)')"`. CPython 3.14 shows a `LOAD_SMALL_INT 14` instruction, with surrounding bookkeeping/return instructions: its compiler folded the constant, exactly as above. Older versions print `LOAD_CONST 14`.

## Key takeaways
- Calc uses integer floor division and nonnegative integer powers.
- Tokens identify pieces; the AST records grouping; constant folding computes known results.

## Further reading
- [Compiler stages — Crafting Interpreters](https://craftinginterpreters.com/a-map-of-the-territory.html)
- [LLVM language reference](https://llvm.org/docs/LangRef.html)
- [LLVM analysis and transform passes](https://llvm.org/docs/Passes.html)
- [CPython bytecode reference](https://docs.python.org/3.14/library/dis.html)
