---
id: compu-cyk-parsing
title: Dynamic programming with CYK
level: basic
minutes: 4
summary: CYK builds membership answers from short spans to long ones.
sourceLesson: compu-cfg
---

The preceding unit put the positive equal-block grammar into Chomsky normal form. This unit uses that form to decide whether a particular string belongs to the grammar’s language.

## Building a membership table

The **CYK algorithm** (Cocke–Younger–Kasami) fills a table where `t[i][j]` holds every variable that can derive the substring from position i to j:

```python
RULES = [("S", "A", "T"), ("S", "A", "B"),
         ("T", "S", "B")]
TERM = {"a": {"A"}, "b": {"B"}}

def cyk(w):
    n = len(w)
    t = [[set() for _ in range(n)]
         for _ in range(n)]
    # Seed length-one spans from terminals.
    for i, c in enumerate(w):
        t[i][i] = set(TERM.get(c, ()))
    for L in range(2, n + 1):     # span
        for i in range(n - L + 1):
            j = i + L - 1
            for k in range(i, j):  # split
                for A, B, C in RULES:
                    if (B in t[i][k] and
                        C in t[k+1][j]):
                        # Combine derivable
                        # adjacent spans.
                        t[i][j].add(A)
    return n > 0 and "S" in t[0][n-1]

for w in ["ab", "aabb", "aab", "abab"]:
    print(w, cyk(w))
# ab True / aabb True
# aab False / abab False
```

The three nested loops over span, start and split point, each running up to n times, plus a loop over the rules, give the running time:

```formula
T_CYK(n) = O(n^3 × |G|)
where
T_CYK(n): the number of basic steps CYK takes on an input string
n: the length of the input string, in tokens (characters here)
|G|: the size of the grammar, roughly its number of rules
O(…): big-O: grows no faster than the expression inside, up to a constant factor, for large n
In words: CYK's work grows with the cube of the input length, times the size of the grammar.
```

Under a cubic timing model with a fixed grammar, a tenfold longer input costs about a thousand times as much: a hundred tokens corresponds to a million cubic combinations, and a thousand tokens to a billion. Big-O is an upper growth bound, not an exact measured runtime prediction. That proves every CFL (context-free language) can be parsed in polynomial time, but it is too slow for compilers handling large files.

## Real-world use

- **Language specifications** are written as grammars, usually in BNF or EBNF notation. The JSON specification at json.org is a short grammar; Python's full grammar is published in its reference manual.
- **Parser generators** take grammars and produce parsers. Deterministic LL(k) and LR(k) parsers have linear input-time bounds for a fixed suitable grammar. Bison also offers GLR parsing, and ANTLR uses adaptive prediction; it is wrong to describe all these capabilities as fixed-k deterministic parsing with the same guarantee.
- **Python 3.9+** replaced its LL(1) parser with a PEG parser (PEP 617). PEGs look like CFGs but use *ordered choice* (`A / B` tries A first and commits), so they are never ambiguous by construction.
- **Natural language processing** used probabilistic CFGs and CYK-style chart parsing for decades before neural parsers.

## Pitfalls

- Formal regular expressions cannot recognise arbitrary balanced nesting. Some practical regex engines add recursion or other non-regular features; HTML parsing also has rules beyond simple balanced tags.
- Left recursion (an expression expanding first into another expression) is fine for LR parsers but sends a naive recursive-descent (LL) parser into infinite recursion. Hand-written parsers rewrite it as a loop.
- A grammar that accepts the right strings can still give the wrong trees. Precedence and operator associativity live in the shape of the grammar, and tests must check the tree, not just acceptance.

## Key takeaways

- CYK records all variables deriving each input span and tries every split point.
- With a fixed grammar, the displayed algorithm has a cubic input-length bound.
- Practical parsing families use different restrictions and guarantees; ordered PEG choice resolves choices operationally.

## Further reading

- [Sipser: grammars, parse trees and pushdown automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec4-1/)
- [CYK algorithm — further reference](https://en.wikipedia.org/wiki/CYK_algorithm)
- [PEP 617: CPython’s PEG parser](https://peps.python.org/pep-0617/)
