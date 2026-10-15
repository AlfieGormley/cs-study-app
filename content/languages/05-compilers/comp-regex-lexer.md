---
id: comp-regex-lexer
title: "Build and trace the Calc regex lexer"
level: basic
minutes: 3
sourceLesson: comp-lexing
summary: "Named groups identify which token rule matched at the current position."
---

The previous unit defined token kinds and patterns. This unit assembles those patterns into a scanner. `Tok` stores kind, text and character position. Read the two Python fences as consecutive parts of one file; the transcript shows token kinds rather than execution of a Calc program.

## A working lexer for Calc

The quickest way to write a lexer in Python is to combine the token patterns into one big regex with named groups, and repeatedly match at the current position.

```python
import re
from typing import NamedTuple

class Tok(NamedTuple):
    kind: str
    text: str
    pos: int

SPEC = [
    ("NUM",  r"\d+"),
    ("NAME", r"[A-Za-z_]\w*"),
    ("OP",   r"[-+*/^()=]"),
    ("WS",   r"\s+"),
]
MASTER = re.compile("|".join(
    f"(?P<{k}>{p})" for k, p in SPEC))
KEYWORDS = {"let", "in"}
```

```python
def lex(src):
    # Keep character offsets for
    # diagnostics.
    pos, out = 0, []
    while pos < len(src):
        # Match here; never skip a bad
        # character.
        m = MASTER.match(src, pos)
        if not m:
            ch = src[pos]
            raise SyntaxError(
                f"bad char {ch!r} at {pos}")
        kind, text = m.lastgroup, m.group()
        # Classify keywords after the whole
        # name.
        if (kind == "NAME"
                and text in KEYWORDS):
            kind = text.upper()
        if kind == "OP":
            kind = text
        if kind != "WS":
            out.append(Tok(kind, text, pos))
        pos = m.end()
    # Give the parser an explicit end
    # marker.
    out.append(Tok("EOF", "", pos))
    return out
```

`m.lastgroup` tells us which named group matched. Operators use their own text as their kind, so the parser can ask "is the next token `+`?". An `EOF` token at the end saves the parser from checking for running off the list.

Running it on our example:

```
>>> [t.kind for t in lex("2 * (3 + 4)")]
['NUM', '*', '(', 'NUM', '+', 'NUM',
 ')', 'EOF']
>>> [t.kind for t in lex(
...     "let x = 5 in x*x")]
['LET', 'NAME', '=', 'NUM', 'IN', 'NAME',
 '*', 'NAME', 'EOF']
```

Note that `x*x` with no spaces still lexes correctly. Whitespace separates tokens only where two tokens would otherwise merge, such as `let x` versus `letx`.

## Key takeaways
- Named groups identify which token rule matched at the current position.
- Recognise a whole name before classifying keywords; append an EOF marker.

## Further reading
- [Scanning — Crafting Interpreters](https://craftinginterpreters.com/scanning.html)
- [Python regular-expression matching](https://docs.python.org/3/library/re.html)
- [NFA simulation and backtracking — Russ Cox](https://swtch.com/~rsc/regexp/regexp1.html)
- [Longest matching and rule order — flex](https://westes.github.io/flex/manual/Matching.html)
- [Scanner performance and backup — flex](https://westes.github.io/flex/manual/Performance.html)
- [docs.rs — regex](https://docs.rs/regex/latest/regex/)
- [tc39.es — ecmascript-language-lexical-grammar.html](https://tc39.es/ecma262/multipage/ecmascript-language-lexical-grammar.html)
