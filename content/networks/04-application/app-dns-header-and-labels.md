---
id: app-dns-header-and-labels
title: "DNS headers and length-prefixed names"
level: intermediate
minutes: 4
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

### What a resolver does with "no such name"

Two different negative answers are easy to confuse:

- **NXDOMAIN** (RCODE 3): the name does not exist at all, for any record type.
- **NODATA**: RCODE 0 (NOERROR) with an empty answer section. The name exists, but has no records of the type asked for, for example an AAAA query for a name that has only an A record.

Resolvers cache negative answers too (**negative caching**, RFC 2308), so a typo'd or missing name does not send a fresh query to the authoritative servers every time. The authoritative server puts the zone's **SOA record** in the authority section, and the negative answer may be cached for the smaller of the SOA record's own TTL and its MINIMUM field. An NXDOMAIN is cached for the name (any type); a NODATA answer only for that name and type. A negative answer without an SOA should not be cached.

The practical consequence: if someone looks up `new.example.com` just before you create it, their resolver can keep answering NXDOMAIN until that negative TTL runs out, even though the record now exists.

> [!analogy] Real-world analogy: A receptionist's "no such person" note
> You ask a receptionist to put you through to a new colleague. The staff list says nobody of that name works there, so the receptionist jots "no such person, recheck after lunch" and gives every later caller the same answer until lunchtime, even if the new colleague starts at 11.
>
> **How it maps:** The receptionist is the recursive resolver, the staff list is the authoritative zone, and "recheck after lunch" is the negative-caching time taken from the zone's SOA record. NXDOMAIN is "nobody of that name"; NODATA is "that person exists but has no desk phone".
>
> **Where it stops:** The resolver does not choose the time freely: it follows the SOA values in the answer (and may cap them further), and the note covers exactly the name, or name and type, that was asked.

### Names as labels

Names are not dotted strings on the wire. Each label is a length byte followed by that many bytes, ending with a zero-length root label:

```
www.example.com  becomes
03 77 77 77 07 65 78 61 6d 70 6c 65
03 63 6f 6d 00
```

A label is at most 63 bytes, and a whole name at most 255 bytes. The 63 comes from the length byte: its top two bits must be `00` (the pattern `11` marks a compression pointer, covered in the next unit), leaving six bits, which count up to 63.

## Key takeaways
- DNS has a twelve-byte header and four sections; names use length-prefixed labels.
- Flag fields describe query or response handling, while a label and whole name have separate length bounds.
- NXDOMAIN (no such name) and NODATA (no records of that type) are both cached for a time set by the zone's SOA record.

## Further reading
- [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035)
- [RFC 2308](https://www.rfc-editor.org/rfc/rfc2308)
- [RFC 4035](https://www.rfc-editor.org/rfc/rfc4035)
