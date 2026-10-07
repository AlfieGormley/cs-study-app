---
id: type-gradual-soundness
title: Gradual typing and soundness
level: advanced
minutes: 15
summary: How TypeScript and Python's type hints add static checking to dynamic languages, what the any type really does, what soundness means and why TypeScript gives it up on purpose, how sound gradual languages enforce types at boundaries, and how to migrate a large codebase.
---

You have 500,000 lines of JavaScript or Python. Rewriting them in a statically typed language is out of the question, but you'd like the checker to catch `None` being passed where a `User` was expected. **Gradual typing** lets you add types one file, one function, even one parameter at a time, with typed and untyped code living side by side.

Examples of incremental static checking include TypeScript for JavaScript, mypy and Pyright for Python, Sorbet for Ruby, Hack for PHP. The strength of the guarantee depends on the tool, runtime checks and escape hatches; optional checking can sacrifice **soundness**. Understanding that trade is what this lesson is about.

## Soundness, precisely

A type system is **sound** if a program that passes the checker can never, when it runs, perform an operation on a value of the wrong type. A variable typed `number` really holds a number, every time.

Formally, soundness is usually proved as two properties of a language's semantics:

- **Progress**: a well-typed program is either finished or can take another step; it never gets stuck on something like `"a" * {}`.
- **Preservation**: each step keeps the program well-typed.

Soundness is about *absence of false negatives*. A sound checker may reject good programs (lesson 1), but never accepts one that will hit a type error. Controlled run-time failures that the type system *declares* can happen, such as an out-of-bounds index or a failed downcast, don't count against it.

## The dynamic type

The central idea, from Jeremy Siek and Walid Taha (2006), is a special type, written `?` in papers and `any`/`Any` in practice, meaning "not statically known".

`any` is *not* just a top type like `unknown` or `object`. It works in **both** directions:

```ts
let a: any = 3;
let s: string = a;   // allowed
a.foo.bar();         // allowed

let u: unknown = 3;
let t: string = u;   // error
u.foo;               // error
```

- `unknown` is a true top type: anything goes in, while type-specific operations require narrowing; operations such as equality checks remain available.
- `any` goes in and comes out as anything. The checker permits unsafe flows and operations. This is a useful intuition, not literal compatibility with every TypeScript type: for example, `any` is not assignable to `never`.

Siek and Taha replace subtyping with a **consistency** relation, written `~`: `?` is consistent with every type, and two concrete types are consistent only if they match. Consistency is deliberately **not transitive**. `number ~ ?` and `? ~ string`, but not `number ~ string`. That's what lets untyped and typed code meet without making everything compatible with everything.

## Gradual guarantee

A well-designed gradual system also satisfies the **gradual guarantee** (Siek and others, 2015): removing type annotations from a program that type-checks and runs should not make it fail to type-check, nor change what it computes. Adding annotations can only surface errors, never change correct behaviour. This is what makes migration incremental: a file with no annotations is still a valid program.

## TypeScript: unsound by design

TypeScript's design goals list "apply a sound or provably correct type system" as an explicit **non-goal**. It prefers to accept common JavaScript idioms. The known holes:

| Hole | Example |
|---|---|
| `any` | `const n: number = JSON.parse(s)` |
| Type assertions | `x as User`, `y!` |
| Covariant arrays | `Dog[]` used as `Animal[]` |
| Method bivariance | lesson 4 |
| Unchecked indexing | `xs[10]` is `T`, not `T \| undefined` |

The indexing one surprises people:

```ts
const xs: number[] = [];
const n: number = xs[0];
n.toFixed(2);
// TypeError: Cannot read properties
// of undefined
```

The checker typed `xs[0]` as `number`; at run time it's `undefined`. The `noUncheckedIndexedAccess` option makes index results `T | undefined`, but it's **not** part of `strict`, and can require explicit handling of missing indexed values.

And because TypeScript **erases** all types when emitting JavaScript, nothing checks them at run time. A wrong `as` cast or an API returning an unexpected shape just flows on until something crashes, possibly far away.

## Python: hints, checked separately

PEP 484 (Python 3.5, 2015) defined type hints, but **the interpreter does not enforce them**; it retains annotation metadata and may evaluate annotations when introspected. Checking is done by a separate tool: mypy, Pyright, Pyre or others. The same program can be fine under one and rejected by another.

```python
import json
from typing import Any

def load() -> Any:
    return json.loads('"42"')

def double(n: int) -> int:
    return n * 2

print(double(load()))
```

mypy accepts this, because `Any` is consistent with `int`. It prints `4242`: the string `"42"` repeated twice.

Python-specific holes and defaults to know:

- **Unannotated functions are skipped.** By default mypy doesn't type-check the body of a function with no annotations, and treats its parameters as `Any`. `--check-untyped-defs` (included in `--strict`) changes that.
- **`cast(T, x)`** does nothing at run time; it just tells the checker to trust you.
- **`# type: ignore`** silences a line.
- **Missing stubs.** Imports lacking usable type information can produce missing-stub diagnostics or `Any`, depending on checker configuration and whether implementation analysis is available.

Because the hints are real objects at run time (`typing.get_type_hints`), libraries can enforce them where it matters. Pydantic validates data against annotated models when it's parsed; tools like `beartype` and `typeguard` check function calls.

## Sound gradual typing: checks at the boundary

There's another design. Keep the dynamic type, but **insert run-time checks** wherever a value crosses from untyped to typed code, so a typed variable can never hold the wrong thing.

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

Typed Racket wraps higher-order values (functions, mutable structures) in **contracts** that check every later use, and on failure assigns blame according to which side violates the contract. Typed Racket also offers shallow and optional modes with different guarantees and costs. Wadler and Findler's blame theorem is the slogan: "well-typed programs can't be blamed".

The catch is cost. Takikawa and colleagues' 2016 paper *Is Sound Gradual Typing Dead?* studied combinations of typed and untyped modules in benchmark programs, and found that some partly typed configurations ran many times slower than either the fully typed or fully untyped versions, because of checks on busy boundaries. Later work (Typed Racket's "shallow" mode, transient checks, better compilers) has cut this, but the tension is real.

Dart took the concrete route: Dart 2 made the type system sound, with run-time checks on casts and covariant generics, and Dart 3 enforces sound null safety. Its compilers use the guarantees for optimisation.

## "Sound" mainstream languages aren't perfect either

- **Java**: Amin and Tate (2016) showed that Java's and Scala's type systems are unsound, using `null` and wildcard bounds. Their exploit compiles and fails at run time with a `ClassCastException`. The JVM's own checks stop it becoming memory corruption.
- **Rust**: the language is designed to be sound in safe code, but the compiler has had long-standing soundness bugs, and incorrect `unsafe` code can violate safety guarantees; the keyword does not itself make correct code unsound.
- **Haskell**: `unsafeCoerce` and `unsafePerformIO` exist; avoiding them is a convention.

The useful question is not "is it sound?" but "where are the holes, and do I control them?"

## Migrating a large codebase

Dropbox's 2019 write-up describes checking over 4 million lines of Python with mypy, adopted gradually over several years. The common pattern in such migrations:

1. **Start permissive.** Turn the checker on with loose settings so the build passes.
2. **Type the core first.** Shared libraries and data models give the most leverage; their types flow into callers.
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
- Gradual typing mixes typed and untyped code using a dynamic type (`any`, `Any`) that is consistent with every type, in both directions.
- `unknown`/`object` are safe top types; `any` switches checking off.
- Soundness means a program that passes the checker never hits an unexpected type error at run time; TypeScript and mypy deliberately give it up for compatibility.
- Common holes: `any`, casts and assertions, covariant arrays, method bivariance, unchecked indexing, unannotated Python functions.
- Sound gradual systems (Typed Racket, Dart) check values at typed/untyped boundaries, at a run-time cost that can be large.
- Migrate incrementally, type the core first, ratchet strictness, and validate external data at the edges.

## Further reading
- [Gradual typing — Wikipedia](https://en.wikipedia.org/wiki/Gradual_typing)
- [What is gradual typing — Jeremy Siek](https://jsiek.github.io/home/WhatIsGradualTyping.html)
- [TypeScript design goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)
- [Type compatibility and soundness — TypeScript handbook](https://www.typescriptlang.org/docs/handbook/type-compatibility.html)
- [PEP 484: Type hints](https://peps.python.org/pep-0484/)
- [Using mypy with an existing codebase — mypy docs](https://mypy.readthedocs.io/en/stable/existing_code.html)
- [Our journey to type checking 4 million lines of Python — Dropbox](https://dropbox.tech/application/our-journey-to-type-checking-4-million-lines-of-python)
- [Is sound gradual typing dead? (Takikawa et al., POPL 2016, PDF)](https://www2.ccs.neu.edu/racket/pubs/popl16-tfgnvf.pdf)
- [The Dart type system](https://dart.dev/language/type-system)
- [Primary verification source 3](https://docs.racket-lang.org/ts-guide/typed-untyped-interaction.html)
- [Primary verification source 7](https://io.livecode.ch/learn/namin/unsound?img=java8)
