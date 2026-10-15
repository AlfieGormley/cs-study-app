---
id: tcp-handshake-sequence-space
sourceLesson: tcp-connections
title: Reading the TCP handshake
level: intermediate
minutes: 4
summary: Reading the TCP handshake, with worked examples and explicit assumptions.
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

The header is 20 bytes without options and at most 60 with them. The limit comes from the 4-bit **data offset** field, which gives the header length in 4-byte words:

```formula
H_max = D_max × 4 B = 15 × 4 B = 60 B
O_max = H_max − H_min = 60 B − 20 B = 40 B
where
H_max: the largest possible TCP header, in bytes (B)
D_max: the largest value a 4-bit field can hold, 15 (binary 1111)
O_max: the most space left for TCP options
H_min: the fixed part of the header, 20 bytes
B: bytes; one byte is 8 bits
In words: the header can be at most 15 four-byte words (60 bytes); 20 of those are fixed fields, so options get at most 40 bytes.
```

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

Applied to the trace above, rule 1 gives the numbers each side uses next:

```formula
N_c = ISN_c + 1 = 1000 + 1 = 1001
N_s = ISN_s + 1 = 5000 + 1 = 5001
where
N_c: the client's next sequence number after its SYN: the number of its first data byte, and the ACK number the server sends
ISN_c: the client's initial sequence number, 1000 in the trace
N_s: the server's next sequence number after its SYN+ACK, and the ACK number the client sends
ISN_s: the server's initial sequence number, 5000 in the trace
In words: a SYN uses up one sequence number, so each side's data starts one after its ISN, and that is the number the other side acknowledges.
```

The wraparound in rule 2 occurs because the sequence number is a 32-bit field. Arithmetic on it wraps round like a clock: after the largest 32-bit value comes 0 again.

```formula
N_next = (N + L) mod 2^32
(4,294,967,295 + 1) mod 2^32 = 0
where
N_next: the sequence number just after a segment: the ACK number that acknowledges it
N: the segment's sequence number (its first position)
L: how many sequence numbers the segment uses: its data bytes, plus 1 for a SYN and 1 for a FIN
mod: modulo, the remainder after dividing; "mod 2^32" divides by 4,294,967,296 (32 twos multiplied together) and keeps the remainder, so totals wrap back into the range 0 to 4,294,967,295
In words: add the segment's length to its first number; if the total passes the largest 32-bit value, wrap round to 0 and keep counting.
```

So the client's first data byte will be numbered 1001, and the server's 5001. The final ACK may carry data itself; clients often send the HTTP request or TLS ClientHello right behind it.

## Key takeaways

- The handshake exchanges and acknowledges both initial sequence numbers.
- Each SYN or FIN consumes one sequence position; ordinary ACK-only segments do not.
- Sequence arithmetic wraps at the end of the 32-bit space, and an ACK does not certify application processing.

## Further reading

- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [SYN cookies — Wikipedia](https://en.wikipedia.org/wiki/SYN_cookies)
- [Coping with the TCP TIME-WAIT state on busy Linux servers — Vincent Bernat](https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)
- [RFC 6528: Defending against Sequence Number Attacks](https://www.rfc-editor.org/rfc/rfc6528)
- [Linux TCP configuration defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
