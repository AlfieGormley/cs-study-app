---
id: fund-estimation-media-bandwidth
title: Estimate media storage and delivery bandwidth
level: intermediate
minutes: 5
summary: Work through a social feed and a video service to separate structured records from large media and egress.
sourceLesson: fund-estimation
---

The preceding record estimate is only part of a media service. Large objects and repeated delivery can dominate the storage and network budget even when the metadata database is modest.

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

Read:write is approximately 50:1. Reads dominate, so caching and precomputed feeds are candidates; freshness, fan-out costs and measured access patterns determine whether they are worthwhile.

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

## Key takeaways
- Photos can dominate storage even when only a small share of posts contain them.
- Estimate media bytes delivered as well as bytes retained, with bits and bytes kept distinct.
- A CDN supports offload, geography and redundancy; assumed NIC rates need workload-specific validation.

## Further reading
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Netflix Open Connect](https://openconnect.netflix.com/en/)
