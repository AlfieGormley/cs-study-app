---
id: type-generic-relationships
title: Generics preserve type relationships
level: intermediate
minutes: 3
sourceLesson: type-generics
summary: A type parameter links arguments and results without replacing them with an unchecked universal container.
---

You want a function that returns the first element of a list. Lists of ints, lists of strings, lists of users: the logic is identical. In a statically typed language without generics you have two bad options.

1. Write it once per type: `firstInt`, `firstString`, `firstUser`. Duplicated code.
2. Write it once for "anything", using `Object` or `void*`, and cast the result back. The type checker loses track, and a wrong cast fails at run time (or, in C, silently).

Java before version 5 (2004) used non-generic collections. This modern raw-list example illustrates that API style; the autoboxing of `42` itself requires Java 5 or later:

```java
List names = new ArrayList();
names.add("Ada");
names.add(42);  // nothing stops this
String s = (String) names.get(1);
// ClassCastException at run time
```

**Generics** fix this. A type gets a **type parameter**, a placeholder filled in at each use, and the checker tracks it:

```java
List<String> names = new ArrayList<>();
names.add(42);  // compile error
String s = names.get(0); // no cast
```

## Parametric polymorphism

A function that works uniformly for every type shows **parametric polymorphism**. "Uniformly" is the important word: it runs the same code whatever the type, never inspecting it.

```haskell
first :: [a] -> Maybe a
-- Absence is explicit for an empty list.
first []      = Nothing
first (x : _) = Just x
```

```ts
function first<T>(xs: T[]): T | undefined {
  // Empty arrays yield undefined.
  return xs[0];
}
const n = first([1, 2]);
// n: number | undefined
```

```python
def first[T](xs: list[T]) -> T:
    # Empty lists raise IndexError.
    return xs[0]   # Python 3.12+ syntax
```

In the Haskell line, `::` reads "has type", `[a]` means "a list of `a`", and `->` separates the argument type from the result type, so `first` takes a list of `a` and returns a `Maybe a` (either `Nothing` or `Just` one `a`). On an empty list these examples differ: Haskell returns `Nothing`, TypeScript returns `undefined`, and Python raises `IndexError`. The type variable (`a`, `T`) links the input to the output. Calling `first` on a list of numbers gives a number back, and the checker knows it.

This is one of three kinds of polymorphism:

| Kind | Idea | Example |
|---|---|---|
| Parametric | Same code for all types | `first<T>` |
| Ad hoc | Different code per type | Overloading, type classes |
| Subtype | Use a subclass where a superclass is expected | `Animal a = new Dog()` |

## Key takeaways
- A type parameter links arguments and results without replacing them with an unchecked universal container.
- Empty-input behaviour differs between Maybe, undefined and an exception.

## Further reading
- [Java generics: Type erasure](https://docs.oracle.com/javase/tutorial/java/generics/erasure.html)
- [TypeScript Handbook: Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [PEP 695: Type parameter syntax](https://peps.python.org/pep-0695/)
- [Haskell 2010: Standard classes](https://www.haskell.org/onlinereport/haskell2010/haskellch6.html)
