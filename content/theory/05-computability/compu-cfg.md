---
id: compu-cfg
title: Context-free grammars
level: basic
minutes: 11
summary: Grammars that can count and nest, how derivations and parse trees work, ambiguity, Chomsky normal form and the CYK parsing algorithm.
---

Finite automata have a fixed, finite memory. That is why no DFA can recognise `aⁿbⁿ` (some number of a's followed by the same number of b's): to check the b's, it would have to remember an unbounded count of a's.

Yet the languages programmers care about are full of exactly this kind of matching. Every `(` needs a `)`. Every `{` needs a `}`. Nested block structures can have arbitrarily many pending delimiters in the mathematical model; concrete language and markup rules add their own exceptions and constraints. **Context-free grammars** (CFGs) are the next step up the ladder. They can describe nesting, and they are the formal basis of almost every programming-language parser.

## The idea: rewrite rules

A grammar is a set of rewrite rules. You start from a start symbol and keep replacing symbols until only real characters remain.

Here is a grammar for `aⁿbⁿ` (n ≥ 0):

```
S → a S b
S → ε
```

Read it as: "an S is either an `a`, then another S, then a `b`; or it is the empty string ε". Writing both on one line with a bar is the usual shorthand: `S → aSb | ε`.

To produce `aabb`, rewrite step by step. Each `⇒` is one rule application, called a **derivation step**:

```
S ⇒ aSb ⇒ aaSbb ⇒ aabb
```

Every time an `a` is added, a matching `b` is added on the other side. The grammar never has to count; the structure of the rule does the matching for it.

## The formal definition

A context-free grammar is a 4-tuple G = (V, Σ, R, S):

- **V**: a finite set of **variables** (non-terminals), such as S, E, T.
- **Σ**: a finite set of **terminals**, the actual characters, disjoint from V.
- **R**: a finite set of **rules** of the form `A → w`, where A is a single variable and w is any string of variables and terminals (possibly ε).
- **S**: the start variable, S ∈ V.

The language of G, written L(G), is the set of all terminal strings that can be derived from S. A language is **context-free** if some CFG generates it.

> [!note] Why "context-free"?
> The left-hand side of every rule is a single variable. So you may rewrite A no matter what surrounds it: its context is irrelevant. *Context-sensitive* grammars allow rules like `aAb → aXb`, where A may only be rewritten between an a and a b. Those are strictly more powerful.

Every regular language is context-free (a DFA translates directly into a grammar with rules like `A → 0B`), but not the other way round: `aⁿbⁿ` is context-free and not regular.

## Simulating a grammar in Python

For the balanced-parentheses grammar below, breadth-first search over **sentential forms** (partly rewritten strings), always expanding the leftmost variable, enumerates all strings up to the bound. Terminals are single characters, and all variables must be keys of G. This routine is not a terminating enumerator for arbitrary CFGs: a rule such as S → SS can grow variables indefinitely without exceeding a terminal-count bound. For general CFGs, enumerate the finitely many candidate terminal strings and decide membership with a parser.

```python
from collections import deque

def generate(G, start, maxlen):
    out, seen = set(), set()
    q = deque([(start,)])
    while q:
        f = q.popleft()
        if f in seen:
            continue
        seen.add(f)
        terms = [x for x in f if x not in G]
        if len(terms) > maxlen:
            continue
        i = next((k for k, x in enumerate(f)
                  if x in G), None)
        if i is None:   # all terminals
            out.add("".join(f))
            continue
        for rhs in G[f[i]]:
            q.append(f[:i] + rhs + f[i+1:])
    return sorted(out, key=lambda s:
                  (len(s), s))

P = {"S": [("(", "S", ")", "S"), ()]}
print(generate(P, "S", 6))
```

The grammar `S → (S)S | ε` describes balanced parentheses. The output lists all 9 balanced strings of length at most 6: `''`, `()`, `(())`, `()()`, and the five of length 6. (The counts 1, 1, 2, 5 for lengths 0, 2, 4, 6 are the Catalan numbers, which turn up all over grammar theory.)

## Parse trees

A derivation is a sequence; a **parse tree** shows the structure. Each internal node is a variable, its children are the right-hand side of the rule used, and reading the leaves left to right gives the string.

For arithmetic, a classic grammar is:

```
E → E + T | T
T → T * F | F
F → ( E ) | id
```

The parse tree for `id + id * id` is:

```
          E
        / | \
       E  +  T
       |   / | \
       T  T  *  F
       |  |     |
       F  F     id
       |  |
       id id
```

The tree puts `id * id` lower down, so it is grouped first. That is operator precedence, encoded purely by the shape of the grammar: `*` lives at the T level, beneath `+` at the E level. Left recursion (`E → E + T`) makes `+` left-associative, so `a + b + c` means `(a + b) + c`.

A **leftmost derivation** always rewrites the leftmost variable. There is a one-to-one match between parse trees and leftmost derivations, so "how many parse trees" and "how many leftmost derivations" are the same question.

## Ambiguity

A grammar is **ambiguous** if some string has two or more different parse trees. The tempting short grammar for arithmetic is ambiguous:

```
E → E + E | E * E | id
```

`id + id * id` now has two trees: one groups `(id + id) * id`, the other `id + (id * id)`. The grammar alone leaves grouping unspecified; a parser needs an additional disambiguation policy or an unambiguous grammar.

The problem gets worse with length. With n operands, the number of parse trees is the Catalan number C(n−1): 1, 1, 2, 5, 14, 42, 132 for n = 1 to 7. This short recursive count confirms it:

```python
from functools import lru_cache

@lru_cache(None)
def trees(n):          # n operands
    if n == 1:
        return 1
    # split into left k and right n-k
    return sum(trees(k) * trees(n - k)
               for k in range(1, n))

print([trees(n) for n in range(1, 8)])
# [1, 1, 2, 5, 14, 42, 132]
```

The famous real-world case is the **dangling else**:

```
S → if C then S
  | if C then S else S
  | other
```

In `if a then if b then x else y`, does `else y` belong to the inner or the outer `if`? C, C++ and Java all resolve it by convention: the `else` binds to the nearest eligible unmatched `if`. Parser generators such as yacc and Bison report this as a *shift/reduce conflict* and resolve it by shifting, which gives the same answer.

> [!warning] Ambiguity is a property of grammars, mostly
> You can usually remove ambiguity by rewriting the grammar (as the E/T/F grammar does). But some context-free *languages* are **inherently ambiguous**: every grammar for them is ambiguous. A standard example is { aⁱbʲcᵏ : i = j or j = k }. In the obvious union grammar, strings with i = j = k have two derivations. That observation alone does not prove inherent ambiguity: the theorem rules out every equivalent unambiguous CFG, not just this construction. Deciding whether an arbitrary CFG is ambiguous is also undecidable; a full proof of these results is beyond this lesson.

## Chomsky normal form and CYK

A grammar is in **Chomsky normal form** (CNF) if every rule is one of:

- `A → B C` (exactly two variables), or
- `A → a` (exactly one terminal),
- plus optionally `S → ε` if the empty string is in the language. If this exception is used, S must not appear on any right-hand side, so the empty production cannot occur inside a nonempty derivation.

Every CFG can be converted to CNF mechanically: add a fresh start variable, remove ε-rules, remove unit rules like `A → B`, replace terminals in mixed/long right-hand sides with fresh variables, and break long right-hand sides into chains of pairs. For `aⁿbⁿ` with n ≥ 1:

```
S → A T | A B
T → S B
A → a
B → b
```

CNF matters because it makes parsing a clean dynamic programme. In CNF, a derivation of a string of length n ≥ 1 takes exactly 2n − 1 steps, with n terminal-production nodes and n − 1 binary-production nodes. The variable skeleton is a full binary tree; terminal-production nodes still have one terminal child in the complete parse tree.

The **CYK algorithm** (Cocke–Younger–Kasami) fills a table where `t[i][j]` holds every variable that can derive the substring from position i to j:

```python
RULES = [("S", "A", "T"), ("S", "A", "B"),
         ("T", "S", "B")]
TERM = {"a": {"A"}, "b": {"B"}}

def cyk(w):
    n = len(w)
    t = [[set() for _ in range(n)]
         for _ in range(n)]
    for i, c in enumerate(w):
        t[i][i] = set(TERM.get(c, ()))
    for L in range(2, n + 1):     # span
        for i in range(n - L + 1):
            j = i + L - 1
            for k in range(i, j):  # split
                for A, B, C in RULES:
                    if (B in t[i][k] and
                        C in t[k+1][j]):
                        t[i][j].add(A)
    return n > 0 and "S" in t[0][n-1]

for w in ["ab", "aabb", "aab", "abab"]:
    print(w, cyk(w))
# ab True / aabb True
# aab False / abab False
```

The three nested loops over span, start and split point give **O(n³ · |G|)** time, where |G| is the grammar size. That proves every CFL can be parsed in polynomial time.

## Real-world use

- **Language specifications** are written as grammars, usually in BNF or EBNF notation. The JSON specification at json.org is a short grammar; Python's full grammar is published in its reference manual.
- **Parser generators** take grammars and produce parsers. Deterministic LL(k) and LR(k) parsers have linear input-time bounds for a fixed suitable grammar. Bison also offers GLR parsing, and ANTLR uses adaptive prediction; these capabilities should not all be described as fixed-k deterministic parsing with the same guarantee.
- **Python 3.9+** replaced its LL(1) parser with a PEG parser (PEP 617). PEGs look like CFGs but use *ordered choice* (`A / B` tries A first and commits), so they are never ambiguous by construction.
- **Natural language processing** used probabilistic CFGs and CYK-style chart parsing for decades before neural parsers.

## Pitfalls

- Formal regular expressions cannot recognise arbitrary balanced nesting. Some practical regex engines add recursion or other non-regular features; HTML parsing also has rules beyond simple balanced tags.
- Left recursion (`E → E + T`) is fine for LR parsers but sends a naive recursive-descent (LL) parser into infinite recursion. Hand-written parsers rewrite it as a loop.
- A grammar that accepts the right strings can still give the wrong trees. Precedence and associativity live in the shape of the grammar, and tests must check the tree, not just acceptance.

## Key takeaways
- A CFG is (V, Σ, R, S) with rules `A → w`; one variable on the left means rewriting ignores context.
- CFGs can express nesting and matching, such as `aⁿbⁿ` and balanced brackets, which no finite automaton can.
- Parse trees capture structure; a grammar is ambiguous if some string has two trees. Some CFLs are inherently ambiguous.
- Grammar shape encodes precedence (layers E/T/F) and associativity (left or right recursion).
- Any CFG converts to Chomsky normal form, and CYK then decides membership in O(n³) time. Fixed-grammar deterministic LL/LR parsers can run in linear input time; other practical parsing methods have different guarantees.

## Further reading
- [Context-free grammar (Wikipedia)](https://en.wikipedia.org/wiki/Context-free_grammar)
- [CYK algorithm (Wikipedia)](https://en.wikipedia.org/wiki/CYK_algorithm)
- [Ambiguous grammar (Wikipedia)](https://en.wikipedia.org/wiki/Ambiguous_grammar)
- [Dangling else (Wikipedia)](https://en.wikipedia.org/wiki/Dangling_else)
- [Introducing JSON, with its full grammar (json.org)](https://www.json.org/json-en.html)
- [PEP 617: New PEG parser for CPython](https://peps.python.org/pep-0617/)
