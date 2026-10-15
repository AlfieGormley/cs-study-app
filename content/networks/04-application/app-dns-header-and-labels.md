---
id: app-dns-header-and-labels
title: "DNS headers and length-prefixed names"
level: intermediate
minutes: 3
sourceLesson: app-dns-wire
summary: "DNS has a twelve-byte header and four sections; names use length-prefixed labels."
---

DNS is a compact binary protocol. Its transaction identifiers and matching rules matter because a resolver must not accept an arbitrary arriving datagram as the answer to its query.

## The message format

Queries and responses share one format: a 12-byte **DNS header** followed by four sections.

```
+---------------------------+
| Header (12 bytes)         |
+---------------------------+
| Question   (QDCOUNT)      |
| Answer     (ANCOUNT RRs)  |
| Authority  (NSCOUNT RRs)  |
| Additional (ARCOUNT RRs)  |
+---------------------------+
```

The header:

```
Flags word (16 bits):
+--+------+--+--+--+--+---+-----+
|QR|Opcode|AA|TC|RD|RA| Z |RCODE|
| 1|  4   | 1| 1| 1| 1| 3 |  4  |
+--+------+--+--+--+--+---+-----+

Header: six 16-bit fields, in order
ID, flags, QDCOUNT, ANCOUNT,
NSCOUNT, ARCOUNT
```

- **ID**: chosen by the client and copied into the response. It is how a client matches answers to questions over connectionless UDP.
- **QR**: 0 query, 1 response. The **DNS opcode** is almost always 0 (standard query).
- **AA**: authoritative answer. **TC**: truncated. **RD**: recursion desired (set by stub clients). The **RA bit**: recursion available.
- The Z bits now include **AD** (authenticated data) and **CD** (checking disabled) for DNSSEC.
- **RCODE**: 0 NOERROR, 1 FORMERR, 2 SERVFAIL, 3 NXDOMAIN, 5 REFUSED.

### Names as labels

Names are not dotted strings on the wire. Each label is a length byte followed by that many bytes, ending with a zero-length root label:

```
www.example.com  becomes
03 77 77 77 07 65 78 61 6d 70 6c 65
03 63 6f 6d 00
```

A label is at most 63 bytes (the top two bits of the length must be `00`), and a whole name at most 255 bytes. The 63 comes from the six bits left for the length:

```formula
L_max = (2^6 − 1) B = 63 B
where
L_max: the longest label, in bytes (B)
^: "to the power of": 2^6 means 6 copies of 2 multiplied together, which is 64
B: bytes
In words: with two of the length byte's eight bits reserved, six bits remain, and six bits count from 0 to 63.
```

## Key takeaways
- DNS has a twelve-byte header and four sections; names use length-prefixed labels.
- Flag fields describe query or response handling, while a label and whole name have separate length bounds.

## Further reading
- [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035)
- [RFC 4035](https://www.rfc-editor.org/rfc/rfc4035)
