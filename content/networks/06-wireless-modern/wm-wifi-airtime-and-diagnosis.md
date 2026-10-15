---
id: wm-wifi-airtime-and-diagnosis
title: Sharing airtime and diagnosing slow Wi-Fi
level: basic
minutes: 4
summary: Equal frame opportunities can give a slow active client disproportionate airtime in the simplified DCF model.
sourceLesson: wm-wifi
---

This unit focuses on sharing airtime and diagnosing slow Wi-Fi. It builds on the earlier units in this module; the examples below state their additional assumptions.

## 3. Half duplex and sharing

An ordinary single radio link cannot simultaneously transmit and receive on that link. Uploads and downloads consume radio resources; scheduling, OFDMA/MU-MIMO, spatial reuse and multiple links make modern sharing more complex than a single global turn-taking sequence.

## 4. The performance anomaly

In a simplified saturated, equal-priority DCF model with comparable frame sizes, stations obtain similar access opportunities rather than equal airtime. Slow transmissions can then reduce faster stations’ throughput. QoS, frame aggregation, AP scheduling and airtime policies change this model.

> [!example] One slow client
> A fast client at 54 Mbit/s and a slow one at 6 Mbit/s alternate 1,500-byte frames, ignoring overhead. Each cycle moves one frame for each, so **both** get the same throughput, about 5.4 Mbit/s. The fast client loses 90% of its throughput.

The calculation behind the example:

```formula
T_F = L / R_F
T_F = 12,000 bit / 54 Mbit/s ≈ 222 µs
T_S = L / R_S
T_S = 12,000 bit / 6 Mbit/s = 2,000 µs
X = L / (T_F + T_S)
X = 12,000 bit / 2,222 µs ≈ 5.4 Mbit/s
where
T_F: the airtime of one fast-client frame, in microseconds (µs)
T_S: the airtime of one slow-client frame
R_F: the fast client's link rate, 54 Mbit/s
R_S: the slow client's link rate, 6 Mbit/s
X: the throughput each client gets, in megabits per second (Mbit/s)
L: the frame size in bits: 1,500 bytes × 8 = 12,000 bits
µs: microsecond, one millionth of a second; bits per µs equal Mbit/s
bit: one binary digit
Mbit/s: megabits per second
≈: approximately equal to
In words: taking turns frame by frame means both clients move at the pace set mostly by the slow one.
```

The fast client gets 5.4 of its possible 54 Mbit/s. The model assumes both clients always have a frame waiting and get equal turns.

Some APs implement **airtime fairness** policies to mitigate this; capabilities and effectiveness vary. Moving compatible clients to another band can separate contention, but does not guarantee high rates there.

## 5. Loss and retries

Interference and fading cause corrupted frames. Wi-Fi retries at the link layer, which can hide some radio losses from TCP but adds latency and jitter. Under load, large buffers in the AP add more: an illustrative loaded link might show 5 ms idle RTT and 200 ms during a download; this is not a universal measurement or unique diagnosis.

## Practical consequences
- Survey placement, interference, client capabilities and backhaul before changing configuration. Wired backhaul avoids consuming wireless backhaul airtime; a dedicated radio still has coexistence and capacity constraints.
- Compare permitted bands for the actual devices and coverage needs. Extra APs need channel and power planning; more is not automatically better.
- Wired connections can remove active traffic from radio contention. An idle device’s removal need not produce a measurable improvement.
- Compare local wired and wireless tests, RSSI/SNR, negotiated rates, retries, airtime use and loaded latency to locate the bottleneck.

> [!note] Evidence limits
> Universal handset stream counts, fixed TCP efficiency ratios, driver defaults and guaranteed channel-plan outcomes are omitted because they need device-specific evidence. Regional spectrum rules are time-sensitive; consult the regulator before deployment. No RF, coverage, interference or throughput measurements were performed for this lesson.

## Key takeaways
- Equal frame opportunities can give a slow active client disproportionate airtime in the simplified DCF model.
- Separate airtime, retries, queueing and backhaul with measurements before changing a deployment.

## Further reading
- [WiFi — High Performance Browser Networking](https://hpbn.co/wifi/)
- [Heusse et al.: Performance Anomaly of 802.11b](https://web.cs.wpi.edu/~rek/Nets2/C10/Performance_Anomaly.pdf)
