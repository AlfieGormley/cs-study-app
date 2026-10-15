---
id: pki-signatures-purpose
title: What signatures prove
level: basic
minutes: 3
sourceLesson: pki-signatures
summary: A signature separates signing authority from public verification; a shared-key MAC does not.
---

A **digital signature** lets a signature verifier with a trusted public key check message integrity and authenticity to the corresponding signing key, under the scheme's security assumptions. It does not identify a human or establish freshness by itself.

Message authentication codes (MACs), introduced in cryptographic primitives, authenticate with a shared secret. MACs also prove integrity and origin, but both sides share the same secret key, so either side could have produced the tag. A signature splits the key in two. Holders of the private key can sign; anyone with the public key can verify. That asymmetry is what makes signatures useful between strangers, and it is the foundation of certificates, software updates and TLS.

## What a signature scheme is

Every signature scheme is three algorithms:

1. **KeyGen** produces a key pair: a private signing key `sk` and a public verification key `pk`.
2. **Sign(sk, message)** produces a signature, a short string of bytes.
3. **Verify(pk, message, signature)** returns true or false.

The security goal is called **existential unforgeability under chosen-message attack** (EUF-CMA). Even after obtaining signatures on chosen messages, an efficient attacker should have only negligible probability of producing a valid signature on a message not previously submitted for signing, under the scheme's assumptions.

| Property | MACs | Signatures |
|---|---|---|
| Keys | One shared secret | Private + public |
| Who can create | Anyone with the key | Private key holder |
| Who can verify | Anyone with the key | Anyone |
| Signature verifier can check without signing power | No (shared key) | Yes |
| Speed | Usually lower computational cost | Cost depends on scheme and operation |

Signatures can support evidence of origin because verification need not grant signing authority. Attribution also needs trustworthy identity binding, key custody and protocol context.

> [!note] Content gap: legal effect
> This lesson supplies no jurisdiction-specific legal assessment. It does not claim a signature alone proves a person acted, guarantees admissibility or determines a dispute.

> [!warning] Signing is not encrypting
> A signature alone does nothing for confidentiality: its message may remain readable unless separately encrypted. If both are needed, use a suitable authenticated-encryption protocol. TLS certificate handshakes use signatures for authentication; Signal's message protection is not simply a publicly verifiable signature on every message.

## Hash, then sign

Many signature schemes hash messages as part of their encoding, but the construction is scheme-specific. For example, pure Ed25519 hashes the message together with secret-derived material and signature/public-key data; it is not simply Sign(SHA256(message)). Follow the API's message or prehash interface. The diagram is only a simplified hash-then-sign construction.

```
simplified hash-then-sign example
message
     |
  SHA-256
     |
 32-byte digest --Sign(sk)--> signature
```

This is why hash **collision resistance** matters so much. If an attacker can find two documents with the same hash, a signature on the harmless one is also a valid signature on the harmful one. That is exactly how researchers forged a rogue CA certificate using MD5 collisions in 2008, and why SHA-1 was retired from certificates, a decision vindicated by the SHAttered collision in 2017.

## Key takeaways
- A signature separates signing authority from public verification; a shared-key MAC does not.
- Signatures authenticate bytes to a key, without hiding the message or proving a human identity.
- Message hashing and encoding belong to the specified scheme; collisions can undermine digest-only signing.

## Further reading
- [RSA signature schemes — RFC 8017](https://www.rfc-editor.org/rfc/rfc8017)
- [EdDSA — RFC 8032](https://www.rfc-editor.org/rfc/rfc8032)
- [Deterministic ECDSA — RFC 6979](https://www.rfc-editor.org/rfc/rfc6979)
