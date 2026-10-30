---
id: pki-key-management-hsm-kms
title: HSMs, KMS and authorised misuse
level: intermediate
minutes: 3
sourceLesson: pki-key-management
summary: Non-exportable HSM keys resist ordinary extraction but can still be misused by an authorised caller.
---

A secrets manager can deliver plaintext secrets to authorised applications. An HSM or managed key-operation API offers a different boundary: the caller can request an operation without receiving the protected key.

## Hardware security modules

An **HSM** is a dedicated, tamper-resistant computer whose job is to hold keys and perform operations with them. Keys can be generated inside and marked non-exportable; supported import, backup and export policies vary. Properly configured non-exportable keys remain within the device's protected boundary during normal operations. You send it data; it sends back a signature or ciphertext.

- **Tamper response**: physical detection and response depend on the module and its validated security policy; supported responses to specified attacks can include zeroising protected secrets.
- **Certification**: deployment or payment-security policies can require validation such as **FIPS 140-3** (levels 1 to 4) or PCI PTS HSM. The validated configuration and security policy define the covered protection and authentication requirements; do not infer an all-purpose assurance guarantee from a level alone.
- **Standard interfaces**: PKCS#11, Microsoft CNG or a vendor API.
- **Limited throughput**: benchmark the specific device, algorithm, key size and concurrency before sizing a service.

Where HSMs are used: CA root and intermediate keys, card-payment PIN and key processing, DNSSEC signing, code-signing keys, and hardware-backed tiers of cloud key-management services. Smaller versions are everywhere: a phone's Secure Enclave or StrongBox, a TPM in a laptop, a YubiKey.

> [!warning] An HSM stops theft, not misuse
> If an attacker compromises an authorised caller, a correctly enforced non-exportable key can resist extraction while the attacker still requests signatures permitted by its policy. Treat HSM access as a privilege to restrict, rate-limit and log, and alert on unusual use.

> [!analogy] Real-world analogy: A notary who keeps the seal
> A notary keeps the official seal in a locked drawer and stamps documents brought to the counter. You can never take the seal home, but anyone who gets to the counter with a document the notary is willing to stamp walks away with a genuine stamped document.
>
> **How it maps:** The seal is the non-exportable key and the notary is the HSM or KMS: it performs signatures and decryptions for callers but never hands out the key. A compromised application server is a fraudster standing at the counter. The protection against them is the notary's rules about what may be stamped, how often, and with whose approval, which correspond to signing policy, rate limits, quorum and logging.
>
> **Where it stops:** A human notary might recognise a suspicious customer or a forged document. An HSM checks only what its policy encodes, so anything an authorised caller is allowed to request will be signed, however suspicious it would look to a person.

## Cloud KMS: an HSM as an API

Running HSMs yourself means hardware, firmware and operator procedures. **Cloud KMS** services expose key operations through APIs with access policies and audit facilities. Protection levels differ: Google Cloud KMS, for example, supports software, HSM and external protection; hardware backing is not universal.

For service-generated non-exportable keys, normal APIs return operation results rather than key material. Imported or externally managed keys have different custody boundaries. You call `Encrypt`, `Decrypt`, `Sign` or `GenerateDataKey`, and calls are checked against policy and can be audited (in AWS, through CloudTrail configuration). But KMS is a network service with request quotas, implementation-dependent latency, and a payload limit: AWS KMS symmetric `Encrypt` accepts at most 4,096 bytes of plaintext; RSA limits are smaller and depend on modulus and padding. You cannot send it a 50 GB backup. That is where envelope encryption comes in.

## Key takeaways
- Non-exportable HSM keys resist ordinary extraction but can still be misused by an authorised caller.
- Cloud key-management protection levels, quotas and audit configuration differ by service.
- Small KMS payload limits motivate local bulk encryption with separately protected data keys.

## Further reading
- [AWS KMS cryptographic details](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html)
- [Hardware security module — Wikipedia](https://en.wikipedia.org/wiki/Hardware_security_module)
