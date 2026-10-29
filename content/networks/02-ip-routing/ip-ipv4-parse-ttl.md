---
id: ip-ipv4-parse-ttl
title: Parse a header and trace TTL
level: basic
minutes: 4
sourceLesson: ip-ipv4
summary: Extract IPv4 header fields in Python and interpret a TTL difference only when its assumptions hold.
---

The previous lesson described the header on paper. Here a short parser pulls the same fields out of real bytes, and the second half asks what the TTL field can and cannot tell you.

### Reading a header in Python

```python
import struct, socket

def parse_ipv4(pkt):
    # Header only; no payload validation.
    if len(pkt) < 20:
        raise ValueError("short header")
    # Split the first byte into two nibbles.
    version, ihl = pkt[0] >> 4, pkt[0] & 15
    if version != 4 or ihl < 5:
        raise ValueError("bad version/IHL")
    if len(pkt) < ihl * 4:
        raise ValueError("missing options")
    (vihl, tos, total, ident, ff,
     ttl, proto, csum, src, dst) = (
        # ! selects network byte order.
        struct.unpack("!BBHHHBBH4s4s",
                      pkt[:20]))
    if total < ihl * 4:
        raise ValueError("bad total length")
    return {
        "version": vihl >> 4,
        "ihl_bytes": (vihl & 0xF) * 4,
        "total_len": total,
        # Mask flags separately from offset.
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

This prints version 4, a 20-byte header, total length 84, DF set, MF clear, offset 0, TTL 64, protocol 1 (ICMP), from `192.168.1.5` to `8.8.8.8`. This is a synthetic header illustrating a packet with an 8-byte ICMP header and 56 bytes of payload. Source address, identification, TTL and options depend on configuration; it is not a capture of a universal `ping` default. This parser extracts fields and validates basic lengths, but does not validate the checksum, option contents or complete payload.

## TTL: a hop budget

**Time To Live** is specified in seconds, but each forwarding router must decrement it by at least one. This also makes it a **hop-count limit**, without requiring a measurement of router queueing times.

If TTL reaches zero, the router discards the packet and normally sends ICMP **Time Exceeded**, subject to the rules suppressing errors for certain packets and to rate limiting.

Why bother? Transient routing loops can occur while routers disagree about the topology (see the interior routing lesson). Without TTL, forwarding has no hop-count expiry, though congestion or faults can still drop packets. With initial TTL at most 255 and compliant forwarding, an ordinary datagram cannot be forwarded indefinitely. Tunnel encapsulation uses its own outer TTL and needs separate consideration.

The sender chooses the initial TTL. If you know that starting value, and each router subtracts exactly one without rewriting or encapsulation, the amount that has gone missing counts the routers crossed: a packet sent with 64 that arrives with 52 passed 12 routers. Hosts and layer 2 switches do not decrement TTL; only forwarding routers do.

Both assumptions matter. An observed TTL alone does not establish the starting TTL, the path length or the sender's operating system, because the starting value is configurable and some devices rewrite TTL.

> [!note] Content omitted after review
> A universal OS-default table and Internet hop-count range are omitted because they depend on platform versions, configuration and measurements not established here.

## Key takeaways
- The parser extracts fields and checks basic lengths, not checksum or payload validity.
- TTL is decremented by at least one by forwarding routers.
- A hop count follows from a TTL difference only with a known initial TTL and one decrement per hop.

## Further reading
- [RFC 791: Internet Protocol](https://www.rfc-editor.org/rfc/rfc791)
- [RFC 1812: IPv4 router requirements](https://www.rfc-editor.org/rfc/rfc1812.html)
- [Python struct module](https://docs.python.org/3/library/struct.html)
