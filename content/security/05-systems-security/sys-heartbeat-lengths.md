---
id: sys-heartbeat-lengths
title: Validate the bytes that actually arrived
level: intermediate
minutes: 4
sourceLesson: sys-memory-bugs
summary: A read past a live buffer is a spatial error and can disclose information.
---

## Out-of-bounds reads: Heartbleed

Reading beyond an object can disclose memory if the result becomes observable. It may instead fault or have other undefined behaviour. Potential disclosures include secrets and addresses that weaken ASLR.

**Heartbleed** (CVE-2014-0160) in OpenSSL is the famous case. The TLS heartbeat message said "here are N bytes, echo them back". OpenSSL trusted the attacker-supplied N without checking it against how much data had actually arrived. Simplified:

```c
/* BUG: len is an untrusted claim. */
memcpy(reply, payload, len);  /* BUG */
```

A malformed request could make vulnerable OpenSSL disclose up to 64 KB of process memory, potentially including secrets. A crash or other outcome was also possible. The 64 KB limit comes from the size of the length field, which is two bytes (16 bits):

```formula
N_max = 2^16 − 1
N_max = 65,536 − 1 = 65,535 B
where
N_max: the largest payload length the heartbeat's length field can claim, in bytes (B)
2^16: 16 copies of 2 multiplied together, 65,536: the number of different values 16 bits can hold
1: subtracted because the values start at 0, so the largest is one less than the count
B: byte, 8 bits
In words: a 16-bit length field can claim at most 65,535 bytes, just under 64 KiB (64 × 1,024 bytes), so one malicious heartbeat could leak up to about 64 KB.
```

A heartbeat message (RFC 6520) is laid out as a one-byte type, the two-byte payload length, the payload, then at least 16 bytes of random padding. Everything the length claims must fit inside what actually arrived:

```formula
1 + 2 + L + 16 ≤ R
L ≤ R − 3 − 16
where
1: the one-byte message type
2: the two-byte payload-length field
L: the payload length the message claims, in bytes; attacker-controlled (len in the code)
16: the minimum padding, in bytes, that RFC 6520 requires after the payload
R: the number of bytes of heartbeat message actually received (record_len in the code)
≤: less than or equal to
In words: the header, the claimed payload and the minimum padding must all fit in the received bytes, so the claimed length can be at most the received size minus 19.
```

For example, if 40 bytes arrive, the payload can be at most 40 − 3 − 16 = 21 bytes, and a claimed length of 65,535 must be rejected. Vulnerable OpenSSL skipped this check and copied as many bytes as were claimed, reading far past the real payload.

So first ensure the three-byte header exists before parsing its length, and reserve the required minimum 16-byte padding too. `size_t` is unsigned, so if `record_len` were below 19, `record_len - 3 - 16` would wrap to a huge number (integer wraparound) and the length check would pass. With non-negative `size_t` lengths and a sufficiently large reply buffer, the following guard prevents that subtraction underflow:

```c
/* Guard subtraction before checking len. */
if (record_len < 3 + 16)
    return 0;
if (len > record_len - 3 - 16)
    return 0;  /* discard bad message */
/* Both ranges must fit and not overlap. */
memcpy(reply, payload, len);
```

Treat externally supplied lengths, indices and counts as untrusted. Validate both the arithmetic and the resulting range against actual available storage before parsing or copying.

## Key takeaways
- A read past a live buffer is a spatial error and can disclose information.
- Validate the heartbeat header before parsing its claimed length, then account for minimum padding.
- Guard unsigned subtraction before using a received length to derive a remaining capacity.

## Further reading
- [Heartbleed advisory — OpenSSL](https://openssl-library.org/news/secadv/20140407.txt)
- [TLS heartbeat — RFC 6520](https://www.rfc-editor.org/rfc/rfc6520.html)
- [The Heartbleed Bug](https://heartbleed.com/)
