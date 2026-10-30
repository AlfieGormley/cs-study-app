---
id: wm-cellular-architecture
title: Mobile-core functions and session anchors
level: intermediate
minutes: 3
summary: Separate the device, radio access network and core roles.
sourceLesson: wm-cellular
---

Cellular systems centrally schedule much of their radio traffic, unlike basic Wi-Fi contention. This is a distinction in access mechanisms, not a guarantee of collision-free radio or predictable latency: random access, interference, coverage and load still matter. Cellular deployments can use licensed, shared or unlicensed spectrum; Wi-Fi also has scheduled multi-user modes.

For applications, mobile paths introduce changing capacity, radio-state transitions, possible address changes and provider-specific translation or filtering. Design for interruption and measure the devices and networks you support.

## The big picture

Every cellular network has three parts: the phone (the **UE**, user equipment), the **radio access network** (RAN) of base stations, and the **core network** that handles identity, sessions and the packet gateway to the Internet.

```
 UE ~~radio~~ eNodeB/gNodeB
                 |  (backhaul)
     +-----------+----------+
     | Core                 |
     |  control: MME / AMF  |
     |  sessions: SMF       |
     |  user plane:         |
     |  S-GW+P-GW / UPF ----+--> Internet
     +----------------------+
```

| Part | 4G (LTE / EPC) | 5G (NR / 5GC) |
|---|---|---|
| Base station | eNodeB | gNodeB |
| Attach, mobility | MME | AMF |
| Session control | distributed across MME and gateway control functions | 5G SMF (session management function) |
| Packet gateway | S-GW + P-GW | UPF |
| Subscriber data / authentication | HSS with associated authentication functions | UDM/UDR for subscriber data; AUSF for authentication |

The 5G core defines **service-based** control-plane functions with HTTP-based service interfaces. Not every interface is HTTP/2: user-plane tunnels and control interfaces such as N4 use other protocols. Functions can be virtualised; earlier generations also support virtualisation, so “5G software versus 4G fixed boxes” is misleading.

## Tunnels keep your IP address still

For an IP session, session establishment selects/allocates addressing and user-plane resources. LTE uses EPS bearers with a P-GW anchor. In 5G, the session management function manages the PDU session and address allocation, potentially using a UPF or external allocation mechanism; a session-anchor UPF forwards user traffic. Not every PDU session carries IP: Ethernet and unstructured types also exist. Relevant radio-to-core user-plane interfaces use **GTP-U**, whose registered destination UDP port is 2152.

The P-GW or anchor UPF is the **session anchor**: to the Internet, your phone lives there. During a supported handover that preserves the session anchor/address, user-plane paths can be updated while the application retains its IP address. Connections can survive, but radio interruption, loss, session changes or timeout can still break them; no particular vehicle speed guarantees continuity.

> [!analogy] Real-world analogy: A fixed postal address with forwarding
> You keep one published address at a central sorting office while you travel. Letters always go there first, and the office forwards each one to wherever you are staying this week; when you move on, you tell the office and it updates the forwarding instruction. Your correspondents never need to know you moved.
>
> **How it maps:** The published address is the phone's IP address, the sorting office is the session anchor (P-GW or anchor UPF), and the forwarding instruction is the GTP-U tunnel towards the current base station. A handover updates that tunnel, so servers keep sending to the same address.
>
> **Where it stops:** Forwarding happens per packet in milliseconds, not per letter in days, and the network coordinates the update rather than the traveller writing in. Letters in transit during a move can be lost or delayed, just as packets can be during a handover, and a different provider's network (such as home Wi-Fi) has no arrangement with this sorting office.

Moving to an independently addressed Wi-Fi path commonly changes the effective endpoint address. Keeping the old path alive, provider-integrated access, tunnels or mobility-capable transports can change the outcome.

## Key takeaways
- Separate the device, radio access network and core roles.
- Supported anchored handovers can retain an IP address; interruption and session changes can still break a connection.

## Further reading
- [5G System Overview — 3GPP](https://www.3gpp.org/technologies/5g-system-overview)
- [System Architecture Evolution (the LTE core) — Wikipedia](https://en.wikipedia.org/wiki/System_Architecture_Evolution)
- [3GPP TS23.501 Release17: 5G system architecture](https://www.etsi.org/deliver/etsi_ts/123500_123599/123501/17.09.00_60/ts_123501v170900p.pdf)
