---
id: type-soundness-model
title: Soundness and its assumptions
level: advanced
minutes: 4
sourceLesson: type-gradual-soundness
summary: Progress and preservation establish soundness for a specified semantics and its assumptions.
---

You have 500,000 lines of JavaScript or Python. Rewriting them in a statically typed language is out of the question, but you'd like the checker to catch `None` being passed where a `User` was expected. **Gradual typing** lets you add types one file, one function, even one parameter at a time, with typed and untyped code living side by side.

Examples of incremental static checking include TypeScript for JavaScript, mypy and Pyright for Python, Sorbet for Ruby, Hack for PHP. The strength of the guarantee depends on the tool, runtime checks and escape hatches; optional checking can sacrifice **soundness**. Understanding that trade is what this lesson is about.

## Soundness, precisely

A type system is **sound** when accepted programs avoid the erroneous states ruled out by its formal model, under that model’s assumptions. A calculus may express this as the absence of unexpected runtime type errors; it does not mean every source-language failure or exception is impossible.

Formally, soundness is usually proved as two theorems about a language's semantics, **progress and preservation**. Type-theory papers write them like this:

```formula
⊢ e : τ  ⇒  e ∈ V  or  e ⟶ e′
⊢ e : τ  and  e ⟶ e′  ⇒  ⊢ e′ : τ
where
e: a program (an expression) being run
e′: e-prime: the program after one more step of execution
τ: tau, a type such as number or string
⊢: the typing judgement: ⊢ e : τ means "the type checker proves that e has type τ". In general it is written Γ ⊢ e : τ, where Γ (gamma) lists the types of the variables in scope; for a whole program Γ is empty and is left out
:: "has type"
V: the set of values: finished results such as 3 or "hi" that cannot run any further
∈: "is a member of"
⟶: "takes one step of execution to"
⇒: "guarantees": if the left side holds, so does the right
In words: progress (first line): a well-typed program is either finished or can take another step, so it never gets stuck; preservation (second line): taking a step keeps the program's type.
```

- **Progress** rules out getting stuck on something like `"a" * {}`, where no rule says what to do next.
- **Preservation** means the guarantee lasts: after a million steps the program is still well-typed, so progress applies again.

Together they mean a well-typed program never reaches a stuck state. This style of proof is due to Wright and Felleisen (1994).

Soundness is about *absence of false negatives* for the errors excluded by the model. A sound checker may reject programs whose executions would avoid those errors, but never accepts one that reaches an excluded state under its assumptions. Controlled runtime failures explicitly allowed by that semantics, such as a bounds failure or checked downcast exception, do not contradict the theorem.

## "Sound" mainstream languages aren't perfect either

- **Java**: Amin and Tate (2016) showed that Java's and Scala's type systems are unsound, using `null` and wildcard bounds. Their exploit compiles and fails at run time with a `ClassCastException`. The JVM's own checks stop it becoming memory corruption.
- **Rust**: the language is designed to be sound in safe code, but the compiler has had long-standing soundness bugs, and incorrect `unsafe` code can violate safety guarantees; the keyword does not itself make correct code unsound.
- **Haskell**: `unsafeCoerce` and `unsafePerformIO` exist; their correct use requires additional reasoning beyond the ordinary safe fragment; the operations’ existence alone does not invalidate a theorem about that fragment.

The useful question is not "is it sound?" but "where are the holes, and do I control them?"

## Key takeaways
- Progress and preservation establish soundness for a specified semantics and its assumptions.
- Language/runtime escape hatches and implementation bugs affect the guarantee available in practice.

## Further reading
- [Wright and Felleisen: Type soundness](https://courses.grainger.illinois.edu/cs522/sp2016/ASyntacticApproachToTypeSoundness.pdf)
- [Luca Cardelli: Type systems](https://lucacardelli.name/Papers/TypeSystems.pdf)
- [Amin and Tate: Java and Scala unsoundness](https://www.cs.cornell.edu/~ross/publications/unsound/unsound-oopsla16.pdf)
- [The Rust Book: Unsafe Rust](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html)
