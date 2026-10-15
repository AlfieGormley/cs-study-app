---
id: pki-tls-key-updates
title: TLS usage limits and key updates
level: intermediate
minutes: 2
sourceLesson: pki-tls
summary: AES-GCM has a record-usage bound well before the sequence counter would wrap.
---

TLS 1.3 protects each record using AEAD and a nonce derived from a static IV plus an implicit sequence counter. A unique nonce is necessary, but the AEAD also imposes an earlier usage limit.

AEAD keys also have **usage limits**. RFC 9846 says to send no more than roughly 23.7 million full-size records (roughly 24 million records, close to 400 GB) under one AES-GCM key. In bytes:

```formula
D_max = R_max × S_rec
D_max = 2^{24.5} × 16,384 B
D_max ≈ 23.7 × 10^6 × 16,384 B
D_max ≈ 3.89 × 10^{11} B ≈ 389 GB
where
D_max: the most data one AES-GCM key should protect, in bytes (B)
R_max: RFC 9846's record limit for AES-GCM, 2^24.5 ≈ 23.7 million full-size records; the RFC states an authenticated-encryption security margin of approximately 2^−57 under its cited analysis, rather than an unconditional real-world attack probability
S_rec: the content of one full-size record, 16 KiB = 16,384 bytes
≈: approximately equal to
B: bytes
GB: gigabytes; 1 GB = 10^9 bytes
In words: one AES-GCM key is good for roughly 389 GB of full records before it should be replaced.
```

A connection streaming 50 MB/s reaches that in about 7,800 seconds, a little over two hours. The limit is a safety margin chosen by the RFC, not a cliff: the risk grows gradually with the amount encrypted. For ChaCha20-Poly1305, RFC 9846 notes that the 64-bit sequence number would wrap before the safety limit is reached. Long-lived connections send a **KeyUpdate** message, which updates the sender's write secret and receiver's corresponding read secret with HKDF, giving a new key and resetting that direction's sequence number. Updating the opposite direction requires its own KeyUpdate.

Older TLS suites permitted CBC with a separate HMAC, traditionally MAC-then-encrypt; RFC 7366 later defined an encrypt-then-MAC extension. BEAST targeted predictable IVs in TLS 1.0, Lucky 13 exploited timing in CBC processing, and the original POODLE targeted SSL 3.0 padding. TLS 1.3 allows only AEAD.

## Key takeaways
- AES-GCM has a record-usage bound well before the sequence counter would wrap.
- At 50 MB/s, the illustrative full-record allowance is exhausted in a little over two hours.
- KeyUpdate advances one direction’s traffic secret and resets its sequence count under a new key.

## Further reading
- [TLS 1.3 — RFC 9846](https://www.rfc-editor.org/rfc/rfc9846)
- [TLS example traces — RFC 8448](https://www.rfc-editor.org/rfc/rfc8448)
