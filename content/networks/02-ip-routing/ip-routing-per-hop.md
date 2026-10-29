---
id: ip-routing-per-hop
title: Follow a packet across Ethernet hops
level: intermediate
minutes: 3
sourceLesson: ip-routing-basics
summary: Trace TTL, checksum and link-address changes, and choose which next-hop address ARP resolves.
---

Trace TTL, checksum and link-address changes, and choose which next-hop address ARP resolves.

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

> [!analogy] Real-world analogy: A parcel and its courier stickers
> A parcel's address label names the final recipient and never changes. For each leg of the journey, the depot sticks a fresh routing sticker on top saying only "to the next depot" and peels off the previous one.
>
> **How it maps:** The address label is the IP header with its source and destination; the per-leg sticker is the Ethernet frame with the next hop's MAC address. Each router (depot) reads the label, picks the next leg from its table, and writes a new sticker.
>
> **Where it stops:** A router also changes the label slightly at every hop, decrementing TTL and updating the header checksum. NAT and tunnels change much more, and links that are not Ethernet may use no MAC addresses at all.

A host does the same LPM decision. If the selected route marks the destination as on-link on Ethernet, it ARPs for the destination itself. For a route via a gateway, it resolves that route's next hop. That may be a more-specific gateway route rather than the default; no matching route is also possible.

## Key takeaways
- Ordinary forwarding decrements TTL and updates the IPv4 header checksum.
- With the stated assumptions, IP endpoints remain unchanged across the router.
- The next Ethernet frame targets the selected next hop, which may be the destination or a gateway.
- The diagram excludes NAT, tunnelling and fragmentation.

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
