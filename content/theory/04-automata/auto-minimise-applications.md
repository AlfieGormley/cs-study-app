---
id: auto-minimise-applications
title: Minimal machines in practice
level: advanced
minutes: 3
sourceLesson: auto-minimisation
summary: A product search can find a shortest counterexample without fully minimising either DFA.
---

A minimal complete DFA merges equivalent states after unreachable states have been removed. The Myhill–Nerode units explain why its states are determined by the language.

## What minimal DFAs are used for

- **Automaton equivalence testing.** To check `a(ba)*` against `(ab)*a`, build both minimal DFAs and compare. Both describe alternating strings that start and end with a, so they come out identical. In practice tools skip full minimisation and search the product automaton for a reachable pair (p, q) where exactly one accepts; the path to it is a counterexample. For a*b* versus (ab)*, a and b are both shortest counterexamples; alphabet traversal order determines which is returned.
- **Lexer generators.** Generators that emit a DFA as code or tables, such as re2c, minimise it first, which directly shrinks the generated scanner.
- **Hardware.** Fewer logical states may reduce storage or logic, but encoding and synthesis matter. The same binary bit count can cover several state counts, and next-state logic can become more complex.
- **Model checking and verification.** Verification tools minimise automata to shrink the state spaces they have to explore and store.
- **Learning automata.** Angluin's L* algorithm learns a minimal DFA using membership queries and equivalence queries that return counterexamples when a hypothesis is wrong. It is used to infer models of black-box network protocols and software.

## Pitfalls

- **Minimising an NFA is hard.** Uniqueness and these fast algorithms apply to DFAs. The decision problem of whether an equivalent NFA with at most a given number of states exists is PSPACE-complete, even when the input is a DFA. Minimum NFAs need not be unique.
- **Forgetting the dead state.** If your DFA is partial, add the dead state before refining, otherwise states that "fall off" on different symbols may be wrongly merged.
- **Forgetting unreachable states.** They do not change the language, but they inflate the count. Partition refinement on its own will not delete them.
- **Merging on one step.** Two states with identical rows and the same accepting status are equivalent, but states with different rows can still be equivalent (B and D in the earlier refinement example have different rows). Refinement has to run to a fixed point.

## Key takeaways
- A product search can find a shortest counterexample without fully minimising either DFA.
- Uniqueness and fast minimisation apply to complete DFAs over a fixed alphabet; minimum NFAs behave differently.

## Further reading
- [Minimization of Automata — Berstel, Boasson, Carton and Fagnot](https://arxiv.org/abs/1010.5318)
