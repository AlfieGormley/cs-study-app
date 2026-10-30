---
id: wm-fabric-failure-and-scale
title: Failed spines, pods and larger Clos fabrics
level: intermediate
minutes: 3
summary: One equal spine failure removes a corresponding fraction of leaf uplink capacity in the supplied model.
sourceLesson: wm-datacentre
---

Switches fail. A leaf-spine fabric is designed so that losing a spine costs some capacity everywhere rather than cutting anyone off, and the size of each spine decides how much a single failure costs. The same structure can be stacked into more tiers when one spine layer runs out of ports.

## What a spine failure costs

Take the previous lesson's leaf: 1,200 Gbit/s of server ports and one 100 Gbit/s uplink to each of 6 spines. Lose one spine:

- **Connectivity survives.** Every leaf still reaches every other leaf through the 5 remaining spines, once routing has converged. Convergence time and transient loss depend on the implementation, not on the topology alone.
- **Capacity shrinks everywhere.** Every leaf loses one of its six uplinks, a sixth of its uplink capacity, so its oversubscription worsens from 2:1 to 1,200 / 500 = 2.4:1.
- **Smaller pieces, smaller blast radius.** With 2 big spines, one failure would halve every leaf's uplink capacity; with 16 small ones it costs about 6%. More, smaller spines give smaller blast radii, one of the strongest arguments for wide Clos fabrics.

## Scaling past one spine layer

The number of leaves is capped by spine port count. To go further, data centres add a third tier: groups of leaves and spines form **pods**, and a **super-spine** layer connects the pods. This is a 5-stage Clos.

The classic academic version is the **k-ary fat-tree** (Al-Fares et al., 2008), built entirely from identical switches with the same even port count. Each pod has half that many edge switches and half that many aggregation switches, and each edge switch uses half its ports for hosts. The striking result is how fast it grows:

```formula reference
H = k^3 / 4
where
H: the number of hosts (servers) the fat-tree supports
k: the number of ports on every switch, an even number
k^3: k cubed, k × k × k
In words: the host count grows with the cube of the switch port count, so doubling the port count gives eight times as many hosts.
```

With 48-port switches that is 27,648 hosts from identical, inexpensive switches. The provisioned capacity does not mean hash-based routing achieves full throughput for every traffic pattern.

Real examples include Facebook's (now Meta's) 2014 data-centre fabric (server pods of 48 racks with four fabric switches each, connected by four planes of spine switches) and Google's Jupiter, which the 2015 *Jupiter Rising* paper described as delivering more than 1 Pbit/s of bisection bandwidth.

## Key takeaways
- One equal spine failure removes a corresponding fraction of leaf uplink capacity in the supplied model.
- Additional tiers extend scale; in the academic fat-tree, host count grows with the cube of the switch port count.

## Further reading
- [A Scalable, Commodity Data Center Network Architecture (Al-Fares et al.)](http://ccr.sigcomm.org/online/files/p63-alfares.pdf)
- [Introducing data center fabric — Engineering at Meta](https://engineering.fb.com/2014/11/14/production-engineering/introducing-data-center-fabric-the-next-generation-facebook-data-center-network/)
- [Jupiter Rising — Google Research](https://research.google/pubs/jupiter-rising-a-decade-of-clos-topologies-and-centralized-control-in-googles-datacenter-network/)
