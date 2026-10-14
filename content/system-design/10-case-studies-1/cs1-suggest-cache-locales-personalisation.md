---
id: cs1-suggest-cache-locales-personalisation
title: Scale shared candidates across locales and users
level: intermediate
minutes: 3
summary: Benchmark core capacity at the target latency before sizing.
sourceLesson: cs1-typeahead
---

## Deep dive 2: Scaling the serving path

If a representative benchmark establishes 1,000 requests/s per core at the target latency, the core count is the peak rate divided by that:

```formula
cores = peak / cap
cores = 180,000/s / (1,000/s) = 180
where
cores: CPU cores needed if every one runs flat out
peak: peak suggestion requests per second
cap: requests per second one core handles, an assumed 1,000
/s: per second
In words: 180,000 requests a second at an assumed 1,000 per core needs 180 fully busy cores, before headroom and before the CDN takes its share.
```

So 180,000/s requires 180 fully utilized cores before headroom and cache offload. A 1 ms response time alone does not establish CPU cost or throughput.

> [!note] Content gap: index and serving benchmarks
> No reproducible 100-million-query corpus, memory layout or serving benchmark is supplied. The 30–50 GB index size and per-core throughput are hypothetical sizing inputs, not guarantees.

### Edge and browser caching

Suggestions for a given prefix are the **same for everyone** in a locale (until personalisation). That makes them perfectly cacheable:

- Short prefixes are both the most requested (every query starts with one or two characters) and the most cacheable. The number of possible short prefixes depends on the alphabet and Unicode normalization; it is not necessarily a few thousand for every locale.
- A CDN with a 5–15 minute TTL can serve a large fraction of all requests without ever reaching your servers.
- The browser caches responses too, so backspacing costs nothing.

### Sharding, if it outgrows one machine

Suppose many locales and personal history push the index past what one machine holds.

- **Shard by locale** first: natural, and requests never cross locales.
- **Shard by prefix range** (a–f, g–m...) is tempting but **skewed**: far more English queries start with "s" or "c" than "x" or "q". Use ranges sized by measured traffic, or shard by hash of the first few characters.
- With a flattened `prefix → list` KV store, hashing spreads distinct prefixes, but a very hot prefix still maps to one shard and may need replicas or caching.

## Deep dive 3: Ranking and personalisation

Popularity alone is a decent baseline. Real systems use a **two-stage** approach:

1. **Candidate generation**: the trie returns the top ~50 by global score. Fast and cacheable.
2. **Re-ranking**: a lightweight model reorders the candidates using context: the user's location, language, recent searches, time of day.

Personalisation prevents sharing the same final cached response across users unless the cache key safely separates their results. A common compromise: cache the global top-50 at the edge, and do the personal re-ranking (or blend in the user's own recent searches) on the client or in a thin per-user service.

Facebook's original typeahead took personalisation further: when you focused the search box, it preloaded your friends and frequently visited pages into the browser, so the first few characters were matched entirely client-side.

## Key takeaways

- Benchmark core capacity at the target latency before sizing.
- Cache shared locale-specific candidates and personalise after that stage.
- Partition by measured traffic and protect very hot prefixes with replicas or caching.

## Further reading

- [Meta: the life of a typeahead query](https://engineering.fb.com/2010/05/17/web/the-life-of-a-typeahead-query/)
- [Elasticsearch: completion suggesters](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-suggesters)
- [RFC 9111: HTTP caching](https://www.rfc-editor.org/rfc/rfc9111.html)
