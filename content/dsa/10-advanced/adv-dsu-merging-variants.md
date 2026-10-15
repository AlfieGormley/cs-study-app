---
id: adv-dsu-merging-variants
title: Accounts merging and Union-Find variants
level: intermediate
minutes: 3
summary: Shared identifiers create a transitive closure of account groups.
sourceLesson: adv-union-find
---

## Application 3: accounts merge

Each account is a name plus a list of emails. In this exercise, sharing an email is a trusted signal to merge accounts, and we take its transitive closure: A shares with B and B shares with C, so all three join one component. Directly sharing an email is not itself transitive. Assume each account has at least one email and merged accounts have consistent names; real entity resolution needs stronger domain rules.

Union the account indices through shared emails:

```python
def merge_accounts(accounts):
    dsu = DSU(len(accounts))
    owner = {}   # email -> account index
    for i, acc in enumerate(accounts):
        for email in acc[1:]:
            if email in owner:
                # Shared email joins account
                # components.
                dsu.union(i, owner[email])
            else:
                owner[email] = i
    groups = {}
    for email, i in owner.items():
        # Group each unique email under its
        # root.
        r = dsu.find(i)
        groups.setdefault(r, [])
        groups[r].append(email)
    return [[accounts[r][0]] + sorted(es)
            for r, es in groups.items()]
```

The same shape appears in **entity resolution** (deduplicating customer records that share a phone number or address), clustering, and compilers: type inference in ML-family languages unifies type variables with a union-find structure.

## Variants worth knowing

- **Weighted union-find** stores, for each node, a value relative to its parent (an offset, a ratio, a bit recording whether a path length is odd or even). `find` accumulates values along the path. This solves "evaluate division" (given some ratios between variables, work out others, as in the block below) and "is this graph bipartite?" online.

```formula
a / b = 2
b / c = 3
a / c = (a / b) × (b / c) = 2 × 3 = 6
where
a, b, c: unknown non-zero quantities that are only described by their ratios to each other
In words: if a is twice b and b is three times c, then a is six times c; weighted union-find stores each ratio on the edge to the parent and multiplies along the path to the root.
```

- **Offline deletion**: union-find cannot split a set. For a known deletion-only history, first build the final graph, then process removals backwards as additions. Mixed additions and deletions need extra machinery.
- Hash-map parents: when elements are strings or sparse coordinates, use a dict instead of a list, creating entries on first sight.

## Pitfalls

- Comparing parents, not roots. `parent[a] == parent[b]` is not the same as being connected. Always compare `find(a)` and `find(b)`.
- Linking non-roots. `parent[b] = a` instead of `parent[find(b)] = find(a)` loses the rest of b's tree.
- Forgetting it is undirected. Union-find has no notion of direction, so it cannot detect cycles in a directed graph or find strongly connected components. Use DFS-based algorithms for those.

## Key takeaways

- Shared identifiers create a transitive closure of account groups.
- Weighted parents carry relations; known deletion-only histories can be processed backwards.

## Further reading
- [Disjoint-set data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [Disjoint Set Union — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Ackermann function — Wikipedia](https://en.wikipedia.org/wiki/Ackermann_function)
