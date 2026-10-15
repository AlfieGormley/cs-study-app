---
id: nsec-tunnel-pmtu
title: Diagnosing tunnel MTU black holes
level: advanced
minutes: 3
summary: Small successful requests do not prove the path can carry full-size packets.
sourceLesson: nsec-vpns
---

A tunnel can authenticate correctly and still stall on large transfers. Its added headers reduce the inner IP packet budget. This unit follows what happens when the sender does not learn that smaller budget.

### When the MTU is wrong

If an inner packet exceeds the tunnel’s selected MTU, the encapsulating endpoint must handle that limit; implementations may fragment where permitted or reject it and report the smaller budget. At a forwarding router, an oversized IPv4 packet with Don’t Fragment set is dropped and can trigger an ICMP fragmentation-needed message; IPv6 routers do not fragment and use ICMPv6 Packet Too Big. The error lets the source adapt its packet size. This is **path MTU discovery** (PMTUD).

Firewalls that block all ICMP break it. The result is a **PMTU black hole**: the TCP handshake and small requests work, but anything large stalls. "SSH connects but `git clone` hangs" through a VPN is the classic symptom.

The usual fixes:

- Set the tunnel interface MTU correctly (using the actual underlay budget; wg-quick can infer an initial value).
- **Clamp the TCP MSS** at the tunnel edge to advertise an appropriate data budget. The maximum segment size (MSS) is how much TCP data fits in one packet once the IP and TCP headers are taken out (the formula follows this list). Senders must account for options, and an MSS clamp does not fix UDP or later path changes.
- Allow ICMP "packet too big" (ICMPv4 type 3 code 4, ICMPv6 type 2) through firewalls.

The MSS to clamp to, with minimum-size IPv4 and TCP headers:

```formula
MSS = MTU − (H_IP + H_TCP)
MSS = 1420 B − (20 B + 20 B) = 1380 B
where
MSS: maximum segment size: the most TCP payload in one segment, in bytes
MTU: the maximum transmission unit of the tunnel interface, in bytes; here 1,420
H_IP: the IPv4 header without options, 20 bytes (an IPv6 header is 40)
H_TCP: the TCP header without options, 20 bytes
B: bytes
In words: inside a 1,420-byte tunnel, each TCP segment can carry at most 1,380 bytes of data once the 40 bytes of IPv4 and TCP headers are subtracted.
```

Over IPv6 the subtraction is 60 bytes instead of 40, and TCP options such as timestamps reduce the data further.

## Key takeaways
- Small successful requests do not prove the path can carry full-size packets.
- Permit necessary Packet Too Big signalling and configure the tunnel MTU correctly.
- MSS clamping changes TCP’s advertised data budget and does not repair all UDP traffic.

## Further reading
- [RFC 4301: Security Architecture for the Internet Protocol](https://www.rfc-editor.org/rfc/rfc4301)
- [RFC 4303: IP Encapsulating Security Payload (ESP)](https://www.rfc-editor.org/rfc/rfc4303)
- [WireGuard: Next Generation Kernel Network Tunnel (whitepaper)](https://www.wireguard.com/papers/wireguard.pdf)
- [WireGuard: protocol and cryptography](https://www.wireguard.com/protocol/)
- [RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348)
- [RFC 4459: MTU and Fragmentation Issues with In-the-Network Tunneling](https://www.rfc-editor.org/rfc/rfc4459)
