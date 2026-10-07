---
id: pki-key-management
title: Key management, HSMs and envelope encryption
level: intermediate
minutes: 14
summary: Why the hard part of cryptography is the keys, how HSMs and cloud KMS keep them out of reach, how envelope encryption scales that to petabytes, and how rotation, access control and crypto-shredding work in practice.
---

Encryption does not make a secret go away. It turns a big secret (a database, a disk, a backup) into a small one: the key. Whoever gets the key gets everything, so the security of the whole system now rests on where that key lives, who can use it, and what happens when it leaks or is lost.

Key handling is a major source of encryption failures, alongside implementation errors and protocol misuse. Publicly exposed credentials must be treated as compromised.

> [!note] Content gap
> A percentage of failures attributed to key management, a universal credential-discovery time and generic HSM throughput figures are omitted because no supporting measurement dataset was available.

## The key lifecycle

A typical key lifecycle includes these stages, and each one has its own failure modes:

1. **Generate** from a cryptographically secure RNG, ideally inside the device that will use it.
2. **Store** with controls against unauthorised copying: not in source code, not in a config file next to the data.
3. **Distribute** only to the systems that need it, over authenticated channels.
4. **Use** for one purpose only, with access control and an audit trail.
5. **Rotate** on a schedule and after any suspected compromise.
6. **Revoke and destroy** when it is no longer needed, including in backups.

> [!tip] One key, one job
> Never use the same key for encryption and signing, or for two different applications. If one use leaks the key, or interacts badly with another (for example, an RSA key used for both decryption and signatures), both are compromised. Derive separate keys with a KDF if you must start from one secret.

## Where keys can live

| Location | Key extractable? | Typical use |
|---|---|---|
| Source code / env var | Readable by sufficiently privileged code | Avoid committed secrets; runtime injection still exposes the process |
| Secrets manager | Yes, by the app | API tokens, DB passwords |
| Cloud KMS | Usually not exported through normal key APIs; origin/protection level matters | Wrapping data keys |
| HSM | Depends on key attributes and export policy | CA roots, payment keys |

A **secrets manager** (HashiCorp Vault, AWS Secrets Manager) stores secrets encrypted and hands them to authorised workloads at runtime. That beats a config file, but the application ends up holding the plaintext secret in memory.

Hardware isolation can strengthen key custody; a software service can also hide key material from ordinary calling applications, with a different trusted boundary.

## Hardware security modules

An **HSM** is a dedicated, tamper-resistant computer whose job is to hold keys and perform operations with them. Keys can be generated inside and marked non-exportable; supported import, backup and export policies vary. Properly configured non-exportable keys remain within the device's protected boundary during normal operations. You send it data; it sends back a signature or ciphertext.

- **Tamper response**: higher-grade HSMs detect drilling, probing, voltage or temperature attacks and wipe their keys.
- **Certification**: governments and payment networks require validation such as **FIPS 140-3** (levels 1 to 4) or PCI PTS HSM. Level 3 adds tamper response and identity-based authentication of operators.
- **Standard interfaces**: PKCS#11, Microsoft CNG or a vendor API.
- **Limited throughput**: benchmark the specific device, algorithm, key size and concurrency before sizing a service.

Where HSMs are used: CA root and intermediate keys, card-payment PIN and key processing, DNSSEC signing, code-signing keys, and hardware-backed tiers of cloud key-management services. Smaller versions are everywhere: a phone's Secure Enclave or StrongBox, a TPM in a laptop, a YubiKey.

> [!warning] An HSM stops theft, not misuse
> If an attacker compromises an authorised caller, a correctly enforced non-exportable key can resist extraction while the attacker still requests signatures permitted by its policy. Treat HSM access as a privilege to restrict, rate-limit and log, and alert on unusual use.

## Cloud KMS: an HSM as an API

Running HSMs yourself means hardware, firmware and operator procedures. **Cloud KMS** services expose key operations through APIs with access policies and audit facilities. Protection levels differ: Google Cloud KMS, for example, supports software, HSM and external protection; hardware backing is not universal.

For service-generated non-exportable keys, normal APIs return operation results rather than key material. Imported or externally managed keys have different custody boundaries. You call `Encrypt`, `Decrypt`, `Sign` or `GenerateDataKey`, and calls are checked against policy and can be audited (in AWS, through CloudTrail configuration). But KMS is a network service with request quotas, implementation-dependent latency, and a payload limit: AWS KMS symmetric `Encrypt` accepts at most 4,096 bytes of plaintext; RSA limits are smaller and depend on modulus and padding. You cannot send it a 50 GB backup. That is where envelope encryption comes in.

## Envelope encryption

Use two layers of keys:

- A **data encryption key** (DEK): a fresh random AES key per object, file or record, used locally to encrypt the data.
- A **key encryption key** (KEK): a long-lived key inside the KMS or HSM, used only to encrypt ("wrap") DEKs.

```
       KMS / HSM
     +-----------+
     |   KEK     |  never leaves
     +-----------+
        | wrap / unwrap (32 bytes)
        v
  wrapped DEK  +  data encrypted
  (stored)        locally with DEK
```

To write: ask the KMS for a new data key. It returns the DEK in plaintext *and* wrapped under the KEK. Encrypt the data locally, store the wrapped DEK beside the ciphertext, and minimise the plaintext DEK's lifetime. Reliable erasure is runtime-dependent; the Python illustration below does not securely erase immutable byte objects.

To read: send the wrapped DEK (whose encoded size depends on the service) to the KMS, get the plaintext DEK back if policy allows, and decrypt locally.

Here is the whole idea, with a local AES key standing in for the KMS:

```python
import os
from cryptography.hazmat.primitives \
    .ciphers.aead import AESGCM
from cryptography.exceptions import \
    InvalidTag

# stands in for a KMS key; a real one
# never leaves the KMS or HSM
KEK = AESGCM(AESGCM.generate_key(256))

def seal(data, ctx):
    dek = AESGCM.generate_key(256)
    n1, n2 = os.urandom(12), os.urandom(12)
    ct = AESGCM(dek).encrypt(n1, data, ctx)
    wrapped = n2 + KEK.encrypt(n2, dek, ctx)
    return wrapped, n1 + ct

def unseal(wrapped, blob, ctx):
    dek = KEK.decrypt(wrapped[:12],
                      wrapped[12:], ctx)
    return AESGCM(dek).decrypt(
        blob[:12], blob[12:], ctx)

w, b = seal(b"card 4242", b"user=42")
print(len(w), len(b))
print(unseal(w, b, b"user=42"))
try:
    unseal(w, b, b"user=99")
except InvalidTag:
    print("wrong context")
```

This prints `60 37`, then `b'card 4242'`, then `wrong context`. The wrapped DEK is 12 bytes of nonce, 32 of key and 16 of tag. The ciphertext is 12 + 9 + 16 bytes. The context (`user=42`) is AEAD associated data: it is not secret, but decryption fails if it differs, so a ciphertext copied into another user's row will not decrypt when the application derives the expected context from trusted identity/row information. AWS KMS calls this the **encryption context**, and it can appear in CloudTrail events, so it must not contain secret data.

With the real service, the first two lines of `seal` become one call:

```python
r = kms.generate_data_key(
    KeyId="alias/orders",
    KeySpec="AES_256",
    EncryptionContext={"user": "42"})
dek = r["Plaintext"]
wrapped = r["CiphertextBlob"]
```

### Why the envelope pays off

- **Scale**: the bulk data never crosses the network to the KMS; only key-sized values and request metadata do; wrapped keys include format overhead.
- **Blast radius**: each object has its own DEK, so one leaked DEK exposes one object.
- **Access control and audit in one place**: unwrap operations pass through KMS access controls and audit facilities. Cached plaintext DEKs allow subsequent reads without another KMS call, so an unwrap log is not a complete data-access log.
- **Cheap rotation**: moving DEKs to a new uncompromised KEK can require only re-wrapping. Automatic version rotation may retain old wraps unchanged; compromise recovery can require fresh DEKs and data re-encryption.
- **Crypto-shredding**: destroy every usable copy of the relevant keys and wrapped-key recovery paths to make remaining ciphertext unrecoverable, assuming sound encryption and no retained plaintext copies.

This is how S3 server-side encryption with KMS, EBS volumes, Google Cloud's default encryption at rest and some database transparent-data-encryption designs work; details vary by service. Google's stack goes one level further: DEKs wrapped by KEKs wrapped by a root KMS key, with the root material held in a small number of hardware-protected locations.

## Rotation

Rotating a key means new data is protected by new key material. In envelope systems there are two separate things to rotate:

- **KEK rotation**: for AWS-generated symmetric encryption keys, AWS KMS keeps every previous version of a key's material, wraps new DEKs with the latest, and still unwraps old ones automatically. The key ID does not change, and nothing is re-encrypted. Once enabled, automatic rotation runs yearly by default (configurable down to 90 days).
- **DEK rotation**: generate fresh DEKs for new data. With AES-GCM and random 96-bit nonces, NIST limits a key to 2^32 encryptions, so a DEK shared by billions of records must be replaced.

Rotation limits how much data one key protects; it does *not* fix a compromise on its own. If a KEK leaked, old versions can still unwrap old DEKs. After a real compromise you must re-encrypt the data under keys the attacker never had.

## Controlling who can use keys

- **Least privilege**: configure policies so the order service may decrypt only its intended data/context and analysts may not. Administrative and cryptographic-use permissions can be separated; this is a policy design, not an automatic guarantee.
- **Dual control and quorum**: critical operations need several people. HSMs support M-of-N smart-card quorums, and backup keys are often split with Shamir's secret sharing.
- **Key ceremonies**: the DNSSEC root key is used in scripted, filmed ceremonies at two ICANN facilities. Trusted community members hold smart cards, and several of them must be present to activate the HSM.
- **Deletion safeguards**: AWS KMS enforces a waiting period of 7 to 30 days before deleting a key, because loss of the last usable decryption key makes its ciphertext unrecoverable. It does not physically delete ciphertext or copies of plaintext.

## Pitfalls

- **Secrets in source control.** Bots scan public commits continuously. Use secret scanning and pre-commit hooks, and rotate any key that was ever pushed, even after deleting the commit.
- **Logging plaintext keys** or decrypted data in debug output or crash dumps.
- **KMS as a single point of failure.** If every request decrypts a DEK through KMS, a regional outage or quota limit stops your service. Cache plaintext DEKs in memory for a short time, accepting longer plaintext-key residency, weaker per-read audit granularity and delayed revocation. Cached keys help only until eviction or expiry; newly needed keys still require KMS.
- **Lost keys mean lost data.** Keep KEKs durable and backed up within the HSM or KMS's own mechanisms; test recovery.
- **Encrypting with the KEK directly.** Calling KMS `Encrypt` on records works for small values, but adds latency to every operation and fails above the API's algorithm-specific payload limit (4,096 bytes for symmetric KMS encryption).
- **Forgetting the threat model.** Disk encryption protects a stolen drive. It does nothing against SQL injection, because the database decrypts for any query it is allowed to run.

## Key takeaways
- Encryption turns a data-protection problem into a key-protection problem; secure key handling and correct protocol implementation both matter.
- HSMs can generate and use non-exportable keys within tamper-resistant hardware; policy enforcement reduces extraction risk but authorised-call misuse remains possible.
- Cloud KMS exposes managed key operations behind access policies and audit facilities; hardware protection depends on the service/tier, but with quotas, latency and small payload limits.
- Envelope encryption uses a per-object DEK for data and a KMS-held KEK to wrap DEKs, giving scale, small blast radius, central audit and cheap rotation.
- Bind ciphertexts to their context with AEAD associated data (KMS encryption context).
- Rotation limits exposure going forward; recovering from a compromise needs re-encryption under new keys.

## Further reading
- [AWS KMS concepts: envelope encryption — AWS docs](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html)
- [Encryption at rest in Google Cloud](https://cloud.google.com/docs/security/encryption/default-encryption)
- [Hardware security module — Wikipedia](https://en.wikipedia.org/wiki/Hardware_security_module)
- [NIST SP 800-57 Part 1: Recommendation for Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [Root KSK Ceremonies — IANA](https://www.iana.org/dnssec/ceremonies)
- [Key Management Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html)
