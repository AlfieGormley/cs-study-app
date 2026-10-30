---
id: tree-structure-edges
title: Tree structure and edges
level: basic
minutes: 4
sourceLesson: tree-basics
summary: A rooted tree is connected and acyclic; only the root has no parent.
---

Arrays and linked lists are **linear**: every element has at most one successor. A **tree** lets an element have several successors, which is exactly the shape of a lot of real data: a file system, the HTML DOM, an organisation chart, a parsed expression, a JSON document.

Trees also matter for speed. In this module, n is the number of items (keys or nodes) stored, and O(…) is Big O notation: it describes how the work grows as n grows. O(n) is a linear upper growth bound; O(log n) is a logarithmic upper growth bound using the base-2 logarithm of n, roughly the number of times you can halve n before reaching 1 (about 20 for a million). O(1) means a fixed amount of work however large n is.

A sorted array lets you search in O(log n) but inserts cost O(n), because every later item must shift along. A balanced binary search tree gives O(log n) search and insertion under constant-cost key comparisons: its height is logarithmic, and those operations follow a root-to-leaf path. An arbitrary well-shaped tree does not provide ordered search.

## What makes something a tree

A tree is a set of **nodes** joined by **edges**, with one special node, the **root node**, such that:

- every node except the root has exactly one **parent node**;
- following parents from any node always leads back to the root;
- there are no cycles.

Equivalently (in graph terms) a tree is a connected undirected graph with no cycles, with a root chosen for the rooted representation.

Because every node except the root has exactly one edge up to its parent, you can count the edges of any tree without looking at its shape:

```formula essential
E = n − 1
where
n: the number of nodes in the tree, a whole number of at least 1
E: the number of edges (parent–child links) in the tree
In words: a nonempty tree always has exactly one edge fewer than it has nodes, because the root is the only node with no edge to a parent.
```

So the tree below, with 8 nodes, has **7 edges**, and a tree of a million nodes has 999,999, whatever its shape. The rule needs a single connected tree; a collection of separate trees (a forest) has fewer edges.

The count is also a quick diagnostic. If a structure that should be a tree has as many links as nodes, something has a second parent or the links loop back on themselves. If it has fewer, part of it is disconnected from the root. The right count alone does not prove a tree, though: a loop in one part and a disconnected piece elsewhere can also add up to n − 1 links.

> [!analogy] Real-world analogy: a company org chart
> In a strict org chart, the chief executive reports to nobody and every other employee reports to exactly one manager. Ask any employee who their manager is, then that manager, and you always end at the chief executive.
>
> **How it maps:** the chief executive is the root, each manager is a parent node, each reporting line is an edge, and staff with no reports are leaves. Because everyone except the chief executive has exactly one line upwards, a company of 250 people has 249 reporting lines however the departments are arranged.
>
> **Where it stops:** real organisations often have dotted-line reporting, where someone answers to two managers. That gives a node two parents, so the chart is no longer a tree. A data-structure tree also has no job titles: the only thing that matters is who links to whom.

```
            A          <- root (depth 0)
          / | \
         B  C  D       <- depth 1
        / \     \
       E   F     G     <- depth 2
           |
           H           <- depth 3
```

## Where trees appear

- **File systems**: a directory hierarchy is often modelled as a tree; empty directories are also leaves, and hard links or followed symbolic links need extra care.
- **Compilers**: source code is parsed into an *abstract syntax tree*; `(2 + 3) * 4` becomes a `*` node with children `+` and `4`.
- **Databases**: many indexes use B-trees, a many-children generalisation of search trees (covered in the System Design databases module).
- **Ordered maps**: Java's TreeMap uses a red-black tree; common std::map implementations do too, but the C++ interface does not require that representation (the balanced-tree units).
- **Schedulers and priority queues**: binary heaps (the binary heap units).
- **Autocomplete and routing tables**: tries (the trie units).

## Key takeaways
- A rooted tree is connected and acyclic; only the root has no parent.
- A nonempty tree has one fewer edge than nodes.
- Ordered search requires an ordering rule as well as a useful shape.

## Further reading
- [Tree (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Tree_(data_structure))
- [Binary expression tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_expression_tree)
