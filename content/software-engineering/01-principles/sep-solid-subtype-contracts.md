---
id: sep-solid-subtype-contracts
title: Subtypes must preserve behavioural contracts
level: intermediate
minutes: 3
summary: A subtype must preserve the parent’s accepted inputs and promised outcomes.
sourceLesson: sep-solid
---

SOLID examines responsibility, extension, subtyping, interfaces and dependency direction. This unit focuses on one of those questions; the earlier units establish the shared vocabulary.

## L: Liskov substitution principle

Barbara Liskov, 1987, later formalised with Jeannette Wing: if one type is a behavioural subtype of another, code written against the parent’s documented contract must keep working when given the subtype. Subtypes must honour the parent's **behavioural contract**, not just its method signatures.

The classic violation, in Java:

```java
// Square setters update both dimensions.
class Rectangle {
    protected int w, h;
    void setWidth(int w) { this.w = w; }
    void setHeight(int h) { this.h = h; }
    int area() { return w * h; }
}

class Square extends Rectangle {
    @Override
    void setWidth(int w) {
        this.w = w; this.h = w;
    }
    @Override
    void setHeight(int h) {
        this.w = h; this.h = h;
    }
}
```

```java
// A Square ends with two sides of four.
void resize(Rectangle r) {
    r.setWidth(5);
    r.setHeight(4);
    assert r.area() == 20; // fails: 16
}
```

Geometrically a square *is a* rectangle. Behaviourally, a *mutable* square is not: `Rectangle`'s contract says setting the width leaves the height alone, and `Square` breaks it.

Important requirements for behavioural subtyping include:

- **Preconditions** cannot be strengthened (accept at least what the parent accepts).
- **Postconditions** cannot be weakened (promise at least what the parent promises).
- **Invariants** of the parent must be preserved, including constraints on observable state changes over time.
- Exceptions must remain within the outcomes permitted by the parent’s contract; a new exception class is not inherently forbidden if that contract already allows it.

Common real-world violations:

```python
# This breaks a promised writable contract.
class ReadOnlyFile(File):
    def write(self, data):
        raise NotImplementedError
```

Java's own `Collections.unmodifiableList()` returns a `List` whose `add` throws `UnsupportedOperationException`. The JDK explicitly documents these as "optional operations", so rejecting one is permitted by the `List` contract. Code that accepts any `List` and adds to it compiles fine and fails at runtime.

Fixes: don't inherit (make `Square` and `Rectangle` separate types sharing a `Shape` interface), use a compatible read-only contract (an immutable square can then be a valid rectangle subtype), or split the interface (`ReadableFile`, `WritableFile`).

## Key takeaways
- A subtype must preserve the parent’s accepted inputs and promised outcomes.
- Mutable Square breaks the independent-dimension contract of the Rectangle example.
- Substitutability depends on the documented contract, including optional operations.

## Further reading
- [LiskovWing94.pdf](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf)
- [List](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html)
