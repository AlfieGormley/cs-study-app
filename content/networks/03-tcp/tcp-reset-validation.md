---
id: tcp-reset-validation
sourceLesson: tcp-connections
title: Resets, refusal and challenge ACKs
level: intermediate
minutes: 3
summary: What RST means, how refusal differs from silence, and how challenge ACKs blunt blind reset attacks.
---

## RST: aborting a connection

An accepted, valid RST tells the peer "this connection does not exist, or is being torn down now". A reset is not itself acknowledged and normally aborts the connection without a graceful FIN/TIME_WAIT sequence. Invalid RSTs can be ignored or challenged, and existing TIME_WAIT handling has additional rules. Common causes:

- **SYN to a port nobody listens on**: normal unfiltered TCP processing replies with RST, which the client can report as `ECONNREFUSED` ("connection refused"). If a firewall silently drops the SYN instead, the client sees a timeout.
- **Segment for an unknown connection**: for example after a server reboots and forgets its connections. The client can receive a reset once traffic reaches the rebooted peer; the exact API error depends on state and operations.
- **Abortive close**: on Linux, enabled `SO_LINGER` with a timeout of 0, then `close()`, sends RST instead of FIN. Load balancers sometimes do this to avoid TIME_WAIT.
- **Closing with unread data**: Linux sends RST if the application closes a socket while received data sits unread in its buffer, because that data will never be delivered.
- **Middleboxes**: firewalls and NATs that time out an idle connection may reset it.

A forged valid RST can abort a connection. For synchronized connections, [RFC 5961](https://www.rfc-editor.org/rfc/rfc5961) specifies accepting an RST only when its sequence number exactly matches the next expected sequence-space position. Opening-state reset validation follows separate rules. If it is merely in the window, the stack sends a **challenge ACK** instead, which can elicit a correctly sequenced reset from a peer that has lost the connection. This is a robustness check, not cryptographic authentication; rate limits and side channels affect practical attack resistance.

> [!analogy] Real-world analogy: A bank that calls back before cancelling
> A bank receives a letter asking it to close your account. If the letter quotes your exact reference number, it acts. If the reference is merely plausible, it rings you on the number it already holds to check; a genuine request will be confirmed, a forged one will not.
>
> **How it maps:** The cancellation letter is an RST; the exact reference is the next expected sequence number. An in-window but inexact RST gets a challenge ACK sent to the real peer, and only a peer that has really lost the connection answers with a correctly numbered reset.
>
> **Where it stops:** A bank verifies identity; TCP only checks sequence numbers, so an attacker who can see the traffic can still forge a valid reset. TCP also limits how many challenge ACKs it sends, so an attacker cannot use them to flood the real peer.

## Key takeaways

- A valid accepted reset normally aborts a connection rather than completing a FIN exchange.
- A refused SYN and a silently dropped SYN produce different observable outcomes.
- RFC 5961 challenges an in-window but inexact reset instead of accepting it as an exact reset.

## Further reading

- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
