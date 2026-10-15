---
id: comp-parser-engineering
title: "Production parsers and recovering from errors"
level: intermediate
minutes: 3
sourceLesson: comp-parsing
summary: "PEG ordered choice differs from grammar ambiguity and from universal memoisation."
---

## Parsers in the real world

- **Hand-written recursive descent is used by major compilers.** GCC replaced its Bison-generated C++ parser with a hand-written one in GCC 3.4 (2004) and did the same for C in 4.1. Clang, Go, rustc, V8 and Swift have hand-written parsing code, as does the TypeScript 5.9 source parser with recursive-descent structure. Expression handling varies: some use precedence climbing, while Swift can first collect an operator sequence for later precedence handling.
- **Generators also serve production languages.** PostgreSQL's SQL grammar is a Bison file of many thousands of lines.
- **PEG parsers.** Since Python 3.9 (PEP 617), CPython uses a parser generated from a **parsing expression grammar**. PEGs use ordered choice, committing to the first successful alternative, so choice is defined rather than ambiguous. Memoization is an implementation technique (packrat parsing), not part of the definition of every PEG; CPython uses selective memoization and supports left recursion.
- **Editors.** Tree-sitter generates incremental GLR-style parsers that reuse unchanged subtrees and re-parse the affected region, which can extend beyond the literal edit and keep producing a tree when the code is half-typed.

## Error recovery

A parser that stops at the first error is annoying; one that reports 40 bogus errors after a single typo is worse. Calc's parser stops at the first problem but says exactly where:

```
>>> parse("2 * (3 +")
SyntaxError: unexpected 'EOF' at 8
>>> parse("let x = 1 x")
SyntaxError: expected IN, got 'x' at 10
```

One production technique is **panic-mode recovery**: on an error, skip tokens until a **synchronising token** such as `;` or `}`, then carry on, so one compile reports many independent errors. Hand-written parsers can also make guesses ("did you forget a `)`?"), one reason compilers abandon generators.

## Pitfalls

- **Forgetting `EOF`.** Without `expect("EOF")` at the end, `parse("2 3")` would quietly return `2` and ignore the rest. Calc reports `expected EOF, got '3' at 2`.
- **Wrong associativity.** Using `nxt = prec` for `-` makes `10 - 4 - 3` evaluate as 9. Test chains of every operator.
- **Unary minus precedence.** Languages disagree: in Python `-2 ** 2` is -4, while in Excel `=-2^2` is 4. Decide deliberately and write a test.
- **Deep nesting.** A recursive parser uses one stack frame per nesting level, so 10,000 nested pairs of brackets can exceed the parser or host stack limit. CPython limits nesting depth in its parser for this reason.

## Key takeaways
- PEG ordered choice differs from grammar ambiguity and from universal memoisation.
- Require EOF and bound nesting; recovery should avoid a cascade of false diagnostics.

## Further reading
- [Parsing expressions — Crafting Interpreters](https://craftinginterpreters.com/parsing-expressions.html)
- [eli.thegreenplace.net — parsing-expressions-by-precedence-climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing)
- [CPython’s PEG parser — PEP 617](https://peps.python.org/pep-0617/)
- [www.gnu.org — Algorithm.html](https://www.gnu.org/software/bison/manual/html_node/Algorithm.html)
- [www.gnu.org — Shift_002fReduce.html](https://www.gnu.org/software/bison/manual/html_node/Shift_002fReduce.html)
- [tree-sitter.github.io — tree-sitter](https://tree-sitter.github.io/tree-sitter/)
