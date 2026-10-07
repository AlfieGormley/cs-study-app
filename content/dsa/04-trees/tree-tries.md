---
id: tree-tries
title: Tries
level: intermediate
minutes: 12
summary: Prefix trees for strings, with insert, search and prefix queries in time proportional to the key length, the memory costs, compressed tries and radix trees, and how autocomplete is built on them.
---

Hash-table lookup uses expected O(1) probes under suitable hashing assumptions; hashing and equality on uncached strings can cost O(L) for length L. They cannot answer "which words **start with** `inte`?" without scanning every key. Balanced BSTs can, but each comparison is a string comparison, so a lookup costs O(L log n).

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
        node = node.kids[ch]
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
| `search("car")` | True | path exists, flag set |
| `search("ca")` | False | path exists, no flag |
| `starts_with("ca")` | True | path exists |
| `search("dot")` | False | no `t` under `do` |

With constant-time child access, insertion, exact lookup and prefix-path lookup take O(L + 1). The dict-backed example uses expected constant-time child lookups. For an empty prefix, starts_with returns True even on an empty trie because the root exists; this tests path existence, not whether any word is stored.

> [!note] O(L) is not automatically faster than hashing
> Hashing a previously unhashed string inspects its characters; some runtimes cache string hashes, and equality costs also matter. Tries directly support prefix navigation and can stop early on a miss. Practical exact-match performance depends on representation and workload.

## Autocomplete

Autocomplete is "walk to the prefix node, then enumerate words below it".

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

An autocomplete design may rank by popularity. Enumerating and sorting every match can be expensive, so one option is to cache top-k word IDs at selected prefix nodes. Looking up such a cached list costs expected O(L + k) in this representation, excluding retrieval and transmission of the completion text. The trade-off is memory, and slower updates when popularity changes.

> [!example] Sizing an autocomplete trie
> In a hypothetical dataset, 10 million queries with mean length exactly 20 have 200 million characters in total, but shared prefixes typically cut the node count substantially. Storing the top 10 completions at every node as 4-byte IDs adds 40 bytes per node, before container overhead. A design can store these lists only at selected shallow nodes and compute other results on demand; the best policy depends on query traffic.

## The memory problem

Tries are fast but notoriously **memory-hungry**, because every character of every unshared suffix gets its own node, and each node carries overhead.

Common child representations:

| Children as | Lookup | Memory per node |
|---|---|---|
| Array of 26 (or 256) pointers | O(1) index | 208 B (or 2 KB) on 64-bit, mostly empty |
| Hash map / dict | O(1) expected | Small, but high constant overhead |
| Sorted list | O(log σ) | Compact |

Here σ is the alphabet size; pointer-array sizes assume 8-byte pointers and exclude headers. Dictionary and node object sizes vary by interpreter build.

> [!note] Evidence gap
> The claimed CPython dictionary sizes and 100,000-word, 65 MB benchmark are omitted because the pinned build, word list, measurement code and retained-object accounting were unavailable. No measured tenfold memory ratio is established.

With long mostly unshared suffixes, many nonterminal trie nodes have exactly one child: the unshared tail of a single word like `...ication`. That observation drives the fix.

## Compressed tries and radix trees

A **radix tree** (also called a compressed trie, or a **Patricia** trie in its binary form) merges chains of single-child nodes that do not mark a key end into one edge labelled with a **string** rather than a character.

```
 trie              radix tree
  c                 "ca"
  |                 /   \
  a              "r"*   "t"*
 / \             /  \
r*  t*         "d"*  "e"*
/ \
d* e*
```

- Except possibly the root, every internal node now has at least two children (or marks a word end), so the node count is at most about 2n for n keys, independent of key length.
- Lookups compare chunks of characters along each edge, with the same O(L) total.
- Inserting can **split** an edge: adding `cab` to the tree above splits nothing because `ca` already exists, but adding `co` would split `ca` into `c` with children `a` and `o`.

Radix trees are where tries meet production:

- **IP routing**: a router finds the **longest prefix match** of a destination address against a table of CIDR prefixes. Binary tries over address bits, compressed (Patricia, LC-tries), are a classic implementation; Linux's IPv4 routing table uses an LC-trie (`fib_trie`).
- **HTTP routers**: Go's `httprouter` and many others match URL paths with a radix tree.
- Redis Streams use a radix tree of listpacks; a radix-tree entry represents a packed group of stream entries rather than necessarily one node per message.
- **Ethereum** stores its world state in a Merkle Patricia trie.
- The Linux page cache historically used a "radix tree", now the **XArray**, to map file offsets to pages.

## Other variants, briefly

- **Ternary search trees** store one character per node with less/equal/greater children, like a BST over characters. They use far less memory than array tries and still support prefix search.
- **Suffix tries and suffix trees** hold every suffix of a text, answering "does pattern P occur anywhere?" in O(|P|). Suffix arrays are the space-efficient alternative.
- **Aho–Corasick** adds failure links to a trie of patterns, finding all occurrences of many patterns in one pass over a text (the original Unix `fgrep` was built on it, and intrusion-detection systems use it to match thousands of signatures).
- Finite-state transducers can merge equivalent states and share suitable suffix structure as well as prefixes. Compression depends on the vocabulary and outputs.

## When to reach for a trie

Use one when you need:

- prefix queries: autocomplete, "all keys under `/api/v1/`", routing;
- longest-prefix matching;
- many patterns matched at once (Aho–Corasick);
- sorted iteration over strings with shared prefixes.

Avoid one when you only do exact-match lookups (use a hash set), when keys share few prefixes (random IDs, hashes: the trie degenerates into one long chain per key), or when memory is tight and a sorted array with binary search on prefixes will do.

## Key takeaways
- A trie stores one character per edge; keys sharing a prefix share a path, and an end-of-word flag marks complete keys.
- Insert, search and prefix checks take O(L + 1) with constant-time child access (expected for dict children), independent of how many keys are stored.
- Autocomplete walks to the prefix node and enumerates below it; one possible design caches top-k completion IDs at selected nodes.
- Plain tries are memory-hungry; radix trees collapse single-child chains into string-labelled edges, bounding nodes to about 2n.
- Radix and Patricia tries power IP longest-prefix routing, HTTP routers and Redis Streams.

## Further reading
- [Trie — Wikipedia](https://en.wikipedia.org/wiki/Trie)
- [Radix tree — Wikipedia](https://en.wikipedia.org/wiki/Radix_tree)
- [Tries — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/52trie/)
- [Longest prefix match — Wikipedia](https://en.wikipedia.org/wiki/Longest_prefix_match)
- [Ternary search tree — Wikipedia](https://en.wikipedia.org/wiki/Ternary_search_tree)
- [Aho–Corasick algorithm — Wikipedia](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm)
