---
id: cs1-suggest-decay-privacy-freshness
title: Build fresh suggestions without exposing rare queries
level: intermediate
minutes: 4
summary: Rank submitted searches with explicit decay and eligibility rules.
sourceLesson: cs1-typeahead
---

## Deep dive 1: The data collection pipeline

1. **Log** every submitted search (not every keystroke; we rank on what people *searched*) with timestamp, locale and a pseudonymous user ID (which is not automatically anonymous). At 1B/day, sampling 1 in 10 still gives plenty of signal for popular queries.
2. **Aggregate** with a stream processor (Flink, Kafka Streams) into counts per `(query, locale, hour)`. For truly huge streams, approximate structures such as a [count-min sketch](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch) with a heavy-hitters heap find frequent queries in fixed memory.
3. **Score** with time decay so last week counts more than last year (formula below).
4. **Filter**: remove queries on a blocklist (hate, violence, adult), and apply a **privacy threshold**: only consider queries searched by at least a minimum number of distinct users. This reduces rare-query exposure but does not guarantee privacy: sensitive information can be searched by many people or bots. Add explicit sensitive-data filtering and review.
5. **Build** the trie with top-k at every node (Spark job: for every query, emit `(prefix, query, score)` for each of its prefixes, group by prefix, keep the top k). With 100M queries and up to 20 prefixes each, that's up to 2 billion records to shuffle, a substantial batch workload whose duration depends on cluster resources.
6. **Publish** the serialised trie to object storage with a version number. Serving nodes download it, load it into memory alongside the current one, then publish the new root atomically with suitable synchronization. Retain the old trie snapshot until all readers using it finish. Roll out to a few nodes first and compare metrics, just like a code deploy.

The time-decayed score in step 3 weights each day's searches by how old they are:

```formula
score = Σ(count_d × 0.9^{age_d})
0.9^{6.6} ≈ 0.5
0.9^{30} ≈ 0.04
where
score: the query's ranking score
Σ: sigma, "add up over every day d" in the history
d: one day of history
count_d: how many times the query was searched on day d
age_d: how many days ago day d was (0 for today)
0.9^{age_d}: age_d copies of 0.9 multiplied together, the weight for that day; it shrinks by 10% per day of age
≈: approximately equal to (rounded)
In words: each day of age multiplies a search's weight by 0.9, so a search's weight halves roughly every 6.6 days and a month-old search keeps only about 4%.
```

The decay factor sets the trade-off: closer to 1 (say 0.98) keeps long-term favourites; smaller (say 0.7) makes suggestions chase the last few days.

### Freshness for trending queries

A daily rebuild can't surface "earthquake in Tokyo" ten minutes after it happens. Add a small **trending overlay**: the stream aggregator tracks queries whose last-hour count is far above their baseline, and the suggest service merges this small "trending" list into results for matching prefixes. The big trie stays daily; only a few thousand trending entries change minute to minute.

### Removing a suggestion urgently

Sometimes a suggestion must disappear *now*: a defamatory phrase, a victim's name, a legal takedown. Waiting for tomorrow's build isn't acceptable, and the CDN may hold the bad response for its whole TTL. So:

- Keep a small **serve-time blocklist** that every suggest node checks before returning results. It's pushed in seconds, like a config change.
- **Purge** affected prefixes using the selected CDN's documented purge mechanism, or keep edge TTLs short enough that the worst-case exposure is acceptable.
- Add the term to the pipeline's blocklist so the next build drops it at source.

## Key takeaways

- Rank submitted searches with explicit decay and eligibility rules.
- A distinct-user threshold reduces rare exposure but is not a privacy guarantee.
- Combine a trending overlay, serve-time blocklist and cache purge for urgent changes.

## Further reading

- [Meta: the life of a typeahead query](https://engineering.fb.com/2010/05/17/web/the-life-of-a-typeahead-query/)
- [Exponential decay](https://en.wikipedia.org/wiki/Exponential_decay)
