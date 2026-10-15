---
id: comp-precedence-climbing
title: "Precedence climbing, power and unary minus"
level: intermediate
minutes: 5
sourceLesson: comp-parsing
summary: "A stronger recursive threshold makes binary operators left associative."
---

This alternative parser uses the Calc lexer and AST node constructors. The complete token helpers and atom method are scaffolding omitted from this teaching excerpt: atom accepts numbers and parenthesised expressions, while the outer parse wrapper requires EOF. Keep the operator table’s minimum level aligned with the default expression threshold.

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
            # Leave weaker operators for the
            # caller.
            if prec < min_prec:
                break
            self.advance()
            if assoc == "L":
                nxt = prec + 1
            else:
                nxt = prec
            # The threshold controls
            # associativity.
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

For a left-associative operator, the recursive call demands a *stronger* operator, so a second `-` is left for the outer loop. For `^`, the recursive call accepts the same level, so the second `^` is swallowed on the right. Maths convention, and Python's `**`, make power right-associative, and the two groupings give very different answers:

```formula
2 ^ (3 ^ 2) = 2^9 = 512
(2 ^ 3) ^ 2 = 8^2 = 64
where
^: "raised to the power": as many copies of the left number multiplied together as the right number says, so 3 ^ 2 = 3 × 3 = 9 and 2 ^ 3 = 2 × 2 × 2 = 8
2^9: 2 raised to the power 9 (nine 2s multiplied together)
8^2: 8 raised to the power 2, which is 8 × 8
In words: right associativity works out the top exponent first, so `2 ^ 3 ^ 2` means 2 to the power 9, which is 512, not 8 squared, which is 64.
```

So `2 ^ 3 ^ 2` in Calc is 512.

## Unary minus and let

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
        # The initializer precedes the IN
        # token.
        value = self.expr()
        self.expect("IN")
        body = self.expr()
        return Let(name, value, body,
                   tok.pos)
```

Parsing the operand with `expr(3)` lets `^` bind tighter than unary minus, so `-2 ^ 2` is `-(2 ^ 2)`, which is -4, matching Python's `-2 ** 2`. And because `let`'s body is a full `expr()`, it extends as far right as possible: `let x = 1 in x + 2` is `let x = 1 in (x + 2)`.

> [!note] Pratt parsing
> Vaughan Pratt's 1973 "top-down operator precedence" generalises this: each token has a *prefix* handler (for `-x`, `(`, literals) and an *infix* handler with a binding power. Its expression core is closely related to precedence climbing, while its per-token handlers also organise prefix and other operator forms, and it powers many hand-written parsers, including the one in *Crafting Interpreters*' clox.

## Extending the table safely

The default minimum precedence is 1. Adding an equality operator at level 0 without lowering the initial threshold leaves that operator unconsumed, and the whole-input EOF check rejects it. Every entry point that should accept the new level must use an appropriate threshold. The table, lexer and wrapper therefore form one contract.

## Key takeaways
- A stronger recursive threshold makes binary operators left associative.
- Calc’s power is right associative and binds more tightly than unary minus.

## Further reading
- [Parsing expressions — Crafting Interpreters](https://craftinginterpreters.com/parsing-expressions.html)
- [eli.thegreenplace.net — parsing-expressions-by-precedence-climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing)
- [CPython’s PEG parser — PEP 617](https://peps.python.org/pep-0617/)
- [www.gnu.org — Algorithm.html](https://www.gnu.org/software/bison/manual/html_node/Algorithm.html)
- [www.gnu.org — Shift_002fReduce.html](https://www.gnu.org/software/bison/manual/html_node/Shift_002fReduce.html)
- [tree-sitter.github.io — tree-sitter](https://tree-sitter.github.io/tree-sitter/)
