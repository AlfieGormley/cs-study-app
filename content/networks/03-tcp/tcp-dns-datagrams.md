---
id: tcp-dns-datagrams
sourceLesson: tcp-udp-ports
title: Choosing UDP for DNS
level: basic
minutes: 3
summary: Why DNS asks its questions over UDP, and what happens when an answer is too big.
---

## Why would anyone choose UDP?

TCP gives you reliability and ordering, but you pay in **latency** (a normal new-connection handshake and possible waits for retransmissions; extensions and connection reuse change this cost) and **control** (the kernel decides when to send and what to wait for). UDP is right when one of those costs is unacceptable.

## DNS: one question, one answer

A DNS lookup is usually a single small query and a single small response. With UDP the whole exchange takes **one round trip**. A fresh ordinary TCP connection adds a handshake; an already open connection can be reused, and TCP Fast Open can alter setup timing. Total resolution latency also includes DNS processing and any upstream queries.

Reliability is handled by the application: if no reply arrives within a timeout, the resolver asks again or tries another server. If a response is too big for UDP, the server sets the **TC (truncated)** flag and the client retries over TCP. EDNS(0) allows UDP responses bigger than the original 512-byte limit; DNS Flag Day 2020 recommended a 1,232-byte UDP payload limit. The number comes from the smallest packet every IPv6 link must carry: 1,280 bytes, minus the 40-byte base IPv6 header and the 8-byte UDP header, leaves 1,232 bytes. A DNS message of that size fits in one packet on any IPv6 path when no extra headers or tunnels are added.

This reduces fragmentation risk under those assumptions rather than proving every path can carry it.

## Key takeaways

- A small DNS query/response can use one UDP round trip, with application retry policy supplying recovery.
- A truncated DNS response prompts TCP retry; EDNS advertises a larger UDP capacity.
- The 1,232-byte recommendation follows from minimal IPv6/UDP headers and the 1,280-byte IPv6 minimum MTU, with stated path assumptions.

## Further reading

- [DNS Flag Day 2020 guidance](https://www.dnsflagday.net/2020/)
- [RFC 8085: UDP Usage Guidelines](https://www.rfc-editor.org/rfc/rfc8085)
