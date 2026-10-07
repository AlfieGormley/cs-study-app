---
id: sep-solid
title: SOLID with examples
level: intermediate
minutes: 12
summary: The five SOLID principles with before-and-after code in Python and Java, what each one actually says, and where following them blindly does more harm than good.
---

**SOLID** is an acronym for five object-oriented design principles collected by Robert C. Martin around 2000. Michael Feathers coined the acronym a few years later. They are less rules than *questions to ask* when a design starts to hurt:

| Letter | Principle | Question it asks |
|---|---|---|
| S | Single responsibility | Who asks for this to change? |
| O | Open/closed | Can I add a case without editing old code? |
| L | Liskov substitution | Can a subtype stand in for its parent? |
| I | Interface segregation | Do clients depend on what they don't use? |
| D | Dependency inversion | Does policy depend on detail? |

All five are really about the previous lesson's themes: put things that change together in one place (cohesion), and keep the connections between places narrow (coupling).

## S: Single responsibility principle

The popular version, "a class should do one thing", is vague. Martin's sharper version is: **a module should be responsible to one, and only one, actor**. An actor is a group of people who might request a change.

```python
# Before: three actors, one class
class Employee:
    # asked for by finance
    def calculate_pay(self): ...
    # asked for by operations
    def report_hours(self): ...
    # asked for by IT / DBAs
    def save(self): ...
```

Imagine `calculate_pay` and `report_hours` share a helper `regular_hours()`. Finance asks for a change to how overtime is counted; a developer edits the helper; the operations report silently changes too. Two actors were coupled through one class.

```python
# After: one reason to change each
class PayCalculator:
    def pay(self, emp): ...

class HoursReporter:
    def report(self, emp): ...

class EmployeeRepository:
    def save(self, emp): ...
```

`Employee` becomes plain data. Each class now changes for one group's reasons.

> [!tip] The "and" test
> If describing a class needs "and" ("it parses the file *and* emails the result"), it probably serves more than one actor.

## O: Open/closed principle

Bertrand Meyer, 1988: software entities should be **open for extension but closed for modification**. You should be able to add new behaviour by adding code, not by editing code that already works.

```python
# Before: every new shape edits this
def area(shape):
    if shape.kind == "circle":
        return math.pi * shape.r ** 2
    elif shape.kind == "square":
        return shape.side ** 2
    # add triangle here... and in
    # perimeter(), draw(), to_json()...
```

The real cost isn't one `elif`. It's that the same `if kind ==` ladder tends to appear in many functions, so a new shape means finding and editing all of them.

```python
# After: new shapes are new classes
import math
from dataclasses import dataclass
from typing import Protocol

class Shape(Protocol):
    def area(self) -> float: ...

@dataclass
class Circle:
    r: float
    def area(self):
        return math.pi * self.r ** 2

@dataclass
class Square:
    side: float
    def area(self):
        return self.side ** 2
```

Adding `Triangle` touches no existing code. Plug-in architectures, middleware chains and strategy objects are all OCP in practice.

> [!warning] You can't be closed against everything
> OCP protects you along the axis you predicted. Polymorphic shapes make adding a *shape* easy but adding an *operation* (say `volume`) harder, since every class changes. Choose the axis that actually varies. This trade-off is known as the **expression problem**.

## L: Liskov substitution principle

Barbara Liskov, 1987, later formalised with Jeannette Wing: if `S` is a subtype of `T`, code written against `T` must keep working when given an `S`. Subtypes must honour the parent's **behavioural contract**, not just its method signatures.

The classic violation, in Java:

```java
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
- No **new exceptions** that callers of the parent wouldn't expect.

Common real-world violations:

```python
class ReadOnlyFile(File):
    def write(self, data):
        raise NotImplementedError
```

Java's own `Collections.unmodifiableList()` returns a `List` whose `add` throws `UnsupportedOperationException`. The JDK documents these as "optional operations", which is an honest admission that the `List` interface promises less than it appears to. Code that accepts any `List` and adds to it compiles fine and fails at runtime.

Fixes: don't inherit (make `Square` and `Rectangle` separate types sharing a `Shape` interface), use a compatible read-only contract (an immutable square can then be a valid rectangle subtype), or split the interface (`ReadableFile`, `WritableFile`).

## I: Interface segregation principle

**Clients should not be forced to depend on methods they do not use.** Big "fat" interfaces couple every client to every method.

```java
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
class SupportsRead(Protocol):
    def read(self, n: int) -> bytes: ...

def checksum(src: SupportsRead) -> int:
    ...
```

## D: Dependency inversion principle

Two parts:

1. High-level modules should not depend on low-level modules. **Both should depend on abstractions.**
2. Abstractions should not depend on details. Details should depend on abstractions.

"High-level" means policy (business rules); "low-level" means mechanism (databases, HTTP, files).

```python
# Before: policy depends on detail
class InvoiceService:
    def __init__(self):
        self.db = PostgresClient(DSN)
        self.mail = SmtpMailer("smtp")

    def bill(self, cust):
        ...
```

`InvoiceService` constructs concrete clients, making isolated tests and substitutions harder; monkey-patching can still replace those names in Python. Injecting a narrow abstraction makes the seam explicit.

```python
# After: policy owns the abstraction
class InvoiceRepo(Protocol):
    def save(self, inv): ...

class Mailer(Protocol):
    def send(self, to, body): ...

class InvoiceService:
    def __init__(self, repo: InvoiceRepo,
                 mail: Mailer):
        self.repo = repo
        self.mail = mail
```

```
 Before:
   InvoiceService --> PostgresClient

 After:
   InvoiceService --> InvoiceRepo
                          ^
                          | implements
   PostgresRepo ----------+
```

The arrow from the database now points *up* towards the abstraction: that's the inversion. Crucially, the interface belongs to the high-level module and is shaped by what it needs, not by what Postgres happens to offer.

### DIP is not the same as dependency injection

- **Dependency injection** is a technique: pass dependencies in (constructor, parameter) rather than creating them inside.
- **Dependency inversion** is a design principle about which way source-code dependencies point.

You can inject a concrete `PostgresClient` (DI without DIP), and you can follow DIP with a factory instead of injection. They work well together, and DI frameworks (Spring, Guice) are just one way to wire it up. Python projects usually manage with plain constructor arguments.

## Where SOLID goes wrong

- **Interface explosion.** An `IUserService` with exactly one implementation, created "for DIP", can add indirection without a demonstrated benefit. Introduce the abstraction when there's a second implementation or a real need to isolate (tests count).
- **SRP as "one method per class".** Splitting to the point where a feature is spread over twenty classes destroys cohesion. The test is actors and reasons to change, not size.
- **OCP everywhere.** Designing every class for extension is speculative; most code is best closed by simply being easy to edit.
- **Inheritance hierarchies.** Most LSP trouble starts with inheritance used for code reuse. Prefer composition; inherit only when the subtype truly honours the contract.

## Key takeaways
- SRP: a module should answer to one actor; split code that changes for different people's reasons.
- OCP: add behaviour by adding code; protect the axis of change that actually varies.
- LSP: subtypes must honour the parent's contract (no stronger preconditions, weaker postconditions or surprise exceptions). The mutable Square is the classic failure.
- ISP: prefer small, role-based interfaces; `typing.Protocol` makes this cheap in Python.
- DIP: policy defines abstractions and details implement them; it's a design principle, distinct from the dependency-injection technique.
- Apply SOLID in response to real change pressure, not by default.

## Further reading
- [SOLID — Wikipedia](https://en.wikipedia.org/wiki/SOLID)
- [The Single Responsibility Principle — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html)
- [A Behavioral Notion of Subtyping — Liskov and Wing (PDF)](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf)
- [Open–closed principle — Wikipedia](https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle)
- [Inversion of Control Containers and the Dependency Injection pattern — Martin Fowler](https://martinfowler.com/articles/injection.html)
- [PEP 544: Protocols (structural subtyping)](https://peps.python.org/pep-0544/)
