---
id: ip-ipv4
title: IPv4, fragmentation and ICMP
level: basic
minutes: 14
summary: The IPv4 header field by field, what TTL is really for, how fragmentation and Path MTU Discovery work, and how ping and traceroute use ICMP.
---

The **Internet Protocol** (IP) has one job: get a packet from one host to another, across any number of networks, on a best-effort basis. It does not promise delivery, ordering or protection against duplicates. Those are left to the layers above (TCP) or to the application.

That modesty is the point. Because IP asks so little of the networks underneath, it runs over Ethernet, Wi-Fi, 4G, fibre and satellite links alike. Basic forwarding examines the IP header and a forwarding table; real routers also apply validation, queueing and policy.

The unit IP moves is a **datagram** (often just called a packet). Each one carries its own source and destination address and is routed independently. Two packets from the same download can take different paths.

## The IPv4 header

Every IPv4 datagram starts with a header of at least 20 bytes. Here it is, 32 bits per row:

```
0       8       16      24      31
+---+---+-------+---------------+
|Ver|IHL|DSCP|EC|  Total Length |
+---+---+-------+---+-----------+
| Identification    |Flg|FragOff|
+-------+-------+---+-----------+
|  TTL  | Proto |   Checksum    |
+-------+-------+---------------+
|        Source address         |
+-------------------------------+
|      Destination address      |
+-------------------------------+
|   Options (0 to 40 bytes)     |
+-------------------------------+
```

Field by field:

| Field | Bits | Purpose |
|---|---|---|
| Version | 4 | Always 4 |
| IHL | 4 | Header length in 32-bit words |
| DSCP / ECN | 6 / 2 | QoS class, congestion marks |
| Total Length | 16 | Header + data, in bytes |
| Identification | 16 | Groups fragments |
| Flags | 3 | Reserved, DF, MF |
| Fragment Offset | 13 | Position, in 8-byte units |
| TTL | 8 | Hop budget |
| Protocol | 8 | What's inside |
| Header Checksum | 16 | Header integrity only |
| Source / Dest | 32 each | Addresses |

A few details worth knowing:

- **IHL** counts 4-byte words, so the usual value is 5 (20 bytes) and the maximum is 15 (60 bytes). Options add header bytes and can encounter filtering or slower processing, depending on the option and equipment.
- **Total Length** is 16 bits, so a datagram can be at most 65,535 bytes. Basic Ethernet commonly carries 1,500-byte IP packets, but other links, jumbo configurations and encapsulations have different MTUs.
- **Protocol** tells the receiver which handler gets the payload: 1 is ICMP, 6 is TCP, 17 is UDP.
- **DSCP** (Differentiated Services Code Point) marks traffic classes, for example "expedited forwarding" for voice. **ECN**, when supported by endpoints and the network, permits congestion marking of eligible packets; it does not eliminate all packet drops.
- The **checksum** covers the header only, not the data. Because every router decrements TTL, a forwarding router must update it, possibly incrementally. IPv6 has no corresponding header checksum.

### Reading a header in Python

```python
import struct, socket

def parse_ipv4(pkt):
    # Header only; no payload validation.
    if len(pkt) < 20:
        raise ValueError("short header")
    version, ihl = pkt[0] >> 4, pkt[0] & 15
    if version != 4 or ihl < 5:
        raise ValueError("bad version/IHL")
    if len(pkt) < ihl * 4:
        raise ValueError("missing options")
    (vihl, tos, total, ident, ff,
     ttl, proto, csum, src, dst) = (
        struct.unpack("!BBHHHBBH4s4s",
                      pkt[:20]))
    if total < ihl * 4:
        raise ValueError("bad total length")
    return {
        "version": vihl >> 4,
        "ihl_bytes": (vihl & 0xF) * 4,
        "total_len": total,
        "DF": bool(ff & 0x4000),
        "MF": bool(ff & 0x2000),
        "offset": (ff & 0x1FFF) * 8,
        "ttl": ttl,
        "proto": proto,
        "src": socket.inet_ntoa(src),
        "dst": socket.inet_ntoa(dst),
    }

hdr = bytes.fromhex(
    "45000054abcd40004001bd1e"
    "c0a8010508080808")
print(parse_ipv4(hdr))
```

This prints version 4, a 20-byte header, total length 84, DF set, MF clear, offset 0, TTL 64, protocol 1 (ICMP), from `192.168.1.5` to `8.8.8.8`. This is a synthetic header illustrating a packet with an 8-byte ICMP header and 56 data bytes. Source address, identification, TTL and options depend on configuration; it is not a capture of a universal `ping` default. This parser extracts fields and validates basic lengths, but does not validate the checksum, option contents or complete payload.

## TTL: a hop budget

**Time To Live** is specified in seconds, but each forwarding router must decrement it by at least one. This also makes it a **hop-count limit**, without requiring a measurement of router queueing times.

A forwarding router decrements TTL by at least one. If it expires, the router discards the packet and normally sends ICMP **Time Exceeded**, subject to the rules suppressing errors for certain packets and to rate limiting.

Why bother? Transient routing loops can occur while routers disagree about the topology (see the interior routing lesson). Without TTL, forwarding has no hop-count expiry, though congestion or faults can still drop packets. With initial TTL at most 255 and compliant forwarding, an ordinary datagram cannot be forwarded indefinitely. Tunnel encapsulation uses its own outer TTL and needs separate consideration.

The sender chooses the initial TTL. If it is known to be 64 and each router subtracts exactly one without rewriting or encapsulation, arrival at 52 means 12 forwarding hops. An observed TTL alone does not establish the starting value or identify an operating system.

> [!note] Content omitted after review
> A universal OS-default table and Internet hop-count range are omitted because they depend on platform versions, configuration and measurements not established here.

## Fragmentation

An IP interface's **maximum transmission unit** (MTU) is the largest IP packet it supports without IP fragmentation. Link-specific mechanisms may fragment below IP. Basic Ethernet commonly uses 1,500 bytes. PPPoE plus PPP consumes 8 bytes within its Ethernet payload, giving 1,492 unless larger payload support is negotiated as in RFC 4638. Encapsulation reduces the inner MTU for a fixed outer path MTU.

If a router must forward a datagram bigger than the next link's MTU, IPv4 gives it two choices:

1. **Fragment** it into smaller datagrams, if the **DF** (Don't Fragment) flag is clear.
2. **Drop** it if DF is set, and report ICMP "Fragmentation Needed" when error-generation and rate rules permit.

In ordinary IP forwarding, reassembly is performed at the **destination**, not as a normal transit-router step. Firewalls/NATs may track or reassemble fragments for their separate functions, and a tunnel endpoint is the destination of the outer packet. Each fragment has its own IP header; option-copy rules mean not every option appears in every fragment. Fragments share **Identification**, carry an **offset** in 8-byte units and have **MF** set unless they contain the end of the original payload.

> [!example] Fragmenting 4,000 bytes over a 1,500-byte link
> A datagram has a 20-byte header and 3,980 bytes of data. Each fragment can carry 1,500 − 20 = 1,480 data bytes (a multiple of 8, as required).
>
> - Fragment 1: 1,480 bytes, offset 0, MF = 1
> - Fragment 2: 1,480 bytes, offset 185 (1,480 ÷ 8), MF = 1
> - Fragment 3: 1,020 bytes, offset 370, MF = 0
>
> Check: 1,480 + 1,480 + 1,020 = 3,980. Total lengths on the wire are 1,500, 1,500 and 1,040.

```python
def fragment(data_len, mtu, hdr=20):
    # Unfragmented, DF-clear input.
    # Equal headers; no option-copy logic.
    sizes = (data_len, mtu, hdr)
    integer = all(type(v) is int
                  for v in sizes)
    if not integer:
        raise ValueError("not integers")
    if (hdr < 20 or hdr > 60 or hdr % 4
            or data_len < 0
            or data_len + hdr > 65535
            or mtu < hdr):
        raise ValueError("invalid sizes")
    capacity = mtu - hdr
    if data_len <= capacity:
        yield 0, data_len, False
        return
    per = capacity // 8 * 8
    if per == 0:
        raise ValueError("MTU too small")
    off = 0
    while off < data_len:
        left = data_len - off
        size = min(left, capacity)
        if left > capacity:
            size = per
        mf = off + size < data_len
        yield off // 8, size, mf
        off += size

for f in fragment(3980, 1500):
    print(f)
# (0, 1480, True)
# (185, 1480, True)
# (370, 1020, False)
```

### Why fragmentation is avoided

Fragmentation works, but it is bad news in practice:

- **Loss amplification.** Lose any one fragment and the whole datagram is useless. IP itself has no fragment retransmission. Higher-layer or link-layer recovery is a separate mechanism.
- **The first fragment starts with the transport header.** A tiny first IPv4 fragment need not hold the complete TCP header. Later fragments normally lack ports, complicating stateless classification; stateful devices can associate fragments, while some policies drop them.
- **Reassembly costs memory** at the receiver and is a classic denial-of-service target (overlapping-fragment attacks, fragment floods).
- **ID wrap-around.** At high speeds the 16-bit Identification wraps quickly, risking fragments from different datagrams being stitched together.

IPv6 takes the lesson to heart: routers **never** fragment. Only the sending host may, using an extension header, and every IPv6 link must present an MTU of at least 1,280 bytes to IPv6, using fragmentation below IPv6 if the physical link needs it.

## Path MTU Discovery

The better approach is for the sender to learn the smallest MTU on the path (the **path MTU**) and send datagrams that fit. That is **Path MTU Discovery** (PMTUD, RFC 1191):

1. The sender sets **DF** on every packet and starts with its own link MTU.
2. A router that cannot forward a packet drops it and returns ICMP type 3, code 4 ("Fragmentation Needed and DF set"), which an RFC 1191 router fills with the next-hop MTU. Older messages may report zero and require fallback estimation.
3. The sender lowers its path estimate; retransmission or repacketisation depends on the transport/application. IP itself does not promise to resend.

```
Host        R1          R2        Server
 |  1500,DF  |           |           |
 |---------->|  1500,DF  |           |
 |           |---------->| MTU 1400! |
 |           |  ICMP 3/4 |           |
 |<----------------------| mtu=1400  |
 |  1400,DF  |           |           |
 |---------------------------------->|
```

IPv6 does the same with ICMPv6 **Packet Too Big**.

### The PMTUD black hole

Classic ICMP-based PMTUD depends on error feedback reaching the sender. If that feedback is blocked and no effective probing/fallback recovers, a **black hole** can result: the TCP handshake works (small packets), but as soon as full-size data packets are sent, they vanish silently. Users see web pages that start loading and then hang.

Common fixes:

- **Permit necessary ICMP errors.** IPv4 type 3/code 4 and ICMPv6 type 2 carry MTU feedback. ICMPv6 also supports essential functions such as neighbour discovery; treat message types appropriately rather than applying a blanket rule.
- **MSS clamping.** Routers on tunnels or PPPoE links rewrite the TCP **MSS** option in SYN packets to limit what the receiving peer sends. Bidirectional coverage requires handling MSS advertisements in both directions; MSS is not one jointly negotiated value. For inner IPv4 with fixed 20-byte IP/TCP headers, a 1,492-byte IP MTU gives MSS 1,452. MSS does not constrain UDP; senders must also account for any options when forming packets (RFC 6691).
- **Packetization Layer PMTUD** (RFC 4821, and RFC 8899 for datagram protocols like QUIC) probes with progressively larger packets and watches for loss, without relying on ICMP.

## ICMP: IP's error and diagnostic channel

The **Internet Control Message Protocol** (ICMP, RFC 792) rides inside IP (protocol 1). Routers and hosts use it to report problems and answer probes. Each message has a **type** and a **code**:

| Type | Name | Used by |
|---|---|---|
| 0 | Echo Reply | ping |
| 3 | Destination Unreachable | errors, PMTUD |
| 8 | Echo Request | ping |
| 11 | Time Exceeded | TTL expiry or reassembly timeout |

The IPv4 errors discussed here quote the offending IP header and at least the first 8 bytes of its payload, so the sender can match the error to the right connection (for a first fragment carrying TCP or UDP, these include the ports). The returned data cannot exceed what was actually available.

To avoid storms, hosts never send an ICMP error about an ICMP error, about a fragment other than the first, or about a broadcast. Routers also **rate-limit** the ICMP they generate.

### ping

`ping` sends ICMP Echo Requests and measures reply **round-trip time**. A reply establishes that this probe/response exchange worked; it does not establish application service health. A lost reply does not prove the host is down: many hosts and firewalls drop echo requests.

### traceroute: abusing TTL on purpose

`traceroute` discovers the routers along a path by sending probes with deliberately small TTLs:

1. Send a probe with TTL = 1. The first router decrements it to 0, drops it and returns **Time Exceeded**. Its source address reveals hop 1.
2. Send with TTL = 2. The second router replies. And so on.
3. Eventually a probe reaches the destination, which replies differently, and traceroute stops.

The classic Unix traceroute sends **UDP** probes to unlikely high ports (starting at 33434). The destination answers with ICMP **Port Unreachable** (type 3, code 3), which signals "you've arrived". Windows `tracert` sends ICMP Echo Requests instead and stops on an Echo Reply. Probe counts, starting ports and stopping rules depend on the implementation and options.

Illustrative output, not a live measurement:

```
$ traceroute example.net
 1  192.168.1.1     1.2 ms  1.0 ms  1.1 ms
 2  10.20.0.1       8.4 ms  8.1 ms  8.9 ms
 3  * * *
 4  203.0.113.9    15.3 ms 14.8 ms 15.0 ms
```

> [!warning] Reading traceroute honestly
> - `*` means no matching reply arrived before the timeout. The probe or reply may have been lost, filtered or rate-limited. Later replies show some probes got further, not that every packet took the same path or that forwarding is faultless.
> - Each displayed time is a round trip to the responding interface, including reply generation and the return path. Differences between hops do not isolate one link's delay.
> - Flow-preserving probes, such as Paris traceroute, reduce artefacts from per-flow load balancing. They cannot guarantee a fixed path through per-packet balancing or routing changes.

## Key takeaways
- IP is best-effort datagram delivery; reliability lives above it.
- The IPv4 header, at least 20 bytes long, carries addresses, a TTL hop budget, a protocol number and fragmentation fields; its checksum covers the header only.
- TTL stops packets looping for ever; forwarding routers decrement it and normally report expiry through ICMP, subject to suppression and rate limits.
- IPv4 non-final fragments carry multiples of 8 data bytes; the final fragment need not. Ordinary forwarding leaves reassembly to the destination. Fragmentation creates loss, state and middlebox complications.
- Blocking MTU feedback can cause PMTUD black holes. Permit necessary feedback; TCP MSS adjustment and PLPMTUD address different parts of the problem.
- traceroute sends probes with increasing TTL and reads the Time Exceeded replies.

## Further reading
- [RFC 791: Internet Protocol](https://www.rfc-editor.org/rfc/rfc791)
- [RFC 792: Internet Control Message Protocol](https://www.rfc-editor.org/rfc/rfc792)
- [RFC 1191: Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc1191)
- [RFC 4821: Packetization Layer Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc4821)
- [IP fragmentation — Wikipedia](https://en.wikipedia.org/wiki/IP_fragmentation)
- [Traceroute — Wikipedia](https://en.wikipedia.org/wiki/Traceroute)

- [RFC 8900: IP Fragmentation Considered Fragile](https://www.rfc-editor.org/rfc/rfc8900.html)
- [RFC 6864: IPv4 Identification field](https://www.rfc-editor.org/rfc/rfc6864)
- [RFC 4638: Larger PPPoE MTUs](https://www.rfc-editor.org/rfc/rfc4638.html)
- [RFC 6691: TCP options and MSS](https://www.rfc-editor.org/rfc/rfc6691.html)
- [RFC 1812: IPv4 router requirements](https://www.rfc-editor.org/rfc/rfc1812.html)
