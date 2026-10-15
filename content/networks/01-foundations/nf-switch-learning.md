---
id: nf-switch-learning
sourceLesson: nf-ethernet
title: Learn, forward, filter or flood
level: intermediate
minutes: 3
summary: Trace a simple learning switch and explain its omitted policies and attack limitations.
---

## Switches and MAC learning

A **switch** connects many links and forwards frames between them. Unlike a hub, which repeated every bit out of every port, a bridge can restrict known unicast forwarding, while some traffic is still flooded. To do that it builds a **MAC address table** (often called the CAM table) by watching traffic:

Assume valid frames, one VLAN, eligible forwarding ports, ordinary learning and no configured exceptions.

1. **Learn**: when a frame arrives on port P with source MAC S, record "S is reachable via P".
2. **Forward**: look up the destination MAC.
   - Known, on another port: send it out of that port only.
   - Known, on the same port it arrived on: drop it (filter).
   - Unknown, broadcast or (by default) multicast: use **Ethernet flooding** to copy it to eligible forwarding ports in the same VLAN, excluding ingress. Multicast snooping/filtering can narrow the set.
3. **Age**: remove dynamic entries after the configured ageing interval when they are not refreshed. Static entries and topology-change handling have different rules.

Basic learning can work automatically, but VLANs, spanning tree, security and management still require suitable configuration.

This toy models ordinary unicast labels plus an unknown broadcast label on one VLAN. It omits FCS validation, MAC-format checks, multicast policy, aging, VLANs, spanning tree, capacity and special ingress-reflection modes.

```python
class Switch:
    def __init__(self, ports):
        self.ports = tuple(ports)
        self.table = {}  # mac -> port

    def receive(self, port, src, dst):
        if port not in self.ports:
            raise ValueError("unknown port")
        # Source traffic refreshes its
        # location.
        self.table[src] = port  # learn
        # Destination lookup chooses the
        # output.
        if dst in self.table:
            out = self.table[dst]
            if out == port:
                return []  # filter
            return [out]
        # unknown or broadcast: flood
        return [p for p in self.ports
                if p != port]


# Unknown B floods; its reply teaches port
# 2.
sw = Switch([1, 2, 3, 4])
print(sw.receive(1, "A", "B"))  # [2, 3, 4]
print(sw.receive(2, "B", "A"))  # [1]
print(sw.receive(1, "A", "B"))  # [2]
```

The first frame floods because B is unknown. B's reply teaches the switch where B is, and from then on traffic between A and B goes only between ports 1 and 2.

Hardware forwarding capacity and latency depend on the switch and enabled features. **Store-and-forward** receives and checks the full frame before forwarding. **Cut-through** can begin earlier and may propagate part or all of a frame later found corrupt; its latency is not universally below one microsecond.

> [!warning] MAC-table exhaustion
> Large numbers of spoofed source addresses can exhaust learning capacity. Depending on the device and configuration, unknown unicast may then be flooded within its VLAN, exposing frames to additional ports or causing disruption. Existing learned entries need not all disappear, and flooding is not guaranteed. Configured per-port learning limits and appropriate violation actions can constrain this attack; encrypted payloads remain protected when the encryption is correctly implemented and endpoints are uncompromised.

## Key takeaways
- Learning uses the source; destination lookup determines forwarding.
- Unknown traffic flooding, ageing and exhaustion behaviour depend on policy and implementation.

## Further reading
- [Ethernet frame — Wikipedia](https://en.wikipedia.org/wiki/Ethernet_frame)
- [MAC address — Wikipedia](https://en.wikipedia.org/wiki/MAC_address)
- [Carrier-sense multiple access with collision detection — Wikipedia](https://en.wikipedia.org/wiki/Carrier-sense_multiple_access_with_collision_detection)
- [IEEE 802.1Q — Wikipedia](https://en.wikipedia.org/wiki/IEEE_802.1Q)
- [Network switch — Wikipedia](https://en.wikipedia.org/wiki/Network_switch)
- [Jumbo frame — Wikipedia](https://en.wikipedia.org/wiki/Jumbo_frame)

- [IEEE address-allocation guidelines](https://standards-support.ieee.org/hc/en-us/articles/4888705676564-Guidelines-for-Use-of-Extended-Unique-Identifier-EUI-Organizationally-Unique-Identifier-OUI-and-Company-ID-CID)
- [Cisco auto-negotiation and duplex guidance](https://www.cisco.com/c/en/us/support/docs/lan-switching/ethernet/10561-3.html)
- [Cisco unicast flooding behaviour](https://www.cisco.com/c/en/us/support/docs/switches/catalyst-6000-series-switches/23563-143.html)
- [Apple private Wi-Fi address modes](https://support.apple.com/en-ie/102509)
