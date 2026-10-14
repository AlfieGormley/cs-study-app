---
id: db-time-series-retention-cardinality
title: Time-series retention and cardinality
level: basic
minutes: 2
summary: Model timestamped metrics, choose tags and fields for the deployed engine, and bound retained detail.
sourceLesson: db-nosql-families
---

Metrics are naturally organised by time. Their storage plan needs a retention boundary, an aggregation strategy and metadata choices that fit the specific engine.

## Time-series databases

Metrics, IoT readings and financial ticks share a pattern: append-only writes, ordered by time, queried by time range and aggregated (`avg per minute`). Old data is downsampled or deleted.

- **Examples**: InfluxDB, TimescaleDB (a Postgres extension), Prometheus (for metrics), QuestDB.
- **Tricks**: columnar compression of timestamps (delta-of-delta encoding) and values (Gorilla-style XOR compression), time-partitioned storage so eligible old partitions or files can be removed together, and built-in retention policies and continuous aggregates.

InfluxDB organises data into a *measurement* with *tags* (indexed metadata like `host=web-1`), *fields* (the values) and a timestamp. Each unique combination of tag values is a *series*. In InfluxDB 1.x and 2.x, watch **cardinality**: a tag with millions of distinct values (such as a user id) blows up the series index. InfluxDB 3 uses a different engine and supports high-cardinality tags; choose tags and fields from its version-specific schema guidance rather than carrying the TSM rule over unchanged.

## Bound the older detail

For example, keep fine-grained CPU readings for seven days, then retain one-minute averages with a suitable longer retention period. In the InfluxDB 2.x TSM model, frequently filtered host names suit tags, while the measured CPU percentage is a field. Check the combined series cardinality and available resources, not just one tag in isolation.

## Key takeaways
- Time-series workloads append readings and query or aggregate time ranges.
- Retention and downsampling bound how much old detail is stored.
- InfluxDB tag-cardinality guidance depends on the engine generation.

## Further reading
- [InfluxDB 2: Resolve high series cardinality](https://docs.influxdata.com/influxdb/v2/write-data/best-practices/resolve-high-cardinality/)
- [docs.influxdata.com: schema design](https://docs.influxdata.com/influxdb3/core/write-data/best-practices/schema-design/)
