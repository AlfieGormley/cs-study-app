---
id: wm-internet-interconnection
title: IXPs, private interconnects and embedded caches
level: advanced
minutes: 3
summary: An IXP fabric can connect many agreed peers through a shared attachment.
sourceLesson: wm-internet-structure
---

Networks need physical places to meet. Exchange points, private interconnects and caches placed inside ISPs have flattened the old hierarchy, so much of today's traffic never touches a Tier 1 network.

## The flattening of the Internet

Direct interconnection and distributed content delivery add paths outside the simple hierarchy. Content providers can peer with access networks and operate their own transport infrastructure; their footprints and arrangements vary. Netflix's Open Connect and Google Global Cache go further, placing caching servers **inside** ISPs' networks.

Content served inside an ISP or across direct peering need not cross a Tier 1. The fraction of any user’s traffic taking such paths requires measurement.

## Internet exchange points

Peering needs a physical meeting place. An **Internet exchange point** (IXP) is a shared layer 2 switching fabric, often spread across several colocation buildings in a city, where participating networks connect and establish agreed peerings. Sizes, port counts, physical sites and remote-access arrangements differ.

- A shared-fabric port can reach many willing peers, subject to membership and policy, instead of needing a separate physical link for each.
- **Route servers** distribute eligible participant routes according to policy; they normally do not forward the participants’ data traffic. Not every member joins the route server, and joining does not automatically peer with everyone. Redundant sessions are common.
- Large IXPs include DE-CIX Frankfurt, AMS-IX in Amsterdam and LINX in London; traffic peaks are time-sensitive operational measurements, not fixed properties of an IXP.

Networks may use a **private network interconnect** (PNI), such as a dedicated cross-connect or circuit, for capacity or policy reasons. It need not be one fibre in the same building, and there is no universal traffic threshold or majority-share claim here.

## Key takeaways
- An IXP fabric can connect many agreed peers through a shared attachment.
- Route servers exchange routes rather than forwarding participant data.
- Embedded caches and direct peering can keep traffic away from transit paths.

## Further reading
- [Internet exchange point — Wikipedia](https://en.wikipedia.org/wiki/Internet_exchange_point)
- [Netflix Open Connect](https://openconnect.netflix.com/en/)
- [DE-CIX: Peering and route-server participation](https://docs.de-cix.net/article/n3i1zu0abx-how-to-implement-peering-services)
