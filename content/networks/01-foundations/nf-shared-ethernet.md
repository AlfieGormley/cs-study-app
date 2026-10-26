---
id: nf-shared-ethernet
sourceLesson: nf-ethernet
title: Collisions, backoff and full duplex
level: intermediate
minutes: 4
summary: Explain legacy CSMA/CD timing and why full-duplex links use different rules.
---

## CSMA/CD: how shared Ethernet worked

Original Ethernet put every host on one shared coaxial cable (later, one hub). Only one host could transmit at once, so they needed a rule for taking turns: **carrier-sense multiple access with collision detection**.

1. **Carrier sense**: listen; if someone is transmitting, wait.
2. When the line is idle, transmit.
3. **Collision detect**: while transmitting, listen. If the signal on the wire doesn't match what you're sending, another host started at nearly the same moment. Stop and send a 32-bit **jam signal** so everyone notices.
4. **Binary exponential backoff**: after each collision, wait a random whole number of **slot times** before retrying, still obeying carrier-sense rules. The range of possible waits doubles with every collision on this frame, up to a cap. At 10/100 Mbit/s the slot is 512 bit-times; historical half-duplex Gigabit uses 4096 bit-times. Give up after 16 attempts.

```formula reference
K ∈ {0, 1, …, 2^{min(n, 10)} − 1}
t_wait = K t_slot
where
K: the number of slot times to wait, chosen at random (each value equally likely)
∈: "is one of": K is picked from the set in braces
…: and every whole number in between
n: how many collisions this frame has suffered so far (1 after the first)
min: the minimum, the smaller of the two values; it stops the range growing after the 10th collision
t_wait: the backoff wait before trying again, in seconds
t_slot: the duration of one slot, in seconds: 512 bit-times, or 51.2 µs (microseconds), at 10 Mbit/s
In words: after the first collision wait 0 or 1 slots, after the second 0–3, after the third 0–7, and so on, doubling up to 0–1023 slots from the 10th collision onwards.
```

Backoff adapts to load: with two hosts colliding, after the first collision each picks 0 or 1, so they avoid each other half the time. Repeated collisions widen the range quickly.

### Why the minimum frame is 64 bytes

A sender only knows about a collision if it is still transmitting when the colliding signal gets back to it. The worst case is a collision at the far end of the network: the signal must travel there and back. So the transmission time of the shortest frame must be at least the maximum round-trip time:

```formula reference
L_min / R ≥ (2d_max) / v
where
L_min: the minimum frame length, in bits; 64 bytes = 512 bits
R: the link rate, in bits per second; 10 Mbit/s = 10⁷ bits per second
d_max: the largest distance between two hosts on the shared segment, in metres
v: the signal speed in the cable, in metres per second (about 2 × 10⁸ m/s)
≥: greater than or equal to
In words: sending the smallest frame must take at least as long as a signal needs to reach the far end and come back, so faster links need shorter networks or longer minimum frames.
```

At 10 Mbit/s, 64 bytes (512 bits) takes 51.2 µs to send. The **slot time**, propagation and repeater delays together constrain the collision domain; physical topology rules cannot be inferred from cable speed alone. At gigabit speeds, 512 bits takes only 0.512 µs (the link is a hundred times faster than 10 Mbit/s, so a frame takes a hundredth of the time), which would limit a shared segment to a few tens of metres; half-duplex gigabit worked around this with "carrier extension", an historical half-duplex mechanism distinct from modern full-duplex operation.

### Why it no longer matters

A common modern Ethernet arrangement is a **full-duplex** point-to-point link between a host and a switch port. Other Ethernet deployments include switch links and shared-medium PHYs. Each endpoint can send and receive concurrently. Some PHYs separate directions physically; 1000BASE-T uses both directions on the same four pairs with echo cancellation. A shared half-duplex collision domain is absent. CSMA/CD is switched off. 10 Gigabit Ethernet and faster do not support half duplex at all.

> [!warning] Duplex mismatch
> On legacy 10/100BASE-T links, if one end is forced to full duplex and the auto-negotiating peer detects speed but falls back to half duplex, the half-duplex side sees "collisions" whenever both send. The half-duplex side can back off and report late collisions; the full-duplex side may report FCS or alignment errors. Bidirectional throughput can suffer even when small pings succeed; exact counters and symptoms depend on timing and implementation. Use compatible settings, normally auto-negotiation at both ends. Do not generalise the legacy fallback behaviour to every Gigabit PHY; follow the equipment requirements.

## Key takeaways
- Legacy collision detection needs enough transmission time for a round-trip collision signal.
- Full-duplex Ethernet has no shared half-duplex collision domain or CSMA/CD backoff.

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
