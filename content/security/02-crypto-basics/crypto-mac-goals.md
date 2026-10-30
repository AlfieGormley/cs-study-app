---
id: crypto-mac-goals
sourceLesson: crypto-macs
title: What message authentication proves
level: intermediate
minutes: 5
summary: A MAC supports key-holder authenticity and integrity, with no secrecy or freshness by itself.
---

A hash tells you whether data changed, but only if you trust where the expected digest came from. An attacker who can modify a message can just recompute its SHA-256. What you want is an authentication tag that outsiders cannot feasibly forge under a specified shared-key construction.

That is a **message authentication code (MAC)**. It takes a secret key and a message and outputs a short **tag** (32 bytes for HMAC-SHA256). The sender sends the message with its tag. The receiver, who holds the same key, recomputes the tag over the message that actually arrived and accepts it only if the two tags match.

For example, a sender computes a tag over `transfer £10` and sends both. If an attacker changes the message to `transfer £1000`, the receiver's recomputed tag no longer matches the one that arrived, so the message is rejected. Producing a matching tag for the altered message would need the key; guessing one has only a tiny, nonzero chance of success.

With a suitable MAC, protected key and correct verification, forging a tag for a new message is computationally infeasible within the intended security bounds. A verified tag supports integrity and key-holder authenticity; tag guessing has a nonzero probability, and replay does not establish freshness.

> [!analogy] Real-world analogy: A wax seal from a shared signet ring
> Two merchants each own an identical signet ring. Every letter between them is closed with a wax seal pressed by the ring. A courier cannot change the letter without breaking the seal, and cannot make a new seal without a ring.
>
> **How it maps:** The ring is the shared secret key and the seal is the tag. An unbroken seal shows the letter was not altered and came from someone holding a ring. Because both merchants hold the same ring, the seal cannot show *which* of them wrote it, so it gives no non-repudiation. A courier can still hand over yesterday's genuine sealed letter again, which is a replay.
>
> **Where it stops:** A wax seal sits on the outside and a skilled forger might copy it; a MAC tag is computed from every bit of the message, and forging one without the key is computationally infeasible within its security bounds. A sealed letter is also closed; a MAC alone does not hide the message at all.

## What a MAC does and doesn't give you

| Gives you | Doesn't give you |
|---|---|
| Integrity | Confidentiality |
| Authenticity (key holder) | Non-repudiation |
| Tamper detection | Replay protection |

- **No confidentiality.** The message travels in the clear unless you also encrypt it.
- **No non-repudiation.** Both sides share the key, so either could have produced the tag. The tag alone cannot distinguish which shared-key holder created it. Digital signatures separate signing from verification authority, but attribution to a human and legal effect require additional evidence.
- **No replay protection.** A captured `(message, tag)` pair remains cryptographically valid while that key and message interpretation are accepted. If an attacker resends "transfer £100 to Mallory", the tag still checks out. Protocols add a timestamp, sequence number or nonce *inside* the authenticated data and reject repeats.

The security goal is called **existential unforgeability**: even after seeing tags for many messages of their choice, producing an accepted tag for a new message should be computationally infeasible within the stated resource and success-probability bounds.

## The tempting mistake: hashing the key with the message

The obvious construction is to hash the key followed by the message and use the digest as the tag. It looks as if it should need the key to compute, but it doesn't. With SHA-256 (and SHA-1, MD5, SHA-512) this is **broken by length extension**. As the hashes lesson showed, a Merkle–Damgård digest is the hash function's entire internal state after the last block. An attacker who sees one valid tag can resume hashing from that state.

> [!example] Forging an API request
> An API signs `user=alice&amount=10` by SHA-256-hashing the key followed by the message. The attacker sees the tag. Without knowing the key (only guessing its length), they compute a valid tag for `user=alice&amount=10<padding>&amount=9999`. Application abuse also requires the server to accept the inserted padding and interpret the extra parameter as intended; parser and encoding behaviour matter.

This actually happened. In 2009 Thai Duong and Juliano Rizzo showed Flickr's API signatures, built by MD5-hashing a secret followed by the request parameters, could be forged this way.

Appending a key is not a generic secure construction either: suitable equal-length internal-state collisions in a Merkle–Damgård hash can remain collisions after a common secret suffix. Rather than patch these designs, use the construction built to be safe.

## Key takeaways
- A MAC supports key-holder authenticity and integrity, with no secrecy or freshness by itself.
- A secret-prefix SHA-256 hash is not a secure replacement for HMAC.

## Further reading
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
- [NIST FIPS 180-4: secure hashes](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
