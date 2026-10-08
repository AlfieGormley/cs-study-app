---
id: cs1-typeahead
title: Design typeahead autocomplete
level: intermediate
minutes: 16
summary: Design search-box autocomplete that returns the top suggestions for every keystroke in tens of milliseconds, using tries with precomputed top-k, an offline aggregation pipeline and aggressive edge caching.
---

Type "how to" into a search box and suggestions appear before you finish the word. Every keystroke is a request, so a search engine's autocomplete gets several times the traffic of search itself, and each response must arrive before the user types the next character.

The trick to this problem is realising that **the serving path should do almost no work**. All the expensive thinking (counting, ranking, filtering) happens offline, and the online path is a lookup.

## Step 1: Requirements

**Functional**

- Given a prefix, return the top **k** (say 10) completions.
- Rank by popularity, with some weight for recency so trending queries appear.
- Support multiple languages/locales.
- Never suggest offensive, dangerous or private content.

**Non-functional**

- **Latency**: users type a character every ~100–200 ms. Suggestions should render within ~100 ms end to end, so the server budget is ~10–20 ms.
- **Availability**: if autocomplete is down, search still works, so it's important but not critical. Degrade gracefully (show nothing) rather than slow the search box.
- **Freshness**: a new trending query (breaking news) should appear within minutes to an hour; general popularity can update daily.
- **Eventual consistency** is fine: two users seeing slightly different suggestions is harmless.

Out of scope: spelling correction, full search results.

## Step 2: Estimates

Assume **1 billion searches/day**. Users type ~20 characters per query, but clients **debounce** (wait ~100 ms of idle before sending) and stop once they pick a suggestion, so call it **~6 suggestion requests per search**.

Requests per second are searches per day times requests per search, divided by the seconds in a day:

```formula
rate = 1B × 6 / 10^5 s ≈ 60,000/s
peak = 60,000/s × 3 = 180,000/s
where
rate: average suggestion requests per second
peak: requests per second at the busiest time, using an assumed peak factor of 3
B: billion (10^9) searches per day
6: suggestion requests per search after debouncing
10^5: 100,000, the seconds in a day (86,400) rounded up
s: seconds; /s means per second
≈: approximately equal to (rounded)
In words: a billion searches a day at six requests each is about 60,000 requests a second on average, and three times that at peak.
```

What to store? Most queries are rare; the long tail is huge and mostly useless for suggestions. Keep the **top ~100 million queries** by frequency.

Size the three parts of the index: the query strings, the trie nodes (one per distinct prefix), and a top-10 list at every node:

```formula
strings = 100M × 25 B ≈ 2.5 GB
max nodes = 100M × 20 = 2 bn
nodes ≈ 500M
lists = 500M × 10 × 4 B = 20 GB
where
strings: bytes to store the query text itself
max nodes: the most trie nodes possible, if no two queries shared a prefix
nodes: the assumed number of trie nodes once shared prefixes are counted once
lists: bytes for a top-10 list of 4-byte query IDs at every node (40 bytes per node)
M: million (10^6)
bn: billion (10^9)
B: bytes
GB: gigabyte, 10^9 bytes
≈: approximately equal to (rounded or assumed)
In words: the query text is small; the per-node top-10 lists dominate, at about 20 GB, and with overhead the whole index is assumed to be 30–50 GB.
```

(The node count is an assumption: with no sharing at all, 100M queries capped at 20 characters would need up to 2 billion nodes, but popular queries share long prefixes heavily.) A 4-byte ID is enough because 4 bytes is 32 bits:

```formula
2^32 ≈ 4.3 × 10^9 > 10^8
where
2^32: the number of different values 32 bits can hold, 2 multiplied by itself 32 times
10^9: a billion; 10^8: a hundred million, the number of queries kept
>: is greater than
≈: approximately equal to
In words: 32 bits can number about 4.3 billion things, far more than the 100 million queries to identify.
```

Under these compact-layout assumptions, the index may fit in one large machine's RAM. Measure the built representation: pointers, child maps, strings and allocator overhead can make a naive trie much larger. We'll replicate it rather than shard it, which keeps serving simple. Budget for **two copies** in memory, because a node loads the new trie snapshot before releasing the old one: a 50 GB index wants a machine with well over 100 GB of RAM.

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

Store the top-k completions **at each node**. Lookup becomes "walk to the node, return its list". Big-O notation describes how the work grows:

```formula
naive = O(p + S)
precomputed = O(p + k)
where
O(...): Big-O, "grows at most in proportion to" the expression inside, ignoring constant factors
p: the length of the typed prefix, in characters
S: the number of nodes in the subtree below the prefix, which can be millions for a one-letter prefix
k: the number of suggestions returned, here 10
naive, precomputed: the lookup cost without and with a top-k list stored at each node
In words: storing the answer at each node turns a search of a possibly huge subtree into a walk of a few characters plus reading k items.
```

That is, plus output-string bytes, with no subtree search.

```
node "how t" -> [how to tie a tie (98k),
                 how to train your dragon,
                 ...]
```

The cost is memory (k entries per node) and rebuild work, but we do that offline. Use compact IDs instead of full strings in each list, and cap prefix depth (beyond ~20–30 characters, there's little to suggest).

### Alternatives

- **Flattened trie in a KV store**: store `prefix → top-k list` directly in Redis or Cassandra. Easy to shard and update; slightly more memory than a trie. Good if the index outgrows one machine.
- **Finite-state transducers**: Lucene and Elasticsearch's completion suggester use FSTs, a compressed trie that shares suffixes as well as prefixes, often several times smaller.
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

## Deep dive 1: The data collection pipeline

1. **Log** every submitted search (not every keystroke; we rank on what people *searched*) with timestamp, locale and a pseudonymous user ID (which is not automatically anonymous). At 1B/day, sampling 1 in 10 still gives plenty of signal for popular queries.
2. **Aggregate** with a stream processor (Flink, Kafka Streams) into counts per `(query, locale, hour)`. For truly huge streams, approximate structures such as a [count-min sketch](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch) with a heavy-hitters heap find frequent queries in fixed memory.
3. **Score** with time decay so last week counts more than last year (formula below).
4. **Filter**: remove queries on a blocklist (hate, violence, adult), and apply a **privacy threshold**: only consider queries searched by at least a minimum number of distinct users. This reduces rare-query exposure but does not guarantee privacy: sensitive information can be searched by many people or bots. Add explicit sensitive-data filtering and review.
5. **Build** the trie with top-k at every node (Spark job: for every query, emit `(prefix, query, score)` for each of its prefixes, group by prefix, keep the top k). With 100M queries and up to 20 prefixes each, that's up to 2 billion records to shuffle, a substantial batch workload whose duration depends on cluster resources.
6. **Publish** the serialised trie to object storage with a version number. Serving nodes download it, load it into memory alongside the current one, then publish the new root atomically with suitable synchronization. Retain the old trie snapshot until all readers using it finish. Roll out to a few nodes first and compare metrics, just like a code deploy.

The time-decayed score in step 3 weights each day's searches by how old they are:

```formula
score = Σ count_d × 0.9^{age_d}
0.9^{6.6} ≈ 0.5
0.9^{30} ≈ 0.04
where
score: the query's ranking score
Σ: sigma, "add up over every day d" in the history
d: one day of history
count_d: how many times the query was searched on day d
age_d: how many days ago day d was (0 for today)
0.9^{age_d}: 0.9 multiplied by itself age_d times, the weight for that day; it shrinks by 10% per day of age
≈: approximately equal to (rounded)
In words: each day of age multiplies a search's weight by 0.9, so a search's weight halves roughly every 6.6 days and a month-old search keeps only about 4%.
```

The decay factor sets the trade-off: closer to 1 (say 0.98) keeps long-term favourites; smaller (say 0.7) makes suggestions chase the last few days.

### Freshness for trending queries

A daily rebuild can't surface "earthquake in Tokyo" ten minutes after it happens. Add a small **real-time layer**: the stream aggregator tracks queries whose last-hour count is far above their baseline, and the suggest service merges this small "trending" list into results for matching prefixes. The big trie stays daily; only a few thousand trending entries change minute to minute.

### Removing a suggestion urgently

Sometimes a suggestion must disappear *now*: a defamatory phrase, a victim's name, a legal takedown. Waiting for tomorrow's build isn't acceptable, and the CDN may hold the bad response for its whole TTL. So:

- Keep a small **serve-time blocklist** that every suggest node checks before returning results. It's pushed in seconds, like a config change.
- **Purge** affected prefixes from the CDN (every major CDN has a purge API), or keep edge TTLs short enough that the worst-case exposure is acceptable.
- Add the term to the pipeline's blocklist so the next build drops it at source.

## Deep dive 2: Scaling the serving path

If a representative benchmark establishes 1,000 requests/s per core at the target latency, the core count is the peak rate divided by that:

```formula
cores = peak / cap
cores = 180,000/s / 1,000/s = 180
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

Personalisation breaks edge cacheability. A common compromise: cache the global top-50 at the edge, and do the personal re-ranking (or blend in the user's own recent searches) on the client or in a thin per-user service.

Facebook's original typeahead took personalisation further: when you focused the search box, it preloaded your friends and frequently visited pages into the browser, so the first few characters were matched entirely client-side.

## Bottlenecks and trade-offs

| Decision | Trade-off |
|---|---|
| Top-k at each node | Fast reads, more RAM |
| Daily rebuild | Simple, stale |
| Real-time layer | Fresh, more moving parts |
| Edge caching | Huge offload, no personalisation |

Failure modes to mention:

- **Bad trie snapshot**: a pipeline bug ships an empty or offensive trie. Validate trie snapshots (size, sample lookups, blocklist check) before publishing, and keep the previous version for instant rollback.
- **Manipulation**: bots search a phrase repeatedly to make it a suggestion. Count distinct users rather than raw searches and apply anomaly detection.
- **Slow responses are worse than none**: if the service doesn't answer within ~50 ms, the client should give up; a late suggestion for an old prefix is just noise.

## At 10x scale

At 10 billion searches/day with 50 locales:

```formula
peak = 10B × 6 / 10^5 s × 3 ≈ 1.8M/s
where
peak: peak suggestion requests per second
B: billion
M: million
6: suggestion requests per search
10^5: 100,000, the seconds in a day rounded
3: the assumed peak factor
s: seconds; /s means per second
≈: approximately equal to
In words: ten times the searches gives about 1.8 million, call it 2 million, suggestion requests a second at peak.
```

That is about 2M suggestion requests/s at peak. Then:

- **Edge first**: push the most popular prefixes' responses into CDN workers' memory; the origin sees only the long tail.
- **Partition by locale and region**, each with its own trie and its own replicas.
- **Rebuild incrementally**: instead of recomputing everything daily, apply hourly deltas for queries whose scores changed significantly.
- **Richer ranking** through the two-stage model, with the re-ranker deployed close to users.
- **Fuzzy matching** (typos) via Levenshtein automata over the FST, which Lucene supports, at the cost of more CPU per lookup.

## Key takeaways

- Keep the serving path a pure in-memory lookup; do counting, ranking and filtering offline.
- Precompute top-k at every trie node so a lookup costs only the prefix walk plus reading k items, with no subtree search.
- If the measured index fits with swap/headroom budgets, replication avoids sharding complexity; query count alone does not prove its memory footprint.
- A batch pipeline rebuilds the trie daily; a small real-time layer adds trending queries within minutes.
- Short prefixes dominate traffic and are identical for everyone, so cache them at the CDN and in the browser.
- Filter for safety and privacy (distinct-user thresholds) before anything is suggested, and keep a serve-time blocklist plus CDN purge for urgent removals.
- Budget RAM for two snapshots during a swap, and validate each trie snapshot before rollout.

## Further reading

- [Trie (Wikipedia)](https://en.wikipedia.org/wiki/Trie)
- [Meta engineering: the life of a typeahead query](https://engineering.fb.com/2010/05/17/web/the-life-of-a-typeahead-query/)
- [Elasticsearch: search suggesters (completion suggester)](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-suggesters)
- [Count–min sketch (Wikipedia)](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch)
- [Andrew Gallant: index 1,600,000,000 keys with automata and Rust](https://burntsushi.net/transducers/)
- [Radix tree (Wikipedia)](https://en.wikipedia.org/wiki/Radix_tree)
