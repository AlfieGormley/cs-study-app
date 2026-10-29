---
id: ip-routing-trie-tcam
title: Accelerate lookup with tries and TCAM
level: intermediate
minutes: 3
sourceLesson: ip-routing-basics
summary: Compare bitwise trie lookup with a priority-TCAM model and recognise platform capacity limits.
---

A backbone router may hold hundreds of thousands of routes and must look one up for every packet. Comparing the destination with every route would be far too slow, so routers use structures whose lookup cost does not grow with the table.

## Fast lookup structures

### Binary tries

Store prefixes in a binary tree keyed by address bits. Walk down from the root following the destination's bits, remembering the last node that held a route. When you can't go further, the last route seen is the longest matching IP prefix.

```
root (0/0: isp)
  | next 8 bits 00001010
node 10/8: core
  | next 8 bits 00000001
node 10.1/16: dc1
  | next 8 bits 00000010
node 10.1.2/24: rack7
```

Each step down the tree consumes one bit of the destination address, so a lookup can never take more steps than the address has bits: at most 32 for IPv4 and 128 for IPv6, however many routes the table holds. Growing the table from a thousand routes to a million makes a linear scan a thousand times slower but leaves this bound unchanged. In Big-O notation, where W is the address width in bits, the lookup is O(W).

**Patricia** (path-compressed) tries skip chains of single-child nodes, and **multibit** tries consume 4, 8 or more bits per step to cut memory accesses. Linux's IPv4 FIB uses an LC-trie (level- and path-compressed).

### TCAM

Some forwarding hardware uses **TCAM** (ternary content-addressable memory). Each entry stores bits as 0, 1 or "don't care", so `10.1.0.0/16` becomes 16 fixed bits and 16 wildcards. In a simplified priority-TCAM model, entries are compared in parallel and a priority encoder selects a match. Ordering longer prefixes before shorter ones implements LPM in that model. Real designs can combine banks, stages, tries and separate priority logic.

| Structure | Principal trade-off |
|---|---|
| Trie | Follows address bits through memory; compression and layout influence accesses and capacity |
| Priority TCAM | Parallel masked matching with explicit priority; resource cost and lookup timing depend on implementation |

Cisco's 2014 field notice FN63866 documents FIB TCAM exhaustion on specified Catalyst 6500/7600 configurations, including software switching of some entries and possible elevated CPU usage or instability. This is a platform-specific capacity example, not evidence that every router behaves the same when full.

> [!note] Content omitted after review
> Universal one-cycle lookup claims, nanosecond forwarding promises and a current global prefix count are omitted because no matching hardware specification or dated measurement is established here.

## Key takeaways
- A binary trie follows at most one edge per address bit and remembers the last route.
- Compression reduces memory accesses without changing longest-prefix semantics.
- A first-match priority TCAM needs longer prefixes before shorter ones.
- The 2014 Cisco capacity incident describes specific platforms and configurations.

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
