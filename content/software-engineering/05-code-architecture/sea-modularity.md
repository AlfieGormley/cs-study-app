---
id: sea-modularity
title: Modularity and dependency management
level: advanced
minutes: 15
summary: Information hiding and deep modules, drawing module boundaries, Python's tools for public interfaces, the acyclic and stable dependencies principles, breaking import cycles, modular monoliths and managing third-party packages.
---

Every architecture style in this module comes down to the same two questions. **Where are the boundaries?** And **which way do dependencies cross them?** This lesson looks at those questions directly, at the scale of modules and packages inside one codebase, and then at the dependencies you pull in from outside.

## Information hiding

In 1972 David Parnas published *On the Criteria To Be Used in Decomposing Systems into Modules*. He compared two ways of splitting the same program. One followed the steps of processing (read input, shift lines, sort, print). The other gave each module one **design decision to hide**: how lines are stored, how they're sorted.

When requirements changed, the step-based design needed edits everywhere, because every step knew the storage format. The decision-hiding design needed edits in one module.

The lesson still stands: **decompose around decisions likely to change, and hide each one behind an interface**. A good module boundary is one where the likely changes stay on one side.

### Deep and shallow modules

John Ousterhout (*A Philosophy of Software Design*) frames module quality as the cost of a module's interface versus the functionality it provides:

```
 deep module           shallow module
 +--------+            +----------------+
 |  API   |            |      API       |
 +--------+            +----------------+
 |        |            | implementation |
 |  impl  |            +----------------+
 |        |
 |        |
 +--------+
 small API,            big API,
 lots hidden           little hidden
```

Python's `open()` is deep: one call hides buffering, encodings, OS file handles and platform differences. A class whose methods are `get_x`, `set_x`, `get_y`, `set_y` is shallow: the interface is as complicated as the implementation, so it hides nothing.

Splitting code into many tiny classes and functions can *reduce* modularity if each piece is shallow, because readers must learn all the interfaces to understand any behaviour.

## Making the interface explicit in Python

Python has no `private` keyword, so modularity relies on conventions and tooling.

```
billing/
  __init__.py      # public API
  _invoices.py     # internal
  _tax.py          # internal
  _pdf.py          # internal
```

```python
# billing/__init__.py
from ._invoices import create_invoice
from ._invoices import Invoice

__all__ = ["create_invoice", "Invoice"]
```

- A leading underscore on a module or name means "internal; don't import from outside this package".
- `__init__.py` re-exports the public surface, so callers write `from billing import create_invoice`.
- `__all__` lists the names `from billing import *` exports, and documents intent for tools and readers.

The interpreter enforces __all__ for star imports, but not privacy for explicit underscore imports. A linter rule or import contract is what stops `orders` importing `billing._tax`.

## Dependency direction: the package principles

Robert C. Martin's package principles turn "point dependencies the right way" into rules you can check.

### ADP: no cycles

The **Acyclic Dependencies Principle**: the dependency graph between packages must have no cycles.

```
 cyclic                 acyclic
 orders --> billing     orders --> billing
   ^          |            |          |
   |          v            v          v
   +----- customers       customers <-+
```

With a cycle, the three packages behave as one: isolated testing, reasoning and extraction become harder, and a change to any can ripple to all.

### SDP: depend towards stability

The **Stable Dependencies Principle**: depend in the direction of stability. A package that many others depend on is hard to change (it is *stable* in Martin's sense, meaning costly to change, not "rarely buggy").

To make "stable" measurable, Martin counts the dependency arrows into and out of a package. Arrows coming in mean other code will break if this package changes; arrows going out mean this package can be broken by changes elsewhere. His measure of **instability** is the share of arrows that point outwards:

```formula
I = Ce / (Ca + Ce)
where
I: the instability of one package, a number from 0 (maximally stable) to 1 (maximally unstable); it is a ratio of two counts, so it has no unit
Ce: efferent couplings: how many other packages this package depends on (imports), its outgoing arrows
Ca: afferent couplings: how many other packages depend on (import) this package, its incoming arrows
In words: instability is the fraction of a package's dependencies that point outwards. A package that only imports others and is imported by nobody scores 1; a package that is imported by others and imports nothing scores 0.
```

Martin's original definition counts *classes* on each side of the boundary (classes outside that depend on classes inside, and classes inside that depend on classes outside); counting whole packages or modules, as here, is a common simplification that can give different numbers, though the idea is the same. If a package has no dependencies in either direction, both counts are 0 and the formula becomes 0 divided by 0, which is undefined; tools pick their own convention for that case.

For example, suppose `billing` is imported by `orders` and `checkout`, and itself imports only `money`:

```formula
I = Ce / (Ca + Ce)
I = 1 / (2 + 1)
I ≈ 0.33
where
I: the instability of `billing`, from 0 to 1, no unit
Ce: packages `billing` imports: only `money`, so 1
Ca: packages that import `billing`: `orders` and `checkout`, so 2
≈: approximately equal to (one third, rounded to two decimal places)
In words: one of billing's three dependency arrows points outwards, so it is fairly stable: two packages would feel any change to it.
```

A web package that imports four others and is imported by nothing scores 4 / (0 + 4) = 1; a `money` package imported by four others that imports nothing scores 0 / (4 + 0) = 0.

Volatile code (UI, integrations, experiments) should have high *I* and depend on low-*I* code, never the other way round. If a stable core package imports a volatile one, every experiment risks breaking the core.

The related **Stable Abstractions Principle** says stable packages should be abstract (interfaces or abstract types; a pure calculation is not automatically abstract) so they can be extended without being modified. That is why ports, owned by the core, sit at the stable end.

### Abstractness and the main sequence

Martin also measures how abstract a package is, so the two principles can be checked together:

```formula
A = Na / Nc
where
A: the abstractness of one package, from 0 (no abstract types) to 1 (only abstract types); a ratio of counts, so no unit
Na: the number of abstract classes and interfaces in the package (in Python, abstract base classes and Protocols)
Nc: the total number of classes in the package, abstract and concrete together
In words: abstractness is the fraction of a package's classes that are abstract.
```

Martin's ideal is that a package's abstractness and instability add up to 1: stable packages fully abstract, unstable packages fully concrete, or a balance in between. He calls the line where they add up to 1 the **main sequence**, and measures how far a package sits from it. (His original distance divided this by the square root of 2 to give the true perpendicular distance, at most about 0.707; the simpler form below, which he also gives, runs from 0 to 1.)

```formula
D = |A + I − 1|
where
D: the distance from the main sequence, from 0 (on the ideal line) to 1 (as far from it as possible); no unit
A: the package's abstractness, from 0 to 1, as defined above
I: the package's instability, from 0 to 1, as defined earlier in this section
| |: absolute value: drop any minus sign, so |−0.4| = 0.4
In words: add abstractness and instability; the further the total is from 1, in either direction, the more the package breaks the stable-abstractions guideline.
```

First example: a `core.ports` package holds two Protocols and nothing else. The core and the adapters import it, and it imports nothing.

```formula
A = Na / Nc = 2 / 2 = 1
I = Ce / (Ca + Ce) = 0 / (2 + 0) = 0
D = |A + I − 1| = |1 + 0 − 1| = 0
where
A: abstractness: both of its 2 classes are abstract
Na: abstract classes and interfaces: 2
Nc: all classes in the package: 2
I: instability, from 0 to 1
Ce: packages it imports: none, so 0
Ca: packages importing it: the core and the adapters, counted here as 2
D: distance from the main sequence, from 0 to 1
| |: absolute value: drop any minus sign
In words: the ports package is fully abstract and fully stable, so it sits exactly on the main sequence.
```

Second example: a concrete `pricing` package with no abstract types, which many packages import and which imports nothing.

```formula
A = 0
I = 0
D = |0 + 0 − 1| = 1
where
A: abstractness: no abstract types, so 0
I: instability: nothing imported, so 0
D: distance from the main sequence, from 0 to 1
| |: absolute value: drop any minus sign
In words: a stable but fully concrete package is as far from the main sequence as possible.
```

Martin calls this corner the **zone of pain**: everything depends on the package, and it offers no abstraction to extend instead of edit. Stable concrete code that almost never needs to change, such as a standard string library, is harmless there. The opposite corner, fully abstract and fully unstable, is the **zone of uselessness**: abstract types that nothing implements or uses. These numbers are prompts for a conversation, not targets to optimise.

## Import cycles in Python

Python allows circular imports, but they bite in confusing ways:

```python
# orders.py
from billing import invoice_for

class Order:
    ...
```

```python
# billing.py
from orders import Order

def invoice_for(order: Order):
    ...
```

`import orders` starts executing `orders.py`, which imports `billing`, which runs `from orders import Order`. `orders` is in `sys.modules` but only partly executed, and `Order` isn't defined yet. Python raises `ImportError: cannot import name 'Order' from partially initialized module 'orders'` (exact wording varies by version).

Deferring an import or deferring access after import orders can avoid some initialization failures. Merely changing the import style does not help if Order is still accessed before it is defined, but the **design** cycle remains. Real fixes:

1. **Extract the shared concept.** If both need `Order`, perhaps `Order` belongs in a lower module both can import.
2. **Invert a dependency.** `billing` defines a `Billable` Protocol; `Order` satisfies it; `billing` no longer imports `orders`.
3. **Use events.** `orders` publishes `OrderPlaced`; `billing` subscribes. `orders` doesn't know `billing` exists.
4. **Merge.** If two modules can't be understood apart, they may be one module.

For type-only dependencies, TYPE_CHECKING can avoid executing imports. Annotation evaluation must also be handled: older Python versions may need quoted/postponed annotations, and runtime get_type_hints still needs the referenced names. Python 3.14 defers annotations by default. This can be an appropriate type-only solution; it does not remove genuine runtime coupling.

## Enforcing boundaries

Boundaries erode one convenient import at a time unless a tool says no.

```ini
[importlinter]
root_package = shop
include_external_packages = True

[importlinter:contract:independent]
name = Features are independent
type = independence
modules =
    shop.orders
    shop.billing
    shop.catalogue

[importlinter:contract:no-ui-in-core]
name = Core does not import web
type = forbidden
source_modules = shop.core
forbidden_modules =
    flask
    shop.web
```

`independence` forbids any imports between the listed modules, in either direction, even indirectly through other modules; `forbidden` blocks specific imports. (Forbidding an external package like `flask` also needs `include_external_packages = True` in the root `[importlinter]` section.) Running `lint-imports` in CI turns architecture from a wiki page into a failing build.

## Modular monoliths

A **modular monolith** is one deployable application split into modules with enforced boundaries, each with a public API and private internals. It gets most of the code-level benefits people want from microservices (ownership, independent reasoning, smaller blast radius for changes) without network calls, distributed transactions or separate deploys.

Shopify is one published example. Its core Rails monolith (over 2.8 million lines of Ruby by 2020) was reorganised into components, and the company built **Packwerk**, a static analysis tool that checks references between packages against each package's declared dependencies, fast enough to run on every pull request. Existing violations are recorded in a to-do file per package, so only *new* ones fail the build. Shopify has also written candidly that the work was gradual, and that rules pushed without explaining the reasons mostly added friction.

The usual path is:

1. Group code by business capability (orders, billing, catalogue).
2. Declare each module's public interface.
3. Record current violations as a baseline, so new ones fail CI.
4. Reduce the baseline over time.

A clean code boundary can help later extraction, though data ownership, transactions, failure modes and operations still need redesign.

## Third-party dependencies

Every package you install is code you don't control but must keep working. Some basics:

- **Direct vs transitive.** Installing one web framework can pull in dozens of transitive packages. You are exposed to all of them.
- **Ranges vs pins.** Libraries declare *ranges* (`requests>=2.28,<3`) so they can coexist with others. Applications should **lock** exact versions of everything, including transitive packages, with hashes (`uv lock`, `poetry.lock`, `pip-compile --generate-hashes`), to constrain resolved artifacts. Reproducibility also depends on the interpreter, platform, build tools, system libraries and installation options.
- **Upgrade continuously.** Tools such as Dependabot or Renovate can propose small, frequent upgrades, which may be easier to review and validate than accumulated changes.
- **Diamond conflicts.** If package A needs `lib<2` and package B needs `lib>=2`, pip can't install both into one environment. Python has one version of each package per environment, unlike npm, which can nest different versions.
- **Supply-chain risk.** Typosquatting, compromised maintainer accounts and malicious updates are real. Locking with hashes, reviewing new dependencies and preferring well-maintained packages reduce exposure.

> [!warning] Wrap what you don't trust to stay still
> If a third-party API is spread across 200 files, an incompatible change can affect many call sites. Calling it through one adapter module (a port in hexagonal terms) can limit the number of call sites, provided the changed semantics still fit the port. Don't wrap stable, ubiquitous libraries like the standard library; wrap volatile, swappable ones.

## Key takeaways
- Draw module boundaries around design decisions likely to change, and hide each behind a small interface (Parnas).
- Prefer deep modules: small interfaces hiding substantial functionality.
- In Python, mark internals with underscores, re-export the public API from `__init__.py`, and enforce boundaries with tools such as import-linter.
- Package dependencies must be acyclic and should point towards stable, abstract code.
- Break import cycles by extracting shared concepts, inverting dependencies or using events, not just by moving imports.
- A modular monolith gives strong code boundaries without distributed-system costs.
- Lock exact application dependencies, upgrade often, and isolate volatile third-party APIs behind adapters.

## Further reading
- [Information hiding — Wikipedia](https://en.wikipedia.org/wiki/Information_hiding)
- [Package principles — Wikipedia](https://en.wikipedia.org/wiki/Package_principles)
- [Import Linter documentation](https://import-linter.readthedocs.io/en/stable/)
- [Packwerk — Shopify on GitHub](https://github.com/Shopify/packwerk)
- [Under Deconstruction: The State of Shopify's Monolith](https://shopify.engineering/shopify-monolith)
- [Circular dependency — Wikipedia](https://en.wikipedia.org/wiki/Circular_dependency)
