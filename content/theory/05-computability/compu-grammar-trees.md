---
id: compu-grammar-trees
title: Generating strings and reading parse trees
level: basic
minutes: 3
summary: Bounded breadth-first generation works for the displayed parentheses grammar; arbitrary grammars need a terminating parser.
sourceLesson: compu-cfg
---

## Simulating a grammar in Python

For the balanced-parentheses grammar below, breadth-first search over **sentential forms** (partly rewritten strings), always expanding the leftmost variable, enumerates all strings up to the bound. Terminals are single characters, and all variables must be keys of G. This routine is not a terminating enumerator for arbitrary CFGs: a rule replacing S with two copies of S can grow variables indefinitely without exceeding a terminal-count bound. For general CFGs, enumerate the finitely many candidate terminal strings and decide membership with a parser.

```python
from collections import deque

def generate(G, start, maxlen):
    out, seen = set(), set()
    q = deque([(start,)])
    while q:
        f = q.popleft()
        if f in seen:
            continue
        # Avoid re-expanding the same form.
        seen.add(f)
        terms = [x for x in f if x not in G]
        if len(terms) > maxlen:
            continue
        i = next((k for k, x in enumerate(f)
                  if x in G), None)
        if i is None:   # all terminals
            out.add("".join(f))
            continue
        # Expand only the leftmost variable.
        for rhs in G[f[i]]:
            q.append(f[:i] + rhs + f[i+1:])
    return sorted(out, key=lambda s:
                  (len(s), s))

P = {"S": [("(", "S", ")", "S"), ()]}
print(generate(P, "S", 6))
```

The displayed grammar chooses either an opening bracket, a nested S, a closing bracket and another S, or the empty string. It describes balanced parentheses. The output lists all 9 balanced strings of length at most 6: `''`, `()`, `(())`, `()()`, and the five of length 6. (The counts 1, 1, 2, 5 for lengths 0, 2, 4, 6 are the Catalan numbers, which turn up all over grammar theory.)

## Parse trees

A derivation is a sequence; a **parse tree** shows the structure. Each internal node is a variable, its children are the right-hand side of the rule used, and reading the leaves left to right gives the string.

For arithmetic, a classic grammar is:

```formula
E → E "+" T | T
T → T "*" F | F
F → "(" E ")" | "id"
where
E, T, F: grammar variables for expressions, terms and factors; E is the start variable
→: may be rewritten as
|: separates alternative right-hand sides
"+", "*": terminal operator tokens for addition and multiplication
"(", ")": terminal parentheses
"id": a terminal identifier token
In words: Expressions group multiplication inside terms before joining terms with addition.
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

The tree puts `id * id` lower down, so it is grouped first. That is operator precedence, encoded purely by the shape of the grammar: `*` lives at the T level, beneath `+` at the E level. The expression rule is left-recursive: its recursive expression comes before the plus token. This makes repeated addition left-associative, grouping the first two operands together.

A **leftmost derivation** always rewrites the leftmost variable. There is a one-to-one match between parse trees and leftmost derivations, so "how many parse trees" and "how many leftmost derivations" are the same question.

## Key takeaways

- Bounded breadth-first generation works for the displayed parentheses grammar; arbitrary grammars need a terminating parser.
- Parse trees record grouping; precedence and associativity depend on grammar structure.

## Further reading

- [Sipser: grammars, parse trees and pushdown automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec4-1/)
