---
id: comp-ast-representations
title: "AST structure and source fidelity"
level: intermediate
minutes: 3
sourceLesson: comp-semantic-analysis
summary: "Calc drops redundant grouping syntax but retains source positions."
---

A parser guarantees that a program is *shaped* correctly. It cannot tell you that `let x = 5 in y + 1` is nonsense, because `y` is a perfectly good NAME token in a perfectly good position. Knowing that `y` was never defined requires remembering what *was* defined, and where. That is **semantic analysis**: checking the meaning of a program, not just its form.

It runs on the tree the parser built, so we start there.

## Parse trees versus abstract syntax trees

A **parse tree** (or concrete syntax tree) records every grammar rule used, including brackets and the intermediate `term` and `factor` levels. For `(2 + 3) * 4`:

```
 parse tree               AST
   expr
    |
   term                    *
  / | \                   / \
fac '*' fac              +   4
 |       |              / \
( expr )  4             2   3
  / | \
term + term
 |      |
 2      3
```

Calc's abstract syntax tree omits redundant grammar structure such as brackets. Other ASTs retain more source detail: Clang, for example, preserves parentheses. Chains of single-child nodes vanish too. Many compilers build an AST directly in the parser and never materialise the parse tree. Tools that must reproduce source exactly, such as formatters and refactoring tools, keep a *concrete* tree with whitespace and comments: Roslyn and rust-analyzer use lossless syntax representations. Tree-sitter preserves concrete nodes and source ranges but does not necessarily store every whitespace character as a node; tooling also retains source text.

## Calc's AST

Calc's AST is five Python classes declared with `@dataclass`. Each node also records the position of the token it came from, so later errors can point at the source.

```python
from dataclasses import dataclass, field

# pos is left out of == and repr, so trees
# compare by structure only.
POS = dict(default=0, compare=False,
           repr=False)

@dataclass
class Num:
    value: int
    pos: int = field(**POS)

@dataclass
class Var:
    name: str
    pos: int = field(**POS)

@dataclass
class Neg:
    operand: object
    pos: int = field(**POS)

@dataclass
class BinOp:
    op: str
    left: object
    right: object
    pos: int = field(**POS)

@dataclass
class Let:
    name: str
    value: object
    body: object
    pos: int = field(**POS)
```

Excluding `pos` from comparison means `parse("1+2") == parse("1 + 2")` is `True`, which makes tests pleasant to write.

## Key takeaways
- Calc drops redundant grouping syntax but retains source positions.
- Source-preserving tools can retain concrete syntax and trivia instead.

## Further reading
- [Resolving and binding — Crafting Interpreters](https://craftinginterpreters.com/resolving-and-binding.html)
- [clang.llvm.org — IntroductionToTheClangAST.html](https://clang.llvm.org/docs/IntroductionToTheClangAST.html)
- [clang.llvm.org — classclang_1_1RecursiveASTVisitor.html](https://clang.llvm.org/doxygen/classclang_1_1RecursiveASTVisitor.html)
- [Python symbol-table interface](https://docs.python.org/3/library/symtable.html)
- [docs.python.org — programming.html](https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value)
- [rustc-dev-guide.rust-lang.org — overview.html](https://rustc-dev-guide.rust-lang.org/overview.html)
- [Python arithmetic operators](https://docs.python.org/3/library/operator.html)
