---
id: db-wide-column-query-buckets
title: Wide-column keys and time buckets
level: basic
minutes: 3
summary: Shape Cassandra partitions and clustering columns around a known query without growing one partition forever.
sourceLesson: db-nosql-families
---

A wide-column schema begins with the query you need to answer. Follow the partition key to the owning data, then use clustering order to select a bounded range.

## Wide-column stores

Wide-column stores group related cells into rows and column families, but their partitioning differs. Cassandra and ScyllaDB hash a **partition key** and order rows within that partition by **clustering columns**. HBase and Google Bigtable instead range-partition lexicographically ordered row keys; the Cassandra CQL example below does not describe their key layout.

```sql
-- Cassandra CQL: run in an existing
-- keyspace.
-- Route one sensor-day to its partition.
CREATE TABLE readings (
  sensor_id  text,
  day        date,
  ts         timestamp,
  value      double,
  PRIMARY KEY ((sensor_id, day), ts)
-- Newest timestamps first within the key.
) WITH CLUSTERING ORDER BY (ts DESC);
```

Here `(sensor_id, day)` is the partition key, and `ts` sorts rows within it. "Latest 100 readings for sensor X today" is a partition-targeted ordered query; multiple SSTables, replicas or storage reads may still be involved.

- **Cheap**: huge write throughput (they're built on LSM trees, covered in the indexing lesson), horizontal growth when key distribution and workload permit it, multi-datacentre replication.
- **Expensive**: queries that don't start with the partition key. No joins. You typically make one table *per query*, duplicating data across them.

That's why the example puts `day` in the partition key. Keyed by `sensor_id` alone, a sensor reporting every second would add 86,400 rows a day to one partition, and that partition would never stop growing.

With `day` in the partition key, each partition holds at most one day of one sensor's readings and then stops growing. Huge partitions overload the replicas that own them and slow compaction and repair, so choose time buckets using measured serialized size, tombstones and query/repair behavior; a fixed size target is a rule of thumb, not a universal limit.

> [!analogy] Real-world analogy: one folder per sensor per day
> Picture a filing room where each sensor gets one folder per day, and the pages inside are kept in time order, newest first. To read "sensor X today", you fetch one folder and read from the front.
>
> **How it maps:** The folder label is the partition key `(sensor_id, day)`, which decides where the data lives, and the page order inside is the clustering column `ts`. Starting a new folder each day is the time bucket that stops any one partition growing for ever.
>
> **Where it stops:** The folders are spread across machines by hashing their labels and copied to several replicas, so there is no shelf order between folders. A question that does not name the folder, such as "every reading above 50 last week", means opening every folder in the cluster.

## Key takeaways
- Cassandra hashes partition keys and orders rows within them by clustering columns.
- A day in the partition key bounds each sensor partition to one day of readings.
- Queries without a usable partition key can require expensive filtering across the cluster.

## Further reading
- [Apache Cassandra: Data modeling](https://cassandra.apache.org/doc/latest/cassandra/developing/data-modeling/index.html)
