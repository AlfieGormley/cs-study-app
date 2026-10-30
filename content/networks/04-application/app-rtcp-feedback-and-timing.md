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

RTP's companion, **RTCP**, sends periodic reports:

- **Sender reports** map the RTP timestamp to wall-clock (NTP format) time, which is how receivers **lip-sync** audio and video streams that have unrelated RTP clocks.
- **Receiver reports** give fraction lost, cumulative loss and **interarrival jitter**, a running estimate of how much packet transit times vary.
- **Round-trip time**: a receiver report echoes the timestamp of the last sender report it received (LSR) and says how long it held that report before replying (DLSR, delay since last sender report). The sender subtracts its own send time and the receiver's holding time from the moment the report arrives; what remains is time on the network. Both the send and arrival times come from the sender's clock, so the two machines' clocks need not agree. On the wire these are compact fixed-point values, so the subtraction must handle the counters wrapping round.

The jitter estimate compares each packet's spacing on arrival with its spacing in RTP timestamps, and moves one sixteenth of the way towards the latest difference, so one-off spikes are smoothed:

```formula reference
D = (R_j − R_i) − (S_j − S_i)
J_new = J + (|D| − J) / 16
where
D: the change in transit time between two consecutively received packets i and j (which may arrive out of sequence): how much later or earlier packet j arrived than its timestamp predicts
R_i, R_j: the arrival times of packets i and j, measured in RTP timestamp units
S_i, S_j: the RTP timestamps carried in packets i and j
J: the previous jitter estimate, in RTP timestamp units
J_new: the updated estimate, in RTP timestamp units
|D|: the size of D, ignoring its sign
In words: if packets keep arriving with uneven spacing, J climbs towards the typical unevenness; dividing by 16 smooths out one-off spikes.
```

WebRTC adds RTCP feedback messages: **NACK** (please resend packet 6702, if there's time), **PLI** (picture loss indication, allowing an encoder to respond with recovery information such as an intra picture) and transport-wide congestion feedback, which drives Google Congestion Control in adjusting the encoder's bitrate.

On the receiving side, a **jitter buffer** holds packets briefly to reorder them and smooth out variable delay. It is a direct trade: a bigger buffer survives more jitter but adds latency. How much delay is acceptable depends on the application; interactive calls tolerate far less than one-way streaming.

> [!analogy] Real-world analogy: A water tank between an uneven pipe and a steady tap
> Water arrives at a tank in irregular spurts, but the tap below it runs smoothly. A bigger tank rides out longer gaps in the supply, but each drop spends longer in the tank before it reaches the tap.
>
> **How it maps:** The spurts are packets arriving with jitter, the steady tap is playout at the media clock's pace, and the tank's size is the jitter buffer's added delay. RTCP's jitter figure tells both ends how uneven the supply is.
>
> **Where it stops:** Water is interchangeable, but packets are not: the buffer must also put packets back in order, and a packet that arrives after its playout time is useless and is discarded or concealed. Adaptive buffers also resize themselves as conditions change.

## Key takeaways
- RTCP sender reports relate independent media clocks to wall time for synchronisation.
- Receiver reports describe loss, jitter and timing; a jitter buffer trades added latency for tolerance.

## Further reading
- [RFC 3550](https://www.rfc-editor.org/rfc/rfc3550)
- [RFC 4585](https://www.rfc-editor.org/rfc/rfc4585)
