---
id: arch-tf-idf-corpus-rarity
title: Ranking terms by corpus rarity
level: intermediate
minutes: 3
summary: Explain why frequent terms in one document and rare terms across the corpus influence relevance differently.
sourceLesson: arch-search-systems
---

The previous unit found matching documents. Ranking now asks which matches deserve priority; first isolate the effect of a term's rarity before adding length and repetition controls.

## TF-IDF intuition

Matching tells you *which* documents qualify. Ranking tells you which are *best*. The classic intuition:

- **Term frequency (TF)**: a document mentioning "headphones" 5 times is probably more about headphones than one mentioning it once.
- **Inverse document frequency (IDF)**: rare terms are more informative. "the" appears everywhere and means little; "noise-cancelling" is rare and decisive.

TF-IDF multiplies those two ideas together, giving one score for how well a term marks out a document:

```formula reference
w(t, d) = tf(t, d) × idf(t)
idf(t) = log_10(N / df(t))
where
w(t, d): the TF-IDF weight of term t in document d; bigger means the term says more about this document
t: one search term, e.g. "wireless"
d: one document, e.g. a product listing
tf(t, d): term frequency: how many times t appears in d
idf(t): inverse document frequency: how rare t is across the whole collection
N: the total number of documents in the collection (the corpus)
df(t): document frequency: how many documents contain t at least once
log_10: logarithm to base 10: the power you raise 10 to to get the number, so log_10(1000) = 3 because 10 × 10 × 10 = 1000
In words: a term scores highly in a document when it appears there often (tf) but appears in few documents overall (idf).
```

The optional formula uses a logarithm so rarity differences grow more gently than raw rarity ratios. It applies to terms present in the corpus; scoring variants and smoothing differ by engine. With equal within-document frequency, a term found in fewer documents gets more weight.

## Key takeaways
- Term frequency rewards occurrences inside a document; inverse document frequency rewards rarity across the corpus.
- The displayed base-10 IDF is a teaching variant, so engine-specific score details may differ.
- Equal term frequencies still produce different weights when document frequencies differ.

## Further reading
- [Stanford CS124: Information retrieval and TF-IDF](https://web.stanford.edu/class/cs124/lec/ir_jan17_2026.pdf)
