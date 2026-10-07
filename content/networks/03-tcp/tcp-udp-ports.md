---
id: tcp-udp-ports
title: UDP, ports and multiplexing
level: basic
minutes: 11
summary: What the transport layer adds on top of IP, the 8-byte UDP header, how ports and 5-tuples route data to the right socket, and when UDP beats TCP (DNS, games, QUIC).
---

IP delivers packets from one **host** to another. But a host can run many programs at once: a browser, a DNS resolver, an SSH session, a game. When a packet arrives, something has to decide which program gets it.

That is the transport layer's most basic job: **multiplexing** (many applications sharing one IP address on the way out) and **demultiplexing** (handing each arriving packet to the right application). The tool for it is the **port number**.

Two widely used Internet transports are TCP and UDP. Base **UDP** offers datagram boundaries, ports and a checksum, with few additional services. **TCP** adds a reliable, ordered byte stream with flow and congestion control. This module starts with UDP as a simple datagram transport; transport protocols need not all use the same multiplexing mechanism.

## Ports

A port is a 16-bit number, so 0 to 65,535. IANA splits the range into three bands:

| Range | Name | Examples |
|---|---|---|
| 0–1023 | System (well-known) | 22 SSH, 53 DNS, 443 HTTPS |
| 1024–49151 | User (registered) | 3306 MySQL, 5432 Postgres |
| 49152–65535 | Dynamic (ephemeral) | Client-side ports |

A server often **binds** to a known service port; discovery mechanisms can also advertise dynamically chosen ports. Port zero is reserved in the IANA registry, and asking a socket API to bind port zero typically requests automatic allocation. A client usually lets the OS pick a temporary **ephemeral port** for its end. Operating systems don't all follow the IANA range: Linux picks ephemeral ports from **32768–60999** by default (`net.ipv4.ip_local_port_range`), which spans 28,232 numbers before reserved ports, existing uses and configuration changes are considered.

On Unix, binding to ports below 1024 traditionally needs root (on Linux, typically `CAP_NET_BIND_SERVICE`, with the privileged-port threshold configurable per network namespace). That rule is a historical trust signal, not security.

## The UDP header

UDP ([RFC 768](https://www.rfc-editor.org/rfc/rfc768), 1980) is three pages long. Its header is 8 bytes:

```
 0      7 8     15 16    23 24    31
+--------+--------+--------+--------+
|   Source port   |    Dest port    |
+--------+--------+--------+--------+
|     Length      |    Checksum     |
+--------+--------+--------+--------+
|        data (payload) ...         |
+-----------------------------------+
```

- **Source port**: a reply-port hint when supplied; RFC 768 permits zero when unused. Application protocols can impose additional requirements.
- **Destination port**: which socket on the receiver gets this datagram.
- **Length**: header plus data, in bytes; at least 8 for an ordinary datagram. IPv6 jumbograms use the exception described below.
- **Checksum**: the 16-bit one's complement of the one's-complement sum over the header, the data and a **pseudo-header** of source IP, destination IP, protocol number and UDP length. Including addresses helps detect accidental misdelivery, but the checksum does not detect every error and provides no authentication.

The checksum is optional over IPv4 (a value of 0 means "not computed") and normally **required over IPv6**. RFC 6935/6936 permit narrowly constrained zero-checksum tunnel modes; ordinary IPv6 applications cannot simply disable it.

For ordinary UDP, the 16-bit length field bounds header plus payload at 65,535 bytes. IPv6 jumbograms are a specified exception (RFC 2675), using UDP length zero when required. Over IPv4, with a 20-byte IP header, the largest payload is 65,535 − 20 − 8 = **65,507 bytes**. An IP packet larger than the path MTU may be fragmented where allowed, rejected locally, or dropped with an ICMP error. Linux UDP normally uses PMTU discovery and can return `EMSGSIZE`. IPv6 routers do not fragment. Reassembly needs all fragments, so UDP applications should manage payload sizes using path and protocol constraints rather than assume one universal safe size.

> [!note] What UDP does not do
> Base UDP provides no handshake, acknowledgements, retransmission, ordering, flow control or congestion control. Datagrams may be lost, duplicated or reordered. Ordinary datagram socket calls preserve message boundaries; a too-small receive buffer can truncate a message and discard its remainder. A successful send is not proof of remote delivery.

RFC 9868 (October 2025) defines UDP transport options after the user-data area; it does not enlarge the base eight-byte header. This lesson describes ordinary datagrams without those options or socket segmentation/coalescing extensions.

## Demultiplexing: sockets and 5-tuples

An application talks to the transport layer through a **socket**. The kernel needs a rule for choosing which socket an arriving packet belongs to. UDP and TCP use different rules.

### UDP: match on the destination

An unconnected IPv4 UDP socket bound to `0.0.0.0:53` can receive datagrams addressed to port 53 across local IPv4 addresses. Filtering, competing specific/reuse bindings, multicast membership and implementation rules can affect delivery. A DNS server can use one bound UDP socket for requests from many different client endpoints, reading each sender's address from `recvfrom()`.

```python
import socket

s = socket.socket(socket.AF_INET,
                  socket.SOCK_DGRAM)
s.bind(("127.0.0.1", 9999))
while True:
    data, addr = s.recvfrom(2048)
    s.sendto(data.upper(), addr)
```

The echo example binds loopback and truncates received datagrams above 2,048 bytes; it is a small demonstration, not a production service.

Calling `connect()` on a UDP socket establishes a default peer and normally restricts received datagrams to it. It performs no UDP handshake; route lookup or neighbour resolution and socket error handling can still occur. API details, including whether explicit sends to other destinations are permitted, vary.

### TCP: match on the full 5-tuple

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
> A client connects repeatedly to one backend, `10.0.0.5:5432`. Four of the five fields are fixed; only the source port varies. With Linux's default range, with a single fixed source address and automatic allocation confined to that range, at most 28,232 distinct local ports are available before other reservations and constraints. TIME_WAIT can further restrict tuple reuse (lesson 2). Proxies hit this; fixes are connection pooling, extra source IPs, or more backend IPs.

## Why would anyone choose UDP?

TCP gives you reliability and ordering, but you pay in **latency** (a normal new-connection handshake and possible waits for retransmissions; extensions and connection reuse change this cost) and **control** (the kernel decides when to send and what to wait for). UDP is right when one of those costs is unacceptable.

### DNS: one question, one answer

A DNS lookup is usually a single small query and a single small response. With UDP the whole exchange takes **one round trip**. A fresh ordinary TCP connection adds a handshake; an already open connection can be reused, and TCP Fast Open can alter setup timing. Total resolution latency also includes DNS processing and any upstream queries.

Reliability is handled by the application: if no reply arrives within a timeout, the resolver asks again or tries another server. If a response is too big for UDP, the server sets the **TC (truncated)** flag and the client retries over TCP. EDNS(0) allows UDP responses bigger than the original 512-byte limit; DNS Flag Day 2020 recommended a 1,232-byte UDP payload limit (IPv6 minimum MTU 1,280 minus 40-byte base IPv6 and 8-byte UDP headers). This reduces fragmentation risk under those assumptions rather than proving every path can carry it.

### Real-time games and voice: stale data is useless

Consider a game sending independent full-state position snapshots at 60 Hz, about 16.7 ms apart. A new snapshot can supersede a lost one; delta updates and important game events can have different reliability requirements. TCP would **hold back** every later update until the lost one was retransmitted, delaying delivery of later bytes until the gap is repaired. The delay depends on detection, retransmission and buffering; the whole game loop need not freeze. That is **head-of-line blocking**, and independent deadline-sensitive updates can prefer skipping stale data to waiting for that gap.

Voice and video calls (RTP over UDP) work the same way: a late frame may be concealed or discarded, but timely retransmission and forward error correction can also help. RFC 4588 specifies RTP retransmission; media deadlines determine its usefulness.

### QUIC: build your own transport

QUIC ([RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)), the transport under HTTP/3, uses UDP; HTTP/3 commonly uses **port 443**, but QUIC is not restricted to that port. QUIC provides its own loss recovery, stream reliability, congestion control and protected transport, and can be implemented in user space. UDP is used not because QUIC wants unreliability, but because using existing UDP socket support can ease endpoint and middlebox deployment. UDP is neither the only permitted non-TCP transport nor guaranteed to pass every path. Lesson 6 covers why.

### Others

Examples using UDP include DHCPv4 initial discovery, conventional NTP/SNMP exchanges, UDP syslog, multicast media and WireGuard. Several of these application families also define other transports; “syslog” alone does not imply UDP.

## Pitfalls of UDP

- **You own congestion control.** UDP will happily send faster than the network can carry, hurting everyone. [RFC 8085](https://www.rfc-editor.org/rfc/rfc8085) requires applications to account for congestion and describes suitable control or rate-limiting behaviour for different traffic patterns; low-volume applications are not universally exempt.
- **Amplification attacks.** With no handshake, an attacker can spoof a victim's source address and send small queries to open servers that reply with much bigger responses. Cloudflare documented large amplification from exposed Memcached UDP services in 2018. Amplification depends on the request, stored response and counting of protocol overhead; the attack does not follow merely from choosing UDP.
- **NAT and firewalls.** Idle mapping lifetimes vary. RFC 4787 specifies a normal minimum of two minutes, with a defined exception for some well-known destination ports; actual equipment may differ. Applications needing inbound reachability must account for the relevant timeout and keepalive policy. Some corporate networks block UDP outright, so clients supporting HTTP/2 or HTTP/1.1 can fall back to TCP; a QUIC-only application has no automatic TCP fallback.
- **Fragmentation.** Oversized datagrams may fail locally or require permitted fragmentation. Fragment loss or filtering can prevent reassembly; UDP does not retransmit the missing data.

## Key takeaways
- The transport layer multiplexes many applications onto one IP address using 16-bit port numbers.
- UDP adds only ports, a length and a checksum (8 bytes) to IP. Datagrams keep their boundaries but may be lost, duplicated or reordered.
- Unconnected UDP delivery is primarily selected by local endpoint, while connected sockets can also match the peer; TCP connections are identified by the full 5-tuple, so one server port can serve many clients.
- With one fixed source address and automatic allocation confined to a range, simultaneous connections to one destination are limited by that source-port pool (28,232 numbers in the documented default Linux allocation range, before other constraints).
- Choose UDP when a handshake or head-of-line blocking costs more than the reliability is worth: DNS, real-time media and games, and protocols like QUIC that build their own transport.
- With UDP you take on congestion control, amplification risk and NAT timeouts yourself.

## Further reading
- [RFC 768: User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768)
- [RFC 8085: UDP Usage Guidelines](https://www.rfc-editor.org/rfc/rfc8085)
- [User Datagram Protocol — Wikipedia](https://en.wikipedia.org/wiki/User_Datagram_Protocol)
- [Ephemeral port — Wikipedia](https://en.wikipedia.org/wiki/Ephemeral_port)
- [RFC 6335: IANA port number procedures](https://www.rfc-editor.org/rfc/rfc6335)
- [Memcrashed: amplification attacks from port 11211 — Cloudflare blog](https://blog.cloudflare.com/memcrashed-major-amplification-attacks-from-port-11211/)

> [!note] Scope and omitted evidence
> This lesson does not claim universal game update rates, media packet sizes, NAT timeouts, socket capacity or loss-recovery latency. Those require a specified implementation or measurement. Advanced UDP options and offload APIs are noted but not taught in detail here.

- [Linux UDP socket semantics](https://man7.org/linux/man-pages/man7/udp.7.html)
- [Linux IP sysctl defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
- [RFC 6935: IPv6 UDP checksum exceptions](https://www.rfc-editor.org/rfc/rfc6935)
- [RFC 2675: IPv6 jumbograms](https://www.rfc-editor.org/rfc/rfc2675)
- [RFC 9868: UDP transport options](https://www.rfc-editor.org/rfc/rfc9868)
- [RFC 4588: RTP retransmission](https://www.rfc-editor.org/rfc/rfc4588)
- [DNS Flag Day 2020 guidance](https://www.dnsflagday.net/2020/)
