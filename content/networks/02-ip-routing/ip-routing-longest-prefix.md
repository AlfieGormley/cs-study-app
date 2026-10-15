---
id: ip-routing-longest-prefix
title: Find a route with longest-prefix match
level: intermediate
minutes: 5
sourceLesson: ip-routing-basics
summary: Separate routing from forwarding and implement destination lookup over an installed prefix table.
---

A router does two different jobs, on two very different timescales.

- **Routing** decides *where* each destination should go. It runs protocols (OSPF, BGP), swaps information with neighbours and computes paths. Reaction time depends on failure detection, protocol timers, implementation and topology.
- **Forwarding** takes one packet, looks up its destination, and sends it out of the right interface. It is performed per packet; latency and throughput depend on implementation and workload.

The first is the **control plane**; the second is the **data plane**. Keeping them apart is the central idea of router design. These short lessons examine the data plane: the table, lookup and per-hop work. Later units cover the protocols that fill the table.

## The routing table

A routing table is a list of entries. Each says "packets for this **prefix** go to this **next hop**, out of this **interface**".

| Prefix | Next hop | Interface |
|---|---|---|
| 192.168.1.0/24 | (direct) | eth0 |
| 10.0.0.0/8 | 192.168.1.254 | eth0 |
| 0.0.0.0/0 | 203.0.113.1 | eth1 |

Entries come from three places:

- **Connected routes** are commonly installed when an interface is configured and usable; options can suppress automatic prefix-route installation. Configure `192.168.1.1/24` on eth0 and the router knows 192.168.1.0/24 is directly reachable there.
- **Static routes** are typed in by an operator.
- **Dynamic routes** are learnt from a routing protocol.

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
    # Keep matches, then prefer longest.
    hits = [(n.prefixlen, hop)
            for n, hop in routes if a in n]
    if not hits:
        return None
    return max(hits, key=lambda x: x[0])[1]

print(lookup("10.1.3.1"))   # dc1
print(lookup("8.8.8.8"))    # isp
```

It compares the address with every route, so a table of N routes costs N prefix comparisons per lookup. In Big-O notation that is O(N), where N is the number of routes: the work grows in direct proportion to the table size. It also allocates a list of matches. The example assumes routes already selected by the control plane and one entry per prefix; it does not implement metrics, ECMP or policy routing. None means no matching route. Large tables motivate structures that avoid scanning every entry.

## Key takeaways
- The control plane selects routing state; the data plane forwards packets.
- Connected, static and dynamic routes can populate a table; /0 is the fallback match.
- Among installed eligible prefixes in the selected table, the longest matching IP prefix wins.
- The teaching lookup returns None when nothing matches and scans the whole table.

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
