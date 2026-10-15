---
id: adv-dsu-parent-forests
title: Representing disjoint sets with parent forests
level: intermediate
minutes: 2
summary: A root represents its entire connected component.
sourceLesson: adv-union-find
---

**Union-Find** (also called a **disjoint-set union**, or DSU) keeps track of elements split into non-overlapping groups. It supports two operations:

- `find(x)`: which group is `x` in? It returns a **set representative** element for the group.
- `union(a, b)`: merge the groups containing `a` and `b`.

Two elements are in the same group exactly when `find(a) == find(b)`. That one comparison answers "are these connected?" for road networks, friend circles, pixels in an image or accounts that share an email address.

It is tiny to implement, and with two simple tricks each operation costs so little that for any input you could ever store it is effectively constant.

## The idea: a forest of parent pointers

Each group is a tree. Every element points to a parent; the root points to itself and is the group's representative. All you store is one array, `parent`.

```
parent = [0, 0, 1, 3, 3]

  0       3
  |       |
  1       4
  |
  2
groups: {0, 1, 2} and {3, 4}
```

- `find(x)` follows parent pointers up to the root.
- `union(a, b)` finds both roots and makes one the parent of the other.

The naive version has a problem. Union in an unlucky order (`union(1, 0)`, `union(2, 1)`, `union(3, 2)` and so on, always hanging the old tree under the new element) builds a chain, and `find` on the bottom element walks every link in it: one fewer link than there are elements. If n is the number of elements, a sequence of operations can cost O(n) each in the worst case (O(n) means "grows in proportion to n").

## Key takeaways

- A root represents its entire connected component.
- Compare roots rather than immediate parents.

## Further reading
- [Disjoint-set data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [Disjoint Set Union — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Ackermann function — Wikipedia](https://en.wikipedia.org/wiki/Ackermann_function)
