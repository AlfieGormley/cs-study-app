---
id: fund-latency-percentiles
title: Measure percentiles without hiding slow requests
level: basic
minutes: 4
summary: Interpret typical and tail latency, then aggregate and collect measurements correctly across a service.
sourceLesson: fund-latency-throughput
---

A single average can hide the slow experience that matters to users. Percentiles identify positions in the latency distribution, but only if the measurements include the requests and waits you mean to represent.

## Why averages lie: percentiles

Suppose 100 requests take these times: 98 take 10 ms, and 2 take 2,000 ms. The mean adds all durations and divides by the request count. It is 49.8 ms, which describes neither group's experience well.

A **percentile** instead identifies a position after sorting requests from fastest to slowest. Under the nearest-rank convention, p50 picks the 50th request out of these 100 and p99 picks the 99th. Other percentile conventions can interpolate, so state the method when small samples matter.

Applied to our 100 requests:

- Mean: **49.8 ms**
- Median (p50), the 50th value: **10 ms**
- p99, the 99th value: **2,000 ms**

The mean describes no real request. It's five times the typical case and 40 times better than the slow case. That's why we use **percentiles**:

- **p50 (median)**: at least half of requests are at or below this threshold (ties and percentile conventions matter). The "typical" experience.
- **p95, p99**: roughly 95% / 99% of requests are at or below these thresholds. The experience of your unluckiest users.
- **p99.9 and above**: often called the **tail**.

```
 count
  |#
  |##
  |####
  |######
  |########
  |##########__
  |            '''--..___ .  .   .
  +-------------------------------> ms
       p50        p99       p99.9
               <--- the tail --->
```

Latency distributions are almost never normal (bell-shaped). They have a long right tail caused by garbage-collection pauses, cache misses, retransmits, lock contention, noisy neighbours and queueing.

## Measuring percentiles correctly

- **You can't average percentiles.** The mean of 10 servers' p99s is not the fleet's p99. Aggregate raw histograms (e.g. HdrHistogram, Prometheus histograms) and compute percentiles from the combined data.
- **Beware coordinated omission.** A load tester that waits for each response before sending the next under-reports latency when the server stalls, because it stops sending during the stall. `wrk2` corrects for this by recording latency from when each request was scheduled to start, even if its actual transmission is delayed.
- **Measure at the client, too.** Server-side timing misses network and queueing time before your code runs.

## Key takeaways
- The mean, median and tail percentiles describe different parts of the same distribution.
- Combine histograms or observations before calculating a fleet percentile; do not average server percentiles.
- Client timing and tests that account for coordinated omission expose waits a server-only metric may miss.

## Further reading
- [Service Level Objectives (Google SRE)](https://sre.google/sre-book/service-level-objectives/)
- [Histograms and summaries (Prometheus)](https://prometheus.io/docs/practices/histograms/)
- [The Tail at Scale (Dean and Barroso)](https://www.barroso.org/publications/TheTailAtScale.pdf)
- [wrk2: corrected latency measurement](https://github.com/giltene/wrk2)
