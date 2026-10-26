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

```formula essential
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

Chomsky normal form matters because every multi-character span can be split into two smaller spans. A parser can build answers from short spans to long ones instead of guessing arbitrary derivations.

There is also a useful structural invariant: each binary rule increases the number of variables by one, and each terminal rule finishes one character. Starting from one variable, a nonempty derivation therefore needs one fewer binary rules than characters, plus one terminal rule per character. The compact count is available as a reference:

```formula reference
D(n) = (n − 1) + n = 2n − 1   for n ≥ 1
where
D(n): the number of derivation steps (rule applications) needed for a string of length n in a Chomsky normal form grammar
n: the length of the string, in characters
≥: is at least
In words: a nonempty derivation needs one fewer binary rules than characters, followed by one terminal rule per character: twice the string length minus one steps altogether.
```

The variable skeleton is a full binary tree; terminal-production nodes still have one terminal child in the complete parse tree. The count only holds for strict Chomsky normal form. The optional start-to-empty rule is a separate one-step derivation producing no characters. Normalising rule shape does not settle ambiguity: the same string may still have several trees.

## Key takeaways

- Chomsky normal form uses binary-variable and single-terminal rules.
- The optional empty-string rule needs a start variable absent from right-hand sides.
- Every nonempty derivation takes twice the string length minus one steps.

## Further reading

- [Sipser: grammars, parse trees and pushdown automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec4-1/)
- [CYK algorithm — further reference](https://en.wikipedia.org/wiki/CYK_algorithm)
- [PEP 617: CPython’s PEG parser](https://peps.python.org/pep-0617/)
