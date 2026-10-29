---
id: ip-routing-ecmp-asymmetry
title: ECMP, asymmetry and route failures
level: intermediate
minutes: 5
sourceLesson: ip-routing-basics
summary: Explain flow hashing, path churn and legitimate asymmetric routing, then organise failure checks.
---

Real networks often have several equally good paths, and replies need not follow the same path as requests. Both facts are normal, and both surprise anyone who assumes one fixed path.

## Multiple paths: ECMP

If the routing implementation and policy select multiple eligible paths for the same prefix, the router can install a next-hop group: **equal-cost multi-path** (ECMP). Data centres rely on it to spread traffic over many links.

A common ECMP policy hashes flow-identifying fields, often the IP/port/protocol 5-tuple. Keeping a stable flow on a stable path reduces reordering, which can trigger spurious loss recovery in TCP. Hash inputs vary, and per-packet or flowlet policies also exist. Path changes and fragmentation can disrupt flow affinity; neither ECMP nor TCP treats every reordered packet as lost.

The trade-offs:

- A few huge flows ("elephants") can land on the same link while others sit idle.
- Reusing correlated hashes with similarly ordered next-hop groups can make downstream routers repeat the same path choices (**hash polarisation**). Different hash seeds can reduce correlated choices, without guaranteeing perfect balance.
- When a path is added or removed, naive modulo hashing remaps many flows. **Resilient hashing** limits the churn.

Naive modulo hashing picks a next hop by hashing the flow and taking the remainder after dividing by the number of paths:

```formula reference
i = H(f) mod k
where
i: the index of the chosen next hop, from 0 to k − 1
H(f): a hash function applied to f, giving a large whole number that looks random but is always the same for the same input
f: the flow's identifying fields, such as the 5-tuple of addresses, ports and protocol
mod: modulo: the remainder after whole-number division, so 14 mod 4 = 2 and 14 mod 3 = 2
k: the number of next hops in the equal-cost group
In words: hash the flow and take the remainder after dividing by the number of paths. The same flow always lands on the same path while the number of paths stays the same; change that number and most flows are reassigned.
```

Changing the path count can remap many flows. For the specific change from four paths to three, assume roughly uniform hashes, remove the last-indexed path, and keep the surviving path indices unchanged. A flow keeps its path only when its hash gives the same remainder in both groups: one quarter of possible residues over the shared twelve-value cycle. About three quarters of flows therefore move, although only the quarter on the removed path needed a new path. Different group reordering or nonuniform traffic changes the observed result.

> [!analogy] Real-world analogy: Checkout lanes by surname
> A shop with four tills sends each family to a till chosen from the first letter of their surname, so a family always queues together and its shopping is never split across tills. When one till closes, the manager redraws the letter ranges across the remaining three.
>
> **How it maps:** Each family is a flow, the surname rule is the hash, and the tills are the equal-cost next hops. Keeping a family at one till is flow affinity, which reduces the chance of packets of one connection arriving out of order. Redrawing the ranges moves many families who were not at the closed till: the churn of naive modulo hashing.
>
> **Where it stops:** A shop can see one family with a huge trolley and move it; a simple hash cannot tell an elephant flow from a small one. Resilient hashing keeps the surviving assignments fixed, which the redrawn-letters picture does not capture.

## Asymmetric routing

With ordinary destination-based forwarding, each router makes its own decision; policy routing can consider other fields. Nothing forces the reply to come back the same way, and on the Internet it often doesn't. That's normal, but it breaks things that assume symmetry:

- **Stateful firewalls** may reject traffic when the necessary connection state is absent. Asymmetric-routing support or state shared between firewalls can change the outcome.
- **Strict reverse path filtering** checks whether the ingress interface is a best route back towards the source. It can reject legitimate asymmetric traffic. Loose modes instead check source reachability without requiring the same interface; Linux policy and configuration affect the lookup. Choose a mode appropriate to the routing design.

### Source-specific reply routing

A multihomed Linux server can need different defaults for different local source addresses. A destination outside both connected subnets would otherwise follow the selected main-table default. If replies sourced from `192.168.50.5` must use the gateway on eth1, configure a separate table containing eth1’s connected prefix and its reachable gateway default, then add a suitably prioritised source rule for that address. The connected route lets that table resolve its gateway. Check the resulting lookup with `ip route get` including the source address; an earlier rule or policy can change the result. Packet captures must establish where replies actually leave, and firewall/reverse-path checks remain separate.

## Pitfalls

- **Routing loops**: two routers each pointing at the other for a prefix. Packets bounce until TTL expires; traceroute may show repeated responders, but filtering, rate limits and varying paths can obscure the pattern.
- **Black holes**: a route exists, but the next hop is dead or drops traffic. Operators also create them deliberately with **null routes** to discard attack traffic.
- **Missing return route**: you add a route to a new subnet, but the far side has no route back. Pings go out and nothing returns.

## Key takeaways
- Flow hashing helps preserve packet order on stable paths but does not guarantee equal utilisation.
- Changing a naive modulo path count can move flows that did not use the removed path.
- Reply routes can differ; stateful filters and reverse-path checks must fit the design.
- A present route does not prove a working next hop or network reply path.

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
