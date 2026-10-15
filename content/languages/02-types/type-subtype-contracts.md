---
id: type-subtype-contracts
title: Subtyping, structure and behaviour
level: intermediate
minutes: 3
sourceLesson: type-subtyping-variance
summary: A subtype can stand in for its supertype under the relevant typing and behavioural contract.
---

If a function wants an `Animal` and you hand it a `Dog`, that should be fine: a dog can do everything an animal can. That is **subtyping**, written like this:

```formula
Dog <: Animal
where
<:: "is a subtype of": every value of the left-hand type can be used wherever the right-hand type is expected
Dog, Animal: two example class types; every Dog is an Animal
In words: Dog is a subtype of Animal, so a Dog may be passed anywhere an Animal is wanted.
```

The reverse direction is called a **supertype**: `Animal` is a supertype of `Dog`.

The easy part is classes. The hard part, and the source of real bugs, is what happens to *compound* types. If Dog is a subtype of Animal, is a `List<Dog>` a `List<Animal>`? Is a function that takes a `Dog` usable where a function that takes an `Animal` is expected? The answers are "it depends" and "no", and the rules that decide them are called **variance**.

## The substitution principle

The guiding rule is Barbara Liskov's **substitution principle** (1987, formalised with Jeannette Wing in 1994): a subtype should preserve the behaviour promised by its supertype’s contract.

A type checker can enforce the *shape* part: a subtype must have every member the supertype has, with compatible types. It can't enforce the *behaviour* part. A `Square` subclass whose `setWidth` also changes the height type-checks fine as a `Rectangle`, and still breaks callers that assume width and height are independent.

## Nominal and structural subtyping

Two important ways to establish subtype relationships are nominal declarations and structural compatibility. Real languages may combine them.

**Nominal**: subtyping exists only where you declared it. Java, C# and Kotlin class hierarchies work this way. Rust trait conformance also requires declarations, but trait implementation is not class-style subtyping.

```java
class Animal { String name() {...} }
class Dog extends Animal { ... }
// Dog <: Animal because of "extends"
```

**Structural**: a source type fits a target when it provides the target’s required members with compatible types, subject to the language’s additional rules. TypeScript, Go interfaces and Python `Protocol`s work this way.

```ts
interface Named { name: string }
class Robot { name = "R2"; volts = 5 }
// Extra volts does not remove name.
const n: Named = new Robot(); // ok
```

`Robot` never mentions `Named`, but it has a `name: string`, so it fits. Structural typing is convenient for JSON-shaped data; nominal typing stops two types that merely look alike (`UserId` and `OrderId`, both strings) being mixed up.

Many systems also have a **top** type for their relevant type domain (`Object` for Java reference types, excluding primitive types, `unknown` in TypeScript, `object` in Python, `Any?` in Kotlin) and many have a **bottom** type that is a subtype of everything in its domain and has no normally returned values (`never` in TypeScript, `Nothing` in Kotlin and Scala, `Never`/`NoReturn` in Python). Rust’s uninhabited `!` has a similar practical role, but the Rust Reference specifies coercion of never-typed expressions to other types rather than a universal subtype relation.

## Key takeaways
- A subtype can stand in for its supertype under the relevant typing and behavioural contract.
- Nominal declarations and structural member compatibility establish relationships differently.
- Top and bottom types have different roles; top types are defined relative to a type domain.

## Further reading
- [Liskov and Wing: Behavioural subtyping](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf)
- [TypeScript Handbook: Compatibility and soundness](https://www.typescriptlang.org/docs/handbook/type-compatibility.html)
- [Java Language Specification: Types](https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html)
- [PEP 484: Type hints](https://peps.python.org/pep-0484/)
- [Rust Reference: Never type](https://doc.rust-lang.org/reference/types/never.html)
