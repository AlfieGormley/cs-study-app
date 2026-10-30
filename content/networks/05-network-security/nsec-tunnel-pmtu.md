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

The MSS to clamp to is the tunnel MTU minus the IP and TCP headers:

```formula reference
MSS = MTU − (H_IP + H_TCP)
where
MSS: maximum segment size: the most TCP payload in one segment, in bytes
MTU: the maximum transmission unit of the tunnel interface, in bytes
H_IP: the IP header without options: 20 bytes for IPv4, 40 bytes for IPv6
H_TCP: the TCP header without options, 20 bytes
In words: the TCP data that fits in one packet is the tunnel's packet size minus the IP and TCP headers.
```

For a 1,420-byte WireGuard interface carrying IPv4 TCP, that is 1,380 bytes of data per segment; over IPv6 the headers take 60 bytes instead of 40, and TCP options such as timestamps reduce the data further.

> [!analogy] Real-world analogy: a low bridge with no warning sign
> A lorry route passes under a low railway bridge. Normally a sign warns drivers and they take a lower vehicle next time. If someone removes the sign, small vans keep getting through, but every tall lorry is turned back at the bridge without the depot ever learning why, so it keeps sending tall lorries.
>
> **How it maps:** The bridge height is the tunnel's reduced path MTU, the tall lorries are full-size packets with Don't Fragment set, and the warning sign is the ICMP "packet too big" message. A firewall that blocks all ICMP removes the sign, producing a PMTU black hole: small requests work, large transfers stall. Clamping the MSS is telling the depot in advance to load only lower vehicles.
>
> **Where it stops:** A driver could stop and ask; a sender that never receives the error may simply retransmit the same oversized packet until it times out. And MSS clamping only reshapes TCP; UDP traffic and later path changes still need correct MTU settings and working ICMP.

## Key takeaways
- Small successful requests do not prove the path can carry full-size packets.
- Permit necessary Packet Too Big signalling and configure the tunnel MTU correctly.
- MSS clamping changes TCP’s advertised data budget and does not repair all UDP traffic.

## Further reading
- [RFC 4459: MTU and Fragmentation Issues with In-the-Network Tunneling](https://www.rfc-editor.org/rfc/rfc4459)
- [RFC 8201: Path MTU Discovery for IPv6](https://www.rfc-editor.org/rfc/rfc8201)
- [RFC 4821: Packetization Layer Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc4821)
