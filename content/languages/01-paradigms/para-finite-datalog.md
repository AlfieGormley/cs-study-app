---
id: para-finite-datalog
title: Finite Datalog and fixed-point evaluation
level: intermediate
minutes: 3
sourceLesson: para-logic-dataflow
summary: Finite positive function-free Datalog reaches a least fixed point.
---

A finite set of possible facts supports a different evaluation strategy: repeatedly derive facts until none are new. State the restrictions before relying on this process to terminate.

## Finite facts and practical logic languages

For a small bottom-up trace, take the parent chain a → b → c → d and use the two ancestor rules from the earlier relations unit. Start with no ancestor facts, retaining the parent facts throughout. Each round uses only facts present at its start. Round one derives the three direct ancestor pairs. Round two adds the two pairs two edges apart. Round three adds a as an ancestor of d. A further round adds nothing, so the six ancestor pairs form the fixed point.

This synchronous-round convention matters: an engine that immediately uses facts produced earlier in the same pass may require fewer passes, while deriving the same least fixed point. The finite-domain guarantee here assumes positive rules, no generated new constants and the ordinary set interpretation of facts. A safe rule binds its head variables through positive body relations; real Datalog dialects may offer additional constructs.

- **Datalog** is a restricted logic language: no compound data terms and (in its basic form) every rule must be safe. For basic positive, function-free Datalog over a finite domain, bottom-up fixed-point evaluation terminates because only finitely many facts can be derived. Bottom-up evaluation is common, not the only strategy. Extensions such as arithmetic that generates new values can lose the finite-domain termination guarantee. GitHub's **CodeQL** query language is a Datalog descendant used to find security bugs; **Soufflé** runs Datalog static analyses of Java programs; **Datomic** queries are Datalog.
- **Policy engines**: Open Policy Agent's **Rego** language was inspired by Datalog.
- SQL recursive CTEs compute the same transitive closure as `ancestor`.
- **Constraint logic programming** (for example CLP(FD) in SWI-Prolog) solves scheduling and puzzles by stating constraints instead of search code.
- **Type checkers**: Rust's trait solver and Haskell's type class resolution are logic-programming engines internally.

## Key takeaways
- Finite positive function-free Datalog reaches a least fixed point.
- Extensions must be checked before relying on that termination guarantee.

## Further reading
- [Soufflé: Datalog tutorial](https://souffle-lang.github.io/tutorial)
- [CodeQL overview](https://codeql.github.com/docs/codeql-overview/about-codeql/)
