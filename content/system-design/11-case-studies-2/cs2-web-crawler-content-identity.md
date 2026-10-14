---
id: cs2-web-crawler-content-identity
title: Crawler URL identity and content fingerprints
level: intermediate
minutes: 3
summary: Separate canonical fetch identity from exact and near-duplicate content detection.
sourceLesson: cs2-web-crawler
---

## Dedup at three levels

### 1. URL normalisation
Before checking "seen", canonicalise URLs. Lower-case the scheme and host, drop default ports and fragments (`#...`), resolve `../`, and preserve query semantics. Reordering or stripping parameters is safe only when their equivalence is established for that site; `rel="canonical"` is a publisher hint, not proof that two URLs return identical content.

### 2. Seen-URL test
Ask for each discovered URL: "have we already queued or fetched this?"

- A **Bloom filter** answers in O(k) memory lookups, where k is the number of hash functions (about 7 in the earlier memory example) and O(k) means the work grows in proportion to k, with **no false negatives**. A false positive means you wrongly skip a new URL. At a 1% false-positive rate, approximately 1% of genuinely new membership probes may be skipped. Rediscovering the same URL does not fix a stable false positive: it hashes to the same already-set bits.
- If missing pages is unacceptable, treat the Bloom filter as a fast negative check. "Definitely not seen" proceeds to an atomic exact-store claim and durable enqueue; concurrent Bloom misses must not enqueue twice. "Maybe seen" is checked against the exact `url_state` store.
- Bloom filters can't delete entries. For re-crawl scheduling, use the exact store (or a counting or cuckoo filter).

### 3. Content dedup
Mirrors, printer-friendly pages and session variants can create many duplicates. The proportion depends on the crawl corpus and similarity definition.

- **Exact duplicates**: hash the normalised body with SHA-256 and check a fingerprint store. If using a short fingerprint, compare the candidate bodies before declaring an exact duplicate; collisions matter at billions of pages.
- **Near duplicates**: use **SimHash**. Hash each shingle (word n-gram) and, for each of 64 bit positions, add the shingle's weight if that bit is 1 and subtract it if 0. The sign of each total becomes the bit. Similar weighted feature vectors tend to produce fingerprints with small Hamming distance; small textual edits do not guarantee a fixed number of changed bits. Google's 2007 paper on near-duplicate detection (Manku, Jain and Das Sarma) found that, for a repository of 8 B pages, 64-bit SimHash fingerprints with a threshold of **3 differing bits** worked well. It found matches quickly by splitting the fingerprint into blocks and indexing permuted tables, so any fingerprint within 3 bits must match exactly on at least one block.


## Key takeaways
- Normalise proven URL equivalences without changing arbitrary query semantics.
- Exact durable claims prevent simultaneous misses from enqueueing twice.
- Similarity fingerprints require corpus-specific thresholds rather than exact-body identity.

## Further reading
- [Near-duplicate detection](https://research.google/pubs/detecting-near-duplicates-for-web-crawling/)
- [SimHash](https://en.wikipedia.org/wiki/SimHash)
