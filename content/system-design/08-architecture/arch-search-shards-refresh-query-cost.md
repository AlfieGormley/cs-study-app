---
id: arch-search-shards-refresh-query-cost
title: Tracing distributed search and visibility
level: intermediate
minutes: 5
summary: Follow Elasticsearch writes, scatter-gather queries and refreshes while recognising shard and pagination costs.
sourceLesson: arch-search-systems
---

Matching and scoring happen within Lucene indexes. Elasticsearch distributes them across primary and replica shards; this unit explains how that changes cost and visibility.

## Elasticsearch architecture

Elasticsearch (and its fork OpenSearch) builds a distributed system on top of Lucene.

- An **index** is a logical collection of documents (like a table).
- It is split into **primary shards**; each shard is a complete Lucene index holding a subset of documents. A document's shard comes from its routing value (its `_id` by default). For indexes created before Elasticsearch 9.4, the legacy routing-shard mapping applies; newer indexes use a hash modulo the primary-shard count. Custom partitioned routing adds further rules. The primary-shard count remains an index-creation setting; consult the version and routing settings before migrating.
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

Deep pagination is costly for the same reason. Each shard must return enough results to cover every page up to the one you asked for:

```formula
from = (p − 1) × size
N_shard = from + size
N_shard = (1000 − 1) × 10 + 10 = 10000
where
from: how many results to skip before the page starts (an Elasticsearch search parameter)
p: the page number requested, here 1,000
size: results per page, here 10
N_shard: how many top hits each participating shard must return to the coordinating node
In words: to show results 9,991 to 10,000, every shard sends its top 10,000 and the coordinator sorts them all to keep 10.
```

With 5 shards that is 50,000 hits sorted to show 10. Elasticsearch caps `from + size` at 10,000 by default and offers `search_after` for deep scrolling.

### Near-real-time indexing

New documents are written to an in-memory buffer and a **transaction log** (translog), then made searchable on a **refresh** that writes the buffer out as a new immutable Lucene **segment**. The default refresh_interval is 1 second in Elastic Stack and 5 seconds in Serverless. With the interval left implicit, search-idle shards can skip background refreshes until searched; explicitly setting the interval changes this idle behavior. Segments are merged in the background.

So Elasticsearch is **near-real-time**: search visibility follows refresh rather than acknowledgment; the configured interval is not a hard visibility deadline. A refreshed segment isn't yet fsynced to disk; durability comes from the translog, and a periodic **flush** makes a full Lucene commit. Bulk loads often set `refresh_interval` higher (or to `-1`) to improve throughput.

### Sizing shards

The number of primary shards is fixed at index creation (changing it needs a reindex, split or shrink operation). Elastic's guidance is shards of roughly 10–50 GB (and under about 200 million documents). Too few and you can't spread load; too many and per-shard overhead and scatter-gather cost dominate. For time-based data (logs), use one index per day or week with **index lifecycle management** to roll over and delete old indexes.

## Key takeaways
- Primaries own routed documents; replica copies add read capacity and redundancy while repeating indexing work.
- A query gathers shard candidates, merges them, then fetches selected documents.
- Deep offsets expand each shard's candidate window; search_after supports traversal without that growing offset.
- Search visibility follows refresh rather than write acknowledgement, and deployment settings alter defaults.

## Further reading
- [Elasticsearch: Scalability and resilience](https://www.elastic.co/guide/en/elasticsearch/reference/current/scalability.html)
- [Elasticsearch: Near real-time search](https://www.elastic.co/guide/en/elasticsearch/reference/current/near-real-time.html)
- [Elasticsearch: General index settings](https://www.elastic.co/docs/reference/elasticsearch/index-settings/index-modules)
- [Elasticsearch: General index settings](https://www.elastic.co/docs/reference/elasticsearch/index-settings/index-modules)
