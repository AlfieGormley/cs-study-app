---
id: pki-tls-record-nonces
title: TLS record encryption and sequence nonces
level: intermediate
minutes: 3
sourceLesson: pki-tls
summary: AEAD protects record contents and authenticates the visible header.
---

After the handshake, every byte of application data travels inside AEAD-protected records. TLS 1.3 gets a unique nonce for each record without ever sending one, and that same trick detects deleted or reordered records.

## Job 4: protecting records with AEAD

Data travels in **TLS records** of up to 16 KiB of content. Each record is sealed with the negotiated AEAD (AES-GCM or ChaCha20-Poly1305) under the current traffic key. The plaintext that gets encrypted is the content, followed by one byte giving the real record type (handshake, alert or application data) and optional padding made of zero bytes. The visible 5-byte record header is passed as associated data: authenticated, but not encrypted.

The per-record nonce comes from a fixed IV derived in the TLS 1.3 key schedule and a counter both sides keep:

```formula essential
N = IV ⊕ S
where
N: the per-record nonce, 12 bytes; both sides compute it and it is never sent
IV: the static 12-byte IV derived from the traffic secret with HKDF
⊕: XOR (exclusive OR), byte by byte: each output bit is 1 when the two input bits differ
S: the 64-bit record sequence number (0 for the first record under a key, then 1, 2, …), written as a 12-byte number with zero bytes on the left
In words: each record's nonce is the fixed IV with the record number mixed into its last bytes, so every record under one key gets a different nonce.
```

Three consequences follow:

- **The nonce is never sent.** Each record gets a unique nonce without spending bytes on the wire: for record 0 the nonce equals the IV, and later records change only the IV's last few bytes, never repeating under one key. Because the receiver uses its own count, deletion, reordering or replay within the delivered TLS byte stream causes the next record to fail authentication. Ordinary packet loss is repaired by TCP below TLS.
- **The header is authenticated** as associated data, so its length and type cannot be altered.
- **The real record type is inside the encryption**, along with optional padding, so an observer cannot easily tell handshake messages from alerts or application data.

The uniqueness depends on one rule: a fresh key for every sequence that restarts at zero. TLS gets this for free, because every handshake derives new traffic keys and a KeyUpdate resets the counter only together with a new key. A homemade protocol that copies "IV XOR counter" but restarts the counter while keeping the same key (after a crash, a reconnect, or on a second device sharing the key) reuses nonces.

> [!analogy] Real-world analogy: A numbered cheque book
> A cheque book has pre-printed numbers. The bank expects cheque 101 after cheque 100, so a missing or duplicated cheque stands out, and nobody has to write the number by hand.
>
> **How it maps:** The printed numbers are the record sequence numbers that both sides count independently. Mixing that count into the fixed IV gives every record its own nonce, and a record removed or replayed by an attacker breaks the expected numbering, so the next record fails to decrypt.
>
> **Where it stops:** A bank clerk may just note a gap and carry on. In TLS the number is part of the cryptographic input itself, so a mismatch is not a bookkeeping note: the authentication tag fails and the connection is torn down. A new cheque book starting again at 1 would be harmless, whereas restarting the count under the same key is a serious nonce reuse.

## Key takeaways
- AEAD protects record contents and authenticates the visible header.
- A static IV XOR the implicit sequence number gives unique per-key nonces without transmitting them.
- Removing a record from the delivered byte stream disrupts authentication on the next record.

## Further reading
- [TLS 1.3 — RFC 9846](https://www.rfc-editor.org/rfc/rfc9846)
- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/)
