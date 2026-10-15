---
id: fp-mutation-traps
title: Mutation traps and immutable update costs
level: basic
minutes: 4
sourceLesson: fp-pure-functions
summary: Defaults, aliases and in-place methods can preserve unwanted shared mutation.
---

Defaults, aliases and in-place methods can preserve unwanted shared mutation. This unit develops that mechanism using the earlier units as prerequisites.

## The classic pitfalls

## Python's mutable default argument

Default values are evaluated once, when the `def` runs, not on each call:

```python
# The default list outlives each call.
def add(item, bag=[]):
    bag.append(item)
    return bag

add(1)   # [1]
add(2)   # [1, 2]  same list!
```

Use `bag=None` and create a new list when it is None; this still mutates an explicitly supplied list. To avoid mutation altogether, use `def add(item, bag=()): return [*bag, item]`.

## In-place versus copying methods

Many standard library methods mutate. Know which:

| Mutates | Returns new |
|---|---|
| `list.sort()` | `sorted(list)` |
| `list.reverse()` | `list[::-1]` |
| JS `arr.sort()` | JS `arr.toSorted()` |
| JS `arr.reverse()` | JS `arr.toReversed()` |
| JS `arr.splice()` | JS `arr.toSpliced()` |

JavaScript added the `toSorted`, `toReversed`, `toSpliced` and `with` methods in ES2023 to provide copying counterparts to mutating operations.

## Aliasing

Two names, one object. A change through one is visible through the other.

```python
# Both names refer to the same list.
a = [1, 2]
b = a
b.append(3)
print(a)   # [1, 2, 3]
```

With immutable data, aliasing is harmless, which is why functional languages share structure freely (see the lesson on persistent data structures).

## Costs and trade-offs

Purity and immutability are not free.

- Copying. Naively copying a 1-million-element list to change one item is O(n), where n is the number of elements: the work grows in proportion to the size of the list. Persistent balanced trees and vector tries share unchanged parts and can give O(log n) updates; persistent linked-list indexed updates remain linear.
- Garbage. Creating new values constantly means more allocation. Modern generational garbage collectors handle short-lived objects cheaply, but it still matters in hot loops.
- Awkward fits. Some algorithms (in-place quicksort, union-find, graph algorithms over adjacency arrays) are naturally imperative. Haskell offers the `ST` monad for local mutation that stays invisible from outside.
- Language support. In Python and JavaScript immutability is a discipline, not a guarantee. Nothing stops a colleague mutating your "immutable" dict.

The copying cost is the one most worth quantifying. Big-O notation describes how the work for one update grows as the collection grows:

```formula
W_copy = O(n)
W_tree = O(log_2(n))
log_2(1000000) ≈ 20
where
W_copy: the work to change one item by naively copying the whole list, counted in elements copied
W_tree: the work for one update of a persistent balanced tree, counted in nodes copied (one per level on the path from the root to the changed item)
n: the number of elements in the collection; here 1,000,000
O(...): Big-O notation: how the work grows as n grows, ignoring constant factors; O(n) means "in proportion to n"
log_2(n): the base-2 logarithm of n: how many times you can halve n before reaching 1
≈: approximately equal to
In words: a naive copy touches all n elements, while a balanced persistent tree copies only about one node per level, roughly log_2(n) of them.
```

For a million elements that is 1,000,000 element copies versus about 20 node copies. The tree figure assumes the tree stays balanced; a persistent linked list gets no such saving, because an indexed update must copy the prefix through the changed cell.

> [!tip] Where it pays off most
> React state hooks compare next and previous state using Object.is; React-Redux useSelector uses strict equality by default. Mutating and returning the same object can suppress the update-driven render; unrelated renders can still occur. Immutable updates make identity a useful change signal.

## Key takeaways
- Defaults, aliases and in-place methods can preserve unwanted shared mutation.
- Copying and persistent path copying have different cost models.

## Further reading
- [Python Faq](https://docs.python.org/3/faq/programming.html)
- [ECMAScript: indexed collections](https://tc39.es/ecma262/multipage/indexed-collections.html)
- [React Reducer](https://react.dev/reference/react/useReducer)
- [Okasaki: Purely Functional Data Structures](https://www.cs.cmu.edu/~rwh/students/okasaki.pdf)
