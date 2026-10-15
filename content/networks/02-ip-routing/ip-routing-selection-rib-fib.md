---
id: ip-routing-selection-rib-fib
title: Select routes and program the FIB
level: intermediate
minutes: 3
sourceLesson: ip-routing-basics
summary: Distinguish same-prefix source preference from packet lookup and explain RIB/FIB responsibilities.
---

Distinguish same-prefix source preference from packet lookup and explain RIB/FIB responsibilities.

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

## Key takeaways
- Administrative distance is a vendor-specific source preference for the same prefix.
- Metrics from different protocols are not interchangeable.
- A floating static route requires the preferred route to become ineligible and the backup to remain usable.
- Retained hardware forwarding state does not guarantee correct service after control-plane failure.

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
