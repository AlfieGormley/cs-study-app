---
id: wm-datacentre
title: Data-centre networks: leaf-spine, ECMP and oversubscription
level: intermediate
minutes: 14
summary: Why many data centres use Clos fabrics, how ECMP spreads flows across equal paths, and how to calculate oversubscription, scale and the cost of a failed spine.
---

A service request may fan out to authentication, caches, databases and other services. This can create substantial **east–west** traffic between servers, alongside **north–south** traffic entering or leaving the facility. The actual traffic mix is workload-dependent.

Classic enterprise networks were built for north–south traffic: a hierarchy that funnels traffic between branches of the aggregation layer through a core. A common alternative is a **leaf-spine** fabric, a folded **Clos** topology. Under the simple fully connected model below, each leaf pair has multiple paths of equal configured routing cost, not necessarily identical delay or available bandwidth.

## Why the tree broke

The traditional design had three layers:

```
         [core]     [core]
        /      \   /      \
     [agg]    [agg]     [agg]
     / \       / \       / \
  [acc][acc][acc][acc][acc][acc]
   |    |    |    |    |    |
  servers in racks
```

Problems for east–west traffic:

- **Bottlenecks up the tree.** Traffic between racks in different branches must climb to the core, so aggregate demand can exceed upstream capacity. The required equipment depends on the scale and traffic design.
- **Spanning Tree.** Layer 2 designs ran the Spanning Tree Protocol to prevent loops, which works by *blocking* redundant links. A redundant pair may have only one forwarding path for a particular spanning-tree instance; not every design strands exactly half of all capacity.
- **Uneven latency.** Two servers might be one hop apart or five, depending on where they sit.

## Leaf-spine: a folded Clos network

In 1953 Charles Clos showed how to build large non-blocking telephone switches out of many small ones arranged in stages. Data centres apply the same idea to packet switches:

```
  [S1]   [S2]   [S3]   [S4]   spines
   |\ \  /| |\  /| |\  / /|
   (every leaf to every spine)
   |/ /  \| |/  \| |/  \ \|
  [L1]   [L2]   [L3]   [L4]   leaves
   ||     ||     ||     ||
 servers servers servers servers
```

- In this example each rack has one **leaf** switch; real designs may use dual attachment or other placements.
- Every leaf connects to **every** spine. Spines do not connect to each other, and leaves do not connect to leaves.
- A path between these different leaves traverses three switches: source leaf → spine → destination leaf. Service chains, other fabric tiers and same-leaf traffic differ.
- Between two leaves there are as many equal paths as there are spines. With 4 spines, 4 paths.

Such fabrics can use fixed-port switches, which need not be identical. Adding spines also needs ports and links on every participating leaf. Adding leaves consumes spine ports; cost and topology limits remain.

Links are normally **layer 3** (routed), not layer 2. Each switch runs a routing protocol; RFC 7938 describes the common choice of eBGP, with an ASN allocation scheme suited to the topology and loop-prevention policy. L3 ECMP can use redundant links without STP blocking, but routing convergence, route limits and failure containment require appropriate design. Where tenants need layer 2 segments, an overlay such as VXLAN carries them over the routed fabric (covered in the SDN lesson).

## ECMP: using all the paths

With routing, a leaf sees, say, four routes to the destination rack's prefix, all with the same cost. **Equal-cost multi-path** (ECMP) can install multiple eligible next hops, subject to configuration and implementation limits. The forwarding lookup selects a next hop for each packet, commonly using a flow-stable hash.

Choosing per *packet* can reorder TCP segments, which TCP treats as possible loss. A common policy therefore selects per **flow**: they hash header fields, usually the 5-tuple, and use the hash to pick a next hop. The simplest mapping takes the remainder after dividing by the number of paths:

```formula
i = h mod N
h = 1,000,003, N = 4:  i = 3
where
i: the index of the chosen next hop (uplink), from 0 to N − 1
h: the flow's hash: a large whole number computed from its 5-tuple, the same for every packet of the flow
N: the number of equal-cost next hops
mod: modulo: the remainder after whole-number division, so 1,000,003 mod 4 = 3 because 1,000,003 = 4 × 250,000 + 3
In words: every packet of a flow has the same hash, so it always gets the same remainder and the same uplink.
```

The Python below uses CRC-32 as the hash; `%` is Python's mod operator:

```python
import zlib

def pick_uplink(flow, n_paths):
    if (type(n_paths) is not int
            or n_paths < 1):
        raise ValueError("bad path count")
    key = "|".join(map(str, flow)).encode()
    return zlib.crc32(key) % n_paths

flows = [("10.0.1.5", 40001 + i,
          "10.0.9.7", 443, "tcp")
         for i in range(6)]
print([pick_uplink(f, 4) for f in flows])
# [1, 3, 2, 2, 3, 1]
```

With unchanged inputs and next-hop mapping, a flow selects the same next hop. This avoids reordering caused by this path selector but does not guarantee no reordering elsewhere or during changes. Distinct flows can have different keys and still collide. Note that uplink 0 got nothing here: hashing is statistical, not a perfect balance.

### Where ECMP goes wrong

**Elephant flows collide.** With well-distributed keys and enough similarly sized flows, hashing can spread load approximately evenly. A few large flows (backups, replication, ML training) can land on the same link while others sit idle.

> [!example] How lumpy is hashing?
> Assume 8 equal flows choose independently and uniformly among 8 paths. The chance that every path gets exactly one is only about 0.24%, and on average about a third of the paths carry no flow at all. Actual unused bandwidth also depends on flow demand and other traffic.

The calculation behind that example:

```formula
P_even = n! / n^n
P_even = 40,320 / 16,777,216 ≈ 0.0024
E_empty = n × (1 − 1/n)^n
E_empty = 8 × (7/8)^8 ≈ 2.7
where
P_even: the probability that every path gets exactly one flow
n: the number of flows and also the number of paths, 8 here
n!: n factorial, 1 × 2 × … × n; 8! = 40,320 is the number of ways to put 8 flows on 8 paths one each
n^n: n to the power n; 8^8 = 16,777,216 is the number of ways the 8 flows can choose among 8 paths
E_empty: the expected (average) number of paths that get no flow
(1 − 1/n)^n: the chance that one particular path is missed by all n flows; (7/8)^8 ≈ 0.34
≈: approximately equal to
In words: perfect balance almost never happens by chance, and on average about 2.7 of 8 paths (a third) sit idle.
```

Mitigations include **flowlet switching** (changing path after a gap intended to exceed the path-delay difference; the guarantee depends on that delay bound), congestion-aware load balancing in the fabric, and **packet spraying** with transports that tolerate reordering. Applications can also split big transfers over several connections.

**Rehashing on failure.** If a switch picks `hash mod N` and one of four paths fails, it switches to `hash mod 3`. A flow keeps its path only if both remainders happen to agree:

```formula
f_keep = 1 / N
f_keep = 1 / 4 = 25%
where
f_keep: the fraction of all flows whose next hop stays the same when the path count drops from N to N − 1
N: the number of paths before the failure, 4 here
In words: out of every N × (N − 1) consecutive hash values, only the first N − 1 give the same remainder both ways, so just 1 in N flows stays put.
```

For uniform hashes and a stable ordering of the three surviving next hops, about a quarter of all flows keep their old physical path: most flows on *healthy* links move too, potentially causing reordering or disrupting unsynchronised per-flow state, such as a fleet of stateful load balancers behind ECMP. **Resilient hashing** aims to minimise remapping and can preserve healthy assignments on a simple removal. Bucket policies, rebalancing and implementation details determine whether additional flows move.

**Polarisation.** Correlated hash choices across tiers can underuse some paths, especially with matching path counts and mappings. Different hash seeds or inputs can reduce this polarisation.

## Oversubscription maths

A leaf has downlinks to servers and uplinks to spines. The **oversubscription ratio** compares them: how much traffic the servers could offer, against how much the leaf can send up to the spines.

```formula
OSR = B_down / B_up
B_down = n_down × r_down
B_up = n_up × r_up
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

### Worked example

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

### Failure maths

Lose one of the six spines:

```formula
B_up = 5 × 100 Gbit/s = 500 Gbit/s
OSR = 1,200 / 500 = 2.4:1
f_lost = 1 / n_spine = 1 / 6 ≈ 17%
where
B_up: the leaf's remaining uplink bandwidth, in gigabits per second (Gbit/s)
OSR: the new oversubscription ratio (server-facing 1,200 Gbit/s over uplink)
f_lost: the fraction of uplink capacity lost
n_spine: the number of spines before the failure, 6
Gbit/s: gigabits per second
≈: approximately equal to
In words: losing one of six equal spines removes a sixth of every leaf's uplink capacity.
```

With only this one spine failure and all remaining links/leaves working, racks retain topological connectivity after routing converges. Routing convergence time and transient packet loss are not guaranteed by the topology alone. Compare a design with 2 big spines, where one failure halves capacity. **More, smaller spines** give smaller blast radii, which is one of the strongest arguments for wide Clos fabrics.

### Scaling past one spine layer

The number of leaves is capped by spine port count. To go further, data centres add a third tier: groups of leaves and spines form **pods**, and a **super-spine** layer connects the pods. This is a 5-stage Clos.

For even k, the classic academic version is the **k-ary fat-tree** (Al-Fares et al., 2008), built entirely from k-port switches. Each pod has k/2 edge switches and k/2 aggregation switches, and each edge switch uses half its ports for hosts:

```formula
N_pods = k
H = k × (k/2) × (k/2) = k^3 / 4
H = 48^3 / 4 = 110,592 / 4 = 27,648
C = (k/2)^2 = 24^2 = 576
where
N_pods: the number of pods
k: the number of ports on every switch, an even number; 48 here
H: the number of hosts (servers) the fat-tree supports
k^3: k cubed, k × k × k
C: the number of core switches
In words: the host count grows with the cube of the switch size, so doubling the port count gives eight times as many hosts.
```

Real examples include Facebook's (now Meta's) 2014 data-centre fabric (server pods of 48 racks with four fabric switches each, connected by four planes of spine switches) and Google's Jupiter, which the 2015 *Jupiter Rising* paper described as delivering more than 1 Pbit/s of bisection bandwidth.

## Inside-the-fabric problems

- **Incast.** Concurrent replies can create a short burst exceeding a destination port’s service rate and available buffer. Loss may then trigger fast recovery, RACK/TLP or an RTO, depending on the trace and stack. Linux’s documented global default minimum RTO is 200 ms, but route/socket options and newer configurable controls can alter it; not every tail loss waits for that timeout.
- **Finite buffers.** Switch buffer capacity and allocation vary by model. Burst demand and shared-buffer contention matter even when average utilisation is low.
- **Fixes.** **DCTCP** estimates the fraction of marked bytes and adjusts its congestion window proportionally, aiming to keep queues short (the formula is below); some RoCE deployments combine priority flow control with congestion notification; RDMA does not universally require PFC, and PFC introduces head-of-line/deadlock risks that require engineering. Applications can stagger fan-out replies or limit outstanding requests.

DCTCP's reaction comes from RFC 8257. Switches mark packets with ECN once a queue passes a threshold; the sender keeps a running average of the marked fraction and cuts its window in proportion:

```formula
α ← (1 − g) × α + g × F
cwnd ← cwnd × (1 − α / 2)
where
α: alpha, the sender's running estimate of the fraction of its bytes that were ECN-marked, between 0 and 1
←: "is updated to": the new value replaces the old one, once per window of data
g: the estimation gain, a small weighting fraction between 0 and 1; RFC 8257 leaves the choice to the implementation and notes that 1/16 is used in some
F: the fraction of bytes marked in the most recent window of data
cwnd: the congestion window: how much unacknowledged data the sender may have in flight, in bytes or segments
In words: if few bytes were marked the window shrinks slightly; if marking persists until α approaches 1, it halves, like ordinary TCP.
```

For example, if α has settled at 0.2, a window of 100 segments is cut to 100 × (1 − 0.1) = 90 rather than to 50. Gentle cuts keep queues short without sacrificing throughput.

> [!tip] Reading a utilisation graph
> A link showing 30% average utilisation over five minutes can still drop packets: microbursts lasting a millisecond overflow a shallow buffer and vanish in the average. Look at drop counters and queue depth, not just utilisation.

## Trade-offs at a glance

| Choice | Benefit | Cost |
|---|---|---|
| More spines | capacity, small failure blast | ports, optics |
| Lower oversub | headroom for bursts | money |
| L3 + ECMP | no blocked links | L2 needs overlay |
| Per-flow hash | avoids selector-induced reordering while mapping is stable | elephant collisions |

## Key takeaways
- A fully connected two-tier leaf-spine model offers one path through each spine between different leaves.
- Routed ECMP can use parallel paths, but hashing does not guarantee equal utilisation or congestion-free service.
- Flowlet switching and resilient hashing reduce particular remapping/reordering problems under their assumptions.
- Oversubscription compares aggregate port capacities. Actual delivered rates, bisection capacity and failure recovery require separate analysis.
- Larger Clos fabrics add tiers. Incast and bursts need queue measurements, transport analysis and appropriate traffic controls.

> [!note] Evidence limits
> Universal data-centre traffic percentages, switch-buffer sizes, workload oversubscription ratios and fixed recovery times are omitted because no applicable deployment measurements were established. The capacity, hash and probability examples are models, not hardware benchmarks. This review did not measure fabric convergence, switch queues or an RDMA deployment.

## Further reading
- [Clos network — Wikipedia](https://en.wikipedia.org/wiki/Clos_network)
- [Equal-cost multi-path routing — Wikipedia](https://en.wikipedia.org/wiki/Equal-cost_multi-path_routing)
- [RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938)
- [RFC 2992: Analysis of an Equal-Cost Multi-Path Algorithm](https://www.rfc-editor.org/rfc/rfc2992)
- [A Scalable, Commodity Data Center Network Architecture (Al-Fares et al.)](http://ccr.sigcomm.org/online/files/p63-alfares.pdf)
- [Introducing data center fabric — Engineering at Meta](https://engineering.fb.com/2014/11/14/production-engineering/introducing-data-center-fabric-the-next-generation-facebook-data-center-network/)
- [Jupiter Rising — Google Research](https://research.google/pubs/jupiter-rising-a-decade-of-clos-topologies-and-centralized-control-in-googles-datacenter-network/)

- [RFC 8257: Data Center TCP](https://www.rfc-editor.org/rfc/rfc8257)
- [Google: Maglev load-balancer design](https://research.google/pubs/maglev-a-fast-and-reliable-software-network-load-balancer/)
