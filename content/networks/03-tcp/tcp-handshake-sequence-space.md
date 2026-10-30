---
id: tcp-handshake-sequence-space
sourceLesson: tcp-connections
title: Reading the TCP handshake
level: intermediate
minutes: 4
summary: How SYN, SYN+ACK and ACK set up two sequence spaces, and why SYN and FIN each use up one number.
---

TCP offers a **reliable, ordered byte stream** between two endpoints. Normal establishment synchronises sequence spaces and checks bidirectional reachability; this is not cryptographic peer authentication. Data can accompany handshake segments, and extensions such as TCP Fast Open can allow early application delivery. Graceful closure acknowledges the byte stream in each direction, not application processing or durable storage of those bytes. That bookkeeping is **connection management**.

The rules come from RFC 793 (1981), now consolidated in [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293) (2022).

## The TCP header, briefly

The fields that matter for connection management:

- **Sequence number** (32 bits): the first sequence-space position in the segment; a SYN occupies its own position before any data.
- **Acknowledgement number** (32 bits): the next byte the sender expects to receive. Only valid when the ACK flag is set.
- **Flags**: `SYN` (synchronise sequence numbers), `ACK`, `FIN` (no more data from me), `RST` (abort), plus `PSH`, `URG`, `ECE`, `CWR`.
- **Window** (16 bits): flow control (the flow-control units).
- **Options**: MSS, window scale, SACK-permitted, timestamps. MSS, window scale and SACK permission are exchanged on SYN segments. Negotiated timestamps accompany later segments, and SACK blocks can appear on later ACKs.

The header is 20 bytes without options and at most 60 with them. The limit comes from the 4-bit **data offset** field, which gives the header length in 4-byte words: its largest value, 15, means 60 bytes, leaving at most 40 bytes for options after the 20 fixed bytes.

That 40-byte option budget is small, and options compete for it (the SACK unit shows SACK running into it).

## The three-way handshake

Each side picks an **initial sequence number** (ISN). The handshake exchanges and acknowledges both:

```
Client                       Server
  |  SYN seq=1000              |
  |--------------------------->|
  |                            |
  |  SYN+ACK seq=5000 ack=1001 |
  |<---------------------------|
  |                            |
  |  ACK seq=1001 ack=5001     |
  |--------------------------->|
  |  (data can now flow)       |
```

Two rules make the numbers work:

1. **SYN and FIN each consume one sequence number**, independently of any data carried in the same segment. That is why the server acknowledges 1001, not 1000.
2. The cumulative ACK identifies the next expected sequence-space position in that direction, going back to 0 after 4,294,967,296 positions (the modulo arithmetic is explained below). It acknowledges contiguous received stream data/control positions, not successful application processing.

Applied to the trace above, rule 1 explains every number: the client's SYN uses 1000, so its first data byte will be 1001 and the server acknowledges 1001; the server's SYN uses 5000, so the client acknowledges 5001.

The wraparound in rule 2 occurs because the sequence number is a 32-bit field. Arithmetic on it wraps round like a clock: after the largest 32-bit value, 4,294,967,295, comes 0 again. The general rule for where the next segment starts is:

```formula reference
N_next = (N + L) mod 2^32
where
N_next: the sequence number just after a segment: the ACK number that acknowledges it
N: the segment's sequence number (its first position)
L: how many sequence numbers the segment uses: its data bytes, plus 1 for a SYN and 1 for a FIN
mod: modulo, the remainder after dividing; "mod 2^32" divides by 4,294,967,296 (32 twos multiplied together) and keeps the remainder, so totals wrap back into the range 0 to 4,294,967,295
In words: the next sequence number is the segment's first number plus the data bytes it carries, plus one for a SYN and one for a FIN, wrapping back to 0 after 4,294,967,295.
```

The final ACK may carry data itself; clients often send the HTTP request or TLS ClientHello right behind it.

## Key takeaways

- The handshake exchanges and acknowledges both initial sequence numbers.
- Each SYN or FIN consumes one sequence position; ordinary ACK-only segments do not.
- Sequence arithmetic wraps at the end of the 32-bit space, and an ACK does not certify application processing.

## Further reading

- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
