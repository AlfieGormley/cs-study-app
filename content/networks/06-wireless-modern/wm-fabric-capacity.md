---
id: wm-fabric-capacity
title: Oversubscription and fabric capacity budgets
level: intermediate
minutes: 3
summary: Compare total downlink and uplink capacities to obtain the leaf port ratio.
sourceLesson: wm-datacentre
---

Almost no fabric gives every server enough uplink capacity to send at full speed to other racks all at once. How much it falls short, the oversubscription ratio, is one of the main cost-versus-performance decisions in a data-centre design.

## Oversubscription

A leaf has downlinks to servers and uplinks to spines. The **oversubscription ratio** compares the traffic its servers could offer with what the leaf can send up to the spines:

```formula essential
OSR = B_down / B_up
where
OSR: the oversubscription ratio, written as "x:1"; 1:1 means the uplinks could carry everything the servers send off the rack
B_down: the total server-facing (downlink) bandwidth of the leaf: number of server ports times their speed, in gigabits per second (Gbit/s)
B_up: the total spine-facing (uplink) bandwidth of the leaf: number of uplinks times their speed, in Gbit/s
Gbit/s: gigabits per second, 10^9 bits per second
In words: the ratio says how many times more traffic the servers could send off the rack than the uplinks can carry.
```

Compare total bandwidth, not port counts. For example, a leaf with 48 server ports at 25 Gbit/s (1,200 Gbit/s) and 6 uplinks at 100 Gbit/s (600 Gbit/s) is **2:1** oversubscribed.

What 2:1 means in practice:

- It only bites when off-rack demand is high at the same moment. Most of the time servers are not all sending at line rate, which is why oversubscription is economical.
- If all 48 servers did send off-rack at once, they would share 600 Gbit/s: about 12.5 Gbit/s each with perfectly equal sharing, which ECMP does not guarantee.
- Traffic between servers on the same leaf does not use the uplinks at all, though service chaining or dual attachment can change that.

> [!analogy] Real-world analogy: Town streets feeding a motorway
> A town's many streets together could carry far more cars than the two-lane motorway out of town. That is fine on most days, because only some residents leave at once. At a holiday rush, everyone heads for the slip roads together and queues build.
>
> **How it maps:** The town's streets are the leaf's server ports, the motorway lanes are its uplinks, and the ratio of street capacity to motorway capacity is the oversubscription ratio. The holiday rush is a moment when many servers send off-rack simultaneously, such as a large data shuffle.
>
> **Where it stops:** Network queues fill in microseconds and overflowing packets are dropped rather than waiting patiently, and ECMP spreads traffic across uplinks by hashing rather than drivers choosing the emptiest lane.

## How spine ports bound the fabric

Every leaf uses one port on every spine. So the spine's port count caps the number of leaves: with 64-port spines, at most 64 leaves, which with 48 servers each is 3,072 servers. Adding spines adds paths and uplink capacity per leaf (if leaves have spare uplink ports), but not leaf slots. Growing past the spine port count needs bigger spines or another tier.

The sum of all leaves' uplink capacities (64 leaves × 600 Gbit/s = 38.4 Tbit/s here) is one-direction leaf uplink capacity; it is not a statement of bisection bandwidth or guaranteed delivered traffic.

A 1:1 leaf port ratio provides more uplink headroom than 2:1 or 4:1, but is not by itself proof that every traffic matrix runs without blocking. Routing, hash collisions, destination limits and other stages matter. Choose ratios using measured demand, failure headroom and cost; no universal workload-to-ratio rule is assumed here.

## Key takeaways
- Compare total downlink and uplink capacities to obtain the leaf port ratio.
- Spine ports bound leaf count; summed uplink capacity is not bisection bandwidth or delivered throughput.

## Further reading
- [RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938)
- [A Scalable, Commodity Data Center Network Architecture (Al-Fares et al.)](http://ccr.sigcomm.org/online/files/p63-alfares.pdf)
