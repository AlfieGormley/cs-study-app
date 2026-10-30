---
id: pki-key-management-envelope-tradeoffs
title: Envelope scaling and crypto-shredding
level: intermediate
minutes: 3
sourceLesson: pki-key-management
summary: Per-object data encryption keys reduce a leaked DEK’s scope and keep bulk data away from the KMS API.
---

The previous unit showed how envelope encryption works. This one asks why large storage systems almost all use it, and what it makes possible, such as erasing data you cannot physically reach.

### Why the envelope pays off

- **Scale**: the bulk data never crosses the network to the KMS; only key-sized values and request metadata do; wrapped keys include format overhead.
- **Blast radius**: each object has its own DEK, so one leaked DEK exposes one object.
- **Access control and audit in one place**: unwrap operations pass through KMS access controls and audit facilities. Cached plaintext DEKs allow subsequent reads without another KMS call, so an unwrap log is not a complete data-access log.
- **Cheap rotation**: moving DEKs to a new uncompromised KEK can require only re-wrapping. Automatic version rotation may retain old wraps unchanged; compromise recovery can require fresh DEKs and data re-encryption.
- **Crypto-shredding**: destroy every usable copy of the relevant keys and wrapped-key recovery paths to make remaining ciphertext unrecoverable, assuming sound encryption and no retained plaintext copies.

> [!analogy] Real-world analogy: Destroying the only key to an archive box
> Old records sit in locked boxes in an off-site warehouse you cannot visit or empty. If each customer's papers are in their own locked box, destroying that box's only key makes those papers unreadable, even though the box is still on the shelf.
>
> **How it maps:** The warehouse is an immutable backup or a replicated store; the boxes are ciphertexts, each under its own DEK. Crypto-shredding destroys every usable copy of the DEK (or of its wrapped form), so the ciphertext remains but cannot be read.
>
> **Where it stops:** A physical key is easy to count. Digital keys may survive in caches, logs, key-table backups or a plaintext copy someone exported, and every one of those must be gone. The protection also relies on the cipher staying unbroken for as long as the ciphertext exists.

This is how S3 server-side encryption with KMS, EBS volumes, Google Cloud's default encryption at rest and some database transparent-data-encryption designs work; details vary by service. Google's stack goes one level further: DEKs wrapped by KEKs wrapped by a root KMS key, with the root material held in a small number of hardware-protected locations.

## Key takeaways
- Per-object data encryption keys reduce a leaked DEK’s scope and keep bulk data away from the KMS API.
- Cached unwrapped keys weaken the correspondence between unwrap logs and reads.
- Cryptographic erasure requires removing every usable key recovery path and retained plaintext, including backup paths.

## Further reading
- [Encryption at rest in Google Cloud](https://cloud.google.com/docs/security/encryption/default-encryption)
- [Crypto-shredding — Wikipedia](https://en.wikipedia.org/wiki/Crypto-shredding)
