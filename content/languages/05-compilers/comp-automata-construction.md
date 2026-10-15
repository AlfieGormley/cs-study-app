---
id: comp-automata-construction
title: "From regex rules to an executable DFA"
level: basic
minutes: 4
sourceLesson: comp-lexing
summary: "NFA state sets become DFA states, retaining accepting labels and priorities."
---

## From regex to automaton

How does a regex actually run? The classic route, used by lexer generators such as lex, flex and re2c, has three steps.

## 1. Regex to NFA (Thompson's construction)

Each piece of regex syntax becomes a small **nondeterministic finite automaton** fragment, glued together with ε transitions. ε (the Greek letter epsilon) stands for the empty string, so an ε transition is a move the automaton can make without reading any character. NFA simulation tracks a set of possible states. Thompson construction is linear in the expanded basic regex; counted repetitions may first need expansion.

## 2. NFA to DFA (subset construction)

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

## 3. Minimise

Hopcroft's algorithm merges states that behave identically, producing a minimal equivalent DFA while preserving token labels/priorities. A fixed DFA scans a candidate in linear time, but a maximal-munch lexer may revisit characters after backing up to its last accepting state. Token rules must bound that backup to guarantee overall O(n) time, where n is the number of characters in the input and O(n) means the work grows at most in proportion to n.

## The DFA as code

Hand-written lexers are often just a DFA expressed as `if` and `while`. For ASCII input, this version produces exactly the same tokens as the regex lexer for Calc:

```python
OPS = "+-*/^()="
DIGS = "0123456789"

def is_start(c):
    # Match this hand-written lexer’s ASCII
    # names.
    return c.isascii() and (
        c.isalpha() or c == "_")

def is_part(c):
    # Match this hand-written lexer’s ASCII
    # names.
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
            # Slice the full digit run once.
            num = src[i:j]
            out.append(Tok("NUM", num, i))
            i = j
        elif is_start(c):
            j = i
            while j < n and is_part(src[j]):
                j += 1
            # A keyword prefix is still one
            # name.
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

The branches and loops express scanner state transitions: a digit run, a name run, whitespace or an operator. This is hand-written finite-state scanning, not a literal one-to-one mapping between Python branches and states of the generated combined DFA.

## Key takeaways
- NFA state sets become DFA states, retaining accepting labels and priorities.
- A scanner remembers its last accepting point; unrestricted backup can cause rescanning.

## Further reading
- [Scanning — Crafting Interpreters](https://craftinginterpreters.com/scanning.html)
- [Python regular-expression matching](https://docs.python.org/3/library/re.html)
- [NFA simulation and backtracking — Russ Cox](https://swtch.com/~rsc/regexp/regexp1.html)
- [Longest matching and rule order — flex](https://westes.github.io/flex/manual/Matching.html)
- [Scanner performance and backup — flex](https://westes.github.io/flex/manual/Performance.html)
- [docs.rs — regex](https://docs.rs/regex/latest/regex/)
- [tc39.es — ecmascript-language-lexical-grammar.html](https://tc39.es/ecma262/multipage/ecmascript-language-lexical-grammar.html)
- [A DFA minimisation algorithm — Hopcroft’s original report](https://www.cs.cmu.edu/~cdm/resources/Hopcroft1971.pdf)
