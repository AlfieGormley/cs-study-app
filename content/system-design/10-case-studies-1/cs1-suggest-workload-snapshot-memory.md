---
id: cs1-suggest-workload-snapshot-memory
title: Size suggestion traffic and snapshot memory
level: intermediate
minutes: 4
summary: Debouncing changes the number of requests per search.
sourceLesson: cs1-typeahead
---

Type "how to" into a search box and suggestions appear before you finish the word. Typing can generate several suggestion requests per search; debouncing and local reuse determine how many actually reach the server.

The trick to this problem is realising that **the serving path should do almost no work**. Precompute expensive counting and candidate selection so the online path starts with a lookup. Current removal rules, trending merges and any personal re-ranking still require bounded serve-time work.

## Step 1: Requirements

**Functional**

- Given a prefix, return the top **k** (say 10) completions.
- Rank by popularity, with some weight for recency so trending queries appear.
- Support multiple languages/locales.
- Never suggest offensive, dangerous or private content.

**Non-functional**

- **Latency**: assume a character every 100–200 ms for this interaction budget. Suggestions should render within ~100 ms end to end, so the server budget is ~10–20 ms.
- **Availability**: if autocomplete is down, search still works, so it's important but not critical. Degrade gracefully (show nothing) rather than slow the search box.
- **Freshness**: a new trending query (breaking news) should appear within minutes to an hour; general popularity can update daily.
- **Eventual consistency** is fine: two users seeing slightly different suggestions is harmless.

Out of scope: spelling correction, full search results.

## Step 2: Estimates

Assume **1 billion searches/day**. Users type ~20 characters per query, but clients **debounce** (wait ~100 ms of idle before sending) and stop once they pick a suggestion, so call it **~6 suggestion requests per search**.

Requests per second are searches per day times requests per search, divided by the seconds in a day:

Measure suggestion requests per completed search: typing pauses, cancellation, cache reuse and selection all affect it. A daily search count does not establish a universal keystroke multiplier or a peak profile.

What to store? Most queries are rare; the long tail is huge and mostly useless for suggestions. Keep the **top ~100 million queries** by frequency.

Size the three parts of the index: the query strings, the trie nodes (one per distinct prefix), and a top-10 list at every node:

The index holds query strings, prefix structure and stored candidate lists. Repeating a top-ten list at many prefix nodes can dominate raw text size; pointer, allocator and child-map overhead depend on representation.

The number of distinct prefixes depends on the actual corpus and maximum prefix depth. Do not infer it from the number of queries alone:

Choose an identifier width that covers every retained query, including reserved values. Compact IDs reduce repeated list payload; they do not account for the rest of the index.

If the measured index and its rollout overlap fit the selected machine’s memory budget, full replication is an option. Measure the built representation: pointers, child maps, strings and allocator overhead can make a naive trie much larger. We'll replicate it rather than shard it, which keeps serving simple. Budget for **two copies** in memory, because a node loads the new trie snapshot before releasing the old one: a 50 GB index wants a machine with well over 100 GB of RAM.

## Key takeaways

- Debouncing changes the number of requests per search.
- Measure the built index; a query count does not prove its memory footprint.
- Budget for old and new snapshots to coexist while readers finish.

## Further reading

- [Finite-state transducers and compact indexes](https://burntsushi.net/transducers/)
- [Elasticsearch: completion suggesters](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-suggesters)
