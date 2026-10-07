---
id: type-subtyping-variance
title: Subtyping and variance
level: intermediate
minutes: 14
summary: When one type can stand in for another, nominal versus structural subtyping, why functions are contravariant in their arguments, why mutable containers must be invariant, and how Java, TypeScript, Python, Kotlin, C# and Rust express variance.
---

If a function wants an `Animal` and you hand it a `Dog`, that should be fine: a dog can do everything an animal can. That is **subtyping**. We write `Dog <: Animal`, read "Dog is a subtype of Animal".

The easy part is classes. The hard part, and the source of real bugs, is what happens to *compound* types. If `Dog <: Animal`, is a `List<Dog>` a `List<Animal>`? Is a function that takes a `Dog` usable where a function that takes an `Animal` is expected? The answers are "it depends" and "no", and the rules that decide them are called **variance**.

## The substitution principle

The guiding rule is Barbara Liskov's **substitution principle** (1987, formalised with Jeannette Wing in 1994): `S <: T` should mean any code written for a `T` still works when given an `S`.

A type checker can enforce the *shape* part: a subtype must have every member the supertype has, with compatible types. It can't enforce the *behaviour* part. A `Square` subclass whose `setWidth` also changes the height type-checks fine as a `Rectangle`, and still breaks callers that assume width and height are independent.

## Nominal and structural subtyping

Languages decide `S <: T` in one of two ways.

**Nominal**: subtyping exists only where you declared it. Java, C# and Kotlin class hierarchies work this way. Rust trait conformance also requires declarations, but trait implementation is not class-style subtyping.

```java
class Animal { String name() {...} }
class Dog extends Animal { ... }
// Dog <: Animal because of "extends"
```

**Structural**: `S <: T` if `S` has all of `T`'s members, whatever its name or declaration. TypeScript, Go interfaces and Python `Protocol`s work this way.

```ts
interface Named { name: string }
class Robot { name = "R2"; volts = 5 }
const n: Named = new Robot(); // ok
```

`Robot` never mentions `Named`, but it has a `name: string`, so it fits. Structural typing is convenient for JSON-shaped data; nominal typing stops two types that merely look alike (`UserId` and `OrderId`, both strings) being mixed up.

Many systems also have a **top** type for their relevant type domain (`Object` for Java reference types, excluding primitive types, `unknown` in TypeScript, `object` in Python, `Any?` in Kotlin) and many have a **bottom** type that is a subtype of everything and has no values (`never` in TypeScript, `Nothing` in Kotlin and Scala, `!` in Rust, `Never`/`NoReturn` in Python).

## Variance: the four cases

Take a generic type `F<T>` and suppose `Dog <: Animal`. Variance says how `F<Dog>` relates to `F<Animal>`:

| Variance | Rule |
|---|---|
| Covariant | `F<Dog> <: F<Animal>` |
| Contravariant | `F<Animal> <: F<Dog>` |
| Invariant | neither |
| Bivariant | both (unsound in general) |

Which one is *safe* depends only on how `F` uses `T`:

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

In TypeScript with `strictFunctionTypes`:

```ts
type OnDog = (d: Dog) => void;

const a: OnDog = (x: Animal) => {};
// ok: handles every Dog

const b: (x: Animal) => void =
  (d: Dog) => d.bark();
// error: might be given a Cat
```

## Aliased mutable containers and invariance

A read-only list of dogs can safely be read as a list of animals: everything you take out is an animal. But a *mutable* list lets values go in as well as out:

```ts
const dogs: Dog[] = [new Dog()];
const animals: Animal[] = dogs;
animals.push(new Cat());
dogs[1].bark(); // Cat has no bark
```

Both names point to the **same** array. Through `animals` you put a cat in; through `dogs` you take it out as a dog. TypeScript accepts this code (arrays are covariant there, a deliberate unsoundness) and it crashes at run time with `TypeError: dogs[1].bark is not a function`.

### Java's arrays: covariant, checked at run time

Java made arrays covariant from version 1.0, long before generics existed, so that methods like `Arrays.sort(Object[])` could take any array. To stay safe, the JVM checks **every store** into a reference array:

```java
Object[] objs = new String[2];
objs[0] = "fine";
objs[1] = 42;
// ArrayStoreException at run time
```

It is sound, but the error arrives at run time and runtime checks preserve compatibility, although the JIT may eliminate a check it proves redundant. C# copied this design, with `ArrayTypeMismatchException`.

### Java's generics: invariant, with wildcards

Java generics learnt the lesson. `List<Dog>` is **not** a `List<Animal>`:

```java
List<Dog> dogs = new ArrayList<>();
List<Animal> as = dogs; // compile error
```

Instead, each *use* of the type chooses its variance with a wildcard (**use-site variance**):

```java
// producer: read Animal values
List<? extends Animal> src = dogs;
Animal a = src.get(0); // ok
src.add(new Cat());    // error

// consumer: accepts Dog values
List<? super Dog> dst =
    new ArrayList<Animal>();
dst.add(new Dog());    // ok
Object o = dst.get(0); // only Object
```

An upper-bounded wildcard is not strictly read-only: `clear`, removals and `add(null)` can still be permitted. A lower-bounded list can still be read as `Object`.

Joshua Bloch's mnemonic in *Effective Java* is **PECS: producer extends, consumer super**. The JDK's own signature follows it:

```java
static <T> void copy(
    List<? super T> dest,
    List<? extends T> src)
```

## Declaration-site variance

Writing wildcards at every use is noisy. Kotlin, C# and Scala let the *type's author* declare variance once:

```kotlin
interface Source<out T> {
    fun next(): T      // T only out
}
interface Sink<in T> {
    fun put(x: T)      // T only in
}
```

The compiler checks the declaration: using an `out T` as a method parameter is an error. Kotlin's read-only `List<out E>` is covariant; `MutableList<E>` is invariant. C# marks `IEnumerable<out T>` and `Action<in T>` the same way, though only on interfaces and delegates. TypeScript 4.7 added optional `in`/`out` annotations on type parameters, mainly to make variance explicit and checking faster.

## Python: invariant lists, covariant sequences

Python's type checkers follow the same rules. `list` is mutable, so it's invariant; `Sequence` is read-only, so it's covariant:

```python
from collections.abc import Sequence

def feed(xs: list[Animal]) -> None: ...
def show(xs: Sequence[Animal]) -> None: ...

dogs: list[Dog] = [Dog()]
feed(dogs)  # mypy error: invariant
show(dogs)  # ok: Sequence is covariant
```

`Callable[[Animal], None]` is usable where `Callable[[Dog], None]` is expected (contravariant parameters). For your own generics, older code declares `TypeVar("T_co", covariant=True)`; the Python 3.12 syntax `class Box[T]:` lets the checker **infer** variance from how `T` is used.

## Rust: lifetimes and higher-ranked types

Rust has no subclassing, so `Dog <: Animal` never arises; traits use bounds instead. Its subtyping includes lifetime relationships and higher-ranked function/trait-object types. For references, a longer lifetime can be shortened: `'long <: 'short`, meaning a reference that lives longer can be used where a shorter one is needed. So `&'static str` can go wherever `&'a str` is expected.

Variance still matters, and the compiler infers it from each type's fields:

| Type | Variance in `T` |
|---|---|
| `&'a T`, `Box<T>`, `Vec<T>` | Covariant |
| `&'a mut T` | Invariant |
| `Cell<T>` | Invariant |
| `fn(T) -> U` | Contra in `T`, co in `U` |

`&mut T` is invariant for exactly the mutable-list reason: if `&mut &'static str` could be treated as `&mut &'a str`, you could write a short-lived string through it and later read it back as `'static`, a dangling reference.

## Variance trade-offs and runtime checks

| Language | Hole | Outcome |
|---|---|---|
| Java, C# | Covariant arrays | Run-time store check |
| TypeScript | Covariant arrays | Silent, crashes later |
| TypeScript | Method params bivariant | Silent |
| Eiffel | Covariant method params | Known unsound |

TypeScript's `strictFunctionTypes` (part of `strict`) applies to ordinary function types and function-typed properties. Parameters of methods and constructors declared with method syntax stay bivariant, so DOM-style event handler interfaces keep working:

```ts
// method syntax: bivariant
interface A { m(x: Dog): void }

// property syntax: contravariant
interface B { m: (x: Dog) => void }
```

## Pitfalls

- **Expecting `List<Dog>` to be a `List<Animal>`.** In Java, Python's `list` and Kotlin's `MutableList` it isn't. Accept `List<? extends Animal>`, `Sequence[Animal]` or `List<Animal>` (read-only) instead.
- **Trusting TypeScript arrays.** Passing `Dog[]` as `Animal[]` to a function that pushes into it compiles and corrupts the caller's array. Prefer `readonly Animal[]` parameters.
- **Overriding with a narrower parameter.** A subclass method that only accepts `Dog` where the parent accepted `Animal` breaks substitution. Java treats it as an overload, not an override.
- **Confusing structural fits with intent.** In TypeScript, two unrelated interfaces with the same shape are interchangeable. Use branded types when that matters.

## Key takeaways
- `S <: T` means an `S` can be used anywhere a `T` is expected; checkers enforce the shape, not the behaviour.
- Nominal class systems (Java, C#) need declared relationships; structural systems (TypeScript, Go, Python Protocols) go by members.
- Function types are contravariant in parameters and covariant in results.
- Read-only (producer) types can be covariant, write-only (consumer) types contravariant, and freely aliased read-write interfaces generally need invariance or another safety mechanism.
- Java uses use-site wildcards (PECS); Kotlin, C# and Scala use declaration-site `out`/`in`; Python infers or declares variance on type variables; Rust infers variance from fields; owned containers can remain covariant because mutation through a mutable borrow restricts aliasing.
- Covariant mutable arrays are a known hole: Java and C# check stores at run time, TypeScript doesn't check at all.

## Further reading
- [Covariance and contravariance (computer science) — Wikipedia](https://en.wikipedia.org/wiki/Covariance_and_contravariance_(computer_science))
- [Liskov substitution principle — Wikipedia](https://en.wikipedia.org/wiki/Liskov_substitution_principle)
- [Wildcard guidelines — The Java Tutorials](https://docs.oracle.com/javase/tutorial/java/generics/wildcardGuidelines.html)
- [Generics: in, out, where — Kotlin docs](https://kotlinlang.org/docs/generics.html)
- [Strict function types — TypeScript 2.6 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-6.html)
- [Generics and variance — mypy docs](https://mypy.readthedocs.io/en/stable/generics.html)
- [Subtyping and variance — The Rustonomicon](https://doc.rust-lang.org/nomicon/subtyping.html)
- [Covariance and contravariance in generics — .NET, Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/generics/covariance-and-contravariance)
- [Primary verification source 1](https://doc.rust-lang.org/reference/subtyping.html)
