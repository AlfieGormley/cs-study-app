---
id: cs1-suggest-prefix-lookup-client-contract
title: Precompute prefix answers and control client requests
level: intermediate
minutes: 4
summary: A top-k list at each prefix removes subtree search from serving.
sourceLesson: cs1-typeahead
---

## Step 3: API

```
GET /v1/suggest?q=how%20to%20m
              &locale=en-GB&limit=10
-> 200
{ "prefix": "how to m",
  "suggestions": [
    "how to make pancakes",
    "how to meditate", ...] }
Cache-Control: public, max-age=300
```

Client behaviour matters as much as the server:

- **Debounce** keystrokes (~100 ms) so fast typists don't send a request per character.
- **Cancel** in-flight requests when a newer prefix is typed, and ignore stale responses that arrive out of order.
- **Cache locally**: if the user deletes a character, the previous prefix's results are already in memory.
- **Filter locally**: if the suggestions for "how to m" are known, the client can filter them for "how to ma" as provisional results, but that subset may omit the true top completions for the longer prefix; fetch again when complete results matter.

## Step 4: Data model

### The trie

A [trie](https://en.wikipedia.org/wiki/Trie) stores strings by their characters, one level per character, so all strings sharing a prefix share a path.

```
        (root)
        /    \
       h      t
       |      |
       o      r
      / \     |
     w   t    e
     |   |    |
    ...  e    e
         |
         l
```

A naive lookup walks to the prefix node, one step per character, then searches the entire subtree for the most popular completions. For a short prefix like "s", that subtree contains millions of queries, which is far too slow.

### Precompute top-k at every node

Store the top-k completions **at each node**. Lookup becomes "walk to the node, return its list". The change moves ranking work out of each request:

With a stored candidate list, lookup follows the prefix and reads the selected results instead of searching the entire subtree. The trade-off is extra memory and work when rebuilding the lists.

The response still costs time to copy and transmit its strings.

```
node "how t" -> [how to tie a tie (98k),
                 how to train your dragon,
                 ...]
```

The cost is memory (k entries per node) and rebuild work, but we do that offline. Use compact IDs instead of full strings in each list, and cap prefix depth (beyond ~20–30 characters, there's little to suggest).

### Alternatives

- **Flattened trie in a KV store**: store `prefix → top-k list` directly in Redis or Cassandra. Easy to shard and update; memory relative to a trie depends on key duplication and representation. Good if the index outgrows one machine.
- **Finite-state transducers**: Lucene and Elasticsearch's completion suggester use compact finite-state representations. Equivalent suffix paths can be shared as well as common prefixes; size savings depend on the indexed data and representation.
- **Radix trees** collapse chains of single-child nodes into one edge, saving memory for long unique tails.

## Step 5: High-level design

```
 Browser/app (debounce, cache)
        |
        v
 CDN edge cache
        |  (miss)
        v
 Suggest service x N
 (whole trie in RAM)
        ^
        | load snapshot
 Object store (trie files)
        ^
        | build
 Trie builder (batch)
        ^
        | query counts
 Aggregator (stream + batch)
        ^
        |
 Search logs -> Kafka
```

Two separate paths:

- **Serving path** (top half): read-only, in memory, cached at the edge.
- **Data path** (bottom half): logs → counts → ranked lists → a new trie snapshot every hour or day.

They meet only at the snapshot. The suggest service never writes anything.

> [!analogy] Real-world analogy: An index with recommendations already attached
> A library’s subject index can include a short recommended-reading list, so a visitor need not inspect every book on that subject.
>
> **How it maps:** The prefix path locates a precomputed candidate list; expensive selection happens when building the index.
>
> **Where it stops:** The list can become stale or omit newly relevant items; personalisation and urgent removal require additional mechanisms.

## Key takeaways

- A top-k list at each prefix removes subtree search from serving.
- Debounce, cancel, ignore stale responses and reuse local results.
- Keep the serving path separate from the snapshot-building pipeline.

## Further reading

- [Meta: the life of a typeahead query](https://engineering.fb.com/2010/05/17/web/the-life-of-a-typeahead-query/)
- [Elasticsearch: completion suggesters](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-suggesters)
- [Trie data structure](https://en.wikipedia.org/wiki/Trie)
