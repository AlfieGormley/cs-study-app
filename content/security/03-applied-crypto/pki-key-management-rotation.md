---
id: pki-key-management-rotation
title: Key rotation and random-nonce limits
level: intermediate
minutes: 3
sourceLesson: pki-key-management
summary: KEK version rotation can leave earlier wrapped keys readable under retained material.
---

"Rotate your keys" sounds like one action, but in an envelope system it means two different things with different purposes, and neither one undoes a key that has already leaked.

## Two things to rotate

Rotating a key means new data is protected by new key material. In envelope systems there are two separate things to rotate:

- **KEK rotation**: for AWS-generated symmetric encryption keys, AWS KMS keeps every previous version of a key's material, wraps new DEKs with the latest, and still unwraps old ones automatically. The key's identifier does not change, and nothing is re-encrypted. Automatic rotation runs every 365 days by default once enabled; a custom period between 90 and 2,560 days can be set, and on-demand rotation is also available (as documented in October 2026).
- **DEK rotation**: generate fresh DEKs for new data. This is about how much data one key protects.

## Why DEKs must not be used for ever

With AES-GCM and random 96-bit nonces, the danger is two encryptions under one key picking the same nonce by chance, which breaks GCM's confidentiality and authentication. Every pair of encryptions is a chance for a match, so the risk grows with the square of the number of messages: double the messages and the risk roughly quadruples. (The crypto basics lesson on GCM nonce limits shows this birthday calculation.)

NIST SP 800-38D therefore caps a key used with random 96-bit nonces at 2^32 encryptions, about 4.3 billion. That sounds huge, but a service encrypting 10 million rows a day under one key reaches it in a little over a year, and the count is **per key, across everything that uses it**: twenty servers or a thousand devices sharing one key all add to the same total, even if each one only encrypts a little.

A fresh DEK per object keeps each key far below the random-nonce bound. A deterministic nonce construction with guaranteed uniqueness avoids random collisions, but must also obey its own invocation, length and authentication limits.

> [!analogy] Real-world analogy: A new master key with the old ones kept in a drawer
> A building manager replaces the master key every year, but keeps all the old master keys in a drawer, because old storage boxes were locked with them. New boxes get the new key; old boxes still open.
>
> **How it maps:** That is versioned KEK rotation in a KMS: new DEKs are wrapped under the newest key material, and older material is retained so existing wrapped DEKs still unwrap. Nothing already stored is re-locked.
>
> **Where it stops:** If a thief copied last year's master key, the yearly change does not help with the boxes locked under it, and the copies of old boxes the thief already took stay readable for ever. In cryptography, the fix is to re-encrypt data under new DEKs and keys the attacker never had.

## Rotation is not compromise response

Rotation limits how much data one key protects; it does *not* fix a compromise on its own. If a KEK leaked, its old versions can still unwrap old DEKs, and the attacker may have copied wrapped DEKs and ciphertexts already. After a real compromise, re-encrypt the affected data under fresh DEKs and keys the attacker never had, and accept that copies the attacker already took remain exposed.

## Key takeaways
- KEK version rotation can leave earlier wrapped keys readable under retained material.
- Random-nonce collision risk grows with the number of message pairs across all users of a key.
- Exposure recovery needs uncompromised keys and, where DEKs may be known, data re-encryption.

## Further reading
- [Rotating AWS KMS keys — AWS docs](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html)
- [NIST SP 800-38D: GCM and GMAC](https://csrc.nist.gov/pubs/sp/800/38/d/final)
