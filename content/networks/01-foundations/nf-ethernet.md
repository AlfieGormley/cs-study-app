---
id: nf-ethernet
title: Ethernet and the link layer
level: intermediate
minutes: 14
summary: The Ethernet frame field by field, MAC addresses, how CSMA/CD shared a cable and why it no longer matters, how switches learn where hosts are, VLANs and the 1500-byte MTU.
---

The link layer moves frames across a link or bridged LAN. Ethernet is a widely used family of link technologies with a common MAC framing model. Its PHYs and optional encapsulations vary; this lesson starts with ordinary untagged Ethernet II frames.

## The Ethernet frame

The following is the basic untagged format. Tagged/envelope frames and specific PHY rules need additional accounting.

| Field | Bytes | Purpose |
|---|---|---|
| Preamble | 7 | Clock sync |
| Start frame delimiter | 1 | "Frame starts now" |
| Destination MAC | 6 | Who it's for |
| Source MAC | 6 | Who sent it |
| EtherType | 2 | What's inside |
| Payload | 46–1500 | IP packet etc. |
| FCS | 4 | CRC-32 check |

- The **preamble** is alternating 1s and 0s that lets the receiver lock onto the bit clock. The **SFD** ends in two 1s, signalling that the frame proper begins. Neither is counted in the frame size.
- **Destination first**: a switch can begin a destination lookup early, though VLAN classification and other policy may require more header information. This enables **cut-through** switching, where forwarding begins before the whole frame has arrived.
- **EtherType** values of 1536 (`0x0600`) or more identify the payload protocol. Values of 1500 or less are interpreted as a *length* instead, the IEEE 802.3 length/LLC interpretation. Values 1501–1535 are neither a valid length in that range nor an EtherType.
- The **payload** is at least 46 bytes; shorter payloads are padded. So the smallest frame (destination to FCS) is 6 + 6 + 2 + 46 + 4 = **64 bytes** and the largest basic untagged frame here is **1518 bytes**; that is not a universal maximum for every Ethernet encapsulation.
- The **FCS** is a CRC-32 over the destination address through payload and pad (including any tags), excluding preamble/SFD and the FCS itself. A receiver that finds a mismatch silently drops the frame. Ordinary full-duplex Ethernet MAC service does not acknowledge/retransmit a frame after an FCS failure; recovering from loss is left to higher layers (lesson 6).

Use a nominal **inter-frame gap** of 96 bit-times (12 byte-times) for the steady-rate calculations here. Some PHYs use alignment/deficit-idle rules; gap timing is not literal extra payload bytes. So each frame costs 20 extra bytes of wire time: 8 for preamble and SFD, and 12 for the gap.

> [!example] Packet rates
> A minimum frame occupies 64 + 20 = 84 bytes = 672 bits of wire time. At 1 Gbit/s that is up to 10⁹ / 672 ≈ **1.49 million frames per second**. At full-size 1538 byte-times it is about 81,000 frames per second. Router and firewall vendors quote "packets per second" figures for exactly this reason: small packets are the hard case.

## MAC addresses

A **MAC address** is 48 bits, written as six hex bytes, e.g. `3c:22:fb:11:22:33`.

- For an IEEE MA-L allocation, the first three bytes are an **OUI** assigned to an organisation, which assigns the remaining bits. Other allocation sizes and locally administered addresses do not follow a universal three-byte manufacturer rule.
- The least significant bit of the first byte is the **I/G bit**: 0 for an individual (unicast) address, 1 for a group (multicast) address.
- The next bit is the **U/L bit**: 0 for universally administered addressing (intended to be unique under its allocation rules, not proof of authenticity), 1 for a **locally administered** one.
- **Broadcast** is all ones: `ff:ff:ff:ff:ff:ff`. It addresses all stations in the broadcast domain, subject to filtering and policy.

```
first byte 0x3c = 0011 1100
                         ^^
             U/L = 0 ----+|
             I/G = 0 -----+
-> universal, unicast
```

Many phones and laptops support **private/randomised MAC addresses** for Wi-Fi; persistence, rotation and defaults depend on OS version and configuration. For locally administered **unicast** addresses, U/L is 1 and I/G is 0, so the second hex digit is 2, 6, A or E (for example `da:a1:19:...`). This reduces some cross-network tracking and can conflict with hardware-address allow-lists; it neither prevents all tracking nor makes a MAC a secure identity.

MAC addresses are **flat**: they say nothing about where a device is. That is fine within a LAN but would not scale to the internet, which is why IP prefixes (hierarchically aggregated for routing, rather than a reliable geographical location) exist at layer 3.

## CSMA/CD: how shared Ethernet worked

Original Ethernet put every host on one shared coaxial cable (later, one hub). Only one host could transmit at once, so they needed a rule for taking turns: **carrier-sense multiple access with collision detection**.

1. **Carrier sense**: listen; if someone is transmitting, wait.
2. When the line is idle, transmit.
3. **Collision detect**: while transmitting, listen. If the signal on the wire doesn't match what you're sending, another host started at nearly the same moment. Stop and send a 32-bit **jam** signal so everyone notices.
4. **Binary exponential backoff**: after the nth collision on this frame, pick K at random from 0 to 2^min(n,10) − 1, and wait K slot times before retrying, still obeying carrier-sense rules. At 10/100 Mbit/s the slot is 512 bit-times; historical half-duplex Gigabit uses 4096 bit-times. Give up after 16 attempts.

Backoff adapts to load: with two hosts colliding, after the first collision each picks 0 or 1, so they avoid each other half the time. Repeated collisions widen the range quickly.

### Why the minimum frame is 64 bytes

A sender only knows about a collision if it is still transmitting when the colliding signal gets back to it. The worst case is a collision at the far end of the network: the signal must travel there and back. So the transmission time of the shortest frame must be at least the maximum round-trip time.

At 10 Mbit/s, 64 bytes (512 bits) takes 51.2 µs to send. The **slot time**, propagation and repeater delays together constrain the collision domain; physical topology rules cannot be inferred from cable speed alone. At gigabit speeds, 512 bits takes only 0.512 µs, which would limit a shared segment to a few tens of metres; half-duplex gigabit worked around this with "carrier extension", an historical half-duplex mechanism distinct from modern full-duplex operation.

### Why it no longer matters

A common modern Ethernet arrangement is a **full-duplex** point-to-point link between a host and a switch port. Other Ethernet deployments include switch links and shared-medium PHYs. Each endpoint can send and receive concurrently. Some PHYs separate directions physically; 1000BASE-T uses both directions on the same four pairs with echo cancellation. A shared half-duplex collision domain is absent. CSMA/CD is switched off. 10 Gigabit Ethernet and faster do not support half duplex at all.

> [!warning] Duplex mismatch
> On legacy 10/100BASE-T links, if one end is forced to full duplex and the auto-negotiating peer detects speed but falls back to half duplex, the half-duplex side sees "collisions" whenever both send. The half-duplex side can back off and report late collisions; the full-duplex side may report FCS or alignment errors. Bidirectional throughput can suffer even when small pings succeed; exact counters and symptoms depend on timing and implementation. Use compatible settings, normally auto-negotiation at both ends. Do not generalise the legacy fallback behaviour to every Gigabit PHY; follow the equipment requirements.

## Switches and MAC learning

A **switch** connects many links and forwards frames between them. Unlike a hub, which repeated every bit out of every port, a bridge can restrict known unicast forwarding, while some traffic is still flooded. To do that it builds a **MAC address table** (often called the CAM table) by watching traffic:

Assume valid frames, one VLAN, eligible forwarding ports, ordinary learning and no configured exceptions.

1. **Learn**: when a frame arrives on port P with source MAC S, record "S is reachable via P".
2. **Forward**: look up the destination MAC.
   - Known, on another port: send it out of that port only.
   - Known, on the same port it arrived from: drop it (filter).
   - Unknown, broadcast or (by default) multicast: **flood** it to eligible forwarding ports in the same VLAN, excluding ingress. Multicast snooping/filtering can narrow the set.
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
        self.table[src] = port  # learn
        if dst in self.table:
            out = self.table[dst]
            if out == port:
                return []  # filter
            return [out]
        # unknown or broadcast: flood
        return [p for p in self.ports
                if p != port]

sw = Switch([1, 2, 3, 4])
print(sw.receive(1, "A", "B"))  # [2, 3, 4]
print(sw.receive(2, "B", "A"))  # [1]
print(sw.receive(1, "A", "B"))  # [2]
```

The first frame floods because B is unknown. B's reply teaches the switch where B is, and from then on traffic between A and B goes only between ports 1 and 2.

Hardware forwarding capacity and latency depend on the switch and enabled features. **Store-and-forward** receives and checks the full frame before forwarding. **Cut-through** can begin earlier and may propagate part or all of a frame later found corrupt; its latency is not universally below one microsecond.

> [!warning] MAC-table exhaustion
> Large numbers of spoofed source addresses can exhaust learning capacity. Depending on the device and configuration, unknown unicast may then be flooded within its VLAN, exposing frames to additional ports or causing disruption. Existing learned entries need not all disappear, and flooding is not guaranteed. Configured per-port learning limits and appropriate violation actions can constrain this attack; encrypted payloads remain protected when the encryption is correctly implemented and endpoints are uncompromised.

## VLANs

A basic single-VLAN bridge joins eligible ports into one broadcast domain; port isolation and filtering can further restrict connectivity. A **VLAN** (virtual LAN) splits one physical switch, or a set of switches, into several isolated LANs. Typical uses: separate staff, guest Wi-Fi, phones and servers without separate hardware.

IEEE **802.1Q** inserts a 4-byte **tag** after the source MAC:

| Field | Bits | Purpose |
|---|---|---|
| TPID | 16 | `0x8100`: "tagged" |
| PCP | 3 | Priority (QoS) |
| DEI | 1 | Drop eligible |
| VID | 12 | VLAN ID |

- The 12-bit VID allows 4096 values; 0 indicates priority tagging without a VLAN identifier and 4095 is reserved, leaving **4094 assignable VLAN IDs**. Equipment may support fewer active VLANs.
- Adding one tag to a maximum-size basic 1518-byte frame produces 1522 bytes; additional encapsulation has its own limits.
- An ordinary **access port** presents one untagged data VLAN to a host; voice VLANs, priority tags and vendor-specific configurations are exceptions.
- A **trunk port** carries many VLANs between switches (or to a router or hypervisor), usually with tags distinguishing VLANs. Depending on configuration, untagged traffic may use a native VLAN or be rejected; a native VLAN can also be tagged.
- Hosts in different VLANs cannot talk at layer 2 at all. Traffic between them must go through a **router** (or a layer 3 switch), where it can be filtered.

Large providers outgrew 4094. **802.1ad** ("QinQ") stacks a second tag (TPID `0x88A8`), and data centres use **VXLAN**, which carries Ethernet frames inside UDP with a 24-bit segment ID, allowing about 16 million.

## MTU

The **MTU** (maximum transmission unit) is the largest payload a link can carry in one frame. For standard Ethernet it is **1500 bytes**: the IP packet, not counting Ethernet's own 18 bytes of header and FCS.

- **Jumbo frames** raise the MTU, typically to about 9000 bytes. Fewer, larger frames can reduce per-packet work (interrupt moderation and offloads mean interrupts are not necessarily one per frame), and slightly less header overhead, so storage networks and data-centre fabrics often use them. They are not part of the IEEE standard, and every traversed link/interface must support the sizes actually sent, or the sender must adapt to a smaller path MTU; configured MTUs need not all be identical.
- An MTU **mismatch** can produce a black-hole failure if fragmentation or path-MTU adaptation does not resolve it: small packets (pings, TCP handshakes, short requests) work, but full-size packets are dropped. Connections open and then hang as soon as real data flows. Tunnels (VPNs, VXLAN) cause the same thing by quietly shrinking the effective MTU.

The IP module covers how hosts discover the path MTU and what happens when that discovery fails.

## Key takeaways
- An Ethernet frame is destination MAC, source MAC, EtherType, 46–1500 bytes of payload and a CRC-32 FCS: 64 to 1518 bytes, plus 20 bytes of preamble and gap on the wire.
- MAC addresses are 48-bit and flat; the I/G bit marks multicast and the U/L bit marks locally administered (including randomised) addresses.
- CSMA/CD with exponential backoff shared a cable, and set the 64-byte minimum frame. Modern full-duplex switched Ethernet doesn't use it.
- Switches learn source MACs, forward known destinations, flood unknown and broadcast frames, and age learned entries according to implementation and configuration.
- 802.1Q VLANs use a 12-bit ID (4094 usable) to split one switch fabric into isolated LANs; routing is needed between them.
- The standard MTU is 1500 bytes. Unresolved path-MTU problems can cause "small works, large hangs" failures.

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
