---
id: sea-module-information-hiding
sourceLesson: sea-modularity
title: Information hiding and public interfaces
level: advanced
minutes: 4
summary: Draw boundaries around changing decisions and expose a small Python package interface.
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

Python's `open()` is deep: one call hides buffering, encodings, operating-system file descriptors and platform differences. A class whose methods are `get_x`, `set_x`, `get_y`, `set_y` is shallow: the interface is as complicated as the implementation, so it hides nothing.

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

# Control star imports, not explicit
# imports.
__all__ = ["create_invoice", "Invoice"]
```

- A leading underscore on a module or name means "internal; don't import from outside this package".
- `__init__.py` re-exports the public surface, so callers write `from billing import create_invoice`.
- `__all__` lists the names `from billing import *` exports, and documents intent for tools and readers.

The interpreter enforces __all__ for star imports, but not privacy for explicit underscore imports. A linter rule or import contract is what stops `orders` importing `billing._tax`.

## Key takeaways
- Hide changeable design decisions behind an interface.
- Deep modules provide substantial behavior through a small interface.
- Underscores mark internals by convention; __all__ controls star imports rather than privacy.
- Re-exports make the intended public package surface clear.

## Further reading
- [On the Criteria To Be Used in Decomposing Systems into Modules — David Parnas](https://www.win.tue.nl/~wstomv/edu/2ip30/references/criteria_for_modularization.pdf)
- [A Philosophy of Software Design — John Ousterhout](https://web.stanford.edu/~ouster/cgi-bin/book.php)
- [PEP 8: public and internal interfaces](https://peps.python.org/pep-0008/#public-and-internal-interfaces)
