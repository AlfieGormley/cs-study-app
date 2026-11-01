---
id: sea-module-import-cycles
sourceLesson: sea-modularity
title: Import cycles and automated boundaries
level: advanced
minutes: 4
summary: Explain a partially initialized Python import and enforce real dependency boundaries.
---

A dependency cycle is not only a design smell; in Python it can also stop a program starting. This unit traces one import failure, then turns chosen boundaries into checks that run in CI.

## Import cycles in Python

Python allows circular imports, but they bite in confusing ways:

```python
# orders.py
# billing re-enters orders before Order
# exists.
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

`import orders` starts executing `orders.py`, which imports `billing`, which runs `from orders import Order`. `orders` is in `sys.modules` but only partly executed, and `Order` isn't defined yet. Python raises `ImportError: cannot import name 'Order' from partially initialized module 'orders' (most likely due to a circular import)`.

The wording varies. Since Python 3.13, if these files sit in the same folder as the script you run, the message may instead suggest renaming `orders.py`, as though it shadowed a library. Same `ImportError`, same cause: the circular import.

You can often make the error go away by moving the import inside a function, or by writing `import orders` and reading `orders.Order` only later. That changes *when* the name is looked up: if it is still read before `Order` is defined, it still fails. Either way, the **design** cycle remains. Real fixes:

1. **Extract the shared concept.** If both need `Order`, perhaps `Order` belongs in a lower module both can import.
2. **Invert a dependency.** `billing` defines a `Billable` Protocol; `Order` satisfies it; `billing` no longer imports `orders`.
3. **Use events.** `orders` publishes `OrderPlaced`; `billing` subscribes. `orders` doesn't know `billing` exists.
4. **Merge.** If two modules can't be understood apart, they may be one module.

When one module needs another *only for type hints*, `if TYPE_CHECKING:` lets the type checker see the import while it never runs at runtime. Annotations then need care: before Python 3.14 you quote them or add `from __future__ import annotations`, while 3.14 evaluates annotations lazily by default. Tools that read hints at runtime, such as `typing.get_type_hints`, still need the real names. This is a good fix for a type-only dependency; it does nothing about code that genuinely calls across.

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

## Key takeaways
- An import can fail when a circular dependency reads a name before its definition executes.
- Deferring access can avoid initialization failure while leaving the design cycle intact.
- Extract concepts, invert dependencies, use events or merge inseparable modules to remove cycles.
- Import Linter independence checks include indirect dependencies.
- `TYPE_CHECKING` fixes type-only imports; it does not remove runtime coupling.

## Further reading
- [Import Linter: contract types](https://import-linter.readthedocs.io/en/stable/contract_types/)
- [The import system — Python documentation](https://docs.python.org/3/reference/import.html)
- [typing.TYPE_CHECKING — Python documentation](https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING)
