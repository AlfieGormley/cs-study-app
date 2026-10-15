---
id: tcp-reset-validation
sourceLesson: tcp-connections
title: Resets, refusal and challenge ACKs
level: intermediate
minutes: 3
summary: Resets, refusal and challenge ACKs, with worked examples and explicit assumptions.
---

## RST: aborting a connection

An accepted, valid RST tells the peer "this connection does not exist, or is being torn down now". A reset is not itself acknowledged and normally aborts the connection without a graceful FIN/TIME_WAIT sequence. Invalid RSTs can be ignored or challenged, and existing TIME_WAIT handling has additional rules. Common causes:

- **SYN to a port nobody listens on**: normal unfiltered TCP processing replies with RST, which the client can report as `ECONNREFUSED` ("connection refused"). If a firewall silently drops the SYN instead, the client sees a timeout.
- **Segment for an unknown connection**: for example after a server reboots and forgets its connections. The client can receive a reset once traffic reaches the rebooted peer; the exact API error depends on state and operations.
- **Abortive close**: on Linux, enabled `SO_LINGER` with a timeout of 0, then `close()`, sends RST instead of FIN. Load balancers sometimes do this to avoid TIME_WAIT.
- **Closing with unread data**: Linux sends RST if the application closes a socket while received data sits unread in its buffer, because that data will never be delivered.
- **Middleboxes**: firewalls and NATs that time out an idle connection may reset it.

A forged valid RST can abort a connection. For synchronized connections, [RFC 5961](https://www.rfc-editor.org/rfc/rfc5961) specifies accepting an RST only when its sequence number exactly matches the next expected sequence-space position. Opening-state reset validation follows separate rules. If it is merely in the window, the stack sends a **challenge ACK** instead, which can elicit a correctly sequenced reset from a peer that has lost the connection. This is a robustness check, not cryptographic authentication; rate limits and side channels affect practical attack resistance.

## Key takeaways

- A valid accepted reset normally aborts a connection rather than completing a FIN exchange.
- A refused SYN and a silently dropped SYN produce different observable outcomes.
- RFC 5961 challenges an in-window but inexact reset instead of accepting it as an exact reset.

## Further reading

- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [SYN cookies — Wikipedia](https://en.wikipedia.org/wiki/SYN_cookies)
- [Coping with the TCP TIME-WAIT state on busy Linux servers — Vincent Bernat](https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)
- [RFC 6528: Defending against Sequence Number Attacks](https://www.rfc-editor.org/rfc/rfc6528)
- [Linux TCP configuration defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)

> [!note] Content omitted after review
> A universal request-socket byte size, original cookie bit layout, historical attacker attribution and unconditional timeout/option guarantees are omitted because this pass did not establish adequate implementation-dependent evidence. Cookie handling and state diagrams here are teaching models, not an exhaustive TCP implementation.
