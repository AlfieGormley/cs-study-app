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

The client records when it sent the request and when the reply arrived (on its own clock); the server records when it received the request and when it sent the reply (on its clock). From those four timestamps NTP works out two things:

- **Delay:** the whole round trip measured by the client, minus the time the server spent holding the request. That leaves the time the messages spent on the network.
- **Offset:** how far the server's clock is ahead of the client's. The server's receive time minus the client's send time is the offset *plus* the outbound travel time. The server's send time minus the client's receive time is the offset *minus* the return travel time. Averaging the two cancels the travel time, but only if both directions take equally long.

```formula reference
δ = (t_3 − t_0) − (t_2 − t_1)
θ = ((t_1 − t_0) + (t_2 − t_3)) / 2
e = (d_out − d_back) / 2
where
δ: delta, the round-trip network delay: total time on the wire, both directions, in milliseconds (ms)
θ: theta, the estimated offset: how far the server's clock is ahead of the client's, in ms (negative means the server is behind)
t_0: the client's clock reading when it sent the request
t_1: the server's clock reading when the request arrived
t_2: the server's clock reading when it sent the reply
t_3: the client's clock reading when the reply arrived
e: the error in the offset estimate caused by unequal one-way delays, in ms
d_out: the real one-way delay from client to server, in ms
d_back: the real one-way delay from server to client, in ms
ms: millisecond, one thousandth of a second
In words: the delay is the whole round trip minus the server's holding time; the offset is the average of the two one-way clock differences, and any imbalance between the two directions shifts that estimate by half the difference.
```

For instance, a client that sends at 100 ms and hears back at 120 ms on its own clock, from a server that stamped 160 ms and 161 ms on its clock, computes 19 ms of network delay and a server clock about 50.5 ms ahead.

### The blind spot: asymmetric paths

The offset calculation assumes the network delay is **symmetric**. If the outbound path takes 15 ms and the return only 4 ms, the round trip looks exactly like two 9.5 ms legs, and the offset estimate is wrong by half the imbalance: about 5.5 ms.

> [!analogy] Real-world analogy: timing a letter both ways
> You post a letter to a friend abroad noting the time you sent it. They note when it arrived and when they posted a reply, and you note when the reply arrives. If you assume the post takes equally long each way, you can work out how far their watch is from yours. If outbound post really took three days and the return one, your answer is a day out, and nothing on the four postmarks tells you so.
>
> **How it maps:** The four noted times are NTP's four timestamps, the time your friend held the letter is the time the server held the request, and assuming equal posting times is NTP's symmetric-delay assumption. The day's error is half the difference between the two journeys.
>
> **Where it stops:** NTP repeats the exchange many times, with several servers, and filters out samples with unusually long delays, which reduces random error. A consistent one-way imbalance still survives all that filtering.

NTP has no way to notice this error from the timestamps alone. Typical accuracy: tens of milliseconds over the public internet, better than a millisecond on a local network under ideal conditions, and 100 ms or more with asymmetric routes or congestion. Managed time services differ (as of 2026): Amazon Time Sync supports NTP and, on supported EC2 hardware, a more precise PTP hardware clock. Google Public NTP uses leap smearing but explicitly provides no service-level agreement. Do not infer a universal sub-millisecond error bound from either provider's name.

NTP corrects a clock by **slewing** (running it slightly fast or slow) for small offsets and **stepping** (jumping) for large ones. Steps are what make clocks go backwards.

## Key takeaways
- NTP uses four timestamps to subtract the server's holding time from the round trip and estimate clock offset.
- The offset estimate assumes equal one-way delays; its error is half the path asymmetry.
- Slewing adjusts a clock’s rate; stepping changes its reading abruptly, so wall time remains unsuitable for durations.

## Further reading
- [Network Time Protocol Version 4 (RFC 5905)](https://www.rfc-editor.org/rfc/rfc5905)
- [Amazon Time Sync options](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html)
- [Google Public NTP FAQ](https://developers.google.com/time/faq)
- [Network Time Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Network_Time_Protocol)
