---
id: fund-latency-throughput
title: Latency, throughput and percentiles
level: basic
minutes: 13
summary: How long one request takes versus how many you can handle, why p99 matters more than the average, and the latency numbers every engineer should know.
---

Two numbers describe the performance of almost any system:

- **Latency**: how long a single operation takes, from request to response. Measured in time (ms, µs).
- **Throughput**: how many operations complete per unit time. Measured in requests/s, MB/s, messages/s.

They are related but not the same thing, and confusing them leads to bad designs.

## The pipe analogy

Think of a water pipe. Latency is how long a drop takes to travel from one end to the other. Throughput is how much water comes out per second.

```
 latency = length of pipe
 throughput = width of pipe

 in  ==============================  out
     <---------- 100 ms ---------->
         carries 1,000 req/s
```

You can increase throughput by adding more pipes in parallel (more servers) without changing latency at all. And a London–New York round trip will take around 70 ms no matter how many servers you add, because distance sets a floor on latency. The time a signal needs just to travel a distance is:

```formula
t = d / v
t = 5,570 km / 200,000 km/s
t ≈ 0.028 s = 28 ms
where
t: the one-way propagation delay, the time the signal spends travelling, in seconds (s) or milliseconds (ms)
d: the distance travelled, in kilometres (km); here 5,570 km, the great-circle (shortest over the globe) distance from London to New York
v: the speed of light in optical fibre, about 200,000 km/s, roughly two-thirds of its 300,000 km/s speed in a vacuum
km: kilometre, 1,000 metres
s: second
ms: millisecond, one thousandth of a second
≈: approximately equal to (the result is rounded)
In words: the further the signal travels, the longer it takes, and nothing but a shorter path or faster medium can change that. London to New York costs at least 28 ms each way.
```

So a round trip (there and back) costs at least 2 × 28 = 56 ms before any processing. Real cable routes are longer than the great circle and pass through routers, which is why about 70 ms is typical. Adding servers changes none of this.

> [!example] A lorry full of hard drives
> A lorry carrying 1,000 × 20 TB drives (20 PB) on a 10-hour (36,000-second) drive has enormous throughput: 20 PB delivered in 36,000 s is about 556 GB every second. Its latency is terrible: 10 hours for the first byte. AWS offered exactly this for years: Snowmobile, a lorry-sized container holding up to 100 PB, since retired. Smaller physical-transfer devices use the same principle. AWS stopped accepting new Snowball Edge customers on 7 November 2025 and has announced the end of support for Snowball devices in its commercial Regions on 31 December 2026; check current service availability before choosing a product.

## How they interact: queueing

Latency and throughput meet through **queueing**. When requests arrive faster than a server can process them, they wait. Waiting time is latency.

The simplest model of this is the **M/M/1 queue**: requests arrive at random (the first M), each takes a random amount of work to serve (the second M; "M" stands for Markovian, a particular kind of randomness), and there is 1 server handling one request at a time. For that model, queueing theory gives the average time a request spends in the system, waiting plus being served:

```formula
ρ = λ / μ
W = S / (1 − ρ)
where
W: the average time a request spends in the system (queueing plus being served), in milliseconds (ms); this is the latency the client sees
S: the average service time, the time the server spends actually working on one request when there is no queue, in ms
ρ: rho, the utilisation: the fraction of time the server is busy, from 0 (idle) to just under 1 (always busy)
λ: lambda, the arrival rate, in requests per second (req/s)
μ: mu, the service rate (capacity), the most requests per second the server can complete, equal to 1 / S with S in seconds (a 10 ms service time gives 100 req/s)
ms: millisecond, one thousandth of a second
In words: latency is the service time divided by the fraction of time the server is idle. As the server gets busier, that idle fraction shrinks towards zero, so latency grows without limit.
```

Example: a server with a 10 ms service time at 80% utilisation has an average time in the system of 10 / (1 − 0.8) = 10 / 0.2 = 50 ms, five times the service time. The table shows the same ratio at other loads:

| Utilisation | Latency vs service time |
|---|---|
| 50% | 2x |
| 80% | 5x |
| 90% | 10x |
| 99% | 100x |

This is why systems "fall off a cliff". At 50% load everything looks fine; at 90% latency has quintupled compared with 50%; as utilisation approaches 100% from below, the M/M/1 steady-state mean queue length diverges; at or above 100% the infinite-buffer model has no stable steady state. It's also why capacity planning typically targets 50–70% peak utilisation, leaving headroom.

Real servers aren't exactly M/M/1 (they have many workers, and service times vary differently), and the exact curve depends on arrival/service variability, scheduling and queue limits. Many real systems develop large queues near saturation; a deterministic or admission-controlled system need not follow this curve.

### Little's law: how many requests are in flight

One more relationship ties the two metrics together. It holds for any stable system (one where requests don't pile up forever), averaged over time, whatever the pattern of arrivals:

```formula
L = λ × W
L = 2,000 /s × 0.05 s = 100
where
L: the average number of requests in flight (in the system at once), the concurrency; a plain count with no unit
λ: lambda, the throughput, the average rate at which requests arrive (and leave), in requests per second (/s)
W: the average time each request spends in the system, its latency, in seconds (s); here 50 ms = 0.05 s
s: second
ms: millisecond, one thousandth of a second
In words: requests in flight equal how fast they arrive multiplied by how long each one stays.
```

So a service doing 2,000 req/s at 50 ms average latency has **100 requests in flight on average**. Convert milliseconds to seconds first, or the answer is out by a factor of 1,000. If latency rises tenfold at the same throughput, so does the number in flight, which is why a slow dependency can exhaust every thread you have. The scalability lesson uses this law to size thread and connection pools.

### Bandwidth-bound or latency-bound?

The pipe analogy gives a simple model for how long one transfer takes: a fixed cost for each round trip, plus the time to push the bytes through the pipe.

```formula
T ≈ k × RTT + D / B
where
T: the total time for the transfer or exchange, in seconds (s)
k: the number of round trips that must happen one after another (each waits for the previous reply)
RTT: round-trip time, the time for a message to go to the other end and a reply to come back, in s
D: the amount of data to send, in bits (multiply bytes by 8)
B: the bandwidth of the link, in bits per second (bps)
≈: approximately equal to; the model ignores processing time and protocol overhead
In words: time is the round trips paid one after another plus the data divided by how fast the pipe carries it.
```

Example: fetching a 1 MB file (8,000,000 bits) in one round trip over a 100 Mbps link with a 70 ms RTT takes about 70 ms + 8,000,000 / 100,000,000 s = 70 ms + 80 ms = 150 ms. Both terms matter here; in the two extreme cases below, one term swamps the other.

Big transfers are **bandwidth-bound**: the size term dominates, so a fatter pipe or compression helps. Many small, sequential exchanges are **latency-bound**: the round-trip term dominates, so bandwidth upgrades do nothing and you must cut round trips (batching, parallelism, moving closer).

> [!warning] Throughput limits show up as latency
> Users rarely see "throughput exceeded". They see slow pages and timeouts, because the queue in front of the bottleneck is growing.

## Why averages lie: percentiles

Suppose 100 requests take these times: 98 of them take 10 ms, and 2 take 2,000 ms. The mean (the ordinary average) adds up every time and divides by the count:

```formula
t_mean = (98 × 10 + 2 × 2,000) ms / 100
t_mean = 4,980 ms / 100 = 49.8 ms
where
t_mean: the mean (average) latency, in milliseconds (ms)
ms: millisecond, one thousandth of a second
In words: total time spent by all requests divided by the number of requests.
```

A **percentile** instead sorts the requests from fastest to slowest and reads off one position. One common convention (the nearest-rank method) is:

```formula
r = ⌈ (p / 100) × n ⌉
p = 50: r = ⌈ 0.5 × 100 ⌉ = 50
p = 99: r = ⌈ 0.99 × 100 ⌉ = 99
where
r: the rank, the position in the sorted list (1 = fastest) whose value is the percentile
p: the percentile wanted, from 0 to 100; p50 is the median, p99 the 99th percentile
n: the number of measurements; here 100
⌈ ⌉: ceiling: round up to the next whole number (2.1 becomes 3; a whole number stays as it is)
In words: to find the p-th percentile, sort the values and take the one p% of the way along the list.
```

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

### Why the tail matters more than you'd think

**Your heaviest users hit the tail most.** A user loading a page that makes 50 backend calls is much more likely to experience at least one slow call. Amazon's Dynamo paper describes service-level targets set at p99.9 rather than the mean or median, so that *every* customer gets a good experience, including those with the longest histories and so the most expensive requests.

**Fan-out amplifies the tail.** If a request fans out to several servers in parallel and must wait for all of them, it's as slow as the slowest. The easiest way to get the chance that *at least one* is slow is to work out the chance that *none* is, and subtract it from 1:

```formula
P_slow = 1 − (1 − q)^n
n = 1: 1 − 0.99^1 = 0.01 (1%)
n = 10: 1 − 0.99^10 ≈ 0.096 (~10%)
n = 100: 1 − 0.99^100 ≈ 0.63 (63%)
where
P_slow: the probability that a user request is slow, i.e. at least one of its backend calls is slow, from 0 to 1
q: the probability that any one server responds slowly; here 0.01 (1%), which is what "the p99 is slow" means
n: the number of servers the request fans out to in parallel
^: "to the power of": 0.99^10 means 0.99 multiplied by itself 10 times
≈: approximately equal to (rounded)
In words: each call is fast with probability 0.99; all n are fast with probability 0.99 multiplied by itself n times; anything else means the user waits for a slow one.
```

The formula assumes each server is slow independently of the others. Correlated slowness (a shared overloaded database, say) changes the numbers.

At 100-way fan-out, most requests (63%) wait for at least one server's p99-or-worse response, so a single server's tail becomes your typical latency. This is the central point of Dean and Barroso's paper *The Tail at Scale*. Mitigations include **hedged requests** (send a second copy after the p95 time elapses and use whichever returns first), tied requests, and reducing variability at the source.

### Measuring percentiles correctly

- **You can't average percentiles.** The mean of 10 servers' p99s is not the fleet's p99. Aggregate raw histograms (e.g. HdrHistogram, Prometheus histograms) and compute percentiles from the combined data.
- **Beware coordinated omission.** A load tester that waits for each response before sending the next under-reports latency when the server stalls, because it stops sending during the stall. Tools like `wrk2` correct for this.
- **Measure at the client, too.** Server-side timing misses network and queueing time before your code runs.

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

- Memory is roughly **1,000x faster than SSD** for random access, and an in-datacentre network round trip costs about as much as several SSD reads. That's why Redis (in memory, one network hop) is so popular as a cache.
- A **disk seek** costs as much as millions of CPU instructions. Sequential I/O is vastly faster than random I/O, which is why log-structured designs like Kafka and LSM-tree databases are fast at writes.
- **Cross-region round trips are tens to hundreds of milliseconds.** Any design that requires a synchronous cross-region round trip on every write (e.g. synchronous geo-replication) pays this on every request.
- **Chatty protocols are deadly over distance.** 20 sequential calls at 70 ms each = 1.4 s.

## Throughput in practice

Throughput depends on hardware, payload size, schema, batching, persistence, concurrency and the target latency percentile. A 10 Gbps link has a raw signalling rate equivalent to 1.25 GB/s before protocol overhead; that is not an application throughput guarantee.

> [!note] Content gap: verified throughput benchmarks
> Generic per-server rates for web APIs, PostgreSQL, Redis and Kafka are omitted. No reproducible workload and hardware configuration was provided for those figures, so they cannot be reliably verified as capacity guidance. Benchmark the intended workload and record its settings before using a rate in a design.

## Key takeaways
- Latency is time per operation; throughput is operations per unit time. Adding parallel capacity raises throughput but doesn't lower base latency.
- Queueing links them: latency rises sharply as utilisation approaches 100%, so plan for headroom.
- Little's law (requests in flight = arrival rate × time in system) gives concurrency. Big transfers are bandwidth-bound; many small sequential calls are latency-bound, and need different fixes.
- Use percentiles (p50, p99, p99.9), not averages, and aggregate histograms rather than averaging percentiles.
- Fan-out amplifies tail latency: with 100 parallel calls, a 1%-slow server affects 63% of requests.
- Know the orders of magnitude: memory ~100 ns, SSD ~100 µs, datacentre round trip ~0.5 ms, cross-continent ~100 ms.

## Further reading
- [The Tail at Scale (Dean and Barroso, PDF)](https://www.barroso.org/publications/TheTailAtScale.pdf)
- [Latency numbers every programmer should know (gist)](https://gist.github.com/jboner/2841832)
- [Interactive latency numbers by year (Colin Scott)](https://colin-scott.github.io/personal_website/research/interactive_latency.html)
- [Service Level Objectives (Google SRE book)](https://sre.google/sre-book/service-level-objectives/)
- [Little's law (Wikipedia)](https://en.wikipedia.org/wiki/Little%27s_law)
