---
id: nf-mac-identity
sourceLesson: nf-ethernet
title: Read MAC address bits
level: intermediate
minutes: 3
summary: Interpret individual/group and universal/local bits without treating an address as secure identity.
---

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

MAC addresses use **flat addressing**: they say nothing about where a device is. That is fine within a LAN but would not scale to the internet, which is why IP prefixes (hierarchically aggregated for routing, rather than a reliable geographical location) exist at layer 3.

## Key takeaways
- The lowest first-octet bit marks individual versus group addresses.
- Randomisation and local administration can conflict with allow-lists; MAC addresses are not authentication.

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
