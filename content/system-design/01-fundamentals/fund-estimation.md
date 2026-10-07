---
id: fund-estimation
title: Back-of-the-envelope estimation
level: intermediate
minutes: 13
summary: Turn users and behaviours into QPS, storage, bandwidth and memory figures in minutes, with full worked examples you can reuse.
---

Back-of-the-envelope estimation is quick, approximate arithmetic that tells you **which order of magnitude** you're dealing with. Is this one database or a hundred? Gigabytes or petabytes? One server or a fleet?

The goal is not precision. Being within a factor of 2–3 is fine. Being off by 1,000x because you confused MB with GB is not.

## Numbers to memorise

### Time

```
1 day   = 86,400 s   ≈ 10^5 s
1 month ≈ 2.6 M s    ≈ 2.5 x 10^6 s
1 year  ≈ 31.5 M s   ≈ 3 x 10^7 s
```

A handy shortcut that follows:

| Per day | Per second (avg) |
|---|---|
| 1 million | ~12 |
| 10 million | ~120 |
| 100 million | ~1,200 |
| 1 billion | ~12,000 |

### Size

| Power | Name | Bytes |
|---|---|---|
| 10^3 | KB | thousand |
| 10^6 | MB | million |
| 10^9 | GB | billion |
| 10^12 | TB | trillion |
| 10^15 | PB | quadrillion |

(Using powers of 10 rather than powers of 2 introduces an error of about 2% at KB, growing to about 13% at PB. That's fine for estimates. Strictly, the binary units are KiB, MiB, GiB and so on.)

### Illustrative object-size assumptions

These are exercise inputs, not measured universal sizes. Content gap: no representative dataset is provided for a reliable generic object-size table; measure your own serialized records and media.

| Item | Assumed size |
|---|---|
| ID / timestamp | 8 bytes |
| Short text post + metadata | 300 B – 1 KB |
| User profile row | 1 KB |
| Compressed photo | 200 KB – 2 MB |
| 1 minute of HD video | ~40–100 MB |

### Bandwidth

```
1 Gbps  = 125 MB/s
10 Gbps = 1.25 GB/s
bits -> bytes: divide by 8
```

## The method

1. **State assumptions explicitly.** DAU, actions per user, object sizes, read:write ratio, retention.
2. **Compute average rates**, then **peak** (multiply by 2–10x depending on traffic shape).
3. **Compute storage**: items/day × size × retention × replication factor.
4. **Compute bandwidth**: QPS × response size.
5. **Compute memory** for caches: hot set size.
6. **Sanity-check** against known capacities, and say what the numbers imply for the design.

Round aggressively: 86,400 becomes 100,000; 365 becomes 400 (or 300 if you prefer to undershoot). Keep track of which way you rounded.

## Worked example 1: a URL shortener

**Assumptions**

- 100 M new links per month.
- Read:write ratio 100:1.
- Each record ~500 bytes (short code, long URL, owner, timestamps).
- Keep links for 10 years.

**Write QPS**

```
100M / month / 2.5M s ≈ 40 writes/s
peak (x3)            ≈ 120 writes/s
```

**Read QPS**

```
40 x 100 = 4,000 redirects/s avg
peak (x3) ≈ 12,000 redirects/s
```

**Storage**

```
100M x 12 months x 10 years = 12 B links
12B x 500 B = 6 TB
x3 replication = 18 TB
```

**Cache memory.** Suppose access traces suggest a hot set of 80 million distinct links. At 500 B per record, its raw payload is:

```
80M distinct links x 500 B = 40 GB
```

Add Redis object/index overhead, replication and headroom before choosing nodes. Neither 400 million daily requests nor an 80/20 traffic rule establishes this hot-set size; measure distinct keys at the desired hit rate.

**What this tells us:** these assumed rates are candidates for a straightforward database-and-cache design, but capacity must be measured with the actual queries and durability settings. 6 TB is large but manageable; one big Postgres instance could hold it, and a key-value store like DynamoDB would too. The hard parts are ID generation and availability, not raw scale.

## Worked example 2: a social feed

**Assumptions**

- 200 M daily active users.
- Each posts 2 times/day; each views 100 posts/day.
- 10% of posts contain a photo, ~500 KB after compression.
- Text post + metadata ~1 KB.

**Write QPS**

```
200M x 2 = 400M posts/day
400M / 10^5 = 4,000 posts/s avg
peak (x3) = 12,000 posts/s
```

**Read QPS**

```
200M x 100 = 20B post views/day
20B / 10^5 = 200,000 reads/s avg
peak ≈ 600,000 reads/s
```

Read:write ≈ 50:1. Reads dominate, so precomputed feeds and heavy caching are justified.

**Storage per day**

```
text:  400M x 1 KB          = 400 GB/day
media: 40M x 500 KB         = 20 TB/day
```

**Per year**

```
text:  400 GB x 365 ≈ 150 TB
media: 20 TB x 365  ≈ 7.3 PB
```

Media is ~98% of storage, and belongs in object storage (S3-style) behind a CDN, not in the database.

**Egress bandwidth for media.** Suppose 10% of the 20 B views show a photo:

```
2B x 500 KB = 1 PB/day
1 PB / 10^5 s = 10 GB/s ≈ 80 Gbps avg
```

That is substantial sustained egress. It motivates a CDN for geographic reach, redundancy and offload, but does not prove that one server cannot supply the bandwidth; NIC and storage capacity vary.

> [!tip] Say what the numbers mean
> Estimation is only useful if it changes the design. "At 200k reads/s, benchmark the access pattern and consider caching or replicas if one database cannot meet the target" is the sentence that earns credit, not the arithmetic itself.

## Worked example 3: video streaming bandwidth

**Assumptions:** 1 M concurrent viewers at peak, 5 Mbps average bitrate.

```
1M x 5 Mbps = 5 Tbps
5 Tbps / 8 = 625 GB/s
```

Assuming ~40 Gbps of useful throughput per edge server, you'd need around 125 servers' worth of egress, in practice several times that, spread across many locations for redundancy and proximity. This is why Netflix places its Open Connect appliances inside ISPs' networks.

## Worked example 4: servers needed

**Assumptions:** 50,000 req/s peak, each request uses ~20 ms of CPU, servers have 16 cores, target 60% utilisation.

```
CPU-seconds per second = 50,000 x 0.020
                       = 1,000 cores busy
usable cores/server    = 16 x 0.6 = 9.6
servers                = 1,000 / 9.6 ≈ 105
```

Add N+2 or zone redundancy: if you run across 3 zones and must survive losing one, each zone needs half the load, so provision 3 × 53 ≈ 160 servers.

## Common pitfalls

- **Bits vs bytes.** Network speeds are in bits; storage is in bytes. 1 Gbps = 125 MB/s, not 1 GB/s.
- **Forgetting peaks.** Average QPS sizes nothing; capacity must handle the peak.
- **Forgetting concurrency.** For connections and sessions, use Little's law: concurrent users = arrival rate × time online. 50 M DAU online 30 minutes a day is about 1 M connected at once on average, not 50 M.
- **Forgetting replication and overhead.** Three replicas triple storage; index and metadata overhead depends on the schema and storage engine; state an explicit allowance or measure it.
- **Forgetting growth.** Plan for at least the next 1–2 years.
- **False precision.** "4,629.6 QPS" signals you've missed the point. Say "about 5k".

> [!warning] Check your units at every step
> Write the unit next to every number. Most estimation errors are unit errors, not arithmetic errors.

## Key takeaways
- Aim for the right order of magnitude; round aggressively and state assumptions.
- Memorise: 1 day ≈ 10^5 s; 1 M/day ≈ 12/s; 1 Gbps = 125 MB/s.
- QPS = daily actions / 10^5, then multiply for peak. Storage = items × size × retention × replicas.
- Separate small structured data (database) from large blobs (object storage + CDN); blobs usually dominate storage and bandwidth.
- Use Little's law and CPU-time per request to size fleets, and add redundancy for zone failure.
- Always finish by saying what the numbers imply for the design.

## Further reading
- [The System Design Primer (GitHub)](https://github.com/donnemartin/system-design-primer)
- [Back-of-the-envelope calculation (Wikipedia)](https://en.wikipedia.org/wiki/Back-of-the-envelope_calculation)
- [Fermi problem (Wikipedia)](https://en.wikipedia.org/wiki/Fermi_problem)
- [Latency numbers every programmer should know (gist)](https://gist.github.com/jboner/2841832)
