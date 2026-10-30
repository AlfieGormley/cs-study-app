---
id: pattern-factory-callables
title: Factory methods and callable factories
level: basic
minutes: 3
sourceLesson: pattern-creational
summary: A factory method lets subclasses choose the product used by a base-class operation.
---

Creating an object looks trivial: `Thing()`. The trouble is that a constructor call hard-codes three decisions at the call site: **which class**, **how it's configured** and **whether a new one is made at all**.

When those decisions need to vary (by platform, by configuration, by test), every call site has to change. Creational patterns move those decisions to one place.

Python changes the picture a lot. Classes are objects you can pass around, functions are first-class, and keyword arguments with defaults remove much of the need for builders. So for each pattern below, we'll see the classic shape and then the Python way.

## Factory Method pattern

### The problem

A framework class knows *when* it needs an object but not *which* class to make. Its subclasses do.

For example, a generic list view knows it must fetch records, but only a specific view knows which records.

### The structure

```
  Creator                  Product
  +make() -> Product  ...> (interface)
  +operation()                ^
      ^                       |
      |                       |
  ConcreteCreator ------> ConcreteProduct
  +make()   creates
```

`operation()` in the base class calls `self.make()`. Subclasses override `make()` to return their own product.

The GoF intent is to define an interface for creating an object but let subclasses decide which class to instantiate. A factory method is usually called from inside a template method: the base class keeps the fixed algorithm, and one overridable step happens to create an object.

### In Python

```python
class Exporter:
    def make_writer(self):
        raise NotImplementedError

    def export(self, rows):
        # Dispatch to the subclass factory.
        w = self.make_writer()
        for row in rows:
            w.write(row)
        return w.result()

class CsvWriter:
    # Toy: fields contain no commas,
    # quotes or newlines. Use csv.writer
    # for general CSV serialization.
    def __init__(self):
        self.lines = []

    def write(self, row):
        # Accumulate one simplified CSV row.
        self.lines.append(",".join(row))

    def result(self):
        return "\n".join(self.lines)

class CsvExporter(Exporter):
    def make_writer(self):
        return CsvWriter()

print(CsvExporter().export([["a", "b"]]))
# a,b
```

Often a simpler Python version is to pass the class (or any callable) in: `Exporter(writer_factory=CsvWriter)`. `collections.defaultdict(list)` does exactly this: `list` is the factory it calls for missing-key indexing (d[key]); get() does not invoke it.

### When not to use it

- When there's only ever one product class. Just call it.
- When the subclass exists *only* to override the factory. Passing a callable is lighter than a subclass per product.

### In real libraries

- **Django class-based views**: `get_queryset()` and `get_form_class()` are factory-method-style hooks that subclasses override to choose what the view works with.
- **Django REST Framework**: `get_serializer_class()`.
- **Alternative constructors** such as `datetime.fromtimestamp()` and `dict.fromkeys()` are `classmethod` factories. They're not the GoF pattern exactly, but they serve the same purpose: named ways to create an object.

## Key takeaways
- A factory method lets subclasses choose the product used by a base-class operation.
- Passing a class or callable is often enough in Python.
- Named alternative constructors are useful factories without necessarily being the GoF pattern.

## Further reading
- [collections.defaultdict — Python documentation](https://docs.python.org/3/library/collections.html#collections.defaultdict)
- [Design Patterns — publisher catalogue](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-software-9780201633610)
