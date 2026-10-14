---
id: tree-radix-variants
title: Compressed paths, routing and trie variants
level: intermediate
minutes: 5
sourceLesson: tree-tries
summary: Compress single-child chains only when no intermediate key ends there.
---

A character trie starts at an always-present root representing the empty prefix. Earlier units used Node.kids as a dictionary of character-to-child links and Node.end as the complete-word flag. Here L counts characters in the searched string or prefix and n counts stored keys. Dictionary child access is expected constant time, rather than a worst-case guarantee.

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

- Except possibly the root, every internal node now has at least two children (or marks a word end), so the node count is at most twice the number of stored keys, independent of key length (the count is below).
- Lookups compare chunks of characters along each edge, with the same O(L) total for a key of L characters.
- Inserting can **split** an edge: adding `cab` to the tree above splits nothing because `ca` already exists, but adding `co` would split `ca` into `c` with children `a` and `o`.

The node bound comes from counting the only kinds of node compression leaves behind:

```formula
N ≤ n + (n − 1) + 1 = 2n
N ≤ 2 × 4 = 8
where
N: the number of nodes in the radix tree, including the root
n: the number of distinct keys stored, at least one; 4 (car, card, care, cat) in the example. An empty trie retains its single root, outside this bound
In words: at most n nodes mark key ends, fewer than n others can branch, and there is one root, so a radix tree never has more than about 2n nodes.
```

The radix tree drawn above holds those 4 keys in 5 labelled nodes plus the root, within the bound of 8. A plain trie, by contrast, can need one node per character of every key.

Radix trees are where tries meet production:

- **IP routing**: a router finds the **longest prefix match** of a destination address against a table of CIDR prefixes. Binary tries over address bits, compressed (Patricia, LC-tries), are a classic implementation; Linux's IPv4 routing table uses an LC-trie (`fib_trie`).
- **HTTP routers**: Go's `httprouter` and many others match URL paths with a radix tree.
- Redis Streams use a radix tree of listpacks; a radix-tree entry represents a packed group of stream entries rather than necessarily one node per message.
- **Ethereum** stores its world state in a Merkle Patricia trie.
- The Linux page cache historically used a "radix tree", now the **XArray**, to map file offsets to pages.

## Other variants, briefly

Here P names the pattern string and |P| denotes its character count when quoting a Big O lookup bound.


- **Ternary search trees** store one character per node with less/equal/greater children, like a BST over characters. They use far less memory than array tries and still support prefix search.
- **Suffix tries and suffix trees** hold every suffix of a text, answering "does pattern P occur anywhere?" in time proportional to the length of P, written O(|P|), where |P| is the number of characters in the pattern. Suffix arrays are the space-efficient alternative.
- **Aho–Corasick** adds failure links to a trie of patterns, finding all occurrences of many patterns in one pass over a text (GNU grep uses it for multiple fixed patterns, and intrusion-detection systems can use it to match many signatures).
- Finite-state transducers can merge equivalent states and share suitable suffix structure as well as prefixes. Compression depends on the vocabulary and outputs.

## When to reach for a trie

Use one when you need:

- prefix queries: autocomplete, "all keys under `/api/v1/`", routing;
- longest-prefix matching;
- many patterns matched at once (Aho–Corasick);
- sorted iteration over strings with shared prefixes.

Avoid one when you only do exact-match lookups (use a hash set), when keys share few prefixes (random IDs, hashes: the trie degenerates into one long chain per key), or when memory is tight and a sorted array with binary search on prefixes will do.

## Key takeaways
- Compress single-child chains only when no intermediate key ends there.
- Insertion may split an edge at the first different character.
- Routing uses the longest matching prefix, while exact membership often suits hashing.

## Further reading
- [Radix tree — Wikipedia](https://en.wikipedia.org/wiki/Radix_tree)
- [Longest prefix match — Wikipedia](https://en.wikipedia.org/wiki/Longest_prefix_match)
- [Ternary search tree — Wikipedia](https://en.wikipedia.org/wiki/Ternary_search_tree)
- [Aho–Corasick algorithm — Wikipedia](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm)
- [Fixed-pattern search performance — GNU grep manual](https://www.gnu.org/software/grep/manual/html_node/Performance.html)
