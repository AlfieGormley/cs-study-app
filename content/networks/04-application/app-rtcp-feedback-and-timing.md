---
id: app-rtcp-feedback-and-timing
title: "RTCP reports, jitter and round-trip timing"
level: advanced
minutes: 4
sourceLesson: app-p2p-webrtc
summary: "RTCP sender reports relate independent media clocks to wall time for synchronisation."
---

RTP carries a packet sequence number, media-clock timestamp and source identifier. RTCP is its companion control protocol. RTP clock rates depend on the payload format: Opus uses 48,000 ticks per second, while common video formats use 90,000.

### RTCP: feedback

RTP's companion, **RTCP**, sends periodic reports. In the cards below, i and j label consecutively received packets, which need not have consecutive sequence numbers:

- **Sender reports** map the RTP timestamp to wall-clock (NTP format) time, which is how receivers **lip-sync** audio and video streams that have unrelated RTP clocks.
- **Receiver reports** give fraction lost, cumulative loss and **interarrival jitter**, a running estimate of how much packet transit times vary (formula below).
- **Round-trip time**: the sender works out the network round trip from the report it gets back, subtracting the time the receiver held it (formula below).

The jitter estimate is updated for every packet, moving one sixteenth of the way towards the latest measurement:

```formula
D = (R_j − R_i) − (S_j − S_i)
J_new = J + (|D| − J) / 16
where
D: the change in transit time between two consecutively received packets i and j (which may arrive out of sequence): how much later (or earlier) packet j arrived than its send timestamp predicts
R_i, R_j: the arrival times of packets i and j, measured in RTP timestamp units
S_i, S_j: the RTP timestamps carried in packets i and j
J: the previous jitter estimate, in RTP timestamp units
J_new: the updated estimate, in RTP timestamp units
|D|: the size of D, ignoring its sign
In words: if packets keep arriving with uneven spacing, J climbs towards the typical unevenness; dividing by 16 smooths out one-off spikes.
```

The round-trip time uses three values carried in or measured around the reports:

```formula
RTT = A − LSR − DLSR
where
RTT: the round-trip network delay expressed in units of 1/65,536 second, using modular subtraction of compact timestamps
A: arrival time of the receiver report by the sender's clock, using the middle 32 bits of an NTP timestamp (units of 1/65,536 second)
LSR: last sender report: the echoed middle 32 bits of the most recent sender-report NTP timestamp, in the same 1/65,536-second units as A
DLSR: delay since last sender report: how long the receiver held that report before replying, in units of 1/65,536 second
In words: take the time from sending the report to getting the answer, and subtract the time the receiver sat on it; what is left is time spent on the network.
```

A and LSR come from the sender's own clock, so the two machines' clocks need not agree. On the wire A and LSR use the same compact representation, so the subtraction needs modular arithmetic (it must handle the counters wrapping round) and assumes the clocks run at stable rates.

WebRTC adds RTCP feedback messages: **NACK** (please resend packet 6702, if there's time), **PLI** (picture loss indication, allowing an encoder to respond with recovery information such as an intra picture) and transport-wide congestion feedback, which drives Google Congestion Control in adjusting the encoder's bitrate.

On the receiving side, a **jitter buffer** holds packets briefly to reorder them and smooth out variable delay. It is a direct trade: a bigger buffer survives more jitter but adds latency. A suitable latency budget depends on the application; a universal 150 ms cutoff is omitted because this review did not establish one applicable to every interactive call.

## Key takeaways
- RTCP sender reports relate independent media clocks to wall time for synchronisation.
- Receiver reports describe loss, jitter and timing; a jitter buffer trades added latency for tolerance.

## Further reading
- [RFC 3550](https://www.rfc-editor.org/rfc/rfc3550)
- [RFC 4585](https://www.rfc-editor.org/rfc/rfc4585)
