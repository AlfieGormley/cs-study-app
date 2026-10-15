---
id: comp-grammar-grouping
title: "Grammars, ambiguity and expression grouping"
level: intermediate
minutes: 3
sourceLesson: comp-parsing
summary: "A grammar derives terminal sequences from a start symbol."
---

The lexer hands over a flat list: `NUM * ( NUM + NUM )`. The **parser** recovers the structure hiding in it: which operator applies to which operands, and where each `let` ends. Its output is a tree, and later stages may analyze that tree or lower it into other IRs.

A parser has two jobs. It **recognises** whether the tokens form a valid program, and it **builds** a tree that records how they fit together. Most of the interesting design questions come from one fact: `1 + 2 * 3` must mean `1 + (2 * 3)`, not `(1 + 2) * 3`.

## Grammars

A language's syntax is described by a **context-free grammar** (CFG): a set of rules, each saying how a **nonterminal** (a syntactic category such as `expr`) can be built from terminals (tokens) and other nonterminals. Written in BNF:

```
expr ::= expr "+" expr
       | expr "*" expr
       | "(" expr ")"
       | NUM
```

Reading the notation: `::=` means "can be made of", the vertical bar separates alternatives ("or"), text in quotes is a literal token that must appear exactly, and a capitalised name like `NUM` is a token kind from the lexer. So the first line says "an `expr` can be an `expr`, then a `+` token, then another `expr`".

A token sequence is syntactically admitted by that grammar if you can **derive** it from the start symbol by repeatedly replacing nonterminals. That derivation, drawn as a tree, is the **parse tree**.

Context-free grammars can express unbounded balanced nesting, which classical regular expressions cannot. Some programming regex engines add nonregular features; those are outside that comparison. The rule `"(" expr ")"` refers to itself, so brackets can nest to any depth. This is the power the lexer lacked.

## Ambiguity

The grammar above is an **ambiguous grammar**: `1 + 2 * 3` has two parse trees.

```
     +              *
    / \            / \
   1   *          +   3
      / \        / \
     2   3      1   2
    = 7           = 9
```

Both are valid derivations. A compiler cannot pick one at random, so we rewrite the grammar to encode **precedence** (which operator binds tighter) and **associativity** (which way a chain like `10 - 4 - 3` groups).

The classic fix uses one nonterminal per precedence level, written in **EBNF** (extended BNF). Here `=` plays the role of `::=`, `{ ... }` means "zero or more repetitions of what is inside", and round brackets group alternatives, so `("+" | "-")` means "a `+` or a `-`":

```
expr   = term { ("+" | "-") term }
term   = factor { ("*" | "/") factor }
factor = NUM | "-" factor
       | "(" expr ")"
```

Now `1 + 2 * 3` has only one tree: an `expr` is a sum of `term`s, and `2 * 3` must be a single `term`. Multiplication sits deeper in the grammar, so it binds tighter.

## Key takeaways
- A grammar derives terminal sequences from a start symbol.
- Separate precedence levels remove this expression grammar’s ambiguity.

## Further reading
- [Parsing expressions — Crafting Interpreters](https://craftinginterpreters.com/parsing-expressions.html)
- [eli.thegreenplace.net — parsing-expressions-by-precedence-climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing)
- [CPython’s PEG parser — PEP 617](https://peps.python.org/pep-0617/)
- [www.gnu.org — Algorithm.html](https://www.gnu.org/software/bison/manual/html_node/Algorithm.html)
- [www.gnu.org — Shift_002fReduce.html](https://www.gnu.org/software/bison/manual/html_node/Shift_002fReduce.html)
- [tree-sitter.github.io — tree-sitter](https://tree-sitter.github.io/tree-sitter/)
