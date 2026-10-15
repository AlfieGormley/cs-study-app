---
id: type-generic-implementation
title: Erasure, specialisation and reification
level: intermediate
minutes: 4
sourceLesson: type-generics
summary: Java erases generic arguments while preserving some signature metadata; Python annotations remain metadata.
---

Generic source code can preserve type relationships under several runtime strategies. Distinguish the checker’s guarantee from metadata, representation and generated machine code.

## How generics are implemented

The type checker's job is the same everywhere; the run-time strategy differs a lot.

### Erasure: Java and TypeScript; Python metadata

The compiler checks the types, then **erases** them. At run time, `List<String>` and `List<Integer>` are both just `List`, and the compiler inserts casts where values come out.

Consequences in Java:

- No `new T()` or `new T[10]`: there's no `T` at run time to construct.
- You can't test at run time whether a list is a `List<String>`; only `List<?>`.
- Overloads `f(List<String>)` and `f(List<Integer>)` clash: "same erasure".
- No primitives: `List<int>` is illegal, so ints are **boxed** into `Integer` objects, using object references; caching or existing objects can avoid a fresh allocation for each element.

Java chose erasure in 2004 for **migration compatibility**: generic code had to run on existing JVMs and interoperate with old non-generic libraries.

TypeScript erases *all* types when compiling to JavaScript, generics included. Python keeps annotations as metadata (`list[int]` is a real object you can inspect), but the interpreter never enforces them.

### Monomorphisation: Rust, C++

The compiler specializes generic code for concrete types used. Optimizers and linkers can inline, merge or eliminate instantiations, so the number of machine-code functions need not equal the number of types. `largest::<i32>` and `largest::<f64>` are distinct conceptual instantiations.

- **Pro**: concrete types permit direct specialised operations, inlining opportunities and unboxed value storage. This does not promise that every call is inlined or that every program has zero overhead.
- **Con**: code bloat and longer compile times. More instantiations can increase compilation work; their count is not a guaranteed count of emitted functions.

Rust offers an alternative when you want one copy: `&dyn Trait` uses a **vtable** (dynamic dispatch) instead.

### Dictionary passing: Haskell

In the usual dictionary-passing model, GHC compiles `Ord a => [a] -> a` to a function that takes an extra hidden argument: a **type-class dictionary** (record) of the `Ord` methods for that type. The unspecialised model shares code and selects methods through that dictionary; it need not emit an indirect call for every comparison after optimisation. The optimiser often **specialises** hot call sites to remove the overhead.

### Reification: C#/.NET

.NET keeps generic type information at run time. `typeof(T)` works, `new T()` works with a `where T : new()` constraint, and `List<int>` stores raw ints with no boxing. The usual .NET JIT strategy shares generic code across reference-type instantiations and specializes value types. Details depend on the runtime and compilation mode.

| Strategy | Languages | Run-time types? | Unboxed values? |
|---|---|---|---|
| Erasure | Java, TS | Generic arguments not reified per object; Java signature metadata may remain | Java collections use references |
| Optional hints | Python | Annotation metadata retained | Interpreter-dependent |
| Monomorphise | Rust, C++ | n/a, compiled away | Yes |
| Dictionaries | Haskell | No | Usually boxed |
| Reified | C#, .NET | Yes | Yes |

## Pitfalls

- **Raw types in Java.** Using `List` without a parameter turns off checking and produces "unchecked" warnings. Don't ignore them.
- **Boxing costs.** A Java `List<Integer>` of a million elements holds a million references; these may share cached or pre-existing objects. Use `int[]` or a primitive collection library for hot paths.
- **Monomorphisation bloat.** In Rust, very generic code in a large codebase can noticeably inflate binary size and compile times.

## Key takeaways
- Java erases generic arguments while preserving some signature metadata; Python annotations remain metadata.
- Rust and C++ specialise concrete instantiations; optimisers can merge or eliminate emitted code.
- GHC passes type-class dictionaries; .NET retains generic types and commonly shares reference-type code.

## Further reading
- [Java Language Specification: Types](https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html)
- [Java generics: Type erasure](https://docs.oracle.com/javase/tutorial/java/generics/erasure.html)
- [The Rust Book: Generic types](https://doc.rust-lang.org/book/ch10-01-syntax.html)
- [Microsoft: Generics at runtime](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/generics/generics-in-the-run-time)
- [GHC: Type classes](https://downloads.haskell.org/ghc/latest/docs/users_guide/exts/typeclasses.html)
