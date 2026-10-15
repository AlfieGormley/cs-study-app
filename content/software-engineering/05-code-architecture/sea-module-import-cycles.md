---
id: sea-module-import-cycles
sourceLesson: sea-modularity
title: Import cycles and automated boundaries
level: advanced
minutes: 4
summary: Explain a partially initialized Python import and enforce real dependency boundaries.
---

Acyclic package design helps both reasoning and Python initialization. This unit traces one import failure, then turns chosen boundaries into checks run in CI.

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

## Key takeaways
- An import can fail when a circular dependency reads a name before its definition executes.
- Deferring access can avoid initialization failure while leaving the design cycle intact.
- Extract concepts, invert dependencies, use events or merge inseparable modules to remove cycles.
- Import Linter independence checks include indirect dependencies.
- TYPE_CHECKING solves type-only import execution, with annotation-evaluation caveats.

## Further reading
- [Import Linter: contract types](https://import-linter.readthedocs.io/en/stable/contract_types/)
- [The import system — Python documentation](https://docs.python.org/3/reference/import.html)
- [typing.TYPE_CHECKING — Python documentation](https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING)
