---
id: tree-trie-autocomplete
title: Enumerating and ranking completions
level: intermediate
minutes: 3
sourceLesson: tree-tries
summary: Walk to the prefix node before enumerating descendants.
---

A character trie starts at an always-present root representing the empty prefix. Earlier units used Node.kids as a dictionary of character-to-child links and Node.end as the complete-word flag. Here L counts characters in the searched string or prefix and n counts stored keys. Dictionary child access is expected constant time, rather than a worst-case guarantee.

## Autocomplete

Autocomplete is "walk to the prefix node, then enumerate words below it".

Run this function with the Node, insert and walk definitions from the lookup unit. Populate the trie with car, card, care, cat, do and dog to obtain the illustrative completion list below.

```python
def complete(root, prefix, limit=10):
    if not isinstance(limit, int):
        raise TypeError("integer limit")
    if limit < 0:
        raise ValueError("limit >= 0")
    out = []
    def dfs(node, path):
        if len(out) == limit:
            return
        if node.end:
            out.append(path)
        # Sorting gives code-point
        # word order.
        for ch in sorted(node.kids):
            if len(out) >= limit:
                break
            dfs(node.kids[ch], path + ch)
    start = walk(root, prefix)
    if start:
        dfs(start, prefix)
    return out

# complete(root, "ca")
# ['car', 'card', 'care', 'cat']
```

Sorted child traversal produces Python string lexicographic order (code-point order, not locale-aware alphabetical collation). This simple implementation copies path strings and sorts child keys during recursion; enumeration costs include visited nodes, copied characters and output, and deep words can hit Python's recursion limit.

An autocomplete design may rank by popularity. Enumerating and sorting every match can be expensive, so one option is to cache top-k word IDs at selected prefix nodes. Looking up such a cached list of k IDs for a prefix of L characters costs expected O(L + k) in this representation, excluding retrieval and transmission of the completion text. The trade-off is memory, and slower updates when popularity changes.

> [!example] Sizing an autocomplete trie
> In a hypothetical dataset, 10 million queries with mean length exactly 20 have 200 million characters in total, but shared prefixes typically cut the node count substantially. Storing the top 10 completions at every node as 4-byte IDs adds 40 bytes per node, before container overhead. A design can store these lists only at selected shallow nodes and compute other results on demand; the best policy depends on query traffic.

## Key takeaways
- Walk to the prefix node before enumerating descendants.
- Sorted child traversal gives code-point order, not locale-aware collation.
- Cached top completions exchange update and memory costs for query speed.

## Further reading
- [Tries — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/52trie/)
