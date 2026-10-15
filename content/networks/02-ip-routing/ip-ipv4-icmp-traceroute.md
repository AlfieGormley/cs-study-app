---
id: ip-ipv4-icmp-traceroute
title: Read ICMP and traceroute
level: basic
minutes: 4
sourceLesson: ip-ipv4
summary: Interpret ICMP errors, ping replies and traceroute output without overclaiming what they prove.
---

Interpret ICMP errors, ping replies and traceroute output without overclaiming what they prove.

## ICMP: IP's error and diagnostic channel

The **Internet Control Message Protocol** (ICMP, RFC 792) rides inside IP (protocol 1). Routers and hosts use it to report problems and answer probes. Each message has a **type** and a **code**:

| Type | Name | Used by |
|---|---|---|
| 0 | Echo Reply | ping |
| 3 | Destination Unreachable | errors, PMTUD |
| 8 | Echo Request | ping |
| 11 | Time Exceeded | TTL expiry or reassembly timeout |

The IPv4 errors discussed here quote the offending IP header and at least the first 8 bytes of its payload, so the sender can match the error to the right connection (for a first fragment carrying TCP or UDP, these include the ports). The returned data cannot exceed what was actually available.

To avoid storms, hosts never send an ICMP error about an ICMP error, about a fragment other than the first, or about a broadcast. Routers also apply **rate limiting** to the ICMP they generate.

### ping

`ping` sends ICMP Echo Requests and measures reply **round-trip time**. A reply establishes that this probe/response exchange worked; it does not establish the health of the network application. A lost reply does not prove the host is down: many hosts and firewalls drop echo requests.

### traceroute: abusing TTL on purpose

`traceroute` discovers the routers along a path by sending probes with deliberately small TTLs:

1. Send a probe with a TTL of 1. The first router decrements it to 0, drops it and returns **Time Exceeded**. Its source address reveals hop 1.
2. Send with a TTL of 2. The second router replies. And so on.
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
> - Each displayed time is a round trip to the responding interface, including reply generation and the network reply path. Differences between hops do not isolate one link's delay.
> - Flow-preserving probes, such as Paris traceroute, reduce artefacts from per-flow load balancing. They cannot guarantee a fixed path through per-packet balancing or routing changes.

## Key takeaways
- ICMP types and codes distinguish errors and Echo probes.
- Error suppression and rate limits mean silence does not prove a forwarding failure.
- Traceroute uses increasing TTL values; its displayed times include the network reply path.

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
