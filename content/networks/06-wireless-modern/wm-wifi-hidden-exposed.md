---
id: wm-wifi-hidden-exposed
title: Hidden and exposed terminals
level: basic
minutes: 3
summary: A hidden sender can interfere at a receiver it cannot hear directly.
sourceLesson: wm-wifi
---

This unit focuses on hidden and exposed terminals. It builds on the earlier units in this module; the examples below state their additional assumptions.

## The hidden terminal problem and RTS/CTS

Carrier sense only works if every station can hear every other. Often they cannot.

```
  (A) ~~~~~~ [AP] ~~~~~~ (C)
   A hears AP, C hears AP,
   A and C cannot hear each other
```

A and C both sense an idle channel and transmit at once. Their frames can interfere **at the AP**, causing missing ACKs and retries. Capture effects or different timings can allow some frames to succeed; throughput need not collapse in every such topology.

**RTS/CTS** can mitigate this when the relevant contenders receive the protection frames:

1. A sends a short **Request To Send** to the AP, with the duration of the exchange.
2. The AP replies **Clear To Send**, carrying the remaining protected exchange time.
3. C cannot hear A's RTS, but it *can* hear the AP's CTS, so it sets its NAV and stays quiet.
4. A sends its data; the AP ACKs.

This reduces the chance of wasting a long data transmission on a hidden-terminal collision. Missed CTS frames, other interferers and overlapping reservations still permit data/ACK loss. The cost is two extra frames and gaps per exchange, so implementations can select protection using an **RTS threshold** and other policies; defaults are device-specific. Wi-Fi 6 also uses RTS/CTS-style protection automatically in some situations, such as before multi-user transmissions.

The mirror image is the **exposed terminal**: a station that hears a nearby transmission and defers, even though its own transmission would not have interfered at its intended receiver. RTS/CTS does not fix this; it is one reason dense networks waste airtime.

## Key takeaways
- A hidden sender can interfere at a receiver it cannot hear directly.
- Received RTS/CTS protection can mitigate hidden-terminal collisions; it does not solve exposed-terminal deferral.

## Further reading
- [Hidden node problem — Wikipedia](https://en.wikipedia.org/wiki/Hidden_node_problem)
