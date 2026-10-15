---
id: para-immutable-values
title: Immutability and structural sharing
level: intermediate
minutes: 3
sourceLesson: para-functional-basics
summary: Binding protection and shallow freezing do not freeze nested objects.
---

Keeping old values unchanged makes updates easier to reason about. Check whether a language feature protects a binding, an object's immediate fields or the entire nested structure.

## Immutability

In FP, data is **immutable**: instead of changing a value, you create a new one.

```python
# New list versus mutation of the old one.
# Mutating
cart.append(item)

# Immutable style
new_cart = cart + [item]
```

Immutability removes a whole class of bugs: no function can change your data behind your back, and no other thread can observe a half-updated object.

Languages give you different tools, and some are weaker than they look:

| Language | Tool | Catch |
|---|---|---|
| Python | `tuple`, `frozenset` | Tuples can contain mutable objects; set elements must be hashable |
| JavaScript | `const` | Binding only |
| JavaScript | `Object.freeze` | Shallow |
| Java | `record`, `List.of` | Elements may be mutable |
| Haskell | Ordinary pure values | Mutable references/arrays exist inside controlled IO/ST effects |

> [!warning] `const` is not immutability
> In JavaScript, `const xs = [1, 2]` stops you rebinding `xs`, but `xs.push(3)` works fine. `const` freezes the name, not the value. Likewise `Object.freeze` freezes only the top level of an object.

Copying data on every change sounds expensive. Functional languages use **persistent data structures** that share most of their structure between versions. A map stored as a balanced tree only needs a fresh copy of the nodes on the path from the root to the changed key; every other node is shared with the old version. The path is short:

```formula
copies = O(log_2(n))
log_2(1000000) ≈ 20
where
copies: the number of tree nodes copied to make the new version of the map
n: the number of entries in the map, here 1,000,000
log_2: the base-2 logarithm: how many times you can halve n before reaching 1
O(...): Big-O notation: grows no faster than the expression inside, ignoring constant factors
≈: approximately equal to
In words: changing one key copies a number of nodes that grows with the logarithm of the map's size, not with the size itself.
```

For a balanced binary tree with one million entries, a root-to-leaf path is on the order of 20 nodes; exact path length and rebalancing copies vary. Here n denotes the number of entries: path copying uses O(log n) work rather than copying all O(n) entries. Clojure's persistent hash maps use a hash-array mapped trie with branching up to 32; hash width, sparse nodes and collisions affect the actual path and work. This is a structural model, not a measured allocation count.

## Key takeaways
- Binding protection and shallow freezing do not freeze nested objects.
- Balanced persistent structures reuse unchanged branches.

## Further reading
- [Clojure: persistent data structures](https://clojure.org/reference/data_structures)
- [ECMAScript language specification](https://tc39.es/ecma262/2023/)
