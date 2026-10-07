---
id: db-nosql-families
title: NoSQL families
level: basic
minutes: 13
summary: Key-value, document, wide-column, graph, time-series and search stores, what each is built for, and real examples.
---

"NoSQL" isn't one thing. It's a loose label for databases that drop part of the relational model, usually joins, a fixed schema or multi-row transactions, in exchange for something else: horizontal scale, a more natural data shape, or speed on one access pattern.

The useful way to think about each family: **what does it make cheap, and what does it make expensive?**

## Key-value stores

The simplest model: a giant distributed hash map. You `GET(key)`, `PUT(key, value)` and `DELETE(key)`. In a pure key-value model the value is opaque; products such as Redis and DynamoDB also understand structured values and offer additional operations.

- **Examples**: Redis (in memory), Amazon DynamoDB, Riak, etcd, RocksDB (embedded).
- **Cheap**: lookups by exact key. Actual latency depends on deployment, payload, consistency, load and network distance.
- **Expensive**: anything else. "Find all users in Leeds" means scanning everything unless you build your own index.

Check durability before treating an in-memory store as a system of record. Redis by default only snapshots to disk periodically (RDB), so a crash loses everything since the last snapshot. Its append-only file with `appendfsync everysec` narrows that to about a second of writes.

DynamoDB extends the model a little. Each item has a **partition key** (hashed to pick a partition) and an optional **sort key**, and items with the same partition key are stored together, sorted. That lets you do range queries *within* one partition:

```
PK = USER#42      SK = ORDER#2026-09-01
PK = USER#42      SK = ORDER#2026-09-14
PK = USER#42      SK = PROFILE
```

A `Query(PK = USER#42, SK begins_with ORDER#)` returns that user’s orders in normalized date-key order; results larger than the Query page limit require pagination. This is the basis of *single-table design*: you model access patterns first, then shape keys to serve them.

> [!note] DynamoDB in numbers
> DynamoDB targets single-digit millisecond service latency for common operations, rather than guaranteeing every request latency; items are at most 400 KB, partitions of up to 10 GB, and each partition serving up to 3,000 read units and 1,000 write units per second. DynamoDB splits busy partitions automatically, but it can't split a single hot *item*, so hot keys hit those limits long before the table does. Switching to on-demand billing doesn't lift them.

## Document stores

A document store keeps self-contained, nested documents, usually JSON or BSON. Unlike a key-value store, the database understands the structure, so it can index and query fields inside the document.

```json
{
  "_id": "order-981",
  "customer": { "id": 42, "name": "Priya" },
  "lines": [
    { "sku": "KET-1", "qty": 1,
      "price_p": 2999 },
    { "sku": "MUG-4", "qty": 2,
      "price_p": 899 }
  ],
  "status": "paid"
}
```

- **Examples**: MongoDB, Couchbase, Firestore, and Postgres's own `jsonb` columns.
- **Cheap**: loading a whole aggregate (an order with its lines) in one read, without joins. Flexible schemas can ease evolution, but incompatible shape changes still need validation, migration or reader compatibility.
- **Expensive**: many-to-many relationships and cross-document joins. MongoDB has `$lookup`, but it's not what the engine is optimised for.

The modelling rule is *embed what you read together, reference what you share*. Order lines belong inside the order. A product shared by thousands of orders should be referenced by id, not copied everywhere.

Also keep embedded arrays *bounded*. A MongoDB document is capped at 16 MiB; an ever-growing array increases size and processing pressure, although updates and replication can use deltas rather than rewriting/transmitting the whole document. The **bucket pattern** fixes this: one document per device per hour, say, each holding that hour's readings.

> [!warning] Schemaless isn't schema-free
> The schema still exists; it has moved into your application code. Every reader must handle every historical shape of the document. MongoDB's JSON Schema validation can put some of it back in the database.

## Wide-column stores

Wide-column stores group related cells into rows and column families, but their partitioning differs. Cassandra and ScyllaDB hash a **partition key** and order rows within that partition by **clustering columns**. HBase and Google Bigtable instead range-partition lexicographically ordered row keys; the Cassandra CQL example below does not describe their key layout.

```sql
-- Cassandra CQL
CREATE TABLE readings (
  sensor_id  text,
  day        date,
  ts         timestamp,
  value      double,
  PRIMARY KEY ((sensor_id, day), ts)
) WITH CLUSTERING ORDER BY (ts DESC);
```

Here `(sensor_id, day)` is the partition key, and `ts` sorts rows within it. "Latest 100 readings for sensor X today" is a partition-targeted ordered query; multiple SSTables, replicas or storage reads may still be involved.

- **Cheap**: huge write throughput (they're built on LSM trees, covered in the indexing lesson), horizontal growth when key distribution and workload permit it, multi-datacentre replication.
- **Expensive**: queries that don't start with the partition key. No joins. You typically make one table *per query*, duplicating data across them.

That's why the example puts `day` in the partition key. Keyed by `sensor_id` alone, a sensor reporting every second would add 86,400 rows a day to one partition, forever. Huge partitions overload the replicas that own them and slow compaction and repair, so choose time buckets using measured serialized size, tombstones and query/repair behavior; a fixed size target is a rule of thumb, not a universal limit.

Specific company deployment counts are omitted because this review did not establish a reliable dated primary-source basis for both claims.

## Graph databases

When the relationships *are* the data (social networks, fraud rings, recommendation, access control), a graph database stores **nodes** and **edges** directly, and some engines use direct adjacency structures. Edge traversal cost still depends on caching, representation and network placement; not every graph database uses the same storage design.

```
(:Person {name:'Ana'})-[:FOLLOWS]->(:Person)
```

```
// Neo4j Cypher: friends of friends
MATCH (me:Person {id: 42})-[:FRIEND]->()
      -[:FRIEND]->(fof)
WHERE NOT (me)-[:FRIEND]->(fof)
  AND fof <> me
RETURN fof.name LIMIT 20;
```

- **Examples**: Neo4j, Amazon Neptune, JanusGraph, Dgraph.
- **Cheap**: multi-hop traversals ("within 3 hops"), path finding, pattern matching.
- **Expensive**: bulk aggregation over all nodes, and horizontal sharding (cutting a graph across machines makes traversals cross the network).

In SQL, each hop is another self-join, and a variable-depth search needs a recursive CTE. It works, but cost grows quickly with depth.

## Time-series databases

Metrics, IoT readings and financial ticks share a pattern: append-only writes, ordered by time, queried by time range and aggregated (`avg per minute`). Old data is downsampled or deleted.

- **Examples**: InfluxDB, TimescaleDB (a Postgres extension), Prometheus (for metrics), QuestDB.
- **Tricks**: columnar compression of timestamps (delta-of-delta encoding) and values (Gorilla-style XOR compression), time-partitioned storage so dropping a month is deleting a file, and built-in retention policies and continuous aggregates.

InfluxDB organises data into a *measurement* with *tags* (indexed metadata like `host=web-1`), *fields* (the values) and a timestamp. Each unique combination of tag values is a *series*. In InfluxDB 1.x and 2.x, watch **cardinality**: a tag with millions of distinct values (such as a user id) blows up the series index. InfluxDB 3 uses a different engine and supports high-cardinality tags; choose tags and fields from its version-specific schema guidance rather than carrying the TSM rule over unchanged.

## Search engines

Elasticsearch and OpenSearch (both built on Apache Lucene) maintain **inverted indexes**: a map from each term to the documents containing it. They're excellent at full-text relevance ranking, fuzzy matching and faceted filters, and are usually fed *from* a primary database rather than being the system of record.

They're also **near-real-time**: a newly indexed document becomes searchable only after the next *refresh*, every second by default for actively searched Elastic Stack indexes; serverless deployments and OpenSearch settings may differ. Check the configured interval. Fetching a document by id is real-time. Search architecture is covered in the architecture module.

## Summary table

| Family | Best at | Weak at |
|---|---|---|
| Key-value | Lookup by key | Queries on values |
| Document | Whole aggregates | Many-to-many |
| Wide-column | Writes at scale | Ad-hoc queries |
| Graph | Multi-hop links | Bulk analytics |
| Time-series | Time-range stats | Updates, joins |
| Search | Text relevance | Source of truth |

> [!tip] The lines are blurring
> Postgres has `jsonb`, full-text search and extensions for time series (TimescaleDB) and graphs (Apache AGE). MongoDB has multi-document ACID transactions. DynamoDB has transactions too. Pick based on the *core* access pattern, not the feature checklist.

## Key takeaways
- NoSQL families each make one access pattern cheap by giving up something relational databases offer: joins, rigid schemas, or general queries.
- Key-value and wide-column stores require you to know your queries up front and design keys around them.
- Document stores suit self-contained aggregates; embed what you read together, reference what you share.
- Graph databases make multi-hop traversals cheap but are hard to shard.
- Time-series and search engines are specialists, usually alongside a primary database.

## Further reading
- [Amazon DynamoDB Developer Guide: What is DynamoDB?](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)
- [DynamoDB: NoSQL design best practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-general-nosql-design.html)
- [MongoDB: Data modeling](https://www.mongodb.com/docs/manual/data-modeling/)
- [Apache Cassandra: Data modeling](https://cassandra.apache.org/doc/latest/cassandra/developing/data-modeling/index.html)
- [Wikipedia: NoSQL](https://en.wikipedia.org/wiki/NoSQL)
- [Redis: Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Elasticsearch: Near real-time search](https://www.elastic.co/guide/en/elasticsearch/reference/current/near-real-time.html)
