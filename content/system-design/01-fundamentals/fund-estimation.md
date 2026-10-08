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

### Powers of ten

Estimates juggle very large numbers, so they are written as powers of ten: 10^3 means 10 × 10 × 10 = 1,000, i.e. a 1 followed by three zeros. Multiplying powers of ten adds the exponents (10^3 × 10^6 = 10^9); dividing subtracts them (10^9 / 10^5 = 10^4). That turns most estimation arithmetic into counting zeros.

```formula
10^3 = 10 × 10 × 10 = 1,000
10^6 = 1,000,000
10^a × 10^b = 10^{a + b}
10^a / 10^b = 10^{a − b}
where
10^3, 10^6: ten to the power 3 and ten to the power 6: ten multiplied by itself that many times, which is a 1 followed by that many zeros
^: "to the power of"; the small raised number (the exponent) counts the tens multiplied together
a, b: any two exponents
In words: a power of ten is a 1 followed by that many zeros; multiplying adds the zeros, dividing takes them away.
```

### Time

```formula
1 day = 86,400 s ≈ 10^5 s
1 month ≈ 2.6 M s ≈ 2.5 × 10^6 s
1 year ≈ 31.5 M s ≈ 3 × 10^7 s
where
day: 24 hours = 24 × 60 × 60 = 86,400 seconds
month: an average month, a twelfth of a 365.25-day year, about 30.4 days
year: 365.25 days
s: second
M: million (10^6)
≈: approximately equal to; rounded to keep the arithmetic easy
In words: a day is about a hundred thousand seconds, a month about two and a half million, and a year about thirty million.
```

A handy shortcut follows: divide a daily count by 86,400 to get an average rate per second.

| Per day | Per second (avg) |
|---|---|
| 1 million | ~12 |
| 10 million | ~120 |
| 100 million | ~1,200 |
| 1 billion | ~12,000 |

### Size

| Unit | Bytes | In words |
|---|---|---|
| KB (kilobyte) | 1,000 | thousand |
| MB (megabyte) | 1,000,000 | million |
| GB (gigabyte) | 10 to the power 9 | billion |
| TB (terabyte) | 10 to the power 12 | trillion |
| PB (petabyte) | 10 to the power 15 | quadrillion |

Each step up the table is 1,000 times bigger. (Using powers of 10 rather than powers of 2 introduces an error of about 2% at KB, growing to about 13% at PB: a binary kilobyte is 1,024 bytes, 2.4% more than 1,000. That's fine for estimates. Strictly, the binary units are KiB, MiB, GiB and so on.)

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

Network speeds are quoted in bits per second; storage and file sizes in bytes. A byte is 8 bits, so:

```formula
R_B = R_b / 8
1 Gbps / 8 = 125 MB/s
10 Gbps / 8 = 1.25 GB/s
where
R_B: the rate in bytes per second
R_b: the rate in bits per second
Gbps: gigabits per second, 10^9 bits per second
MB/s: megabytes per second, 10^6 bytes per second
GB/s: gigabytes per second, 10^9 bytes per second
MB: megabyte, 1,000,000 bytes
GB: gigabyte, 10^9 bytes
s: second
In words: divide a network speed in bits by 8 to get bytes per second.
```

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
f: the peak factor, how many times busier the busiest period is than the average, typically 2 to 10
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
n = 100 M × 12 × 10 = 12 B
V = 12 B × 500 B = 6 TB
V_3 = 6 TB × 3 = 18 TB
where
n: the number of links kept (12 billion): 100 million a month, 12 months a year, for 10 years
M: million
B: as a count, billion (12 B = 12,000,000,000); after a number used as a size, bytes (500 B = 500 bytes)
V: storage for one copy of every record, at 500 bytes each
V_3: storage with 3 replicas
TB: terabyte, 10^12 bytes
In words: twelve billion records of 500 bytes is six terabytes, eighteen with three copies.
```

(Estimators often write "B" for both billion and bytes; the number in front tells you which.)

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

## Worked example 2: a social feed

**Assumptions**

- 200 M daily active users.
- Each posts 2 times/day; each views 100 posts/day.
- 10% of posts contain a photo, ~500 KB after compression.
- Text post + metadata ~1 KB.

**Write QPS**

```formula
N_w = 200 M × 2 = 400 M
Q_w = 400 M / 10^5 s = 4,000 /s
Q_{w,peak} = 4,000 /s × 3 = 12,000 /s
where
N_w: posts written per day (400 million): 200 million users posting twice each
M: million
Q_w: average posts per second, using 1 day ≈ 10^5 s (100,000 seconds)
Q_{w,peak}: peak posts per second, assuming 3 times the average
10^5: 100,000, the rounded number of seconds in a day
s: second
In words: 400 million posts a day is about 4,000 a second on average and 12,000 at peak.
```

**Read QPS**

```formula
N_r = 200 M × 100 = 20 B
Q_r = 20 B / 10^5 s = 200,000 /s
Q_{r,peak} ≈ 600,000 /s
where
N_r: post views per day (20 billion): 200 million users viewing 100 posts each
M: million
B: billion (10^9)
Q_r: average post views per second
Q_{r,peak}: peak views per second, 3 times the average
10^5: 100,000, the rounded number of seconds in a day
s: second
≈: approximately equal to
In words: 20 billion views a day is about 200,000 a second on average and 600,000 at peak.
```

Read:write ≈ 50:1. Reads dominate, so precomputed feeds and heavy caching are justified.

**Storage per day**

```formula
V_text = 400 M × 1 KB = 400 GB
V_media = 40 M × 500 KB = 20 TB
where
V_text: text stored per day: 400 million posts of about 1 KB each
V_media: photos stored per day: 10% of posts (40 million) carry a 500 KB photo
M: million
KB: kilobyte, 1,000 bytes
GB: gigabyte, 10^9 bytes
TB: terabyte, 10^12 bytes
In words: the text adds 400 gigabytes a day, the photos 20 terabytes, fifty times as much.
```

**Per year**

```formula
V_{text,yr} = 400 GB × 365 ≈ 150 TB
V_{media,yr} = 20 TB × 365 ≈ 7.3 PB
where
V_{text,yr}: text stored per year (one copy)
V_{media,yr}: photos stored per year (one copy)
GB: gigabyte, 10^9 bytes
TB: terabyte, 10^12 bytes
PB: petabyte, 10^15 bytes
≈: approximately equal to (rounded)
In words: a year of text is about 150 terabytes, a year of photos about 7.3 petabytes.
```

Media is ~98% of storage, and belongs in object storage (S3-style) behind a CDN, not in the database.

**Egress bandwidth for media.** Suppose 10% of the 20 B (billion) views show a photo:

```formula
V_out = 2 B × 500 KB = 1 PB
R = 1 PB / 10^5 s = 10 GB/s
R ≈ 10 GB/s × 8 = 80 Gbps
where
V_out: bytes sent to users per day: 2 billion photo views of 500 KB
B: billion (10^9)
KB: kilobyte, 1,000 bytes
PB: petabyte, 10^15 bytes
R: the average outgoing (egress) bandwidth
10^5: 100,000, the rounded number of seconds in a day
s: second
GB/s: gigabytes per second
Gbps: gigabits per second; multiply bytes by 8 to get bits
≈: approximately equal to
In words: a petabyte a day is about 10 gigabytes every second, which is 80 gigabits per second.
```

That is substantial sustained egress. It motivates a CDN for geographic reach, redundancy and offload, but does not prove that one server cannot supply the bandwidth; NIC and storage capacity vary.

> [!tip] Say what the numbers mean
> Estimation is only useful if it changes the design. "At 200k reads/s, benchmark the access pattern and consider caching or replicas if one database cannot meet the target" is the sentence that earns credit, not the arithmetic itself.

## Worked example 3: video streaming bandwidth

**Assumptions:** 1 M concurrent viewers at peak, 5 Mbps average bitrate.

```formula
R = 1 M × 5 Mbps = 5 Tbps
R = 5 Tbps / 8 = 625 GB/s
where
R: the total streaming bandwidth at peak
M: million; 1 M is the number of viewers watching at once
Mbps: megabits per second, 10^6 bits per second; each stream averages 5 Mbps
Tbps: terabits per second, 10^12 bits per second
GB/s: gigabytes per second; dividing bits by 8 gives bytes
In words: a million viewers at 5 megabits each need 5 terabits a second, or 625 gigabytes a second.
```

Assuming ~40 Gbps of useful throughput per edge server, you'd need around 125 servers' worth of egress, in practice several times that, spread across many locations for redundancy and proximity. This is why Netflix places its Open Connect appliances inside ISPs' networks.

## Worked example 4: servers needed

**Assumptions:** 50,000 req/s peak, each request uses ~20 ms of CPU, servers have 16 cores, target 60% utilisation.

```formula
C = Q × t_cpu
C = 50,000 /s × 0.020 s = 1,000
c_use = 16 × 0.6 = 9.6
n_s = C / c_use = 1,000 / 9.6 ≈ 105
where
C: the number of CPU cores kept busy on average (CPU-seconds of work arriving per second)
Q: requests per second at peak, 50,000
t_cpu: CPU time each request uses, 20 ms = 0.020 s
s: second
c_use: usable cores per server: 16 cores, of which we plan to use 60%
n_s: the number of servers needed
≈: approximately equal to (rounded up)
In words: work arriving per second divided by the work one server can comfortably do per second gives the number of servers. This is Little's law again: busy cores = arrival rate × CPU time per request.
```

Add N+2 or zone redundancy: if you run across 3 zones and must survive losing one, the two surviving zones must carry the whole load, so each zone needs half of the 105 servers' worth (about 53). Provision 3 × 53 ≈ 160 servers.

## Common pitfalls

- **Bits vs bytes.** Network speeds are in bits; storage is in bytes. 1 Gbps = 125 MB/s, not 1 GB/s.
- **Forgetting peaks.** Average QPS sizes nothing; capacity must handle the peak.
- **Forgetting concurrency.** For connections and sessions, use Little's law: the number connected at once is the arrival rate multiplied by the time each stays online. 50 M DAU online 30 minutes a day is about 1 M connected at once on average (50 M × 30 / 1,440 minutes in a day), not 50 M.
- **Forgetting replication and overhead.** Three replicas triple storage; index and metadata overhead depends on the schema and storage engine; state an explicit allowance or measure it.
- **Forgetting growth.** Plan for at least the next 1–2 years.
- **False precision.** "4,629.6 QPS" signals you've missed the point. Say "about 5k".

> [!warning] Check your units at every step
> Write the unit next to every number. Most estimation errors are unit errors, not arithmetic errors.

## Key takeaways
- Aim for the right order of magnitude; round aggressively and state assumptions.
- Memorise: 1 day ≈ 100,000 s; 1 M/day ≈ 12/s; 1 Gbps = 125 MB/s.
- Average QPS is daily actions divided by about 100,000 seconds; multiply for peak. Storage is items × size × retention × replicas.
- Separate small structured data (database) from large blobs (object storage + CDN); blobs usually dominate storage and bandwidth.
- Use Little's law and CPU-time per request to size fleets, and add redundancy for zone failure.
- Always finish by saying what the numbers imply for the design.

## Further reading
- [The System Design Primer (GitHub)](https://github.com/donnemartin/system-design-primer)
- [Back-of-the-envelope calculation (Wikipedia)](https://en.wikipedia.org/wiki/Back-of-the-envelope_calculation)
- [Fermi problem (Wikipedia)](https://en.wikipedia.org/wiki/Fermi_problem)
- [Latency numbers every programmer should know (gist)](https://gist.github.com/jboner/2841832)
