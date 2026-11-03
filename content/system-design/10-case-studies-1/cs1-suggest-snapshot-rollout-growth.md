---
id: cs1-suggest-snapshot-rollout-growth
title: Roll out suggestion snapshots safely as traffic grows
level: intermediate
minutes: 3
summary: Validate sample lookups, size and filtering before publication.
sourceLesson: cs1-typeahead
---

Serving nodes use immutable trie snapshots built offline. A bad snapshot can make suggestions empty or unsafe across an entire region, so a snapshot rollout deserves the same controlled deployment process as application code.

## Bottlenecks and trade-offs

| Decision | Trade-off |
|---|---|
| Top-k at each node | Fast reads, more RAM |
| Daily rebuild | Simple, stale |
| Trending overlay | Fresh, more moving parts |
| Edge caching | Shared-candidate reuse; personalise separately |

Failure modes to mention:

- **Bad trie snapshot**: a pipeline bug ships an empty or offensive trie. Validate trie snapshots (size, sample lookups, blocklist check) before publishing, and keep the previous version for instant rollback.
- **Manipulation**: bots search a phrase repeatedly to make it a suggestion. Count distinct users rather than raw searches and apply anomaly detection.
- **Slow responses are worse than none**: if the service doesn't answer within ~50 ms, the client should give up; a late suggestion for an old prefix is just noise.

## At 10x scale

At 10 billion searches/day with 50 locales:

A tenfold search increase raises serving demand only under the same requests-per-search and peak assumptions. Re-measure client behaviour, locale distribution and caching before scaling.

Choose the next change from observed pressure:

- **Edge first**: push the most popular prefixes' responses into CDN workers' memory; the origin sees only the long tail.
- **Partition by locale and region**, each with its own trie and its own replicas.
- **Rebuild incrementally**: instead of recomputing everything daily, apply hourly deltas for queries whose scores changed significantly.
- **Richer ranking** through the two-stage model, with the re-ranker deployed close to users.
- **Fuzzy matching** (typos) via Levenshtein automata over the FST, which Lucene supports, at the cost of more CPU per lookup.

## A safe snapshot handover

Build and validate a versioned artifact before announcing it as current. A canary downloads it, checks integrity and performs representative lookups, including blocked terms and locales. It loads the new trie alongside the old trie, then changes the root with appropriate synchronisation. Readers that started on the old root must be allowed to finish before that memory is released.

Compare error rates, latency, result coverage and suspicious changes against the previous version. Roll out gradually across regions and retain the old artifact so rollback changes a version pointer rather than waiting for a rebuild. A root swap prevents readers seeing a partly built structure; it does not prove that the contents are correct. Validation, canaries and rollback address that separate risk.

> [!analogy] Real-world analogy: Replacing a reference book
> Prepare a corrected edition, let a small group check it, then give it to readers while allowing those using the old edition to finish.
>
> **How it maps:** Validated immutable snapshots are published gradually, and old readers keep their version alive through the handover.
>
> **Where it stops:** A pointer change needs runtime synchronisation and sufficient memory; an intact new edition can still contain wrong information.

## Key takeaways

- Validate sample lookups, size and filtering before publication.
- Canary snapshots and retain a usable rollback version.
- Use edge serving, locale partitions and incremental updates as measured pressure grows.

## Further reading

- [Finite-state transducers and compact indexes](https://burntsushi.net/transducers/)
- [Elasticsearch: completion suggesters](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-suggesters)
