---
id: compu-cnf-cyk
title: Chomsky normal form and derivation length
level: basic
minutes: 3
summary: Chomsky normal form restricts productions to binary-variable or single-terminal rules, with a controlled empty-string exception.
sourceLesson: compu-cfg
---

## Chomsky normal form and CYK

A grammar is in **Chomsky normal form** if every rule is one of:

- A single variable becomes exactly two variables.
- A single variable becomes exactly one terminal.
- Optionally the start variable becomes the empty string. If this exception is used, the start variable cannot appear on any right-hand side, so the empty production cannot occur inside a nonempty derivation.

Every CFG can be converted to Chomsky normal form mechanically: add a fresh start variable, remove ε-rules, remove unit rules that replace one variable with another, replace terminals in mixed/long right-hand sides with fresh variables, and break long right-hand sides into chains of pairs. For equal positive-length a and b blocks:

```formula
S → A T | A B
T → S B
A → "a"
B → "b"
where
S: the start variable for positive equal a and b blocks
A, B, T: auxiliary grammar variables
→: may be rewritten as
|: separates alternatives
"a", "b": terminal letters
In words: Each binary production adds structure; each terminal production supplies one letter. There is no empty-string production here.
```

Chomsky normal form matters because it makes parsing a clean dynamic programme. In Chomsky normal form, every derivation of a nonempty string has the same, predictable length:

```formula
D(n) = (n − 1) + n = 2n − 1   for n ≥ 1
where
D(n): the number of derivation steps (rule applications) needed for a string of length n in a Chomsky normal form grammar
n: the length of the string, in characters
≥: is at least
In words: you need n − 1 two-variable rules to grow one variable into n of them, then n one-terminal rules to turn each into a character.
```

For `aabb`, the input length is four. Apply the start rule with A and T, replace T by S and B, then replace S by A and B: three binary rules leave A, A, B, B. Four terminal rules finish the string. Twice four minus one gives seven steps. The variable skeleton is a full binary tree; terminal-production nodes still have one terminal child in the complete parse tree. The count only holds for strict Chomsky normal form; the ε-exception for the start variable is the one derivation of length 1 that produces no characters.

## Key takeaways

- Chomsky normal form uses binary-variable and single-terminal rules.
- The optional empty-string rule needs a start variable absent from right-hand sides.
- Every nonempty derivation takes twice the string length minus one steps.

## Further reading

- [Sipser: grammars, parse trees and pushdown automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec4-1/)
- [CYK algorithm — further reference](https://en.wikipedia.org/wiki/CYK_algorithm)
- [PEP 617: CPython’s PEG parser](https://peps.python.org/pep-0617/)
