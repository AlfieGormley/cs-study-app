---
id: pki-key-management-envelope-tradeoffs
title: Envelope scaling and crypto-shredding
level: intermediate
minutes: 2
sourceLesson: pki-key-management
summary: Per-object data encryption keys reduce a leaked DEK’s scope and keep bulk data away from the KMS API.
---

Envelope encryption separates a locally used data encryption key (DEK) from the key encryption key (KEK) protecting it. Key custody and application authorisation remain essential.

### Why the envelope pays off

- **Scale**: the bulk data never crosses the network to the KMS; only key-sized values and request metadata do; wrapped keys include format overhead.
- **Blast radius**: each object has its own DEK, so one leaked DEK exposes one object.
- **Access control and audit in one place**: unwrap operations pass through KMS access controls and audit facilities. Cached plaintext DEKs allow subsequent reads without another KMS call, so an unwrap log is not a complete data-access log.
- **Cheap rotation**: moving DEKs to a new uncompromised KEK can require only re-wrapping. Automatic version rotation may retain old wraps unchanged; compromise recovery can require fresh DEKs and data re-encryption.
- **Crypto-shredding**: destroy every usable copy of the relevant keys and wrapped-key recovery paths to make remaining ciphertext unrecoverable, assuming sound encryption and no retained plaintext copies.

This is how S3 server-side encryption with KMS, EBS volumes, Google Cloud's default encryption at rest and some database transparent-data-encryption designs work; details vary by service. Google's stack goes one level further: DEKs wrapped by KEKs wrapped by a root KMS key, with the root material held in a small number of hardware-protected locations.

## Key takeaways
- Per-object data encryption keys reduce a leaked DEK’s scope and keep bulk data away from the KMS API.
- Cached unwrapped keys weaken the correspondence between unwrap logs and reads.
- Cryptographic erasure requires removing every usable key recovery path and retained plaintext, including backup paths.

## Further reading
- [AWS KMS cryptographic details](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html)
- [NIST key-management guidance](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
