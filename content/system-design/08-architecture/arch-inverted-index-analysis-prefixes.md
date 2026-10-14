---
id: arch-inverted-index-analysis-prefixes
title: Building matching tokens and posting lists
level: intermediate
minutes: 3
summary: Trace inverted-index matching and compatible analysis, then apply prefix indexing to search-as-you-type.
sourceLesson: arch-search-systems
---

`SELECT * FROM products WHERE description LIKE '%wireless headphones%'` usually needs a scan without a suitable text/trigram index, does not perform stemming, and may be case-sensitive depending on the database and collation, and has no idea which result is *best*. Search engines solve all three problems with a different data structure, a text-processing pipeline and a ranking function.

## The inverted index

A normal (forward) index maps document → words. An **inverted index** maps each **term → the list of documents containing it** (a *posting list*), often with positions and frequencies.

```
 doc1: "red wireless headphones"
 doc2: "wireless mouse"
 doc3: "red mouse mat"

 term       postings
 --------   -----------
 headphone  [1]
 mat        [3]
 mouse      [2, 3]
 red        [1, 3]
 wireless   [1, 2]
```

A query for `wireless mouse`:

1. Look up `wireless` → [1, 2] and `mouse` → [2, 3].
2. AND = intersect → [2]; OR = union → [1, 2, 3].
3. Score the candidates and return the top results.

Lookups are fast because each term is found via a sorted term dictionary (in Lucene, a compact finite-state structure) and posting lists are sorted and compressed, so intersection is a merge of sorted lists, often skipping large chunks.

## Text analysis: tokenisation and normalisation

Before indexing (and again at query time), text goes through an **analyser**:

```
"The Runners' Shoes!"
  | tokenise
["The","Runners'","Shoes"]
  | lowercase, strip punctuation
["the","runners","shoes"]
  | stop words (optional)
["runners","shoes"]
  | stem
["runner","shoe"]
```

- **Tokeniser**: splits text into tokens. Whitespace and punctuation for English; languages like Chinese or Japanese need dictionary-based or n-gram tokenisers because they don't use spaces.
- **Token filters**: lowercasing, ASCII folding (`café` → `cafe`), stemming (`running` → `run`), synonyms (`tv` ↔ `television`), stop-word removal.
- **N-grams / edge n-grams**: index `hea`, `head`, `headp`... to support search-as-you-type and partial matches, at the cost of a much larger index.

> [!warning] The same analyser on both sides
> If documents are stemmed at index time but queries aren't, "running" in a query won't match the indexed token "run". Index-time and query-time analysis must be compatible. This is one of the most common search bugs.

### Prefixes have configured limits

Edge n-grams index prefixes only within their configured minimum and maximum lengths, not every possible prefix. A query such as `headp` should remain the intended typed token rather than being expanded into many shorter prefixes. Keep prefix indexing to suitable fields and measure its storage cost. Debounce keystrokes and cancel stale requests in the client to reduce unnecessary work. Search-as-you-type features can also combine shingle and prefix fields, so inspect the actual generated query and mapping.

## Key takeaways
- An inverted index maps terms to sorted posting lists; boolean queries combine candidate document sets.
- Analysis determines stored and queried terms, so both pipelines must be compatible.
- Index-time edge n-grams trade extra terms for direct prefix lookup; query-time analysis should preserve the typed prefix.

## Further reading
- [Wikipedia: Inverted index](https://en.wikipedia.org/wiki/Inverted_index)
- [Elasticsearch: Text analysis](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html)
- [Elasticsearch: Edge n-gram tokenizer](https://www.elastic.co/docs/reference/text-analysis/analysis-edgengram-tokenizer)
