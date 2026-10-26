---
id: fund-estimation-records-cache
title: Estimate request rates, records and cache memory
level: intermediate
minutes: 3
summary: Separate peak traffic, retained copies and a measured cache hot set before choosing capacity.
sourceLesson: fund-estimation
---

With the units established, use a sequence of explicit assumptions and small calculations. A URL shortener demonstrates why read traffic, stored records and cache memory need separate estimates.

## The method

1. **State assumptions:** active users, actions per user, measured record size, retention and copies.
2. **Separate average from peak traffic.** A daily total hides bursts; choose a peak factor from the actual traffic shape.
3. **Count retained data and copies.** Longer retention and more full replicas both increase storage.
4. **Estimate delivered bytes separately.** Reading an item many times adds delivery traffic without creating new stored records.
5. **Measure the cache hot set.** Count distinct keys needed for the intended hit rate, then include memory overhead.
6. **Check the design implication.** Compare each resource demand with a benchmark of the intended workload.

A useful reference for record storage is:

```formula reference
V = N_day × z × t × r
where
V: raw replicated record storage, in bytes
N_day: new records per day
z: bytes per record
t: retention in days
r: number of full copies
In words: storage grows with the daily number of records, each record's size, how long records are retained and how many copies are kept. Indexes, metadata and free-space headroom add to this raw estimate.
```

## A URL shortener: what matters

Assume **100 million new links a month**, **100 redirects per new link**, roughly **500 bytes per record**, **ten years of retention**, and a **threefold peak factor**. These are exercise inputs.

Using a rounded 2.5 million seconds per month gives about 40 writes/s and 4,000 reads/s on average. The assumed peak gives about 120 writes/s and 12,000 reads/s. Reads dominate, so a cache or read replicas may help; a large lifetime record count does not by itself prove the write path needs sharding.

Ten years gives twelve billion records: about **6 TB for one copy** and **18 TB for three**, before indexes, metadata, backups and headroom. Shorter retention changes that storage budget without necessarily changing today's peak traffic.

For cache memory, suppose access traces identify **80 million distinct hot links**. Their raw payload is about **40 GB** at the assumed record size. Add Redis object/index overhead, replication and spare memory before choosing nodes. Total requests or an assumed 80/20 rule cannot establish the number of distinct keys needed for a desired hit rate.

These rates are candidates for a straightforward database-and-cache design. Benchmark the actual queries, contention and durability settings before choosing capacity. The estimate directs attention to read load, retained data, ID generation and availability; it does not certify that one particular database deployment will suffice.

## Key takeaways
- Calculate average traffic, apply an explicit peak factor, then estimate storage, bandwidth and hot-set memory.
- Retention and replication multiply record storage; cache payload still needs overhead and headroom.
- A hot-set size comes from distinct-key access measurements, not total requests or an assumed 80/20 rule.
- Finish with design implications and a workload-specific capacity check.

## Further reading
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Fermi problem](https://en.wikipedia.org/wiki/Fermi_problem)
