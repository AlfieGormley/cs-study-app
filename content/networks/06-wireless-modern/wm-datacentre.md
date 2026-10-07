---
id: wm-datacentre
title: Data-centre networks: leaf-spine, ECMP and oversubscription
level: intermediate
minutes: 14
summary: Why many data centres use Clos fabrics, how ECMP spreads flows across equal paths, and how to calculate oversubscription, scale and the cost of a failed spine.
---

A service request may fan out to authentication, caches, databases and other services. This can create substantial **east–west** traffic between servers, alongside **north–south** traffic entering or leaving the facility. The actual traffic mix is workload-dependent.

Classic enterprise networks were built for north–south traffic: a hierarchy that funnels traffic between aggregation branches through a core. A common alternative is a **leaf-spine** fabric, a folded **Clos** topology. Under the simple fully connected model below, each leaf pair has multiple paths of equal configured routing cost, not necessarily identical delay or available bandwidth.

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

Links are normally **layer 3** (routed), not layer 2. Each switch runs a routing protocol; RFC 7938 describes the common choice of eBGP, with an ASN allocation scheme suited to the topology and loop-prevention policy. L3 ECMP can use redundant links without STP blocking, but convergence, route limits and failure containment require appropriate design. Where tenants need layer 2 segments, an overlay such as VXLAN carries them over the routed fabric (covered in the SDN lesson).

## ECMP: using all the paths

With routing, a leaf sees, say, four routes to the destination rack's prefix, all with the same cost. **Equal-cost multi-path** (ECMP) can install multiple eligible next hops, subject to configuration and implementation limits. The forwarding lookup selects a next hop for each packet, commonly using a flow-stable hash.

Choosing per *packet* can reorder TCP segments, which TCP treats as possible loss. A common policy therefore selects per **flow**: they hash header fields, usually the 5-tuple, and use the hash to pick a next hop.

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
> Assume 8 equal flows choose independently and uniformly among 8 paths. The chance that every path gets exactly one is 8!/8⁸ ≈ 0.24%. The expected number of paths with no flow is 8 × (7/8)⁸ ≈ 2.7, so about a third of paths are empty on average in this model. Actual unused bandwidth also depends on flow demand and other traffic.

Mitigations include **flowlet switching** (changing path after a gap intended to exceed the path-delay difference; the guarantee depends on that delay bound), congestion-aware load balancing in the fabric, and **packet spraying** with transports that tolerate reordering. Applications can also split big transfers over several connections.

**Rehashing on failure.** If a switch picks `hash mod N` and one of four paths fails, it switches to `hash mod 3`. For uniform hashes and a stable ordering of the three surviving next hops, about a quarter of all flows keep their old physical path: most flows on *healthy* links move too, potentially causing reordering or disrupting unsynchronised per-flow state, such as a fleet of stateful load balancers behind ECMP. **Resilient hashing** aims to minimise remapping and can preserve healthy assignments on a simple removal. Bucket policies, rebalancing and implementation details determine whether additional flows move.

**Polarisation.** Correlated hash choices across tiers can underuse some paths, especially with matching path counts and mappings. Different hash seeds or inputs can reduce this polarisation.

## Oversubscription maths

A leaf has downlinks to servers and uplinks to spines. The **oversubscription ratio** compares them:

```
oversub = server-facing bandwidth
          / spine-facing bandwidth
```

### Worked example

A leaf has 48 × 25 Gbit/s server ports and 6 × 100 Gbit/s uplinks, one to each of 6 spines. Each spine has 64 × 100 Gbit/s ports.

```
down:  48 x 25  = 1200 Gbit/s
up:     6 x 100 =  600 Gbit/s
oversub = 1200 / 600 = 2:1

leaves  = spine ports      = 64
servers = 64 x 48          = 3072
uplinks = 64 leaves x 600 = 38.4 Tbit/s
```

The last line sums one-direction leaf uplink capacities; it is not a statement of bisection bandwidth or guaranteed delivered traffic. **2:1** means offered off-rack line-rate demand can be twice the aggregate uplink capacity. With equal sharing and no other bottleneck, 600/48 = 12.5 Gbit/s per server; ECMP does not guarantee that allocation. Direct same-leaf traffic avoids these uplinks, but service chaining or dual-attachment policy can differ.

A 1:1 leaf port ratio provides more uplink headroom than 2:1 or 4:1, but is not by itself proof that every traffic matrix runs without blocking. Routing, hash collisions, destination limits and other stages matter. Choose ratios using measured demand, failure headroom and cost; no universal workload-to-ratio rule is assumed here.

### Failure maths

Lose one of the six spines:

```
up:   5 x 100 = 500 Gbit/s
oversub = 1200 / 500 = 2.4:1
capacity lost = 1/6 = ~17%
```

With only this one spine failure and all remaining links/leaves working, racks retain topological connectivity after routing converges. Convergence time and transient packet loss are not guaranteed by the topology alone. Compare a design with 2 big spines, where one failure halves capacity. **More, smaller spines** give smaller blast radii, which is one of the strongest arguments for wide Clos fabrics.

### Scaling past one spine layer

The number of leaves is capped by spine port count. To go further, data centres add a third tier: groups of leaves and spines form **pods**, and a **super-spine** layer connects the pods. This is a 5-stage Clos.

For even k, the classic academic version is the **k-ary fat-tree** (Al-Fares et al., 2008), built entirely from k-port switches:

```
pods            = k
hosts           = k^3 / 4
k = 48: 48^3/4  = 27,648 hosts
```

Real examples include Facebook's 2014 data-centre fabric (server pods of 48 racks with four fabric switches each, connected by four planes of spine switches) and Google's Jupiter, which the 2015 *Jupiter Rising* paper described as delivering more than 1 Pbit/s of bisection bandwidth.

## Inside-the-fabric problems

- **Incast.** Concurrent replies can create a short burst exceeding a destination port’s service rate and available buffer. Loss may then trigger fast recovery, RACK/TLP or an RTO, depending on the trace and stack. Linux’s documented global default minimum RTO is 200 ms, but route/socket settings and newer configurable controls can alter it; not every tail loss waits for that timeout.
- **Finite buffers.** Switch buffer capacity and allocation vary by model. Burst demand and shared-buffer contention matter even when average utilisation is low.
- **Fixes.** **DCTCP** estimates the fraction of marked bytes and adjusts its congestion window proportionally, aiming to keep queues short; some RoCE deployments combine priority flow control with congestion notification; RDMA does not universally require PFC, and PFC introduces head-of-line/deadlock risks that require engineering. Applications can stagger fan-out replies or limit outstanding requests.

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
- Flowlets and resilient hashing reduce particular remapping/reordering problems under their assumptions.
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
