---
id: wm-fabric-capacity
title: Oversubscription and fabric capacity budgets
level: intermediate
minutes: 3
summary: Compare total downlink and uplink capacities to obtain the leaf port ratio.
sourceLesson: wm-datacentre
---

This unit focuses on oversubscription and fabric capacity budgets. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Oversubscription maths

A leaf has downlinks to servers and uplinks to spines. The **oversubscription ratio** compares them: how much traffic the servers could offer, against how much the leaf can send up to the spines.

```formula
OSR = B_down / B_up
B_down = n_down r_down
B_up = n_up r_up
where
OSR: the oversubscription ratio, written as "x:1"; 1:1 means the uplinks could carry everything the servers send
B_down: the total server-facing (downlink) bandwidth of the leaf, in gigabits per second (Gbit/s)
B_up: the total spine-facing (uplink) bandwidth of the leaf, in Gbit/s
n_down: the number of server ports
r_down: the speed of each server port, in Gbit/s
n_up: the number of uplink ports
r_up: the speed of each uplink port, in Gbit/s
Gbit/s: gigabits per second, 10^9 bits per second
In words: the ratio says how many times more traffic the servers could send off the rack than the uplinks can carry.
```

## Worked example

A leaf has 48 × 25 Gbit/s server ports and 6 × 100 Gbit/s uplinks, one to each of 6 spines. Each spine has 64 × 100 Gbit/s ports.

```formula
B_down = 48 × 25 Gbit/s = 1,200 Gbit/s
B_up = 6 × 100 Gbit/s = 600 Gbit/s
OSR = 1,200 / 600 = 2:1
L = P_spine = 64
S = L × 48 = 64 × 48 = 3,072
U = L × B_up = 64 × 600 Gbit/s
U = 38,400 Gbit/s = 38.4 Tbit/s
where
B_down: the leaf's total server-facing bandwidth
B_up: the leaf's total uplink bandwidth
OSR: the oversubscription ratio
L: the maximum number of leaves: each leaf uses one port on every spine, so it equals the spine port count
P_spine: the number of ports on each spine, 64
S: the maximum number of servers, 48 per leaf
U: the sum of all leaves' uplink capacities in one direction
Gbit/s: gigabits per second, 10^9 bits per second
Tbit/s: terabits per second, 10^12 bits per second (1,000 Gbit/s)
In words: each leaf can offer twice what it can send up, the 64-port spines cap the fabric at 64 racks of 48 servers, and the uplinks add up to 38.4 Tbit/s.
```

The last line sums one-direction leaf uplink capacities; it is not a statement of bisection bandwidth or guaranteed delivered traffic. **2:1** means offered off-rack line-rate demand can be twice the aggregate uplink capacity. With equal sharing and no other bottleneck, each server gets 600 Gbit/s ÷ 48 = 12.5 Gbit/s; ECMP does not guarantee that allocation. Direct same-leaf traffic avoids these uplinks, but service chaining or dual-attachment policy can differ.

A 1:1 leaf port ratio provides more uplink headroom than 2:1 or 4:1, but is not by itself proof that every traffic matrix runs without blocking. Routing, hash collisions, destination limits and other stages matter. Choose ratios using measured demand, failure headroom and cost; no universal workload-to-ratio rule is assumed here.

## Key takeaways
- Compare total downlink and uplink capacities to obtain the leaf port ratio.
- Spine ports bound leaf count; summed uplink capacity is not bisection bandwidth or delivered throughput.

## Further reading
- [RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938)
- [A Scalable, Commodity Data Center Network Architecture (Al-Fares et al.)](http://ccr.sigcomm.org/online/files/p63-alfares.pdf)
