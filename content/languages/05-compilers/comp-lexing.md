---
id: comp-lexing
title: "Lexing: from regular expressions to DFAs"
level: basic
minutes: 11
summary: How a lexer turns characters into tokens, why maximal munch matters, and how regular expressions become NFAs and then fast DFAs, with a working lexer for Calc.
---

Before a compiler can understand `let x = 5 in x * x`, it has to know that `let` is one word, `5` is a number, and the spaces mean nothing. That is the **lexer**'s job (also called a **scanner** or **tokeniser**).

It is the simplest stage of the pipeline, but it touches every character of every file, so it has to be fast. It is also where a surprising number of language design quirks live.

## Tokens, lexemes and kinds

A **lexeme** is a run of characters, such as `in1`. A **token** is a lexeme plus its classification and, usually, its position:

```
Tok(kind='NAME', text='in1', pos=4)
```

Calc chooses grammar branches from the kind (NAME, NUM, +...), while parsing also uses text to create numeric and name nodes: the number's value, or the name to look up.

Calc has five kinds of token:

| Kind | Pattern | Examples |
|---|---|---|
| NUM | `\d+` | `5`, `042` |
| NAME | `[A-Za-z_]\w*` | `x`, `in1` |
| keyword | `let`, `in` | `let` |
| operator | one of `+-*/^()=` | `*` |
| whitespace | `\s+` | discarded |

The patterns are written in regular-expression (regex) notation. Each symbol has a fixed meaning:

| Notation | Matches |
|---|---|
| `\d` | one decimal digit |
| `\w` | one word character: letter, digit or `_` |
| `\s` | one whitespace character |
| `[A-Za-z_]` | one character from the set: here a letter or `_` |
| `+` | the item before it, one or more times |
| `*` | the item before it, zero or more times |
| `{n}` | the item before it, exactly n times |
| `( )` | groups items into one item |

A vertical bar between two patterns means "either one": `let` or `in` is written with a bar between them. So `[A-Za-z_]\w*` reads "a letter or underscore, then any number of word characters".

Every one of these is a **regular expression**. That is no accident: token shapes are almost always **regular languages**, the class of patterns that a finite automaton can recognise using a fixed amount of memory. Nesting, like matching brackets, is *not* regular. That is the parser's problem, not the lexer's.

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
    pos, out = 0, []
    while pos < len(src):
        m = MASTER.match(src, pos)
        if not m:
            ch = src[pos]
            raise SyntaxError(
                f"bad char {ch!r} at {pos}")
        kind, text = m.lastgroup, m.group()
        if (kind == "NAME"
                and text in KEYWORDS):
            kind = text.upper()
        if kind == "OP":
            kind = text
        if kind != "WS":
            out.append(Tok(kind, text, pos))
        pos = m.end()
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

## Maximal munch

What should `letter` lex as? It starts with `let`, but it is obviously the name `letter`. Lexers follow the **maximal munch** (longest match) rule: always take the longest lexeme that forms a valid token.

Our lexer gets this right by matching the general NAME pattern first, which greedily eats `letter`, and only *then* checking a keyword table. `in1` likewise lexes as one NAME, not keyword `in` followed by `1`.

> [!warning] Python's `re` is not longest-match
> Python's alternation is **leftmost-first**: `=|==` matched against `==` returns `=`, because the first alternative that works wins. Lexer generators like flex choose the *longest* match across all rules. With `re`, you must order alternatives so longer operators come first (`==|=`).

Maximal munch has famous consequences. In C, `x---y` lexes as `x -- - y`, because the lexer grabs `--` greedily before the parser gets a say. Before C++11, `vector<vector<int>>` was a syntax error because `>>` lexed as the shift operator.

Ties between rules of equal length are broken by **rule order**: in flex, the rule listed first wins. That is how `let` becomes a keyword rather than a NAME when both match exactly three characters.

## From regex to automaton

How does a regex actually run? The classic route, used by lexer generators such as lex, flex and re2c, has three steps.

### 1. Regex to NFA (Thompson's construction)

Each piece of regex syntax becomes a small **nondeterministic finite automaton** fragment, glued together with ε transitions. ε (the Greek letter epsilon) stands for the empty string, so an ε transition is a move the automaton can make without reading any character. NFA simulation tracks a set of possible states. Thompson construction is linear in the expanded basic regex; counted repetitions may first need expansion.

### 2. NFA to DFA (subset construction)

A **deterministic** automaton (DFA) has exactly one next state per character. The subset (powerset) construction builds DFA states that each represent a *set* of NFA states the NFA could be in.

Here is a tiny example: the keyword `in` against the NAME rule `[a-z]+`, letters only for brevity.

```
NFA:  K0 -i-> K1 -n-> K2 (IN)
      N0 -[a-z]-> N1 (NAME)
      N1 -[a-z]-> N1

DFA state   NFA set      accepts
  S         {K0, N0}     -
  A  (S,i)  {K1, N1}     NAME
  B  (A,n)  {K2, N1}     IN, NAME
  C  other  {N1}         NAME
```

State B accepts both IN and NAME. Rule order breaks the tie, so `in` is a keyword. From B, another letter leads to C, so `ink` is a NAME. Maximal munch falls out naturally: keep running the DFA, remember the last accepting state you passed through, and back up to it when you get stuck.

### 3. Minimise

Hopcroft's algorithm merges states that behave identically, producing a minimal equivalent DFA while preserving token labels/priorities. A fixed DFA scans a candidate in linear time, but a maximal-munch lexer may revisit characters after backing up to its last accepting state. Token rules must bound that backup to guarantee overall O(n) time, where n is the number of characters in the input and O(n) means the work grows at most in proportion to n.

### The DFA as code

Hand-written lexers are often just a DFA expressed as `if` and `while`. For ASCII input, this version produces exactly the same tokens as the regex lexer for Calc:

```python
OPS = "+-*/^()="
DIGS = "0123456789"

def is_start(c):
    return c.isascii() and (
        c.isalpha() or c == "_")

def is_part(c):
    return c.isascii() and (
        c.isalnum() or c == "_")
```

```python
def lex_dfa(src):
    i, n, out = 0, len(src), []
    while i < n:
        c = src[i]
        if c.isspace():
            i += 1
        elif c in DIGS:
            j = i
            while j < n and src[j] in DIGS:
                j += 1
            num = src[i:j]
            out.append(Tok("NUM", num, i))
            i = j
        elif is_start(c):
            j = i
            while j < n and is_part(src[j]):
                j += 1
            text = src[i:j]
            kind = (text.upper()
                    if text in KEYWORDS
                    else "NAME")
            out.append(Tok(kind, text, i))
            i = j
        elif c in OPS:
            out.append(Tok(c, c, i))
            i += 1
        else:
            raise SyntaxError(
                f"bad char {c!r} at {i}")
    out.append(Tok("EOF", "", i))
    return out
```

Each branch is a DFA state; each inner `while` loop is a state with a self-transition.

## Why DFAs can be a trap, and why backtracking is worse

The subset construction can blow up. The classic example is the language "the third character from the end is `a`", over the two letters `a` and `b`, or in general "the nth character from the end". Its regex is `(a|b)*a(a|b){n-1}`: any run of `a`s and `b`s, then one `a`, then exactly n − 1 more letters. An NFA can *guess* which `a` is the one that matters, so it needs only a few states. A DFA cannot guess: it must remember the last n characters it has read, because any of them might turn out to be the one n from the end.

```formula
S_DFA = 2^n
S_NFA = n + 1
where
S_DFA: the number of states in the smallest DFA for the language
S_NFA: the number of states in the simple NFA for the same language
n: how far from the end the required `a` must be (n = 3 means the third character from the end)
2^n: n copies of 2 multiplied together: each of the last n characters is one of 2 letters, and every different history needs its own state
In words: each extra position the DFA must remember doubles its number of states, while the NFA grows by only one state.
```

For n = 3 the DFA needs 2 × 2 × 2 = 8 states against the NFA's 4; for n = 20 it needs 1,048,576. Real token patterns are simple, so lexers rarely hit this.

General-purpose regex engines in Python, Perl, Java and JavaScript take a different approach: **backtracking**. It supports features like back-references (`\1`, "match the same text that group 1 matched"), but some patterns take exponential time. Matching `(a+)+$` (one or more groups of one or more `a`s, then `$`, the end of the input) against `"aaa…ab"` fails because of the final `b`, and before Python's `re` can report the failure it tries every way of splitting the `a`s into groups:

```formula
W = 2^{k−1}
W = 2^{29} ≈ 5.4 × 10^8   when k = 30
where
W: the number of ways to split a run of `a`s into one or more non-empty groups; a backtracking engine may try each one before giving up
k: the number of `a` characters in the input
2^{k−1}: k − 1 copies of 2 multiplied together: each of the k − 1 gaps between neighbouring `a`s either is or is not a group boundary
≈: approximately equal to
In words: every extra `a` doubles the number of splits to try, so the matching time grows exponentially with the input length.
```

So 30 `a`s already mean over half a billion splits, and each extra `a` roughly doubles the time. This class of bug, **ReDoS**, has taken down production services. Engines like Google's RE2 and Rust's `regex` crate use automata-based techniques that avoid this exponential backtracking for supported syntax. A single search is linear in input length for a fixed pattern; regex size and repeated-search APIs also affect bounds.

> [!note] Our regex lexer is safe
> Calc's simple alternatives and disjoint starting classes avoid catastrophic ambiguity; its repeats can still backtrack internally. Nested ambiguous repetition is one source of trouble, not the only one.

## Lexers in the real world

- **Generated lexers.** flex turns a spec of regex rules into a table-driven DFA in C. re2c compiles the DFA into direct `goto` code, with performance depending on the generated scanner, target and workload.
- **Hand-written lexers.** GCC, Clang, Go, V8 and CPython (whose C tokenizer is hand-written) all lex by hand: it is not much code, it is fast, and it gives better error messages.
- **Context-sensitive corners.** Python's tokenizer emits `INDENT` and `DEDENT` tokens by keeping a stack of indentation widths, which a pure DFA cannot do. In JavaScript, `/` may start a regex literal or be division, depending on grammatical context, not just the immediately previous token. C's "lexer hack" feeds the symbol table back into the lexer so it can tell a typedef name from a variable.

## Pitfalls

- **Lexing does not validate structure.** `2x` lexes happily as `NUM NAME`; the parser rejects it.
- **Unicode surprises.** In Python, `\d` on a `str` matches any Unicode decimal digit, such as Arabic-Indic `٣`. Use `[0-9]` or `re.ASCII` if your language means ASCII only.
- **Losing positions.** Discarding positions makes precise source locations harder to recover.
- **Keyword lists in the regex.** Writing `let|in|[A-Za-z_]\w*` with Python's `re` lexes `letter` as `let` + `ter`. Match names first, then look keywords up.

## Key takeaways
- A lexer turns characters into a flat list of tokens (kind, text, position) and discards whitespace and comments.
- Many token shapes are regular; a complete lexer may also use context, modes or an indentation stack.
- Maximal munch takes the longest match; rule order breaks ties, which is how keywords beat names.
- Regex becomes an NFA (Thompson), then a DFA (subset construction), then optionally a minimized DFA; overall linear lexing also requires bounded rescanning for maximal munch.
- Backtracking regex engines can take exponential time; automaton-based engines like RE2 cannot.

## Further reading
- [Scanning — Crafting Interpreters](https://craftinginterpreters.com/scanning.html)
- [Regular Expression Matching Can Be Simple And Fast — Russ Cox](https://swtch.com/~rsc/regexp/regexp1.html)
- [Thompson's construction — Wikipedia](https://en.wikipedia.org/wiki/Thompson%27s_construction)
- [Powerset construction — Wikipedia](https://en.wikipedia.org/wiki/Powerset_construction)
- [Maximal munch — Wikipedia](https://en.wikipedia.org/wiki/Maximal_munch)
- [re — Regular expression operations (writing a tokenizer) — Python docs](https://docs.python.org/3/library/re.html)
- [Primary verification source 2](https://westes.github.io/flex/manual/Matching.html)
- [Primary verification source 3](https://westes.github.io/flex/manual/Performance.html)
- [Primary verification source 4](https://docs.rs/regex/latest/regex/)
- [Primary verification source 6](https://tc39.es/ecma262/multipage/ecmascript-language-lexical-grammar.html)
