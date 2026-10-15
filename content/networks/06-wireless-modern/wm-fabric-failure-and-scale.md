---
id: wm-fabric-failure-and-scale
title: Failed spines, pods and larger Clos fabrics
level: intermediate
minutes: 3
summary: One equal spine failure removes a corresponding fraction of leaf uplink capacity in the supplied model.
sourceLesson: wm-datacentre
---

This unit focuses on failed spines, pods and larger Clos fabrics. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Failure maths

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

## Scaling past one spine layer

The number of leaves is capped by spine port count. To go further, data centres add a third tier: groups of leaves and spines form **pods**, and a **super-spine** layer connects the pods. This is a 5-stage Clos.

The classic academic version is the **k-ary fat-tree** (Al-Fares et al., 2008), built entirely from switches with the same even port count. Each pod has half that many edge switches and half that many aggregation switches. Each edge switch uses half its ports for hosts. The formulas define the port-count symbol:

```formula
N_pods = k
H = k(k/2)(k/2) = k^3 / 4
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

## Key takeaways
- One equal spine failure removes a corresponding fraction of leaf uplink capacity in the supplied model.
- Additional tiers extend scale; the academic even-port fat-tree has explicitly defined host and core counts.

## Further reading
- [A Scalable, Commodity Data Center Network Architecture (Al-Fares et al.)](http://ccr.sigcomm.org/online/files/p63-alfares.pdf)
- [Introducing data center fabric — Engineering at Meta](https://engineering.fb.com/2014/11/14/production-engineering/introducing-data-center-fabric-the-next-generation-facebook-data-center-network/)
- [Jupiter Rising — Google Research](https://research.google/pubs/jupiter-rising-a-decade-of-clos-topologies-and-centralized-control-in-googles-datacenter-network/)
