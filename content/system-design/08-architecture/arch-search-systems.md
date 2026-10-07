---
id: arch-search-systems
title: Search systems
level: intermediate
minutes: 16
summary: How full-text search works under the hood, from tokenisation and inverted indexes to TF-IDF and BM25 ranking, how Elasticsearch distributes it with shards and replicas, and how to keep a search index in sync with your database.
---

`SELECT * FROM products WHERE description LIKE '%wireless headphones%'` usually needs a scan without a suitable text/trigram index, does not perform stemming, and may be case-sensitive depending on the database and collation, and has no idea which result is *best*. Search engines solve all three problems with a different data structure, a text-processing pipeline and a ranking function.

## The inverted index

A normal (forward) index maps document → words. An **inverted index** maps each **term → the list of documents containing it** (a *posting list*), often with positions and frequencies.

```
 doc1: "red wireless headphones"
 doc2: "wireless mouse"
 doc3: "red mouse mat"

 term       postings
 --------   -----------
 headphone  [1]
 mat        [3]
 mouse      [2, 3]
 red        [1, 3]
 wireless   [1, 2]
```

A query for `wireless mouse`:

1. Look up `wireless` → [1, 2] and `mouse` → [2, 3].
2. AND = intersect → [2]; OR = union → [1, 2, 3].
3. Score the candidates and return the top results.

Lookups are fast because each term is found via a sorted term dictionary (in Lucene, a compact finite-state structure) and posting lists are sorted and compressed, so intersection is a merge of sorted lists, often skipping large chunks.

## Text analysis: tokenisation and normalisation

Before indexing (and again at query time), text goes through an **analyser**:

```
"The Runners' Shoes!"
  | tokenise
["The","Runners'","Shoes"]
  | lowercase, strip punctuation
["the","runners","shoes"]
  | stop words (optional)
["runners","shoes"]
  | stem
["runner","shoe"]
```

- **Tokeniser**: splits text into tokens. Whitespace and punctuation for English; languages like Chinese or Japanese need dictionary-based or n-gram tokenisers because they don't use spaces.
- **Token filters**: lowercasing, ASCII folding (`café` → `cafe`), stemming (`running` → `run`), synonyms (`tv` ↔ `television`), stop-word removal.
- **N-grams / edge n-grams**: index `hea`, `head`, `headp`... to support search-as-you-type and partial matches, at the cost of a much larger index.

> [!warning] The same analyser on both sides
> If documents are stemmed at index time but queries aren't, "running" in a query won't match the indexed token "run". Index-time and query-time analysis must be compatible. This is one of the most common search bugs.

## Relevance: TF-IDF and BM25

Matching tells you *which* documents qualify. Ranking tells you which are *best*. The classic intuition:

- **Term frequency (TF)**: a document mentioning "headphones" 5 times is probably more about headphones than one mentioning it once.
- **Inverse document frequency (IDF)**: rare terms are more informative. "the" appears everywhere and means little; "noise-cancelling" is rare and decisive.

```
tf-idf(t, d) = tf(t,d) * log(N / df(t))

N = 1,000,000 docs
"wireless": df = 50,000
   idf = log10(20)    = 1.30
"anc":      df = 1,000
   idf = log10(1,000) = 3.00
```

So a match on the rarer term counts more than twice as much.

**BM25** (Okapi BM25) is the modern default: Lucene switched to it in version 6, Elasticsearch in 5.0, and OpenSearch inherited it. It keeps an IDF factor and improves on TF-IDF in two ways:

- **TF saturation**: the 10th occurrence of a word adds much less than the 2nd. A parameter `k1` (default 1.2) controls how fast it saturates, reducing the marginal reward for repetition; it does not guarantee immunity to keyword stuffing.
- **Length normalisation**: within the same field and with other factors equal, shorter fields receive less length penalty. Scores across different fields also depend on their own statistics and boosts. BM25 compares each field's length with the *average* length of that field across the index. Parameter `b` (default 0.75) controls how strongly length counts; `b = 0` turns it off.

The classic BM25 teaching formula per query term is below. Its constant (k1 + 1) factor is omitted by current Lucene scoring, so the following numerical values explain this formula rather than predict exact Elasticsearch scores:

```
         tf * (k1 + 1)
idf * -------------------
      tf + k1 * (1 - b
         + b * len/avg)
```

A document's score is the sum over the query's terms. With `k1 = 1.2` and an average-length field, one occurrence scores 1.0 × IDF, two score about 1.38 × IDF, and ten only about 1.96 × IDF. However many times a term repeats, its contribution can never exceed `(k1 + 1)` × IDF, which is 2.2 × IDF here.

BM25 is still purely **lexical**: it scores matching tokens and knows nothing about meaning. "Sofa" won't match "couch" unless an analyser adds the synonym.

Real systems layer more signals on top: field boosts (title matches beat body matches), freshness, popularity, personalisation, and increasingly **vector (semantic) search** with embeddings, often combined with BM25 in **hybrid search** and then re-ranked by a learned model.

## Elasticsearch architecture

Elasticsearch (and its fork OpenSearch) builds a distributed system on top of Lucene.

- An **index** is a logical collection of documents (like a table).
- It is split into **primary shards**; each shard is a complete Lucene index holding a subset of documents. A document's shard comes from a hash of its routing value (its `_id` by default), mapped through the index's configured routing-shard scheme to a primary shard (a simple modulo description omits split-routing and partitioned-routing details). That's why the primary count can't simply be changed later.
- Each primary has **replica shards**: full copies, for failover and extra read capacity. Elasticsearch never puts a replica on the same node as its primary. Unlike the primary count, the replica count can be changed at any time.
- Since Elasticsearch 7.0 a new index defaults to **1 primary and 1 replica** (before 7.0 it was 5 primaries).

```
 index "products": 3 primaries, 1 replica

 Node A       Node B       Node C
 [P0] [R2]    [P1] [R0]    [P2] [R1]
```

Any *single* node can lose its disks and every shard still has a copy elsewhere. If a node holding a primary fails, the master promotes an in-sync replica to primary and then rebuilds a new replica on another node. Note that a single-node cluster with 1 replica has nowhere to put the replicas, so the index shows as *yellow* (unassigned replicas).

### How a write runs

1. The write is routed to the shard's **primary**.
2. The primary validates and indexes it, then forwards it to all **in-sync replicas** in parallel.
3. The primary waits for in-sync copies or removal of a failed copy from the in-sync set before acknowledging. Inspect the response shard results and durability settings; an acknowledgment does not guarantee the configured replica count was available.

So replicas add write cost (every copy indexes every document) while adding read capacity. More replicas help a read-heavy cluster and hurt a write-heavy one.

### How a search runs (scatter-gather)

1. The **coordinating node** receives the query.
2. **Query phase**: it sends the query to one copy (primary or replica) of every shard. Each shard returns only the IDs and scores of its own top N (where N is `from + size`).
3. It merges these into a global top N.
4. **Fetch phase**: it asks the relevant shards for the actual documents.

The query phase waits for participating shards, and end-to-end latency also includes coordinating, fetch and network work, which is why too many small shards hurt and why replicas help: since 7.0, **adaptive replica selection** uses response-time, service-time and queue information to choose shard copies.

Deep pagination is costly for the same reason: page 1,000 at 10 per page (from = 9,990) can require each participating shard to return up to its top 10,000, which the coordinator then sorts. Elasticsearch caps `from + size` at 10,000 by default and offers `search_after` for deep scrolling.

### Near-real-time indexing

New documents are written to an in-memory buffer and a **transaction log** (translog), then made searchable on a **refresh** that writes the buffer out as a new immutable Lucene **segment**. The default refresh_interval is 1 second in Elastic Stack and 5 seconds in Serverless. With the interval left implicit, search-idle shards can skip background refreshes until searched; explicitly setting the interval changes this idle behavior. Segments are merged in the background.

So Elasticsearch is **near-real-time**: search visibility follows refresh rather than acknowledgment; the configured interval is not a hard visibility deadline. A refreshed segment isn't yet fsynced to disk; durability comes from the translog, and a periodic **flush** makes a full Lucene commit. Bulk loads often set `refresh_interval` higher (or to `-1`) to improve throughput.

### Sizing shards

The number of primary shards is fixed at index creation (changing it needs a reindex, split or shrink operation). Elastic's guidance is shards of roughly 10–50 GB (and under about 200 million documents). Too few and you can't spread load; too many and per-shard overhead and scatter-gather cost dominate. For time-based data (logs), use one index per day or week with **index lifecycle management** to roll over and delete old indexes.

## Keeping search in sync with the source of truth

The search index is a **derived copy**, not the source of truth. Your database is. The hard part of search architecture is keeping the copy current.

### Option 1: Dual writes (avoid)

```
 app -> write DB
 app -> write Elasticsearch
```

If the second write fails, or two concurrent updates reach ES in the opposite order to the DB, the index silently diverges. There's no transaction across both.

### Option 2: Change data capture (CDC) via a log

```
 [DB] --WAL/binlog--> [Debezium]
                          |
                       [Kafka]
                          |
                   [indexer workers]
                          |
                   [Elasticsearch]
```

- CDC can capture committed changes in source order, provided the snapshot/log handoff is correct and required logs are retained. Monitor connector errors, replication slots and retention; parallel consumers must preserve per-key order or reject stale versions.
- Kafka buffers changes within configured durability and retention limits; monitor lag before records expire.
- Make indexing idempotent and version-aware: map each complete row snapshot to a strictly increasing supported integer version and use version_type=external. Equal as well as older versions are rejected; handle a known duplicate conflict deliberately. Deletes need durable tombstones or another replay strategy because delete-version retention expires. A raw PostgreSQL LSN string is not directly a supported integer version.

An alternative is the **transactional outbox**: write an event row in the same DB transaction, and a relay publishes it.

### Option 3: Periodic reindex

For smaller datasets or as a safety net, rebuild the index from the database periodically. A common pattern is to **build a new index in the background and atomically switch an alias** (`products` → `products_v2`), supporting a cutover without intentionally stopping reads. Coordinate snapshot/live-change ordering, catch up before switching, and keep the old index current if rollback is required.

> [!tip] Plan for full rebuilds from day one
> You'll change analysers, mappings and ranking many times. Changing index-time analysis requires reindexing existing documents. Some search-time analyser or synonym changes can be applied without rebuilding the stored index. Design so you can always rebuild the index from the source of truth (CDC from a snapshot, or a bulk export) and cut over with an alias.

## Key takeaways
- An inverted index maps terms to posting lists, making term lookup and boolean combination fast.
- Analysis (tokenising, lowercasing, stemming, synonyms) determines what matches; index-time and query-time analysis must agree.
- TF-IDF rewards frequent-in-document, rare-in-corpus terms; BM25 adds term-frequency saturation and length normalisation and is the default in Lucene-based engines.
- Elasticsearch splits an index into a fixed number of primary shards, each with an adjustable number of replicas on other nodes. Writes go through the primary and in-sync replication protocol; ordinary queries scatter to eligible shard copies, then coordinate and fetch results. Routing and shard pruning can reduce participation.
- Indexing is near-real-time: documents become searchable on refresh; defaults and idle behavior depend on deployment and settings.
- The search index is a derived view: feed it from CDC or an outbox with version-aware idempotent writes, and keep the ability to rebuild it behind an alias.

## Further reading
- [Wikipedia: Inverted index](https://en.wikipedia.org/wiki/Inverted_index)
- [Wikipedia: Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25)
- [Wikipedia: tf–idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- [Elasticsearch: Text analysis](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html)
- [Elasticsearch: Scalability and resilience](https://www.elastic.co/guide/en/elasticsearch/reference/current/scalability.html)
- [Elasticsearch: Near real-time search](https://www.elastic.co/guide/en/elasticsearch/reference/current/near-real-time.html)
- [Debezium architecture](https://debezium.io/documentation/reference/stable/architecture.html)
