---
id: fund-estimation-records-cache
title: Estimate request rates, records and cache memory
level: intermediate
minutes: 5
summary: Apply a repeatable method to a URL shortener, separating peak traffic, retained copies and a measured hot set.
sourceLesson: fund-estimation
---

With the units established, use a sequence of explicit assumptions and small calculations. A URL shortener demonstrates why read traffic, stored records and cache memory need separate estimates.

## The method

1. **State assumptions explicitly.** DAU, actions per user, object sizes, read:write ratio, retention.
2. **Compute average rates**, then **peak** (multiply by 2–10x depending on traffic shape).
3. **Compute storage**: items/day × size × retention × replication factor.
4. **Compute bandwidth**: QPS × response size.
5. **Compute memory** for caches: hot set size.
6. **Sanity-check** against known capacities, and say what the numbers imply for the design.

Round aggressively: 86,400 becomes 100,000; 365 becomes 400 (or 300 if you prefer to undershoot). Keep track of which way you rounded.

Steps 2 and 3 are two small formulas you'll use in every estimate:

```formula
Q_avg = N_day / 86,400 s
Q_peak = Q_avg × f
V = N_day × z × t × r
where
Q_avg: the average queries per second (QPS), in requests per second
N_day: the number of actions (requests, uploads, writes) per day
s: second; 86,400 s is one day
Q_peak: the peak QPS the system must handle
f: the peak factor, how many times busier the busiest period is than the average; 2 to 10 is an illustrative range, to be replaced with measured traffic
V: the total storage needed, in bytes (B)
z: the size of one item, in bytes
t: the retention period, in days you keep the data
r: the replication factor, how many copies you store (often 3)
In words: average rate is daily count over seconds in a day, peak is that times a burst factor, and storage is items per day times item size times days kept times copies.
```

## Worked example 1: a URL shortener

**Assumptions**

- 100 M new links per month.
- Read:write ratio 100:1.
- Each record ~500 bytes (short code, long URL, owner, timestamps).
- Keep links for 10 years.

**Write QPS**

```formula
Q_w = 100 M / 2.5 M s ≈ 40 /s
Q_{w,peak} = 40 /s × 3 ≈ 120 /s
where
Q_w: average writes (new links) per second
Q_{w,peak}: peak writes per second, assuming peak is 3 times the average
M: million; 100 M links are created in one month of about 2.5 M seconds
s: second
In words: 100 million links spread over the 2.5 million seconds of a month is about 40 a second, 120 at peak.
```

**Read QPS**

```formula
Q_r = 40 /s × 100 = 4,000 /s
Q_{r,peak} = 4,000 /s × 3 = 12,000 /s
where
Q_r: average reads (redirects) per second
Q_{r,peak}: peak reads per second, again 3 times the average
100: the read-to-write ratio: 100 redirects for every link created
s: second
In words: a hundred reads for every write turns 40 writes a second into 4,000 reads a second, 12,000 at peak.
```

**Storage**

```formula
n = 100 M × 12 × 10 = 12 × 10^9
V = 12 × 10^9 × 500 B = 6 TB
V_3 = 6 TB × 3 = 18 TB
where
n: the number of links kept (12 billion): 100 million a month, 12 months a year, for 10 years
M: million
B: byte, the unit of record size; 500 B is 500 bytes
V: storage for one copy of every record, at 500 bytes each
V_3: storage with 3 replicas
TB: terabyte, 10^12 bytes
In words: twelve billion records of 500 bytes is six terabytes, eighteen with three copies.
```

Write large counts as powers of ten when they appear beside sizes, so the symbol B consistently means bytes.

**Cache memory.** Suppose access traces suggest a hot set of 80 million distinct links. At 500 B per record, its raw payload is:

```formula
V_hot = 80 M × 500 B = 40 GB
where
V_hot: the memory needed to hold the hot set's records, before any overhead
M: million; 80 M is the number of distinct links in the hot set
B: bytes; each record is about 500 bytes
GB: gigabyte, 10^9 bytes
In words: 80 million records of 500 bytes each need about 40 gigabytes.
```

Add Redis object/index overhead, replication and headroom before choosing nodes. Neither 400 million daily requests nor an 80/20 traffic rule establishes this hot-set size; measure distinct keys at the desired hit rate.

**What this tells us:** these assumed rates are candidates for a straightforward database-and-cache design, but capacity must be measured with the actual queries and durability settings. 6 TB is large but manageable; one big Postgres instance could hold it, and a key-value store like DynamoDB would too. The hard parts are ID generation and availability, not raw scale.

## Key takeaways
- Calculate average traffic, apply an explicit peak factor, then estimate storage, bandwidth and hot-set memory.
- Retention and replication multiply record storage; cache payload still needs overhead and headroom.
- A hot-set size comes from distinct-key access measurements, not total requests or an assumed 80/20 rule.
- Finish with design implications and a workload-specific capacity check.

## Further reading
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Fermi problem](https://en.wikipedia.org/wiki/Fermi_problem)
