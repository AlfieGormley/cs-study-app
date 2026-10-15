---
id: wm-internet-fibre-latency
title: Fibre propagation and the distance budget
level: advanced
minutes: 3
summary: Propagation follows actual distance and signal speed, separately from queues and processing.
sourceLesson: wm-internet-structure
---

This unit focuses on fibre propagation and the distance budget. It builds on the earlier units in this module; the examples below state their additional assumptions.

## The physics of latency

For signal-envelope delay, use the fibre's effective group index at the operating wavelength, rather than confusing it with the phase index. This teaching model assumes a group index of 1.47, close to Corning's characterised 1.4682 for SMF-28 Ultra at 1550 nanometres:

```formula
v = c / n
v = 299,792 km/s / 1.47 ≈ 204,000 km/s
t_km = 1 km / v ≈ 4.9 µs ≈ 5 µs
RTT = (2d) / v
RTT = (2 × 100 km) / 204,000 km/s
RTT ≈ 1 ms
where
v: the speed of light in the fibre, in kilometres per second (km/s)
c: the speed of light in a vacuum, about 299,792 km/s
n: the dimensionless effective group index used for signal delay, assumed to be 1.47 here; the actual value depends on fibre and wavelength
t_km: the one-way delay per kilometre of fibre
RTT: the propagation round-trip time: there and back, ignoring every other delay
d: the one-way fibre route length, in kilometres (km)
km: kilometre
µs: microsecond, one millionth of a second
ms: millisecond, one thousandth of a second
≈: approximately equal to
In words: light in fibre covers about 204 km every millisecond, so each 100 km of route adds about 1 ms of round-trip time.
```

So light in fibre travels at roughly 204,000 km/s, about **5 µs per km**. A useful rule: **1 ms of round-trip time per 100 km** of fibre. The 5,570 km fibre example is a hypothetical route-length calculation, not a measured transatlantic path. Real cable routes and return paths differ, and transmission, processing and queueing add delay. Shorter routes or nearer servers reduce propagation; reducing queueing can also reduce RTT without changing geography.

## Key takeaways
- Propagation follows actual distance and signal speed, separately from queues and processing.
- Hypothetical route calculations establish conditional bounds, not a measured city-pair RTT.

## Further reading
- [Corning: SMF-28 Ultra optical fibre, including effective group index](https://www.corning.com/content/dam/corning/media/worldwide/coc/documents/Fiber/product-information-sheets/PI-1424-AEN.pdf)
- [BIPM: SI Brochure, including the defined vacuum speed of light](https://www.bipm.org/documents/20126/41483022/SI-Brochure-9.pdf)
