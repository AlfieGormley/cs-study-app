---
id: nf-ethernet-frame-rate
sourceLesson: nf-ethernet
title: Ethernet frames and packet rate
level: intermediate
minutes: 3
summary: Explain padding, frame boundaries and why small frames stress packet-processing capacity.
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
- The **FCS** is a CRC-32 over the destination address through payload and pad (including any tags), excluding preamble/SFD and the FCS itself. A receiver that finds a mismatch silently drops the frame. Ordinary full-duplex Ethernet MAC service does not acknowledge/retransmit a frame after an FCS failure; recovering from loss is left to higher layers (the error-control units).

Use a nominal **inter-frame gap** of 96 bit-times (12 byte-times) for the steady-rate calculations here. Some PHYs use alignment/deficit-idle rules; gap timing is not literal extra payload bytes. So each frame costs 20 extra bytes of wire time: 8 for preamble and SFD, and 12 for the gap.

> [!example] Packet rates
> A minimum frame occupies 64 + 20 = 84 bytes of wire time. At 1 Gbit/s that allows up to about **1.49 million Ethernet frames per second**; at full size it is about 81,000 Ethernet frames per second. Router and firewall vendors quote "packets per second" figures for exactly this reason: small packets are the hard case.

The most frames a link can carry each second is its bit rate divided by the bits each frame occupies on the wire, overhead included:

```formula reference
f_max = R / (b(F + H))
where
f_max: the maximum frame rate, in Ethernet frames per second
R: the link rate, in bits per second; 1 Gbit/s = 10⁹ bits per second
F: the frame size from destination address to FCS, in bytes; 64 for a minimum frame, 1518 for a full-size one
b: eight bits per byte, converting byte counts into bit counts
H: nominal wire overhead beyond the frame, expressed as 20 equivalent bytes of wire time for preamble, SFD and gap
In words: at a fixed link bit rate, smaller frames arrive more often, so processing capacity must be checked in frames per second as well as bits per second; count preamble and gap in the wire-time budget.
```

## Key takeaways
- An ordinary untagged frame spans 64–1518 bytes from destination MAC through FCS.
- Minimum frames require more packets per second at a fixed line rate.

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
