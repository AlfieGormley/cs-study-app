---
id: type-inference-limits
title: Inference limits and useful signatures
level: intermediate
minutes: 3
sourceLesson: type-inference
summary: Worst-case ML typability is exponential-time complete; this does not predict routine application performance.
---

The previous lessons established principal types for the Hindley–Milner core. Real language extensions, diagnostics and compilation costs require additional assumptions.

## Cost and limits

- **Speed.** Small ordinary inference examples can be inexpensive, but there is no general near-linear bound. In theory, deciding ML typability is DEXPTIME-complete (Mairson; Kfoury, Tiuryn and Urzyczyn, 1990): nested `let`s can produce types that double in size at each level. This worst case is not a prediction of typical application performance.
- **Extensions break completeness.** Rich combinations of subtyping, higher-rank types, GADTs and type-level computation can lose principal types, require annotations or make inference undecidable; no such result follows merely from adding any one feature in any form. Consequently, a language with subtyping or overloading needs additional inference rules and design choices; ordinary HM is not a drop-in specification for its whole type system.
- **Type classes add constraints.** Haskell infers `square x = x * x` as `Num a => a -> a`, read "for any type `a` that is a number type (`Num a`), a function from `a` to `a`". Sometimes a constraint can't be resolved: `f = show . read` fails with "ambiguous type variable", because nothing says which type to read.
- **Error messages.** The error is reported where unification fails, which can be far from the real mistake. A wrong argument on line 10 may be blamed on line 40.

> [!tip] Annotate the boundaries
> Idiomatic Haskell and OCaml code still writes type signatures on top-level functions, even though they could be inferred. Signatures document intent, give better error locality, and stop a mistake in the body silently changing the inferred type that callers see. Rust requires function signatures; TypeScript can infer exported return types, so explicit exported signatures are a documentation policy rather than a universal compiler requirement.

## Comparison

| Language | Infers | Needs annotations on |
|---|---|---|
| Java, C# | Locals from initialiser | Ordinary method signatures and fields |
| TypeScript | Locals, returns, lambdas in context | Parameters without contextual types |
| Rust | Many local types, including later constraints | Function signatures, ambiguous locals |
| Haskell, OCaml | HM-style core expressions | Higher-rank uses, restricted or ambiguous extensions |

## Key takeaways
- Worst-case ML typability is exponential-time complete; this does not predict routine application performance.
- Annotations at module boundaries document intended types and localise errors.

## Further reading
- [Mairson: Deciding ML typability](https://static.aminer.org/pdf/20170130/pdfs/popl/o8rbwxmj6h2cxf7qdezlupsbgn5u40wn.pdf)
- [GHC: Generalised algebraic data types](https://downloads.haskell.org/ghc/latest/docs/users_guide/exts/gadt.html)
- [Haskell 2010: Declarations and types](https://www.haskell.org/onlinereport/haskell2010/haskellch4.html)
- [OpenJDK: Local variable inference](https://openjdk.org/projects/amber/guides/lvti-style-guide)
