---
id: pattern-traversal-iterators
title: Iterators, generators and traversal state
level: advanced
minutes: 3
sourceLesson: pattern-behavioural-2
summary: An iterable supplies an iterator; an exhausted iterator stays exhausted.
---

## Iterator pattern

### The problem

Clients want to walk through a collection without knowing how it's stored (array, tree, linked list, paginated API), and possibly have several walks in progress at once.

### The structure

```
 Aggregate              Iterator
 +__iter__() -------->  +__next__()
   returns new iter       next item or
                          StopIteration
```

### In Python

Python built this pattern into the language. A `for` loop calls `iter(x)` and then `next()` repeatedly until `StopIteration` is raised. A **generator function** (a function containing `yield`) writes the iterator for you:

```python
class Tree:
    def __init__(self, val, kids=()):
        self.val = val
        self.kids = kids

    def __iter__(self):
        # Pre-order: this node precedes
        # kids.
        yield self.val
        for k in self.kids:
            # Delegate into each child tree.
            yield from k

t = Tree(1, [Tree(2, [Tree(3)]), Tree(4)])
print(list(t))   # [1, 2, 3, 4]
```

Each call to `__iter__` returns a fresh generator, so two loops over `t` don't interfere.

The iterator protocol obtains one item per next() call; it does not require lazy construction or constant memory. Streaming can avoid loading the entire input, but memory still depends on buffering, maximum line length or fetched batch size, retained output and traversal state. This recursive generator keeps one suspended generator per level of the tree it is currently inside, so its traversal state grows with the tree's height (the number of levels from the root to the deepest node), not with the total number of nodes.

> [!warning] Iterators are single-use
> An iterator is also iterable; once exhausted it stays exhausted. A re-iterable collection such as a list can supply a fresh iterator for another pass. `g = (x * 2 for x in range(3))` then `list(g)` gives `[0, 2, 4]`, and a second `list(g)` gives `[]`.

### When not to use it

- Don't write a hand-rolled iterator class when a generator function will do. It's longer and easier to get wrong.
- Lazy iteration can surprise you. Errors inside a generator function’s body surface when it is advanced, not when the function is called. Expressions evaluated by the caller, including the outer iterable of a Python generator expression, can still fail immediately; and structural mutation during iteration can invalidate traversal. Adding or deleting dictionary keys may raise `RuntimeError`; replacing values for existing keys need not. List insertions/deletions may skip or repeat elements, while replacing an existing element does not inherently invalidate iteration.

### In real libraries

- **Built-in Python collections**, plus `itertools`, file objects (line by line), `os.scandir` and `csv.reader`.
- **Database cursors**: Many DB-API drivers provide iterable cursors (an optional DB-API extension). Server-side cursor modes can fetch batches without loading the whole result into the client.
- **Django QuerySets** are lazy and iterable; `.iterator()` bypasses the QuerySet result cache; database-driver buffering and backend support determine whether results are actually streamed.
- **Java's `Iterator`/`Iterable`** and C++ iterators (where the pattern is also the basis of the STL algorithms).

## Key takeaways
- An iterable supplies an iterator; an exhausted iterator stays exhausted.
- A fresh generator per traversal allows independent loops.
- The iterator protocol alone promises neither laziness nor constant memory.

## Further reading
- [Iterator types — Python documentation](https://docs.python.org/3/library/stdtypes.html#iterator-types)
