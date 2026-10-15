---
id: type-variance-functions
title: Variance and callback substitution
level: intermediate
minutes: 4
sourceLesson: type-subtyping-variance
summary: Covariance preserves a subtype direction; contravariance reverses it.
---

Use the earlier Dog subtype of Animal throughout. A generic constructor builds a compound type from its argument; variance describes whether changing that argument preserves, reverses or prevents a subtype relationship.

## Variance: the four cases

Take a generic type `F<T>` (such as `List<T>`) and suppose Dog is a subtype of Animal. Variance says how `F<Dog>` relates to `F<Animal>`. The two directional cases, as rules:

```formula
A <: B  ⇒  F<A> <: F<B>
A <: B  ⇒  F<B> <: F<A>
where
A, B: any two types where A is a subtype of B, such as Dog and Animal
F<A>: the generic type F with A filled in, such as List<Dog>
F<B>: the same generic type with B filled in, such as List<Animal>
<:: "is a subtype of"
⇒: "guarantees": whenever the left side holds, so does the right
In words: in the first rule (covariance) the subtype arrow keeps its direction; in the second (contravariance) it flips.
```

All four cases:

| Variance | Rule |
|---|---|
| Covariant | Dogs-to-animals direction preserved |
| Contravariant | Dogs-to-animals direction reversed |
| Invariant | neither |
| Bivariant | both (unsound in general) |

In the usual producer/consumer model, permitted operations on the type parameter guide safe variance:

- `T` only comes **out** (returned, read): covariant is safe.
- `T` only goes **in** (passed as an argument, written): contravariant is safe.
- `T` goes both in and out through freely aliased access: invariance is needed unless ownership restrictions or runtime checks provide another safeguard.

## Functions: contravariant in, covariant out

Suppose code expects a callback of type `(Dog) -> Animal`. Which functions can safely be passed instead?

```
expected:   Dog    ->  Animal

param:  may accept MORE  (Animal ok)
return: may give LESS    (Dog ok)

safe:       Animal ->  Dog
```

- The caller will only ever pass in a `Dog`. A function that accepts any `Animal` handles that fine. So a supertype in the parameter is safe: **contravariant**.
- The caller will treat the result as an `Animal`. A function that returns a `Dog` satisfies that. So a subtype in the return is safe: **covariant**.

As a general rule for function types, with the `Dog` example substituted in the last two lines:

```formula
P1 <: P2  and  R2 <: R1
⇒  (P2 → R2) <: (P1 → R1)
Dog <: Animal  and  Dog <: Animal
⇒  (Animal → Dog) <: (Dog → Animal)
where
P1 → R1: the function type the caller expects, with parameter type P1 and result type R1 (here Dog → Animal)
P2 → R2: the type of the function actually passed in (here Animal → Dog)
Dog, Animal: the example types, with Dog <: Animal
<:: "is a subtype of"
→: the function-type arrow: P → R takes a P and returns an R
⇒: "guarantees"
In words: a function can stand in for another if it accepts at least as much (parameters flip direction) and returns no more than promised (results keep direction).
```

In TypeScript with `strictFunctionTypes`:

```ts
type OnDog = (d: Dog) => void;

const a: OnDog = (x: Animal) => {};
// ok: handles every Dog

const b: (x: Animal) => void =
  (d: Dog) => d.bark();
// error: might be given a Cat
```

## Key takeaways
- Covariance preserves a subtype direction; contravariance reverses it.
- A replacement function accepts at least the inputs promised and returns results compatible with its promise.

## Further reading
- [Rustonomicon: Subtyping and variance](https://doc.rust-lang.org/nomicon/subtyping.html)
- [TypeScript 2.6: Strict function types](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-6.html)
- [Microsoft: Generic variance](https://learn.microsoft.com/en-us/dotnet/standard/generics/covariance-and-contravariance)
