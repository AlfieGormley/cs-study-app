---
id: wm-wifi-airtime-and-diagnosis
title: Sharing airtime and diagnosing slow Wi-Fi
level: basic
minutes: 4
summary: Equal frame opportunities can give a slow active client disproportionate airtime in the simplified DCF model.
sourceLesson: wm-wifi
---

One slow device can make a whole Wi-Fi network feel slow, and a fast download can make every video call stutter. Both come from the same fact: stations share airtime, not bits.

## Half duplex and sharing

An ordinary single radio link cannot simultaneously transmit and receive on that link. Uploads and downloads consume the same radio resources; scheduling, OFDMA/MU-MIMO, spatial reuse and multiple links make modern sharing more complex than a single global turn-taking sequence.

## The performance anomaly

In a simplified saturated, equal-priority DCF model with comparable frame sizes, stations obtain similar *access opportunities*, not similar *airtime*. A slow station's frames take much longer on air, so it uses most of the time, and every faster station is dragged down towards its pace.

> [!example] One slow client
> A fast client at 54 Mbit/s and a slow one at 6 Mbit/s alternate 1,500-byte frames, ignoring overhead. The fast frame takes about 0.22 ms and the slow one 2 ms, so each cycle of 2.22 ms moves one frame for each. **Both** get about 5.4 Mbit/s: the fast client loses 90% of its potential throughput.

The model assumes both clients always have a frame waiting and get equal turns. The result is called the **performance anomaly**. A client at the edge of coverage, using a low MCS, is the usual culprit.

> [!analogy] Real-world analogy: One till, taking turns
> Two shoppers share a single till and take strict turns, one item each. One scans in a second; the other pays for each item in coins and takes ten seconds. Both leave at the same slow rate, because every turn includes the slow customer's ten seconds.
>
> **How it maps:** The till is the shared channel, each item is a frame, and strict turns are DCF's equal access opportunities. The coin-paying shopper is the low-rate client whose frames occupy far more airtime, and both leaving at the same rate is equal per-station throughput. Giving each shopper equal *time* at the till instead of equal turns is airtime fairness.
>
> **Where it stops:** Real Wi-Fi turns are random rather than strictly alternating, aggregation lets a station move many frames per turn, and the AP controls downlink scheduling far more than uplink.

Some APs implement **airtime fairness** policies to mitigate this; capabilities and effectiveness vary. Moving compatible clients to another band can separate contention, but does not guarantee high rates there.

## Loss, retries and queues

Interference and fading cause corrupted frames. Wi-Fi retries at the link layer, which can hide some radio losses from TCP but adds latency and jitter. Under load, large buffers in the AP add more: an illustrative loaded link might show 5 ms idle RTT and 200 ms during a download; this is not a universal measurement or unique diagnosis. Queueing delay is the time needed to drain what is already waiting: 2 MB queued ahead of a packet on an 80 Mbit/s link adds about 0.2 s, however short the radio path.

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
