---
id: tree-trie-lookup-prefixes
title: Trie paths, exact lookup and prefixes
level: intermediate
minutes: 4
sourceLesson: tree-tries
summary: Shared prefixes share a root-to-node path.
---

In this lesson L is the length of a key in characters and n is the number of keys stored. Hash-table lookup uses expected O(1) probes (a fixed number on average) under suitable hashing assumptions; hashing and equality on uncached strings can cost O(L), in proportion to the key's length. They cannot answer "which words **start with** `inte`?" without scanning every key. Balanced BSTs can, but each step of the search is a whole string comparison: about 20 comparisons for a million keys, each of which may read the full key. So a BST lookup costs O(L log n) in the worst case, and the trie below brings that down to O(L): it reads each character of the key once. Real string comparisons often stop at the first differing character, so the BST figure is a worst case.

A **trie** (from re*trie*val, usually pronounced "try") is built for prefix questions. Instead of storing whole keys in nodes, it stores **one character per edge**. A key is a path from the root, and every key that shares a prefix shares the path for that prefix.

## The structure

Here is a trie holding `car`, `card`, `care`, `cat`, `do` and `dog`. A `*` marks a node where a word ends.

```
          (root)
          /    \
         c      d
         |      |
         a      o*
        / \     |
       r*  t*   g*
      / \
     d*  e*
```

Things to notice:

- The root represents the empty string. Each node represents the prefix spelled by the path to it.
- `car` and `card` share three nodes. Shared prefixes are stored once.
- `do` is a word *and* a prefix of `dog`, so an end-of-word **flag** is needed; you cannot rely on "is it a leaf?".
- Keys are never compared with each other. Lookup cost depends on the **length of the key**, not on how many keys are stored.

> [!analogy] Real-world analogy: signposts that spell a word
> Imagine a town where every road junction has signposts labelled with single letters. To reach "card" you take the C turning, then A, then R, then D. Some junctions also carry a plaque saying "a destination ends here".
>
> **How it maps:** junctions are trie nodes, each lettered turning is an edge, the route you drive is the key, and the plaque is the end-of-word flag. Everyone heading to a word starting "car" shares the same first three roads, which is how a trie stores shared prefixes once.
>
> **Where it stops:** a real junction has only a few turnings. A trie node may need room for every possible next character, which is why tries can use a lot of memory (the trie-memory unit).

## Insert, search and prefix queries

```python
class Node:
    def __init__(self):
        self.kids = {}    # char -> Node
        self.end = False  # word ends here

def insert(root, word):
    node = root
    for ch in word:
        if ch not in node.kids:
            node.kids[ch] = Node()
        # Shared prefixes reuse
        # existing nodes.
        node = node.kids[ch]
    # The path may also prefix longer words.
    node.end = True

def walk(root, s):
    node = root
    for ch in s:
        node = node.kids.get(ch)
        if node is None:
            return None
    return node

def search(root, word):
    node = walk(root, word)
    return bool(node and node.end)

def starts_with(root, prefix):
    return walk(root, prefix) is not None
```

With the trie above:

| Call | Result | Why |
|---|---|---|
| `search(root, "car")` | True | path exists, flag set |
| `search(root, "ca")` | False | path exists, no flag |
| `starts_with(root, "ca")` | True | path exists |
| `search(root, "dot")` | False | no `t` under `do` |

With constant-time child access, insertion, exact lookup and prefix-path lookup take O(L + 1) for a key or prefix of L characters: one step per character, plus the root (the + 1 covers the empty string, for zero characters). The dict-backed example uses expected constant-time child lookups. For an empty prefix, `starts_with` returns True even on an empty trie because the root exists; this tests path existence, not whether any word is stored.

> [!note] O(L) is not automatically faster than hashing
> Hashing a previously unhashed string inspects its characters; some runtimes cache string hashes, and equality costs also matter. Tries directly support prefix navigation and can stop early on a miss. Practical exact-match performance depends on representation and workload.

## Key takeaways
- Shared prefixes share a root-to-node path.
- An end flag distinguishes complete words from their prefixes.
- Lookup follows key characters with expected constant-cost dictionary access.

## Further reading
- [Trie — Wikipedia](https://en.wikipedia.org/wiki/Trie)
- [Tries — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/52trie/)
