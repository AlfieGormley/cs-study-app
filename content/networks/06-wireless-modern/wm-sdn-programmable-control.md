---
id: wm-sdn-programmable-control
title: SDN architecture and programmable control
level: intermediate
minutes: 3
summary: Separate forwarding operations from the policy that programs them.
sourceLesson: wm-sdn
---

Every router and switch does two jobs. The **data plane** forwards packets: look up the destination, pick an output port, perform the configured forwarding operation in hardware or software, at implementation-dependent rates. The **control plane** decides what the forwarding tables should contain: run OSPF or BGP, compute routes and program forwarding state. MAC learning can also be implemented locally in the data plane.

Traditionally both live in every box, and the network's behaviour emerges from hundreds of devices running distributed protocols, with management that may itself be automated. **Software-defined networking** (SDN) pulls the control plane out into software running on servers, which exposes programmable control interfaces to forwarding devices. Some architectures retain distributed routing and local decision-making.

Cloud virtual networks are a practical application of programmable networking. AWS and Google Cloud use the term VPC; Azure calls its corresponding construct a virtual network (VNet). Their scopes and firewall models differ.

## The SDN architecture

```
  apps: TE, firewall, load balancer
          | northbound API (REST etc.)
   +------+---------------------+
   |   controller (logically    |
   |   centralised, replicated) |
   +------+---------------------+
          | southbound API
          | (OpenFlow, P4Runtime)
  [switch]  [switch]  [switch]
   data plane: match -> action
```

Three ideas:

1. **Separation.** Forwarding behaviour and its policy/control logic can be programmed separately. Local failover, learning and hybrid routing may remain.
2. **Logically central control.** A controller can coordinate a broader view than one device, though observations can be incomplete or stale. Logical centralisation does not require one server or guarantee that a particular implementation is replicated.
3. **Programmability.** Network behaviour is software, so it can be versioned, tested and changed through APIs rather than by logging into boxes.

> [!analogy] Real-world analogy: Restaurant kitchens and a head office
> In a group of independently run restaurants, each kitchen's head chef decides the recipes, swapping notes with nearby kitchens, and the cooks follow them. A centrally run chain instead has head office write every recipe and send it to all kitchens, which then cook exactly as instructed.
>
> **How it maps:** Cooking each order is the data plane forwarding each packet. Deciding the recipes is the control plane, and chefs swapping notes is distributed routing protocols. Head office pushing recipes is an SDN controller programming switches through a southbound API, and keeping recipes in a central, version-controlled book is programmability.
>
> **Where it stops:** Kitchens keep cooking from their last recipes if head office goes quiet, and switches likewise keep forwarding on installed rules, but a new kind of order that needs head office's decision must wait for a reply. Real controllers are usually replicated, and many SDN designs leave some decisions (such as fast local failover) in the switches.

## Where SDN won

- **Hyperscale WANs.** Google's **B4**, described in a 2013 paper, connects its data centres with a centrally controlled traffic-engineering system. The paper reports high utilisation for its controlled workload and traffic-engineering design. This is a historical deployment result, not a universal target or comparison for every WAN; measurement, failure headroom and traffic priorities matter.
- **Data-centre fabrics.** Controllers configure and monitor large Clos fabrics as one system.
- **Network virtualisation.** Building isolated virtual networks for thousands of tenants on shared hardware. This is the cloud VPC.

## Key takeaways
- Separate forwarding operations from the policy that programs them.
- Logical central control does not require one physical controller or eliminate all local control.

## Further reading
- [Software-defined networking — Wikipedia](https://en.wikipedia.org/wiki/Software-defined_networking)
- [B4: Experience with a Globally-Deployed Software Defined WAN — Google Research](https://research.google/pubs/b4-experience-with-a-globally-deployed-software-defined-wan/)
