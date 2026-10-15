---
id: comp-recursive-descent
title: "Recursive descent and left recursion"
level: intermediate
minutes: 3
sourceLesson: comp-parsing
summary: "Recursive descent turns grammar structure into calls and loops."
---

The previous unit introduced Calc’s expression grammar. The excerpt below depends on its lexer and on the Num, Neg and BinOp tree classes introduced structurally in the pipeline trace; their Python declarations appear in the AST units. A whole-input wrapper must call expr and then consume EOF.

## Recursive descent

A common way to parse by hand is **recursive descent**: write one function per nonterminal, and let each function call the others as the grammar says. The grammar *becomes* the code. This is `RDParser` from our Calc compiler (no `let` or `^` yet):

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
        # Advance only after the kind
        # matches.
        self.i += 1
        return tok
```

```python
    def expr(self):
        node = self.term()
        while self.peek() in ("+", "-"):
            op = self.eat(self.peek()).kind
            rhs = self.term()
            # Nest the old result on the
            # left.
            node = BinOp(op, node, rhs)
        return node

    def term(self):
        node = self.factor()
        while self.peek() in ("*", "/"):
            op = self.eat(self.peek()).kind
            rhs = self.factor()
            # Nest the old result on the
            # left.
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

## The left-recursion trap

Why not write the rule the way BNF suggests, `expr = expr "+" term`? Translate it literally:

```python
def expr(self):
    left = self.expr()   # recurses
    ...                  # forever
```

`expr` calls itself before consuming any token, so it recurses until Python raises `RecursionError`. **Naive recursive descent cannot directly handle left recursion.** More advanced top-down algorithms, including CPython's PEG machinery, can support it. The standard fix is to rewrite it as repetition (`term { "+" term }`), exactly what we did, and build left-leaning trees in the loop.

## Delay a common-prefix choice

Suppose a factor may be a bare NAME or a call beginning with NAME followed by an opening bracket. One token cannot choose between these two alternatives: both begin with NAME. **Left factoring** reads NAME once, then examines the next token to choose the optional call suffix. This repairs that local choice; it does not prove the entire grammar LL(1). Empty alternatives also require checking which tokens can legally follow the rule.

## Key takeaways
- Recursive descent turns grammar structure into calls and loops.
- Left factoring delays a choice until the distinguishing token; it does not fix every grammar.

## Further reading
- [Parsing expressions — Crafting Interpreters](https://craftinginterpreters.com/parsing-expressions.html)
- [eli.thegreenplace.net — parsing-expressions-by-precedence-climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing)
- [CPython’s PEG parser — PEP 617](https://peps.python.org/pep-0617/)
- [www.gnu.org — Algorithm.html](https://www.gnu.org/software/bison/manual/html_node/Algorithm.html)
- [www.gnu.org — Shift_002fReduce.html](https://www.gnu.org/software/bison/manual/html_node/Shift_002fReduce.html)
- [tree-sitter.github.io — tree-sitter](https://tree-sitter.github.io/tree-sitter/)
