---
id: ip-routing-basics
title: Forwarding and longest-prefix match
level: intermediate
minutes: 14
summary: What a router actually does with each packet, how the routing table is built and searched with longest-prefix match, what changes at every hop, and how tries and hardware tables accelerate lookup.
---

A router does two different jobs, on two very different timescales.

- **Routing** decides *where* each destination should go. It runs protocols (OSPF, BGP), swaps information with neighbours and computes paths. Reaction time depends on failure detection, protocol timers, implementation and topology.
- **Forwarding** takes one packet, looks up its destination, and sends it out of the right interface. It is performed per packet; latency and throughput depend on implementation and workload.

The first is the **control plane**; the second is the **data plane**. Keeping them apart is the central idea of router design. This lesson is about the data plane: the table, the lookup and the per-hop work. The next two lessons cover the protocols that fill the table.

## The routing table

A routing table is a list of entries. Each says "packets for this **prefix** go to this **next hop**, out of this **interface**".

| Prefix | Next hop | Interface |
|---|---|---|
| 192.168.1.0/24 | (direct) | eth0 |
| 10.0.0.0/8 | 192.168.1.254 | eth0 |
| 0.0.0.0/0 | 203.0.113.1 | eth1 |

Entries come from three places:

- **Connected** routes are commonly installed when an interface is configured and usable; options can suppress automatic prefix-route installation. Configure `192.168.1.1/24` on eth0 and the router knows 192.168.1.0/24 is directly reachable there.
- **Static** routes are typed in by an operator.
- **Dynamic** routes are learnt from a routing protocol.

The **default route** `0.0.0.0/0` matches every address. It means "if nothing better matches, send it here". A simple home-network example has a connected route and a default route pointing at the home router; VPNs and other configuration can add more.

On Linux:

```
$ ip route
default via 192.168.1.1 dev wlan0
10.8.0.0/24 dev tun0 scope link
192.168.1.0/24 dev wlan0 scope link

$ ip route get 10.8.0.7
10.8.0.7 dev tun0 src 10.8.0.2
```

`ip route get` is the most useful command here: it tells you which route the kernel would actually pick for an address. (Output trimmed for width.)

## Longest-prefix match

With CIDR, prefixes overlap. 10.1.2.9 is inside 0.0.0.0/0, 10.0.0.0/8, 10.1.0.0/16 and 10.1.2.0/24 all at once. Which wins?

The rule is **longest-prefix match** (LPM): of all the entries that contain the destination, use the one with the **longest** prefix, because it's the most specific.

Consider this table:

| Prefix | Next hop |
|---|---|
| 0.0.0.0/0 | isp |
| 10.0.0.0/8 | core |
| 10.1.0.0/16 | dc1 |
| 10.1.2.0/24 | rack7 |

Trace a few destinations:

| Destination | Matches | Winner |
|---|---|---|
| 10.1.2.9 | /0, /8, /16, /24 | rack7 |
| 10.1.3.1 | /0, /8, /16 | dc1 |
| 10.200.0.1 | /0, /8 | core |
| 8.8.8.8 | /0 | isp |

Why "most specific wins"? It lets aggregation and exceptions coexist. A provider announces one big block, and a customer who moved elsewhere announces a smaller piece of it. The smaller, more precise announcement takes priority for its addresses without anyone having to delete the big one.

> [!warning] More specific always beats "better"
> An eligible /24 installed in the selected forwarding table takes precedence over an installed /16. Rejected routes or unresolved next hops do not participate, and policy can select a different table. Metrics and protocol preferences only break ties between routes for the **same prefix**. This catches people out when a stray static route or a leaked more-specific steals traffic.

### LPM in Python

A direct translation: find every matching entry and take the longest.

```python
import ipaddress as ip

table = [
    ("0.0.0.0/0",   "isp"),
    ("10.0.0.0/8",  "core"),
    ("10.1.0.0/16", "dc1"),
    ("10.1.2.0/24", "rack7"),
]
routes = [(ip.ip_network(p), hop)
          for p, hop in table]

def lookup(addr):
    a = ip.ip_address(addr)
    hits = [(n.prefixlen, hop)
            for n, hop in routes if a in n]
    if not hits:
        return None
    return max(hits, key=lambda x: x[0])[1]

print(lookup("10.1.3.1"))   # dc1
print(lookup("8.8.8.8"))    # isp
```

This is O(N) per lookup for fixed-width IPv4, allocating a list of matches. The example assumes routes already selected by the control plane and one entry per prefix; it does not implement metrics, ECMP or policy routing. None means no matching route. Large tables motivate structures that avoid scanning every entry.

## When routes tie: distance and metric

Route selection and packet lookup are separate stages. For a Cisco-style destination-based setup:

1. A routing protocol selects candidate paths using its own rules and metrics.
2. For the same exact prefix, the routing table compares eligible candidates from different sources using administrative distance. Lower values are preferred; next-hop reachability also matters.
3. Selected usable routes are programmed for forwarding. A packet lookup then uses **longest-prefix match** among installed prefixes, without comparing administrative distances again.

Metrics from different protocols are not directly interchangeable. Policy routing can choose another table or action before this lookup.

Selected Cisco default administrative distances (configurable and not a universal IP standard):

| Source | Distance |
|---|---|
| Connected | 0 |
| Static | 1 |
| eBGP | 20 |
| OSPF | 110 |
| RIP | 120 |
| iBGP | 200 |

The Linux kernel exposes route priorities/metrics and policy-rule tables, rather than the Cisco source-distance table as a universal kernel mechanism. Routing daemons can apply their own source preferences before installing routes. A lower metric is relevant among otherwise comparable routes, not a replacement for prefix matching or policy.

A common trick uses this: a **floating static** route is a static route given a *high* distance (say 250). It can take over after the preferred route is withdrawn, provided the backup remains eligible and its next hop resolves. Upstream failure need not immediately withdraw a route.

## RIB and FIB

The table described so far is really two:

- The control plane has routing databases (**RIBs**) and protocol-specific state. Which losing candidates are kept in a shared RIB versus a protocol database depends on the implementation.
- The **FIB** (forwarding information base) represents selected forwarding actions, potentially with multiple next hops, recursive resolution and special local/discard entries.

The control plane computes the RIB and pushes changes down to the FIB. Distributed hardware routers can retain programmed forwarding while the control plane is busy or restarting. That does not guarantee continued correct service: failed adjacencies, stale state, shared resources and recovery behaviour still matter.

## What happens at each hop

For an ordinary forwarded IPv4 unicast packet on Ethernet, with no NAT, tunnel, options processing or fragmentation, the logical work includes (the hardware pipeline order can differ):

1. Checks the IPv4 header checksum (and drops on failure).
2. Decrements **TTL**. If it expires, drops the packet and normally reports ICMP Time Exceeded, subject to suppression/rate rules.
3. Updates the header checksum, possibly incrementally.
4. Looks up the destination with LPM to get next hop and interface.
5. Resolves the Ethernet next-hop MAC through ARP, using a valid cached mapping when available. IPv6 instead uses Neighbor Discovery and has no base-header checksum.
6. Builds a new link-layer frame and sends it.

In this Ethernet unicast example, IP source/destination remain unchanged while each routed link uses its next-hop MAC addressing. Other link technologies need not use MAC addresses, and tunnels, NAT and special routing mechanisms need separate treatment.

```
Host A        Router R1       Host B
10.0.0.5      10.0.0.1 |      10.9.0.7
mac aa        mac r1a  | r1b  mac bb

Frame 1 (A to R1)
  src mac aa   dst mac r1a
  src ip 10.0.0.5 dst ip 10.9.0.7

Frame 2 (R1 to B)
  src mac r1b  dst mac bb
  src ip 10.0.0.5 dst ip 10.9.0.7
```

A host does the same LPM decision. If the selected route marks the destination as on-link on Ethernet, it ARPs for the destination itself. For a route via a gateway, it resolves that route's next hop. That may be a more-specific gateway route rather than the default; no matching route is also possible.

## Fast lookup structures

### Binary tries

Store prefixes in a binary tree keyed by address bits. Walk down from the root following the destination's bits, remembering the last node that held a route. When you can't go further, the last route seen is the longest match.

```
root (0/0: isp)
  | next 8 bits 00001010
node 10/8: core
  | next 8 bits 00000001
node 10.1/16: dc1
  | next 8 bits 00000010
node 10.1.2/24: rack7
```

Lookup is O(W) where W is the address width: at most 32 bit-consuming edges for IPv4, 128 for IPv6 (including the root gives at most 33 or 129 visited nodes), regardless of table size. **Patricia** (path-compressed) tries skip chains of single-child nodes, and **multibit** tries consume 4, 8 or more bits per step to cut memory accesses. Linux's IPv4 FIB uses an LC-trie (level- and path-compressed).

### TCAM

Some forwarding hardware uses **TCAM** (ternary content-addressable memory). Each entry stores bits as 0, 1 or "don't care", so `10.1.0.0/16` becomes 16 fixed bits and 16 wildcards. In a simplified priority-TCAM model, entries are compared in parallel and a priority encoder selects a match. Ordering longer prefixes before shorter ones implements LPM in that model. Real designs can combine banks, stages, tries and separate priority logic.

| Structure | Principal trade-off |
|---|---|
| Trie | Follows address bits through memory; compression and layout influence accesses and capacity |
| Priority TCAM | Parallel masked matching with explicit priority; resource cost and lookup timing depend on implementation |

Cisco's 2014 field notice FN63866 documents FIB TCAM exhaustion on specified Catalyst 6500/7600 configurations, including software switching of some entries and possible elevated CPU usage or instability. This is a platform-specific capacity example, not evidence that every router behaves the same when full.

> [!note] Content omitted after review
> Universal one-cycle lookup claims, nanosecond forwarding promises and a current global prefix count are omitted because no matching hardware specification or dated measurement is established here.

## Multiple paths: ECMP

If the routing implementation and policy select multiple eligible paths for the same prefix, the router can install a next-hop group: **equal-cost multi-path** (ECMP). Data centres rely on it to spread traffic over many links.

A common ECMP policy hashes flow-identifying fields, often the IP/port/protocol 5-tuple. Keeping a stable flow on a stable path reduces reordering, which can trigger spurious loss recovery in TCP. Hash inputs vary, and per-packet or flowlet policies also exist. Path changes and fragmentation can disrupt flow affinity; neither ECMP nor TCP treats every reordered packet as lost.

The trade-offs:

- A few huge flows ("elephants") can land on the same link while others sit idle.
- Reusing correlated hashes with similarly ordered next-hop groups can repeat collisions downstream (**hash polarisation**). Different hash seeds can reduce correlated choices, without guaranteeing perfect balance.
- When a path is added or removed, naive modulo hashing remaps many flows. **Resilient hashing** limits the churn.

## Asymmetric routing

With ordinary destination-based forwarding, each router makes its own decision; policy routing can consider other fields. Nothing forces the reply to come back the same way, and on the Internet it often doesn't. That's normal, but it breaks things that assume symmetry:

- **Stateful firewalls** may reject traffic when the necessary connection state is absent. Asymmetric-routing support or shared state can change the outcome.
- **Strict reverse path filtering** checks whether the ingress interface is a best reverse path to the source. It can reject legitimate asymmetric traffic. Loose modes instead check source reachability without requiring the same interface; Linux policy and configuration affect the lookup. Choose a mode appropriate to the routing design.

## Pitfalls

- **Routing loops**: two routers each pointing at the other for a prefix. Packets bounce until TTL expires; traceroute may show repeated responders, but filtering, rate limits and varying paths can obscure the pattern.
- **Black holes**: a route exists, but the next hop is dead or drops traffic. Operators also create them deliberately with **null routes** to discard attack traffic.
- **Missing return route**: you add a route to a new subnet, but the far side has no route back. Pings go out and nothing returns.

## Key takeaways
- Routing (control plane) builds the table; forwarding (data plane) uses it for every packet.
- Routes come from connected interfaces, static configuration and dynamic protocols; the default route matches everything.
- Longest-prefix match picks the most specific matching route; distance and metric only break ties for the same prefix.
- In ordinary IPv4/Ethernet unicast forwarding, TTL is decremented, its header checksum updated and link addressing rebuilt for the next hop.
- Binary tries bound bit-consuming lookup steps by address width; TCAM uses masked comparisons and priority, with hardware-dependent cost and timing.
- Flow-hashed ECMP reduces path-induced reordering. Asymmetric routing can be valid, but filtering and stateful processing must support it.

## Further reading
- [Longest prefix match — Wikipedia](https://en.wikipedia.org/wiki/Longest_prefix_match)
- [Routing table — Wikipedia](https://en.wikipedia.org/wiki/Routing_table)
- [Administrative distance — Wikipedia](https://en.wikipedia.org/wiki/Administrative_distance)
- [Equal-cost multi-path routing — Wikipedia](https://en.wikipedia.org/wiki/Equal-cost_multi-path_routing)
- [RFC 1812: Requirements for IP Version 4 Routers](https://www.rfc-editor.org/rfc/rfc1812)
- [ip-route(8) manual page](https://man7.org/linux/man-pages/man8/ip-route.8.html)

- [Cisco: Administrative distance versus forwarding](https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/15986-admin-distance.html)
- [Linux LC-trie implementation notes](https://docs.kernel.org/networking/fib_trie.html)
- [RFC 2992: ECMP analysis](https://www.rfc-editor.org/rfc/rfc2992.html)
- [Cisco FN63866: TCAM exhaustion](https://www.cisco.com/c/en/us/support/docs/field-notices/638/fn63866.html)
