---
id: type-checked-boundaries
title: Boundary checks and gradual migration
level: advanced
minutes: 4
sourceLesson: type-gradual-soundness
summary: Higher-order contracts protect future calls and track blame, rather than checking a function only once.
---

Optional checkers do not enforce annotations at runtime. A sound gradual design must instead account for interactions between checked and unchecked code, including values that will be called or mutated later.

## Sound gradual typing: checks at the boundary

There's another design. Keep the dynamic type, but **insert run-time checks** wherever a value crosses from untyped to typed code, so interactions preserve the specified soundness guarantee. Deep contracts and shallow checks protect different properties; a shallow list check, for example, does not establish every element’s type for all future uses.

```
untyped module        typed module
                      def f(n: int)
  f("42") ──────►  [ is it an int? ]
                     │ yes      │ no
                     ▼          ▼
                   run f    error, blame
                            the caller
```

| Approach | How | Example |
|---|---|---|
| Optional | No type-enforcement checks inserted | TypeScript, mypy |
| Transient | Cheap shape checks at uses | Reticulated Python |
| Guarded | Wrappers/contracts on values | Typed Racket |

Typed Racket wraps higher-order values (functions, mutable structures) in **higher-order contracts** that check every later use, and on failure assigns blame according to which side violates the contract. Typed Racket also offers shallow and optional modes with different guarantees and costs. Wadler and Findler's blame theorem is the slogan: "well-typed programs can't be blamed".

The catch is cost. Takikawa and colleagues' 2016 paper *Is Sound Gradual Typing Dead?* studied combinations of typed and untyped modules in benchmark programs, and found that some partly typed configurations ran many times slower than either the fully typed or fully untyped versions, because of checks on busy boundaries. Later work (Typed Racket's "shallow" mode, transient checks, better compilers) has cut this, but the tension is real.

Dart took the concrete route: Dart 2 made the type system sound, with run-time checks on casts and covariant generics, and Dart 3 enforces sound null safety. Its compilers use the guarantees for optimisation.

## Migrating a large codebase

Dropbox's 2019 write-up describes checking over 4 million lines of Python with mypy, adopted gradually over several years. The common pattern in such migrations:

1. **Start permissive.** Turn the checker on with loose settings so the build passes.
2. **Type the core first.** Shared modules and data models give the most leverage; their types flow into callers.
3. **Ratchet.** Per-module strictness flags (`mypy` per-module config, TypeScript project references). New files must be strict; old files can't get worse.
4. **Turn on the important flags.** In TypeScript, `strict` (including `noImplicitAny` and `strictNullChecks`); in mypy, `--strict` or at least `--check-untyped-defs` and `--disallow-untyped-defs`.
5. **Validate at the edges.** Types describe what *should* arrive. Validate network JSON with a correctly configured schema (such as Zod or Pydantic); this checks that schema, not every business invariant.
6. **Track the escape hatches.** Count `any`, `as`, `cast` and `type: ignore`; lint against new ones.

## Pitfalls

- **Treating `any` as "some type".** It turns checking off, and spreads: a value derived from `any` is usually `any` too. Use `unknown` or `object` and narrow.
- **Trusting annotations at boundaries.** `fetchUser(): Promise<User>` is a claim, not a check. Validate external data.
- **Assuming mypy checked a function.** Without annotations, or with untyped imports, it may not have.
- **`as` to silence errors.** An assertion is a promise you make to the checker; it's the first place to look when a "typed" program crashes.

## Key takeaways
- Higher-order contracts protect future calls and track blame, rather than checking a function only once.
- Boundary-check overhead depends on mode and workload; benchmark results are not universal forecasts.
- Migrate incrementally, tighten checks, validate external inputs and track escape hatches.

## Further reading
- [Typed Racket: Typed/untyped interaction](https://docs.racket-lang.org/ts-guide/typed-untyped-interaction.html)
- [Wadler and Findler: Well-typed programs cannot be blamed](https://homepages.inf.ed.ac.uk/wadler/papers/blame/blame.pdf)
- [Takikawa et al.: Gradual typing benchmarks](https://www2.ccs.neu.edu/racket/pubs/popl16-tfgnvf.pdf)
- [Dart: Type system](https://dart.dev/language/type-system)
- [Dart: Sound null safety](https://dart.dev/null-safety)
- [Dropbox: Migrating four million Python lines](https://dropbox.tech/application/our-journey-to-type-checking-4-million-lines-of-python)
- [mypy: Existing codebases](https://mypy.readthedocs.io/en/stable/existing_code.html)
