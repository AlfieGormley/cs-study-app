---
id: type-mutation-wildcards
title: Mutation, arrays and Java wildcards
level: intermediate
minutes: 3
sourceLesson: type-subtyping-variance
summary: Freely aliased mutable collections need invariance or another safety mechanism.
---

Assume Dog and Cat are different subclasses of Animal, and Dog alone supplies bark(). Aliases matter because two typed names can still refer to one mutable collection.

## Aliased mutable collections and invariance

A read-only list of dogs can safely be read as a list of animals: everything you take out is an animal. But a *mutable* list lets values go in as well as out:

```ts
const dogs: Dog[] = [new Dog()];
const animals: Animal[] = dogs;
// Both names still point at one array.
animals.push(new Cat());
dogs[1].bark(); // Cat has no bark
```

Both names point to the **same** array. Through `animals` you put a cat in; through `dogs` you take it out as a dog. TypeScript accepts this code (arrays are covariant there, a deliberate unsoundness) and it crashes at run time with `TypeError: dogs[1].bark is not a function`.

### Java's arrays: covariant, checked at run time

Java made reference arrays covariant before generics, allowing operations written for `Object[]` to accept arrays such as `String[]`. Primitive arrays are separate: `int[]` is an `Object`, but is not an `Object[]`. To stay safe, the JVM checks **every store** into a reference array:

```java
Object[] objs = new String[2];
objs[0] = "fine";
// The runtime element type stays String.
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
// The unknown subtype need not accept Cat.
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

## Key takeaways
- Freely aliased mutable collections need invariance or another safety mechanism.
- Java arrays check stores at runtime; TypeScript can accept an alias that fails later.
- Producer extends and consumer super describe permitted reads and writes, not absolute immutability.

## Further reading
- [Java Language Specification: Types](https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html)
- [Java Language Specification: Arrays](https://docs.oracle.com/javase/specs/jls/se21/html/jls-10.html)
- [Java generics: Wildcard guidelines](https://docs.oracle.com/javase/tutorial/java/generics/wildcardGuidelines.html)
- [TypeScript Handbook: Compatibility and soundness](https://www.typescriptlang.org/docs/handbook/type-compatibility.html)
