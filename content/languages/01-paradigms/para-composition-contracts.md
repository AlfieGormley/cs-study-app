---
id: para-composition-contracts
title: Substitution and object composition
level: basic
minutes: 3
sourceLesson: para-oop
summary: Subtyping must preserve the promises callers rely on.
---

An inheritance relationship is useful only when callers can rely on its behavioral contract. Composition offers a separate way to reuse an implementation.

## Liskov substitution

The **Liskov substitution principle** (Barbara Liskov, 1987) says a subtype must be usable anywhere its parent is, without surprising the caller. The famous violation is `Square extends Rectangle`. A rectangle lets you set width and height independently; a square cannot. Code that does `r.setWidth(5); r.setHeight(2)` and expects area 10 breaks when handed a `Square`. In geometry a square *is a* rectangle, but in code a *mutable* square does not behave like a mutable rectangle.

## Composition

**Object composition** builds objects out of other objects: a `Car` *has an* `Engine`. Instead of inheriting behaviour, an object holds a reference to a helper and passes calls on to it, which is called **delegation**.

```java
// Delegate to the separate inner set.
class CountingSet<E> {
  private final Set<E> inner =
      new HashSet<>();
  int added = 0;

  boolean add(E e) {
    added++;
    return inner.add(e);
  }

  boolean addAll(Collection<E> c) {
    added += c.size();
    return inner.addAll(c);
  }
}
```

Now `inner.addAll` calls `inner`'s own `add`, not ours, so the count is correct. The wrapper depends only on `Set`'s public behaviour. You may substitute another Set implementation only if its contract suits callers: TreeSet requires an ordering and has different null and equality/ordering considerations. (In practice you would also `implements Set<E>` and forward the remaining methods, which is the **decorator pattern**.)

The *Design Patterns* book (Gamma, Helm, Johnson and Vlissides, 1994) summed it up as "favour object composition over class inheritance". The rule of thumb:

- Use inheritance for a genuine **is-a** relationship where the subtype honours the parent's contract, ideally when the parent was designed for extension.
- Use composition for **has-a** or **uses-a** relationships, and whenever you just want to reuse code.

Many newer languages lean this way. The **Go language** has no class inheritance: it offers struct embedding (promoted fields and methods) and interfaces. **Rust** has traits but no inheritance between structs.

## Key takeaways
- Subtyping must preserve the promises callers rely on.
- Delegation can reuse behaviour without inheriting internals.

## Further reading
- [Liskov and Wing: behavioral subtyping](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf)
- [Go: embedding and interfaces](https://go.dev/doc/faq#Is_Go_an_object-oriented_language)
