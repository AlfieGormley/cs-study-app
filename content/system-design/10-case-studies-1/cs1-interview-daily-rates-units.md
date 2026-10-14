---
id: cs1-interview-daily-rates-units
title: Convert daily workload into rate and storage
level: basic
minutes: 4
summary: Divide a daily count by 86,400 seconds, or state the 100,000-second shortcut.
sourceLesson: cs1-interview-framework
---

A back-of-the-envelope estimate is useful when it changes a design decision. This unit establishes the rate and storage conversions used throughout the case studies.

## Step 2: Back-of-the-envelope estimates

Estimates tell you which problems are real. A write count alone does not determine capacity: transaction complexity, indexes, contention, durability, hardware and latency targets matter. Don't compute to three significant figures. Round aggressively and keep powers of ten.

Numbers worth memorising. The first one turns "so many per day" into "so many per second", which is how almost every estimate in this module starts, because servers and databases are sized by their per-second load:

```formula
s_day = 24 × 60 × 60 = 86,400 s
s_day ≈ 10^5 s
rate = N_day / s_day
where
s_day: the number of seconds in one day
N_day: how many events (requests, posts, messages) happen in one day
rate: the average number of events per second, often called QPS (queries per second)
s: seconds, the unit of time
10^5: ten to the power 5, a 1 followed by five zeros, which is 100,000
≈: approximately equal to (the value has been rounded)
In words: to get an average per-second rate, divide the daily total by the number of seconds in a day, and round that to 100,000 so the sum is easy to do in your head.
```

Rounding 86,400 up to 100,000 makes every rate about 13.6% too low (86,400 / 100,000 = 0.864), which rarely changes a design decision. Two anchors to remember:

```formula
rate = 1,000,000 / (86,400 s) ≈ 12/s
rate = 1,000,000,000 / (86,400 s) ≈ 12,000/s
where
rate: the average number of events per second
s: seconds
/s: "per second"
≈: approximately equal to (rounded)
In words: one million events a day is about 12 a second; one billion a day is about 12,000 a second.
```

The rate above is an *average*. Traffic is not flat: it rises in the daytime and falls at night (diurnal skew), and campaigns or news events cause spikes. Capacity has to cover the busiest moment, so multiply the average by a peak factor:

```formula
rate_peak = rate_avg × k_peak
where
rate_peak: the requests per second at the busiest time, which is what you size for
rate_avg: the average requests per second over the day
k_peak: the peak factor, peak divided by average; use 2–3 as an explicit illustrative assumption when no traffic profile is given
In words: the busiest second is several times the average one, so plan for the average times a peak factor that you state out loud.
```

Real peak factors can be much higher than 3 (a push campaign or a sports final), so treat 2–3 as a placeholder until real traffic data exists.

Storage works the same way: count times size. Using decimal units, where each step is a factor of 1,000:

```formula
storage = N × size
10^6 × 1 KB = 10^6 × 10^3 B = 10^9 B = 1 GB
10^9 × 1 KB = 10^12 B = 1 TB
where
storage: total bytes needed
N: the number of records stored
size: the size of one record
B: bytes; one byte is 8 bits, enough for one plain English character
KB: kilobyte, 1,000 bytes (10^3 B)
GB: gigabyte, 1,000,000,000 bytes (10^9 B)
TB: terabyte, 10^12 bytes, a thousand gigabytes
10^6: a million; 10^9: a billion; 10^12: a trillion
In words: a million 1 KB records is 1 GB and a billion of them is 1 TB; most storage sums reduce to this.
```

(Some tools count a kilobyte as 1,024 bytes instead. At estimation precision the difference, 2.4% per step, doesn't matter.)

> [!note] Content gap: universal capacity and latency numbers
> No reproducible benchmark supports a universal database writes/s, Redis operations/s, app-server throughput or hardware/network latency for this scenario. Those values are omitted. Use measured workload capacity or explicitly supplied hypothetical inputs when sizing.

## Key takeaways

- Divide a daily count by 86,400 seconds, or state the 100,000-second shortcut.
- State the peak factor as a scenario assumption until traffic measurements exist.
- Use decimal storage units consistently; raw bytes exclude replication and indexes.

## Further reading

- [System Design Primer: design approach](https://github.com/donnemartin/system-design-primer/blob/master/README.md)
- [NIST: decimal SI prefixes](https://www.nist.gov/pml/owm/metric-si-prefixes)
