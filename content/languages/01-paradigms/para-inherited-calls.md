---
id: para-inherited-calls
title: Inheritance and fragile base classes
level: basic
minutes: 3
sourceLesson: para-oop
summary: An inherited method can call an overridden method.
---

Calling an inherited method can run code in both a parent and a child class. Trace those calls before depending on inheritance for reuse.

## Inheritance

**Inheritance** lets a class reuse and extend another. A `Dog` *is an* `Animal`: it gets the parent's fields and methods and can **override** some of them.

```java
// greet dispatches on the actual Dog.
class Animal {
  String speak() { return "..."; }
  String greet() {
    return "I say " + speak();
  }
}

class Dog extends Animal {
  @Override
  String speak() { return "Woof"; }
}
```

`new Dog().greet()` returns `"I say Woof"`. The inherited `greet` calls `speak`, and because the object is a `Dog`, the overridden version runs.

Inheritance does two separate jobs at once:

1. **Code reuse**: the subclass gets the parent's implementation.
2. **Subtyping**: a `Dog` can be used wherever an `Animal` is expected.

Mixing these two jobs is where trouble starts.

## The fragile base class problem

Because subclasses depend on *how* the parent is implemented, not just on what it promises, changes in the parent can break them. Joshua Bloch's *Effective Java* has the classic example: a set that counts attempted insertions, including duplicates.

```java
// addAll can call our overridden add.
class CountingSet<E>
    extends HashSet<E> {
  int added = 0;

  @Override
  public boolean add(E e) {
    added++;
    return super.add(e);
  }

  @Override
  public boolean addAll(
      Collection<? extends E> c) {
    added += c.size();
    return super.addAll(c);
  }
}
```

Calling `addAll(List.of("a", "b", "c"))` leaves `added` at 6, not 3. `HashSet` inherits `addAll` from `AbstractCollection`, which calls `add` once per element, and that call dispatches to the overridden `add`. Nothing in `HashSet`'s public contract tells you this; you had to know its internals.

## Key takeaways
- An inherited method can call an overridden method.
- Subclass dependence on implementation details can double-count work.

## Further reading
- [Java: AbstractCollection.addAll](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/AbstractCollection.html)
- [Java: inheritance and overriding](https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html)
