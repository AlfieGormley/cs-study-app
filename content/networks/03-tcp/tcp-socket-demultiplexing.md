---
id: tcp-socket-demultiplexing
sourceLesson: tcp-udp-ports
title: UDP sockets and TCP connection tuples
level: basic
minutes: 3
summary: UDP sockets and TCP connection tuples, with worked examples and explicit assumptions.
---

## Demultiplexing: sockets and 5-tuples

An application talks to the transport layer through a **socket**. The kernel needs a rule for choosing which socket an arriving packet belongs to. UDP and TCP use different rules.

## UDP: match on the destination

An unconnected IPv4 UDP socket bound to `0.0.0.0:53` can receive datagrams addressed to port 53 across local IPv4 addresses. Filtering, competing specific/reuse bindings, multicast membership and implementation rules can affect delivery. A DNS server can use one bound UDP socket for requests from many different client endpoints, reading each sender's address from `recvfrom()`.

```python
import socket

s = socket.socket(socket.AF_INET,
                  socket.SOCK_DGRAM)
s.bind(("127.0.0.1", 9999))
while True:
    # Each read consumes one datagram.
    data, addr = s.recvfrom(2048)
    # Reply to this datagram's sender.
    s.sendto(data.upper(), addr)
```

The echo example binds loopback and truncates received datagrams above 2,048 bytes; it is a small demonstration, not a production service.

Calling `connect()` on a UDP socket establishes a default peer and normally restricts received datagrams to it. It performs no UDP handshake; route lookup or neighbour resolution and socket error handling can still occur. API details, including whether explicit sends to other destinations are permitted, vary.

## TCP: match on the full 5-tuple

A TCP connection is identified by its **5-tuple**:

```
(protocol, src IP, src port,
           dst IP, dst port)
```

A web server listening on port 443 has one listening socket, plus one **accepted socket per TCP connection**. Two separate connections from one client address can differ in source port; browser tabs can also share pooled connections:

```
TCP 198.51.100.7:51000 -> 203.0.113.5:443
TCP 198.51.100.7:51001 -> 203.0.113.5:443
```

Both arrive at the same server port, but they differ in one field, so they are different connections. This is why a server can handle hundreds of thousands of connections on a single port: capacity depends on resources such as memory, file descriptors, CPU and distinct connection tuples; one server port does not impose a 65,535-connection total limit.

> [!example] Ephemeral port exhaustion
> A client connects repeatedly to one backend, `10.0.0.5:5432`. Four of the five fields are fixed; only the source port varies. With Linux's default range, with a single fixed source address and automatic allocation confined to that range, at most 28,232 distinct local ports are available before other reservations and constraints. TIME_WAIT can further restrict tuple reuse (the connection-management units). Proxies hit this; fixes are connection pooling, extra source IPs, or more backend IPs.

## Key takeaways

- An unconnected UDP socket can receive messages from multiple senders; UDP connect does not perform a handshake.
- Accepted TCP connections share a listening port and are distinguished by their connection tuples.
- A UDP receive buffer that is too small can truncate a datagram rather than save its remainder for another read.

## Further reading

- [RFC 768: User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768)
- [RFC 8085: UDP Usage Guidelines](https://www.rfc-editor.org/rfc/rfc8085)
- [User Datagram Protocol — Wikipedia](https://en.wikipedia.org/wiki/User_Datagram_Protocol)
- [Ephemeral port — Wikipedia](https://en.wikipedia.org/wiki/Ephemeral_port)
- [RFC 6335: IANA port number procedures](https://www.rfc-editor.org/rfc/rfc6335)
- [Memcrashed: amplification attacks from port 11211 — Cloudflare blog](https://blog.cloudflare.com/memcrashed-major-amplification-attacks-from-port-11211/)
- [Linux UDP socket semantics](https://man7.org/linux/man-pages/man7/udp.7.html)
- [Linux IP sysctl defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
- [RFC 6935: IPv6 UDP checksum exceptions](https://www.rfc-editor.org/rfc/rfc6935)
- [RFC 2675: IPv6 jumbograms](https://www.rfc-editor.org/rfc/rfc2675)
- [RFC 9868: UDP transport options](https://www.rfc-editor.org/rfc/rfc9868)
- [RFC 4588: RTP retransmission](https://www.rfc-editor.org/rfc/rfc4588)
- [DNS Flag Day 2020 guidance](https://www.dnsflagday.net/2020/)
