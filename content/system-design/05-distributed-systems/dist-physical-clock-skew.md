---
id: dist-physical-clock-skew
title: Physical clocks, drift and last-write-wins
level: intermediate
minutes: 3
summary: Choose the right clock for durations and see how skew can discard a later write.
sourceLesson: dist-time-ordering
---

Many distributed problems boil down to "which happened first?". Which write wins? Did this message cause that one? Is this lease still valid? On one machine the answer comes from a single clock. Across machines there is no shared clock, so you need to be careful about what "first" even means.

## Physical clocks and their problems

Each server has two kinds of clock:

| Clock | Use | Behaviour |
|---|---|---|
| Time-of-day | Timestamps | Can jump back or forward |
| Monotonic | Measuring durations | Only moves forward |

In Linux these are `CLOCK_REALTIME` and `CLOCK_MONOTONIC`. Rule one: **never measure a timeout with the time-of-day clock**. An NTP step can make an elapsed time negative.

### Drift and skew

Quartz crystals run slightly fast or slow, and it varies with temperature. Drift depends on the oscillator and operating conditions. The 2012 Spanner paper used a conservative allowance of 200 parts per million (ppm): at that rate a clock gains or loses up to 200 microseconds every second.

To see what that means over a day, multiply the drift rate by the time that passes:

```formula
Δ = r × t
Δ = 0.0002 × 86,400 s
Δ ≈ 17 s
where
Δ: delta, the total error the clock builds up, in seconds (s)
r: the drift rate as a fraction; 200 ppm means 200 parts per million, which is 200 / 1,000,000 = 0.0002
t: the time that passes without correction, in seconds; one day is 24 × 60 × 60 = 86,400 s
s: second
≈: approximately equal to (the exact value is 17.28 s)
In words: a clock that drifts by 200 parts per million is off by about 17 seconds after a day if nothing corrects it.
```

This calculation assumes a constant rate. Treat it as a bound only when the hardware and operating conditions justify that maximum drift rate; temperature can change the actual rate. A 10 ppm clock would build up less than a second a day.

**Skew** is the difference between two clocks at one moment. Two clocks that drift in opposite directions grow apart at the sum of their rates.

> [!warning] Last-write-wins with skewed clocks
> Node A's clock is 100 ms fast. A client writes v1 on A at A-time 10.100 (real 10.000). 50 ms later a client writes v2 on B at B-time 10.050 (real 10.050). LWW keeps v1 because 10.100 > 10.050, silently discarding the genuinely later write. This is a well-known hazard in Cassandra and other last-write-wins stores: any two writes closer together than the clock skew can be ordered wrongly.

## Key takeaways
- Use a monotonic clock for durations and timeouts; wall clocks can jump forwards or backwards.
- Drift is a clock’s rate error; skew is the difference between clocks at one moment.
- Timestamp last-write-wins can discard the later write in physical time when coordinator clocks are skewed.

## Further reading
- [Spanner clock assumptions (OSDI 2012)](https://www.usenix.org/system/files/conference/osdi12/osdi12-final-16.pdf)
- [Linux clock interfaces](https://man7.org/linux/man-pages/man2/clock_gettime.2.html)
- [Network Time Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Network_Time_Protocol)
