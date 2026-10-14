---
id: fund-latency-orders-magnitude
title: Compare latency orders of magnitude carefully
level: basic
minutes: 3
summary: Use explicitly hypothetical timing inputs to reason about memory, storage and distance without treating them as benchmarks.
sourceLesson: fund-latency-throughput
---

An estimate should distinguish nanoseconds, microseconds and milliseconds before it chooses an architecture. These examples practise that comparison while keeping their measurement limits explicit.

## Latency numbers every programmer should know

The table below supplies illustrative assumptions for practising unit conversions and comparing orders of magnitude. These are not verified contemporary measurements, and the ratios also vary by hardware and workload.

> [!note] Content gap: latency measurements
> No reproducible hardware/workload record supports this mixed historical latency table. Its values are retained only as hypothetical exercise inputs; benchmark your system before using them for design.

| Operation | Hypothetical exercise time |
|---|---|
| L1 cache reference | 1 ns |
| Branch mispredict | 3–5 ns |
| L2 cache reference | 4–7 ns |
| Mutex lock/unlock | 20 ns |
| Main memory reference | 100 ns |
| Compress 1 KB (Snappy) | 2 µs |
| Send 1 KB over 10 Gbps | 1 µs |
| Random 4 KB SSD read | 20–150 µs |
| Round trip, same datacentre | 0.5 ms |
| Read 1 MB sequentially, SSD | 0.2–1 ms |
| HDD seek | 10 ms |
| Read 1 MB sequentially, HDD | 5–20 ms |
| Round trip, same region (AZs) | 1–2 ms |
| Round trip, London–New York | ~70 ms |
| Round trip, CA–Netherlands–CA | 150 ms |

### What to take away

- Using a 100 µs SSD read from the exercise range, memory is **1,000x faster than SSD** in this comparison, and the assumed in-datacentre round trip costs about as much as several such SSD reads. That's why Redis (in memory, one network hop) is so popular as a cache.
- A **disk seek** costs as much as millions of CPU instructions. Sequential I/O is vastly faster than random I/O, which is why log-structured designs like Kafka and LSM-tree databases are fast at writes.
- **Cross-region round trips are tens to hundreds of milliseconds.** Any design that requires a synchronous cross-region round trip on every write (e.g. synchronous geo-replication) pays this on every request.
- **Chatty protocols are deadly over distance.** 20 sequential calls at 70 ms each = 1.4 s.

## Bulk transfer

> [!example] A lorry full of hard drives
> A lorry carrying 1,000 × 20 TB drives (20 PB) on a 10-hour (36,000-second) drive has enormous throughput: 20 PB delivered in 36,000 s is about 556 GB every second. Its latency is terrible: 10 hours for the first byte. AWS offered exactly this for years: Snowmobile, a lorry-sized container holding up to 100 PB, since retired. Smaller physical-transfer devices use the same principle. AWS stopped accepting new Snowball Edge customers on 7 November 2025 and has announced the end of support for Snowball devices in its commercial Regions on 31 December 2026; check current service availability before choosing a product.

## Key takeaways
- The table supplies exercise assumptions; it is not a reproducible current benchmark.
- Convert timings to the same unit before comparing orders of magnitude.
- Distance and repeated synchronous round trips can dominate designs; validate hardware-specific costs by measuring.

## Further reading
- [Historical latency numbers](https://gist.github.com/jboner/2841832)
- [Interactive historical latency numbers](https://colin-scott.github.io/personal_website/research/interactive_latency.html)
- [Service Level Objectives (Google SRE)](https://sre.google/sre-book/service-level-objectives/)
- [AWS Snowball Edge guide](https://docs.aws.amazon.com/snowball/latest/developer-guide/)
- [AWS Snowball service availability](https://aws.amazon.com/snowball/)
- [AWS Snow device updates](https://aws.amazon.com/blogs/storage/aws-snow-device-updates/)
