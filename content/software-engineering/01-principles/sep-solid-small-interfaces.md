---
id: sep-solid-small-interfaces
title: Ask for the capability a client needs
level: intermediate
minutes: 3
summary: Narrow interfaces keep clients independent of capabilities they do not need.
sourceLesson: sep-solid
---

SOLID examines responsibility, extension, subtyping, interfaces and dependency direction. This unit focuses on one of those questions; the earlier units establish the shared vocabulary.

## I: Interface segregation principle

**Clients should not be forced to depend on methods they do not use.** Big "fat" interfaces couple every client to every method.

```java
// Unsupported roles become throwing stubs.
// Before
interface Machine {
    void print(Doc d);
    void scan(Doc d);
    void fax(Doc d);
}

class BasicPrinter implements Machine {
    public void print(Doc d) { ... }
    public void scan(Doc d) {
        throw new
          UnsupportedOperationException();
    }
    public void fax(Doc d) {
        throw new
          UnsupportedOperationException();
    }
}
```

`BasicPrinter` is forced to implement methods it can't support, which violates LSP if the contract requires those operations to succeed. A changed `fax` signature can affect implementers even when their useful role is only printing; effects on clients and recompilation depend on the change and toolchain.

```java
// Each implementation selects its roles.
// After: small, role-based interfaces
interface Printer { void print(Doc d); }
interface Scanner { void scan(Doc d); }

class BasicPrinter implements Printer {
    public void print(Doc d) { ... }
}

class OfficeHub
        implements Printer, Scanner { ... }
```

In Python, `typing.Protocol` makes this natural. A function declares the narrow capability it needs, and a static checker accepts objects with compatible member signatures, without explicit inheritance. An annotation does not enforce that contract at runtime:

```python
# The annotation asks only for reading.
class SupportsRead(Protocol):
    def read(self, n: int) -> bytes: ...

def checksum(src: SupportsRead) -> int:
    ...
```

## Key takeaways
- Narrow interfaces keep clients independent of capabilities they do not need.
- A Python Protocol supports structural static checking without explicit inheritance.
- Annotations describe a contract; they do not enforce it at runtime.

## Further reading
- [peps.python.org](https://peps.python.org/pep-0544/)
- [RoleInterface](https://martinfowler.com/bliki/RoleInterface.html)
