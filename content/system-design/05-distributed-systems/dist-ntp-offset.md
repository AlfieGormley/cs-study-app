---
id: dist-ntp-offset
title: Estimating clock offset with NTP
level: intermediate
minutes: 5
summary: Calculate round-trip delay and offset, then identify the uncertainty caused by asymmetric paths.
sourceLesson: dist-time-ordering
---

Physical clocks drift, and synchronisation estimates their offset rather than discovering exact time. NTP’s round-trip exchange shows both how the estimate works and what it cannot observe.

### NTP

The Network Time Protocol syncs a client with servers arranged in strata (stratum 0 is an atomic clock or GPS; stratum 1 servers attach to it, and so on). A client estimates offset from a round trip:

```
client            server
 t0 |--request--->|
    |             | t1 (receive)
    |             | t2 (send)
 t3 |<--reply-----|
```

The client records when it sent the request and when the reply arrived (on its own clock); the server records when it received the request and when it sent the reply (on its clock). From those four timestamps NTP works out two things: how long the messages spent on the network, and how far apart the two clocks are.

```formula
δ = (t_3 − t_0) − (t_2 − t_1)
θ = ((t_1 − t_0) + (t_2 − t_3)) / 2
where
δ: delta, the round-trip network delay: total time on the wire, both directions, in milliseconds (ms)
θ: theta, the estimated offset: how far the server's clock is ahead of the client's, in ms (negative means the server is behind)
t_0: the client's clock reading when it sent the request
t_1: the server's clock reading when the request arrived
t_2: the server's clock reading when it sent the reply
t_3: the client's clock reading when the reply arrived
ms: millisecond, one thousandth of a second
In words: the delay is the whole round trip minus the time the server spent holding the request; the offset is the average of the two one-way clock differences, which cancels out the network delay if both directions take equally long.
```

Why the offset formula works: the difference t_1 − t_0 is the offset plus the outbound travel time, and t_2 − t_3 is the offset minus the return travel time. Adding them and halving cancels the travel time, but only when both directions take the same time.

Worked example: the client sends at 100 ms, the server receives at 160 ms and replies at 161 ms, and the reply arrives at 120 ms (each time on its own side's clock):

```formula
δ = (120 − 100) − (161 − 160) = 19 ms
θ = ((160 − 100) + (161 − 120)) / 2
θ = (60 + 41) / 2 = 50.5 ms
where
δ: delta, the round-trip network delay, in milliseconds (ms)
θ: theta, the offset of the server's clock relative to the client's, in ms; positive means the server is ahead
ms: millisecond
In words: the messages spent 19 ms on the network in total, and the server's clock is about 50.5 ms ahead of the client's.
```

The offset formula assumes the network delay is **symmetric**. If the outbound path is slow and the return fast, the estimate is wrong by half the asymmetry:

```formula
e = (d_out − d_back) / 2
e = (15 ms − 4 ms) / 2 = 5.5 ms
where
e: the error in the offset estimate, in milliseconds (ms)
d_out: the real one-way delay from client to server, in ms; here 15 ms
d_back: the real one-way delay from server to client, in ms; here 4 ms
ms: millisecond
In words: NTP can't see how the round trip splits between the two directions, so any imbalance turns into an offset error of half the difference.
```

NTP has no way to notice this error from the timestamps alone. Typical accuracy: around 1 ms on a good LAN, tens of ms over the internet, and much worse under congestion. Managed time services differ: Amazon Time Sync supports NTP and, on supported EC2 hardware, a more precise PTP hardware clock. Google Public NTP uses leap smearing but explicitly provides no service-level agreement. Do not infer a universal sub-millisecond error bound from either provider's name.

NTP corrects a clock by **slewing** (running it slightly fast or slow) for small offsets and **stepping** (jumping) for large ones. Steps are what make clocks go backwards.

## Key takeaways
- NTP uses four timestamps to subtract server processing time from round-trip delay and estimate clock offset.
- The offset estimate assumes equal one-way delays; its error is half the path asymmetry.
- Slewing adjusts a clock’s rate; stepping changes its reading abruptly, so wall time remains unsuitable for durations.

## Further reading
- [Network Time Protocol Version 4 (RFC 5905)](https://www.rfc-editor.org/rfc/rfc5905)
- [Amazon Time Sync options](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html)
- [Google Public NTP FAQ](https://developers.google.com/time/faq)
- [Network Time Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Network_Time_Protocol)
