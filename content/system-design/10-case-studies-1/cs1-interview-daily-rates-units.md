---
id: cs1-interview-daily-rates-units
title: Convert daily workload into rate and storage
level: basic
minutes: 4
summary: Separate average volume, peak demand and the resources retained.
sourceLesson: cs1-interview-framework
---

A daily total tells you volume; it does not tell you the busiest moment or how much work each request performs. Use estimates to identify which measurements and design decisions matter.

## Average, peak and capacity

An average rate spreads the daily count evenly across the day. For example, one million events a day averages about 12 events a second. A campaign can concentrate those same events into a short burst, so the average alone cannot size the system.

Keep this conversion as a reference rather than a memorisation exercise:

```formula reference
r = N / T
where
r: mean event rate, in events per second
N: number of events observed during the interval
T: observation interval in seconds; a day has 86,400 seconds
In words: divide the event count by the duration to find the average rate; this says nothing about how unevenly the events arrive.
```

Use measured busy periods when available. If a hypothetical exercise supplies a peak multiplier, label it as an assumption and test how the design changes when it is wrong. There is no universal safe multiplier or database capacity.

## Count what is retained

For storage, identify records retained, their average encoded size and the retention policy. Then add indexes, replication, temporary migration copies and backup requirements. A million 1 KB records occupy 1 GB of raw payload in decimal units; that is not a complete database footprint.

State the units consistently: a decimal kilobyte is 1,000 bytes, while a kibibyte is 1,024 bytes. Differences accumulate across larger units, so do not silently mix them when checking a capacity boundary.

## Turn the estimate into a decision

Ask which part is uncertain and consequential. Query complexity, contention, durability and latency targets affect throughput. A representative benchmark tells you whether a proposed deployment meets those targets; a daily request count does not.

## Key takeaways

- Average rate describes volume over time; peaks describe concentrated demand.
- Include retention, indexes, copies and recovery in a storage plan.
- Use estimates to choose measurements and designs, not to prove universal machine capacity.

## Further reading

- [NIST: day, hour and minute conversions](https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-5-units-outside-si)
- [NIST: decimal SI prefixes](https://www.nist.gov/pml/owm/metric-si-prefixes)
- [AWS: static stability and availability zones](https://aws.amazon.com/builders-library/static-stability-using-availability-zones/)
