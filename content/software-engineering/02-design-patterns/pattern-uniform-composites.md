---
id: pattern-uniform-composites
title: Treating leaves and trees uniformly
level: intermediate
minutes: 3
sourceLesson: pattern-structural
summary: Composite gives leaves and groups the same relevant operation.
---

## Composite pattern

### The problem

You have a tree (files and folders, UI widgets, an expression) and want clients to treat a single item and a group of items **the same way**.

### The structure

```
        Component
        +size()
        ^       ^
        |       |
      Leaf    Composite
      size()  children: [Component]
              size(): sum of children
```

### In Python

```python
class File:
    def __init__(self, n):
        self.n = n

    def size(self):
        return self.n

class Folder:
    def __init__(self, *children):
        self.children = children

    def size(self):
        # Leaves and groups share size().
        # An empty group sums to zero.
        return sum(c.size()
                   for c in self.children)

tree = Folder(File(10),
              Folder(File(5), File(7)))
print(tree.size())
# 22
```

### When not to use it

- When leaves and groups genuinely behave differently. Forcing `add_child()` onto a leaf (to keep one interface) means a method that can only raise errors.
- Very deep trees can hit the active recursion limit; inspect sys.getrecursionlimit() rather than assuming a universal depth.

### In real libraries

- **scikit-learn's `Pipeline`** is itself an estimator, so a pipeline can sit inside another pipeline or a grid search.
- **The DOM**: elements contain elements, and most operations work on any node.
- **GUI toolkits** (Qt, Tkinter): a frame is a widget that contains widgets.
- **Python's `ast`**: a `Module` node contains statement nodes, which contain expression nodes.

## Key takeaways
- Composite gives leaves and groups the same relevant operation.
- Recursive delegation lets the group combine child results.
- Uniformity has limits when a leaf cannot sensibly support a group-only operation.

## Further reading
- [ast — Python documentation](https://docs.python.org/3/library/ast.html)
- [Iterator types — Python documentation](https://docs.python.org/3/library/stdtypes.html#iterator-types)
