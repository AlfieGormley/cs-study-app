---
id: type-checking-guarantees
title: What static checks can guarantee
level: basic
minutes: 4
sourceLesson: type-static-dynamic
summary: Checked casts, bounds and array-store checks can remain in statically typed languages.
---

Static checking can rule out classes of mistakes before execution while deliberately retaining some runtime checks. Its guarantee is relative to a language’s rules, implementation and explicit escape hatches.

## Static languages still check at run time

Static checking cannot prove everything, so static languages keep some dynamic checks:

- **Downcasts**: in Java, `(String) obj` is checked at run time and may throw `ClassCastException`.
- **Array bounds**: Java, Rust and C# check indices at run time.
- **Covariant array stores**: Java checks that each value stored into a reference array fits the array's real element type (the JIT may eliminate checks it proves unnecessary) (the later variance units explain why).

And dynamic languages can be checked statically: TypeScript adds static checking to JavaScript-compatible source, and mypy or Pyright check Python type hints. That hybrid is **gradual typing** (the later gradual-typing units).

## Static checkers are conservative

A static checker must decide *without running the program*. Deciding exactly which programs will hit a type error is undecidable in general (it would solve the halting problem), so a checker has to approximate. Sound checkers err on the safe side and **reject some programs that would actually run fine**:

```java
Object o = "hi";
// Fine at run time, rejected statically:
int n = o.length(); // Object has no length
```

The programmer knows `o` holds a String; the checker only knows its declared type is `Object`. You fix this with a cast or a better declared type. A checker’s accepted programs depend on its rules: an annotation, narrowing test or checked cast can communicate information its analysis does not otherwise retain.

## Trade-offs

| | Static | Dynamic |
|---|---|---|
| Type checks | Static constraints before execution; runtime checks may remain | Operation rules checked during execution |
| Tooling | Declared/inferred types can guide tooling | Inference, annotations and runtime knowledge can guide tooling |
| Speed | Depends on representation and implementation | Depends on representation and implementation |
| Flexibility | Must satisfy checked constraints | Runtime operation rules still apply |
| Quick experiments | REPLs and incremental checkers are possible | REPLs and compilation are possible |

What does this buy in practice? A 2017 study, *To Type or Not to Type* (Gao, Bird and Barr), examined a sample of fixed bugs in public JavaScript projects, added annotations, and found that TypeScript 2.0 and Flow 0.30 each detected about **15%**. This historical sample does not estimate every project or current checker; undetected bugs were not all established to be inherently beyond type checking.

> [!tip] A useful way to think about it
> A sound type system can prove specified properties about all executions within its model and assumptions. Practical checkers may intentionally be unsound. Tests are **evidence about some executions**, but can check anything. They complement each other.

## Common pitfalls

- **Confusing the axes.** Calling Python weak solely because it is dynamic confuses two questions. Calling C strong solely because it is static makes the same mistake; the strength labels are informal.
- **Assuming static means safe.** C and C++ are static but allow memory-unsafe casts and undefined behaviour.
- **Assuming annotations are enforced.** Python type hints can be checked by separate tools and remain available as annotation metadata (with deferred evaluation in Python 3.14); Python does not enforce them by itself. TypeScript type annotations are erased during compilation. `def f(x: int)` will happily accept a string at run time.
- **Relying on coercion.** JavaScript's `==` converts operands; use `===`, which never coerces.

## Key takeaways
- Checked casts, bounds and array-store checks can remain in statically typed languages.
- Exact prediction of arbitrary runtime type errors is undecidable; sound analysis may reject safe executions.
- Historical bug-detection samples are evidence about that sample, not a universal forecast.

## Further reading
- [Luca Cardelli: Type systems](https://lucacardelli.name/Papers/TypeSystems.pdf)
- [Java Language Specification: Conversions](https://docs.oracle.com/javase/specs/jls/se21/html/jls-5.html)
- [Java Language Specification: Arrays](https://docs.oracle.com/javase/specs/jls/se21/html/jls-10.html)
- [Gao et al.: To type or not to type](https://earlbarr.com/publications/typestudy.pdf)
