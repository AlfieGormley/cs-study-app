---
id: app-dns-wire
title: DNS on the wire, DNSSEC and encrypted DNS
level: intermediate
minutes: 17
summary: The DNS message format byte by byte, name compression, EDNS and truncation, how cache poisoning works and is defended, DNSSEC's chain of signatures, and what DoT and DoH do and do not hide.
---

The System Design subject covered DNS from the outside: the resolution chain, record types, TTLs and using DNS to steer traffic. This lesson opens the messages. DNS is a compact binary protocol from 1987 ([RFC 1035](https://www.rfc-editor.org/rfc/rfc1035)), and most of its security story comes straight from its wire format: a small transaction ID space, traditionally unauthenticated transport and the checks required before caching a response. Resolvers must not simply trust whichever datagram arrives first.

## The message format

Queries and responses share one format: a 12-byte **header** followed by four sections.

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
- **QR**: 0 query, 1 response. **Opcode** is almost always 0 (standard query).
- **AA**: authoritative answer. **TC**: truncated. **RD**: recursion desired (set by stub clients). **RA**: recursion available.
- The Z bits now include **AD** (authenticated data) and **CD** (checking disabled) for DNSSEC.
- **RCODE**: 0 NOERROR, 1 FORMERR, 2 SERVFAIL, 3 NXDOMAIN, 5 REFUSED.

### Names as labels

Names are not dotted strings on the wire. Each label is a length byte followed by that many bytes, ending with a zero-length root label:

```
www.example.com  becomes
03 77 77 77 07 65 78 61 6d 70 6c 65
03 63 6f 6d 00
```

A label is at most 63 bytes (the top two bits of the length must be `00`), and a whole name at most 255 bytes.

### Building a query by hand

This builds an ordinary ASCII-label question, not a full resolver. It accepts an optional final dot, checks wire-length bounds, and uses a random transaction ID unless a test ID is supplied. Internationalised presentation names require a suitable IDNA conversion before this restricted encoder.

```python
import secrets, struct

def build_query(name, qtype=1, qid=None):
    if qid is None:
        qid = secrets.randbelow(65536)
    if (type(qid) is not int
            or not 0 <= qid <= 65535
            or type(qtype) is not int
            or not 0 <= qtype <= 65535):
        raise ValueError("bad field")
    if name == ".":
        labels = []
    else:
        if name.endswith("."):
            name = name[:-1]
        labels = [p.encode("ascii")
                  for p in name.split(".")]
        if any(not 1 <= len(p) <= 63
               for p in labels):
            raise ValueError("bad label")
    qname = b"".join(
        bytes([len(p)]) + p
        for p in labels) + b"\0"
    if len(qname) > 255:
        raise ValueError("name too long")
    header = struct.pack("!HHHHHH",
        qid, 0x0100, 1, 0, 0, 0)
    return header + qname + struct.pack(
        "!HH", qtype, 1)

q = build_query("example.com", qid=0xABCD)
print(len(q))  # 29
print(q[:4].hex(" "))  # ab cd 01 00
```

29 bytes: 12 of header, 13 of name (`07 example 03 com 00`) and 4 of type and class. A hypothetical reply with flags `0x8180` would decode as QR=1, RD=1, RA=1 and RCODE 0.

### Resource records and compression

Each answer is a **resource record** (RR): name, TYPE (16 bits), CLASS (16), TTL (32-bit seconds), RDLENGTH (16) and RDATA. An A record's RDATA is 4 bytes; AAAA's is 16.

Names repeat constantly in a response, so DNS uses **compression pointers**. A length byte whose top two bits are `11` is not a length: it and the next byte form a 14-bit offset into the message where the rest of the name can be found. An illustrative A answer could begin with this compressed owner name:

```
c0 0c  name: pointer to offset 12
00 01  TYPE A
00 01  CLASS IN
00 00 01 0e  TTL 270 s
00 04  RDLENGTH 4
xx xx xx xx  IPv4 address
```

Offset 12 is where the question's name starts, straight after the header, so `c0 0c` means "example.com". Parsers must guard against pointer loops; a self-referential pointer can otherwise cause an infinite loop or resource exhaustion. Parsers also need bounds and expanded-name-length checks.

## Size limits, EDNS and TCP

Classic DNS over UDP limits messages to **512 bytes**. If required response data does not fit, the server sets **TC** and a resolver can retry over **TCP** (port 53, with each message prefixed by a 2-byte length).

**EDNS(0)** ([RFC 6891](https://www.rfc-editor.org/rfc/rfc6891)) extends DNS without changing the header. The client adds an **OPT** pseudo-record to the additional section that advertises a larger UDP buffer size and carries flags such as **DO** ("DNSSEC OK", please include signatures) and options such as cookies and client subnet.

UDP datagrams exceeding path capacity can be fragmented, dropped or trigger an error, depending on IP version, flags and path. Fragment handling can create reliability and spoofing risks. The 2020 **DNS Flag Day** recommended an EDNS buffer of **1,232 bytes**, because 1,232 + 40 bytes of basic IPv6 header + 8 bytes of UDP equals 1,280. This reduces fragmentation risk with those assumptions; extension headers, tunnels and IPv4 paths can require different budgets. Larger required answers can fall back to TCP.

## Cache poisoning

A recursive resolver caches answers for their TTL. If an attacker gets a forged answer accepted, later matching lookups may receive poisoned cached data until expiry or replacement. Other caches, record types, validation and application authentication affect the result. That is **cache poisoning**.

For ordinary outstanding UDP queries, necessary response-matching checks include:

- the question (name, type, class),
- the transaction **ID**,
- the source IP and port it sent to, arriving at the **source port** it sent from.

An off-path attacker cannot see the query, so they must guess. With a fixed source port, if all other checked fields are known and the ID is uniform, the ID-match probability is **1 in 65,536** per distinct guess. Acceptance also depends on racing the real response and passing other checks.

### The Kaminsky attack (2008)

The old wisdom was that a poisoning attempt only worked when the target name was not already cached, so an attacker got one try per TTL. Dan Kaminsky removed that limit:

1. Make the resolver look up a fresh random name unlikely to have a cached answer: `x71.bank.example`.
2. Race the real answer with a flood of forged responses with guessed IDs.
3. Each forged response says "I don't know `x71`, but the name server for **bank.example** is `ns.bank.example` at **192.0.2.66**" (attacker-controlled), in the authority and additional sections.
4. If one wins, the resolver caches the attacker's server as authoritative for the whole zone.
5. If none wins, try `x72.bank.example` immediately. There is no TTL to wait for.

In a simplified model with 100 distinct guesses and only a uniform 16-bit ID unknown, p = 100 / 65,536 ≈ 0.153% per attempt. Independent attempts need about 454 trials for 50% success. This is probability arithmetic, not a measured attack duration; resolver caching and checks can change feasibility.

### Defences

- **Source port randomisation.** The emergency fix: pick a random UDP source port per query. For a hypothetical 28,000 independent uniformly selected ports and 16-bit ID, the joint space is 1,835,008,000 combinations. Actual resolver pools, NAT behaviour and predictability determine effective entropy; they need not equal the OS ephemeral range.
- **Bailiwick checking.** Restrict which supplied records can update cache entries under the responding server’s authority and the resolver’s delegation context. A response about `x71.bank.example` must not set records for `google.com`.
- **0x20 encoding.** Randomise the letter case of the query (`wWw.ExAmPlE.cOm`). With compatible servers that preserve question case and a resolver that checks it, randomising each independently chosen ASCII letter adds a bit to the guessing model. Not every server preserves case, and fallback policies matter.
- **DNS cookies** (RFC 7873) and TCP make some off-path spoofing harder, but do not provide DNSSEC’s signed-data chain or protect against every on-path attacker.
- **DNSSEC** cryptographically authenticates covered RRsets through a configured trust chain. Other authenticated transports protect their own endpoints and hops; these guarantees are different.

Port randomisation is not the end of the story. The 2020 **SAD DNS** attack used a side channel (the global rate limit on ICMP "port unreachable" replies in Linux) to discover which port a resolver was using, bringing back the guessing game on the 16-bit ID alone.

## DNSSEC: signed answers

DNSSEC adds **authenticity and integrity**, not confidentiality. A signed zone publishes signatures over covered RRsets, and a validating resolver checks the signatures up a chain to a key it already trusts.

New record types:

| Type | Holds |
|---|---|
| DNSKEY | The zone's public keys |
| RRSIG | A signature over an RRset |
| DS | Key tag, algorithm and digest fields binding a child owner name and DNSKEY, in the parent |
| NSEC / NSEC3 | RRsets used with signatures for authenticated denial of a name/type or delegation properties |

Signatures cover an **RRset** (records with the same owner name, class and type) and have an inception and expiry time, so signatures must be renewed before they expire; affected data becomes bogus for validators enforcing the chain if no valid signatures remain.

A split-key design uses a **KSK** to authenticate the DNSKEY RRset and a **ZSK** for other signed RRsets. These are operational roles, not mandatory two-key enforcement; a combined signing key is possible. A parent DS authenticates a selected child DNSKEY, which then authenticates the child DNSKEY set.

```
configured root trust anchor
  verifies root DNSKEY RRset
  root key verifies DS RRset for com.
  DS authenticates com. DNSKEY
  child key verifies its DNSKEY RRset
  com. key verifies example.com DS
  DS authenticates child DNSKEY set
  child key verifies A RRset RRSIG
```

A validating resolver walks this chain. AD can signal that the relevant answer/authority data was validated, subject to request flags and response rules. With checking enabled, bogus data normally produces SERVFAIL; an authenticated unsigned delegation is **insecure**, not automatically bogus. CD can request data without that rejection. A non-validating stub must trust the resolver and protected path for its AD assertion; a validating stub can check signatures itself.

### Proving non-existence

An attacker could also forge "this name does not exist". To sign a negative answer without signing every possible name, **NSEC** records chain the zone's existing names in sorted order: "the next name after `alpha` is `delta`" proves the exact covered name does not exist; a complete NXDOMAIN proof also needs appropriate wildcard/closest-encloser handling. The side effect is **zone walking**: following a conventional static NSEC chain can enumerate names represented in that chain. Delegations, empty nonterminals and online-signed denial techniques require care. **NSEC3** chains hashes of names instead, which slows walking but does not prevent offline dictionary attacks against the hashes.

### Costs and pitfalls

- **Bigger answers.** Signatures and keys make responses much larger, which means more truncation, TCP fallback and fragmentation, and makes signed zones more attractive for **amplification** DDoS. ECDSA P-256 (algorithm 13) has far smaller signatures than RSA-2048 in the compared algorithms (64-byte ECDSA signatures versus 256-byte RSA-2048 signatures). No deployment-prevalence claim is made here.
- **Operational fragility.** Expired signatures or a key rollover with a stale DS record can make affected signed data fail validation once usable cached data and overlapping valid chains are exhausted.
- **Validator DoS.** The 2024 KeyTrap vulnerability showed that crafted key-tag collisions and many candidate signatures can force excessive validation work in vulnerable implementations. This refers to key-tag matching, not a break of signature cryptography; no universal CPU duration is asserted here.
- **Last mile.** DNSSEC authenticates signed data to whichever endpoint performs validation, through intervening caches or transports. It does nothing about who can *see* your queries.

## Encrypted DNS: DoT and DoH

Classic DNS is plaintext. An observer on an unprotected DNS transport can inspect its messages and attempt modification; caches avoid some lookups, and validation can detect tampering. Encrypted transports protect the hop between stub and recursive resolver.

| | DoT | DoH | DoQ |
|---|---|---|---|
| RFC | 7858 | 8484 | 9250 |
| Transport | TLS/TCP | HTTPS | QUIC |
| Port | 853 | 443 | 853 (UDP) |

**DNS over TLS** wraps the normal TCP DNS format (2-byte length, then message) in TLS. Because it has its own port, networks can easily identify and block it. Android supports DoT; eligible updated Android versions can also use DoH over HTTP/3 for supported resolvers. The selected transport depends on version, updates and configuration.

**DNS over HTTPS** sends the same binary message as an HTTP request with media type `application/dns-message`, either POSTed or base64url-encoded in a GET (`/dns-query?dns=...`). Sharing HTTPS transport can make classification less direct than a dedicated port, but resolver addresses, endpoint policy and traffic patterns can still enable blocking. DoH is not guaranteed indistinguishable from other HTTPS. Browsers such as Firefox and Chrome can use it directly.

What encrypted DNS does **not** do:

- It does not hide your queries from the **resolver** itself; you have moved trust from your ISP to, say, Cloudflare or Google. Oblivious DoH (RFC 9230) adds a proxy to separate client addressing from query contents under its non-collusion and deployment assumptions. Correlation, colluding parties and identifying query contents remain limits.
- It authenticates and integrity-protects the transport to the selected resolver, but does not independently authenticate authoritative *data*; a malicious or compromised resolver can still lie. That is DNSSEC's job.
- It does not hide the destination entirely: the server's IP address, and often the TLS SNI, still reveal where you went (Encrypted Client Hello addresses SNI).

An independently selected DoH resolver can bypass policies implemented only in the network’s default resolver, which is why administrators can disable it by policy and why Firefox checks a "canary" domain (`use-application-dns.net`) before enabling it automatically.

## Key takeaways
- A DNS message is a 12-byte header (ID, flags, four counts) plus question, answer, authority and additional sections.
- Names are length-prefixed labels; pointers with top bits `11` compress repeated names, as in `c0 0c`.
- UDP DNS is limited to 512 bytes without EDNS; TC signals truncation and can prompt a TCP retry. The 1,232-byte recommendation assumes a basic IPv6+UDP budget and is not a universal path guarantee.
- Off-path poisoning is a guessing game on ID and source port; Kaminsky made it repeatable, and randomisation, bailiwick rules and DNSSEC defend against it.
- DNSSEC signs RRsets in a chain from the root's key via DS records; it gives integrity, not privacy. Authenticated DoT/DoH protect confidentiality and integrity on the client-resolver transport. They do not replace independent DNSSEC validation of authoritative data.

## Further reading
- [RFC 1035: Domain Names, Implementation and Specification — IETF](https://www.rfc-editor.org/rfc/rfc1035)
- [DNS Flag Day 2020](https://www.dnsflagday.net/2020/)
- [An illustrated guide to the Kaminsky DNS vulnerability — Unixwiz.net](http://unixwiz.net/techtips/iguide-kaminsky-dns-vuln.html)
- [DNSSEC: what is it and why is it important? — ICANN](https://www.icann.org/resources/pages/dnssec-what-is-it-why-important-2019-03-05-en)
- [RFC 8484: DNS Queries over HTTPS (DoH) — IETF](https://www.rfc-editor.org/rfc/rfc8484)
- [Domain Name System Security Extensions — Wikipedia](https://en.wikipedia.org/wiki/Domain_Name_System_Security_Extensions)

> [!note] Content omitted after review
> Universal attack completion times, resolver port pools, DNSSEC algorithm prevalence and a current browser/device encrypted-DNS policy matrix are absent because those implementation-specific measurements were not reliably established. The retained probability and packet-size calculations state their assumptions.

- [RFC5452: forged-answer matching and defences](https://www.rfc-editor.org/rfc/rfc5452.html)
- [RFC6840: DNSSEC validation clarifications](https://www.rfc-editor.org/rfc/rfc6840.html)
- [RFC6781: DNSSEC operational practices](https://www.rfc-editor.org/rfc/rfc6781.html)
- [RFC9230: Oblivious DoH security assumptions](https://www.rfc-editor.org/rfc/rfc9230.html)
