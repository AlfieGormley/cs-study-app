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

- Except possibly the root, every internal node now has at least two children (or marks a word end), so the node count is at most twice the number of stored keys, independent of key length (see below).
- Lookups compare chunks of characters along each edge, with the same O(L) total for a key of L characters.
- Inserting can **split** an edge: adding `cab` to the tree above splits nothing because `ca` already exists, but adding `co` would split `ca` into `c` with children `a` and `o`.

The node bound comes from counting the only kinds of node compression leaves behind: nodes that mark a key end (at most one per key), branching nodes (always fewer than the number of keys, as in any tree whose branch points have at least two children), and the root. So a radix tree holding at least one key has at most about twice as many nodes as keys, however long the keys are. The radix tree drawn above holds 4 keys (car, card, care, cat) in 5 labelled nodes plus the root. A plain trie, by contrast, can need one node per character of every key.

Radix trees are where tries meet production. Many of these uses rely on **longest prefix match**: among all stored prefixes of a lookup key, pick the longest.

> [!analogy] Real-world analogy: the most specific delivery rule wins
> A parcel depot has rules such as "anything for Leeds goes to van 1" and "anything for Park Lane, Leeds goes to van 4". A letter for 10 Park Lane, Leeds matches both, and the more specific rule wins. A letter for another Leeds street matches only the first.
>
> **How it maps:** each rule is a stored prefix with a route attached, the address is the lookup key read from the general part to the specific, and choosing the most specific matching rule is longest prefix match. Walking a trie and remembering the last rule passed finds it in one pass.
>
> **Where it stops:** delivery rules match names, and a person can read the whole address at once. A router matches a fixed number of address bits, from the most significant bit down, and has to make the decision for millions of packets a second.

- **IP routing**: a router finds the **longest prefix match** of a destination address against a table of CIDR prefixes. Binary tries over address bits, compressed (Patricia, LC-tries), are a classic implementation; Linux's IPv4 routing table uses an LC-trie (`fib_trie`).
- **HTTP routers**: Go's `httprouter` and many others match URL paths with a radix tree.
- Redis Streams use a radix tree of listpacks; a radix-tree entry represents a packed group of stream entries rather than necessarily one node per message.
- **Ethereum** stores its world state in a Merkle Patricia trie.
- The Linux page cache historically used a "radix tree", now the **XArray**, to map file offsets to pages.

## Other variants, briefly

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
