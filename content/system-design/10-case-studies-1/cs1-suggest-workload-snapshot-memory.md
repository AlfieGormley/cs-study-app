---
id: cs1-suggest-workload-snapshot-memory
title: Size suggestion traffic and snapshot memory
level: intermediate
minutes: 4
summary: Debouncing changes the number of requests per search.
sourceLesson: cs1-typeahead
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

- **Latency**: assume a character every 100–200 ms for this interaction budget. Suggestions should render within ~100 ms end to end, so the server budget is ~10–20 ms.
- **Availability**: if autocomplete is down, search still works, so it's important but not critical. Degrade gracefully (show nothing) rather than slow the search box.
- **Freshness**: a new trending query (breaking news) should appear within minutes to an hour; general popularity can update daily.
- **Eventual consistency** is fine: two users seeing slightly different suggestions is harmless.

Out of scope: spelling correction, full search results.

## Step 2: Estimates

Assume **1 billion searches/day**. Users type ~20 characters per query, but clients **debounce** (wait ~100 ms of idle before sending) and stop once they pick a suggestion, so call it **~6 suggestion requests per search**.

Requests per second are searches per day times requests per search, divided by the seconds in a day:

```formula
rate = 1B × 6 / (10^5 s) ≈ 60,000/s
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
2^32: the number of different values 32 bits can hold, 32 copies of 2 multiplied together
10^9: a billion; 10^8: a hundred million, the number of queries kept
>: is greater than
≈: approximately equal to
In words: 32 bits can number about 4.3 billion things, far more than the 100 million queries to identify.
```

Under these compact-layout assumptions, the index may fit in one large machine's RAM. Measure the built representation: pointers, child maps, strings and allocator overhead can make a naive trie much larger. We'll replicate it rather than shard it, which keeps serving simple. Budget for **two copies** in memory, because a node loads the new trie snapshot before releasing the old one: a 50 GB index wants a machine with well over 100 GB of RAM.

## Key takeaways

- Debouncing changes the number of requests per search.
- Measure the built index; a query count does not prove its memory footprint.
- Budget for old and new snapshots to coexist while readers finish.

## Further reading

- [Finite-state transducers and compact indexes](https://burntsushi.net/transducers/)
- [Elasticsearch: completion suggesters](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-suggesters)
