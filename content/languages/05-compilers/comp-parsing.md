---
id: comp-parsing
title: "Parsing: grammars, recursive descent and precedence"
level: intermediate
minutes: 14
summary: How a parser turns a flat list of tokens into a tree, using grammars, recursive descent and precedence climbing, and how top-down LL parsing compares with bottom-up LR parsers like yacc and Bison.
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

A token sequence is syntactically admitted by that grammar if you can **derive** it from the start symbol by repeatedly replacing nonterminals. That derivation, drawn as a tree, is the **parse tree**.

Grammars can express nesting, which regular expressions cannot. The rule `"(" expr ")"` refers to itself, so brackets can nest to any depth. This is the power the lexer lacked.

### Ambiguity

The grammar above is **ambiguous**: `1 + 2 * 3` has two parse trees.

```
     +              *
    / \            / \
   1   *          +   3
      / \        / \
     2   3      1   2
    = 7           = 9
```

Both are valid derivations. A compiler cannot pick one at random, so we rewrite the grammar to encode **precedence** (which operator binds tighter) and **associativity** (which way a chain like `10 - 4 - 3` groups).

The classic fix uses one nonterminal per precedence level, written in **EBNF** where `{ ... }` means "zero or more":

```
expr   = term { ("+" | "-") term }
term   = factor { ("*" | "/") factor }
factor = NUM | "-" factor
       | "(" expr ")"
```

Now `1 + 2 * 3` has only one tree: an `expr` is a sum of `term`s, and `2 * 3` must be a single `term`. Multiplication sits deeper in the grammar, so it binds tighter.

## Recursive descent

The most popular way to parse by hand is **recursive descent**: write one function per nonterminal, and let each function call the others as the grammar says. The grammar *becomes* the code. This is `RDParser` from our Calc compiler (no `let` or `^` yet):

```python
class RDParser:
    def __init__(self, src):
        self.toks, self.i = lex(src), 0

    def peek(self):
        return self.toks[self.i].kind

    def eat(self, kind):
        tok = self.toks[self.i]
        if tok.kind != kind:
            raise SyntaxError(
                f"expected {kind}"
                f" at {tok.pos}")
        self.i += 1
        return tok
```

```python
    def expr(self):
        node = self.term()
        while self.peek() in ("+", "-"):
            op = self.eat(self.peek()).kind
            rhs = self.term()
            node = BinOp(op, node, rhs)
        return node

    def term(self):
        node = self.factor()
        while self.peek() in ("*", "/"):
            op = self.eat(self.peek()).kind
            rhs = self.factor()
            node = BinOp(op, node, rhs)
        return node

    def factor(self):
        if self.peek() == "NUM":
            tok = self.eat("NUM")
            return Num(int(tok.text))
        if self.peek() == "-":
            self.eat("-")
            return Neg(self.factor())
        self.eat("(")
        node = self.expr()
        self.eat(")")
        return node
```

Notice how the `while` loop builds the tree. For `10 - 4 - 3`, `expr` first gets `10`, then wraps it: `BinOp('-', 10, 4)`, then wraps *that*: `BinOp('-', BinOp('-', 10, 4), 3)`. Folding to the left gives **left associativity**, which is what we want: the answer is 3, not 9.

The parser decides what to do by looking at one upcoming token. In `factor`, `NUM`, `-` and `(` each select a different branch, and no token selects two. A grammar where one token of lookahead always picks the rule is called **LL(1)**: read **L**eft to right, build a **L**eftmost derivation, **1** token of lookahead.

### The left-recursion trap

Why not write the rule the way BNF suggests, `expr = expr "+" term`? Translate it literally:

```python
def expr(self):
    left = self.expr()   # recurses
    ...                  # forever
```

`expr` calls itself before consuming any token, so it recurses until Python raises `RecursionError`. **Naive recursive descent cannot directly handle left recursion.** More advanced top-down algorithms, including CPython's PEG machinery, can support it. The standard fix is to rewrite it as repetition (`term { "+" term }`), exactly what we did, and build left-leaning trees in the loop.

## Precedence climbing

One function per level gets tedious. C has around 15 precedence levels, so the "expression" in a C parser would be 15 nearly identical functions. **Precedence climbing** replaces them with one function and a table. Here are excerpts from a precedence-climbing parser that adds right-associative ^. It uses token-returning peek/advance/expect helpers, unlike the earlier kind-returning RDParser; these are alternative parser designs, not drop-in method replacements.

```python
BINARY = {               # op: (prec, assoc)
    "+": (1, "L"), "-": (1, "L"),
    "*": (2, "L"), "/": (2, "L"),
    "^": (3, "R"),
}
```

```python
    def expr(self, min_prec=1):
        if self.peek().kind == "LET":
            return self.let()
        left = self.unary()
        while self.peek().kind in BINARY:
            tok = self.peek()
            prec, assoc = BINARY[tok.kind]
            if prec < min_prec:
                break
            self.advance()
            if assoc == "L":
                nxt = prec + 1
            else:
                nxt = prec
            right = self.expr(nxt)
            left = BinOp(tok.kind, left,
                         right, tok.pos)
        return left
```

The idea: `expr(min_prec)` parses an expression containing only operators at least as strong as `min_prec`. When it meets a weaker operator, it stops and lets its caller deal with it.

The single line `nxt = prec + 1` versus `nxt = prec` controls associativity. Trace both:

```
1 - 2 - 3          expr(1)
  left = 1
  '-' prec 1 >= 1: right = expr(2)
     left = 2
     '-' prec 1 < 2: stop -> 2
  left = (1 - 2)
  '-' prec 1 >= 1: right = expr(2) -> 3
  left = ((1 - 2) - 3)      = -4
```

```
2 ^ 3 ^ 2          expr(1)
  left = 2
  '^' prec 3 >= 1: right = expr(3)
     left = 3
     '^' prec 3 >= 3: right = expr(3)
        -> 2
     left = (3 ^ 2)
  left = (2 ^ (3 ^ 2))      = 512
```

For a left-associative operator, the recursive call demands a *stronger* operator, so a second `-` is left for the outer loop. For `^`, the recursive call accepts the same level, so the second `^` is swallowed on the right. Maths convention, and Python's `**`, make power right-associative: `2 ^ 3 ^ 2` is 2⁹ = 512, not 8² = 64.

### Unary minus and let

The rest of Calc's parser is plain recursive descent:

```python
    def unary(self):
        if self.peek().kind == "-":
            tok = self.advance()
            # operand binds at ^ level,
            # so -2^2 is -(2^2)
            operand = self.expr(3)
            return Neg(operand, tok.pos)
        return self.atom()

    def let(self):
        tok = self.expect("LET")
        name = self.expect("NAME").text
        self.expect("=")
        value = self.expr()
        self.expect("IN")
        body = self.expr()
        return Let(name, value, body,
                   tok.pos)
```

Parsing the operand with `expr(3)` lets `^` bind tighter than unary minus, so `-2 ^ 2` is `-(2 ^ 2)` = -4, matching Python's `-2 ** 2`. And because `let`'s body is a full `expr()`, it extends as far right as possible: `let x = 1 in x + 2` is `let x = 1 in (x + 2)`.

> [!note] Pratt parsing
> Vaughan Pratt's 1973 "top-down operator precedence" generalises this: each token has a *prefix* handler (for `-x`, `(`, literals) and an *infix* handler with a binding power. It is essentially the same algorithm as precedence climbing, and it powers many hand-written parsers, including the one in *Crafting Interpreters*' clox.

## Bottom-up: LR parsing

Recursive descent is **top-down**: it starts from `expr` and predicts what comes next. **LR** parsers work **bottom-up**: they read tokens onto a stack (**shift**) and, when the top of the stack matches the right-hand side of a rule, replace it with the rule's nonterminal (**reduce**). Using the left-recursive grammar `E → E + T | T`, `T → T * F | F`, `F → NUM`:

```
stack      input      action
           2+3*4$     shift
2          +3*4$      reduce F
F          +3*4$      reduce T
T          +3*4$      reduce E
E          +3*4$      shift
E+         3*4$       shift
E+3        *4$        reduce F
E+F        *4$        reduce T
E+T        *4$        shift (see *)
E+T*       4$         shift
E+T*4      $          reduce F
E+T*F      $          reduce T->T*F
E+T        $          reduce E->E+T
E          $          accept
```

The key moment is `E+T` with `*` next. Reducing `E+T` to `E` would compute `2 + 3` first, which is wrong. The parser's lookahead says *shift*, so `3 * 4` is grouped first. A generator such as **yacc** or **GNU Bison** precomputes these decisions into a table from the grammar (usually LALR(1), a compact LR variant).

When a generated parse table has multiple possible actions for a state/lookahead, the generator reports a **conflict**. The famous one is the **dangling else**: in `if a if b s1 else s2`, does `else` belong to the inner or outer `if`? Bison reports a shift/reduce conflict and, by default, shifts, attaching `else` to the nearest `if`, which is what C and Java specify.

### LL versus LR

| | LL (top-down) | LR (bottom-up) |
|---|---|---|
| Usually | Hand-written | Generated |
| Left recursion | Must rewrite | Fine |
| Grammars | Smaller class | Larger class |
| Errors | Easy to tailor | Harder |

Every LL(1) grammar is LR(1), but not the reverse, so LR is strictly more powerful. In practice the power rarely matters, because real recursive descent parsers cheat: they peek further ahead, backtrack in a few places, or consult the symbol table.

## Parsers in the real world

- **Hand-written recursive descent is used by major compilers.** GCC replaced its Bison-generated C++ parser with a hand-written one in GCC 3.4 (2004) and did the same for C in 4.1. Clang, Go, rustc, V8, Swift and TypeScript all use hand-written recursive descent with precedence climbing for expressions.
- **Generators also serve production languages.** PostgreSQL's SQL grammar is a Bison file of many thousands of lines.
- **PEG parsers.** Since Python 3.9 (PEP 617), CPython uses a parser generated from a **parsing expression grammar**. PEGs use ordered choice, committing to the first successful alternative, so choice is defined rather than ambiguous. Memoization is an implementation technique (packrat parsing), not part of the definition of every PEG; CPython uses selective memoization and supports left recursion.
- **Editors.** Tree-sitter generates incremental GLR-style parsers that re-parse only the edited region and keep producing a tree when the code is half-typed.

## Error recovery

A parser that stops at the first error is annoying; one that reports 40 bogus errors after a single typo is worse. Calc's parser stops at the first problem but says exactly where:

```
>>> parse("2 * (3 +")
SyntaxError: unexpected 'EOF' at 8
>>> parse("let x = 1 x")
SyntaxError: expected IN, got 'x' at 10
```

One production technique is **panic mode** recovery: on an error, skip tokens until a **synchronising token** such as `;` or `}`, then carry on, so one compile reports many independent errors. Hand-written parsers can also make guesses ("did you forget a `)`?"), one reason compilers abandon generators.

## Pitfalls

- **Forgetting `EOF`.** Without `expect("EOF")` at the end, `parse("2 3")` would quietly return `2` and ignore the rest. Calc reports `expected EOF, got '3' at 2`.
- **Wrong associativity.** Using `nxt = prec` for `-` makes `10 - 4 - 3` evaluate as 9. Test chains of every operator.
- **Unary minus precedence.** Languages disagree: in Python `-2 ** 2` is -4, while in Excel `=-2^2` is 4. Decide deliberately and write a test.
- **Deep nesting.** A recursive parser uses one stack frame per nesting level, so `((((...))))` 10,000 deep can overflow the stack. CPython limits nesting depth in its parser for this reason.

## Key takeaways
- A parser checks a token list against a context-free grammar and builds a tree; grammars, unlike regexes, can describe nesting.
- Ambiguous grammars are fixed by encoding precedence (levels) and associativity (which side recurses).
- Simple recursive descent uses functions for grammar rules; naive left recursion is rewritten as loops, while specialized algorithms can support it.
- Precedence climbing uses one function and a table; `prec + 1` gives left associativity and `prec` gives right.
- LR parsers shift and reduce bottom-up, handle more grammars, and are usually generated (yacc, Bison); major compilers also use hand-written recursive descent.

## Further reading
- [Parsing Expressions — Crafting Interpreters](https://craftinginterpreters.com/parsing-expressions.html)
- [Parsing expressions by precedence climbing — Eli Bendersky](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing)
- [Simple but Powerful Pratt Parsing — Alex Kladov](https://matklad.github.io/2020/04/13/simple-but-powerful-pratt-parsing.html)
- [LR parser — Wikipedia](https://en.wikipedia.org/wiki/LR_parser)
- [PEP 617: New PEG parser for CPython](https://peps.python.org/pep-0617/)
- [GNU Bison manual](https://www.gnu.org/software/bison/manual/html_node/index.html)
- [Primary verification source 2](https://www.gnu.org/software/bison/manual/html_node/Shift_002fReduce.html)
