---
id: arch-bm25-saturation-field-length
title: Controlling repetition and length with BM25
level: intermediate
minutes: 3
summary: Trace BM25 saturation and per-field length normalisation without treating teaching scores as exact Lucene scores.
sourceLesson: arch-search-systems
---

TF-IDF established term frequency and corpus rarity in the previous unit. BM25 retains those ideas while preventing linear repetition rewards and accounting for field length.

## BM25 mechanics

**BM25** (Okapi BM25) is the default lexical similarity in Lucene and Elasticsearch. It keeps an IDF factor and improves on raw-TF weighting in two ways:

- **TF saturation**: the 10th occurrence of a word adds much less than the 2nd. A parameter `k1` (default 1.2) controls how fast it saturates, reducing the marginal reward for repetition; it does not guarantee immunity to keyword stuffing.
- **Length normalisation**: within the same field and with other factors equal, shorter fields receive less length penalty. Scores across different fields also depend on their own statistics and boosts. BM25 compares each field's length with the *average* length of that field across the index. Parameter `b` (default 0.75) controls how strongly length counts; setting b to zero turns it off.

The optional classic BM25 formula below makes those controls explicit. Current Lucene omits its constant saturation multiplier, so the raw numerical scale differs; use the engine’s explanation when inspecting actual scores.

```formula reference
score(t, d) = idf(t) × tf × (k1 + 1) / D
D = tf + k1 × (1 − b + b × L / L_avg)
where
score(t, d): the BM25 score that query term t contributes to document d
t: the query term being scored
d: the document containing the scored field
idf(t): inverse document frequency of t: higher for rarer terms
tf: term frequency: how many times t appears in the field being scored
k1: the saturation parameter, default 1.2: lower means repeats stop counting sooner
b: the length-normalisation parameter, between 0 and 1, default 0.75; 0 turns length normalisation off
D: the denominator (bottom line) of the fraction, written separately to fit the screen
L: the length of this document's field, in terms
L_avg: the average length among documents containing the scored field
In words: start from how rare the term is, then multiply by a term-frequency factor that grows with repeated occurrences but levels off, and is pulled down for longer-than-average fields.
```

A multi-term query combines term contributions. Repetition has diminishing returns rather than a linear reward; field statistics, boosts and query structure also affect the final score.

BM25 still performs purely **lexical search**: it scores matching tokens and knows nothing about meaning. "Sofa" won't match "couch" unless an analyser adds the synonym.

Real systems layer more signals on top: field boosts (title matches beat body matches), freshness, popularity, personalisation, and increasingly **vector (semantic) search** with embeddings, often combined with BM25 in **hybrid search** and then re-ranked by a learned model.

## Key takeaways
- BM25 reduces the marginal reward for repeated terms and normalises length against the same field's average.
- The classic formula shown includes a constant omitted by current Lucene scoring, so raw numerical scales differ.
- Parameter b controls length normalisation; b set to zero disables it.
- Lexical ranking needs synonyms or semantic signals to connect different words with related meanings.

## Further reading
- [Wikipedia: Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25)
- [Lucene: BM25Similarity](https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/search/similarities/BM25Similarity.html)
