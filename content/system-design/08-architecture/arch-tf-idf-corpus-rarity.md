---
id: arch-tf-idf-corpus-rarity
title: Ranking terms by corpus rarity
level: intermediate
minutes: 3
summary: Calculate TF-IDF weights and compare rare and common terms using a fully defined teaching model.
sourceLesson: arch-search-systems
---

The previous unit found matching documents. Ranking now asks which matches deserve priority; first isolate the effect of a term's rarity before adding length and repetition controls.

## TF-IDF intuition and calculation


Matching tells you *which* documents qualify. Ranking tells you which are *best*. The classic intuition:

- **Term frequency (TF)**: a document mentioning "headphones" 5 times is probably more about headphones than one mentioning it once.
- **Inverse document frequency (IDF)**: rare terms are more informative. "the" appears everywhere and means little; "noise-cancelling" is rare and decisive.

TF-IDF multiplies those two ideas together, giving one score for how well a term marks out a document:

```formula
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

The logarithm squashes the range: a term in 1 document out of a million gets an IDF of 6, not a million. Different engines use slightly different variants (natural log, adding 1 to avoid dividing by zero), but the shape is the same. For a collection of a million documents:

```formula
idf("wireless") = log_10(1000000 / 50000)
idf("wireless") = log_10(20) ≈ 1.30
idf("anc") = log_10(1000000 / 1000)
idf("anc") = log_10(1000) = 3.00
where
idf: inverse document frequency of the quoted term
log_10: logarithm to base 10 (log_10(1000) = 3, because 10^3 = 1000)
^: "to the power of"
≈: approximately equal to (rounded)
In words: "wireless" is in 50,000 of a million documents and scores 1.30; "anc" (active noise cancelling) is in only 1,000 and scores 3.00.
```

So a match on the rarer term counts more than twice as much (3.00 / 1.30 ≈ 2.3 times).

## Key takeaways
- Term frequency rewards occurrences inside a document; inverse document frequency rewards rarity across the corpus.
- The displayed base-10 IDF is a teaching variant, so engine-specific score details may differ.
- Equal term frequencies still produce different weights when document frequencies differ.

## Further reading
- [Wikipedia: tf–idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
