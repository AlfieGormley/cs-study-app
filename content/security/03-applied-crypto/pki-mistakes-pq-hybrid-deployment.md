---
id: pki-mistakes-pq-hybrid-deployment
title: Hybrid deployment and migration engineering
level: advanced
minutes: 3
sourceLesson: pki-mistakes-pq
summary: A reviewed hybrid combiner aims to retain secrecy when either component remains secure.
---

Cryptographic security depends on the complete construction and its implementation, including key generation, message authentication and correct nonce handling.

## Hybrids and deployment

Because the new schemes are young, several prominent deployments use **hybrid key exchange**: run classical and post-quantum algorithms together and combine the secrets, so a correctly analysed combiner can preserve security if either component holds; whole-process compromise is outside that guarantee.

- **TLS**: Chrome introduced `X25519MLKEM768` in version 131. Relative to X25519 alone, its key-share payload adds 1,184 bytes client-to-server and 1,088 bytes server-to-client; deployment policies vary.
- **SSH**: OpenSSH made a hybrid with Streamlined NTRU Prime the default in 2022, and moved to `mlkem768x25519-sha256` by default in version 10.0 in 2025.
- **Messaging**: Signal's PQXDH (2023) and SPQR ratchet (2025); Apple's iMessage PQ3 (2024).

Signatures are harder. For an illustrative leaf-plus-one-intermediate chain, two public keys and three signatures are transmitted, including CertificateVerify:

```formula
L_auth = 2 × L_pk + 3 × L_sig
L_auth = 2 × 1,952 + 3 × 3,309
L_auth = 3,904 + 9,927 = 13,831 B
where
L_auth: bytes of keys and signatures the client receives
L_pk: one ML-DSA-65 public key, 1,952 bytes; two are sent (leaf and intermediate; the client already holds the root)
L_sig: one ML-DSA-65 signature, 3,309 bytes; three are sent (on the leaf, on the intermediate, and CertificateVerify)
B: bytes
In words: the post-quantum keys and signatures alone come to about 13.8 KB, against 256 bytes for the same items with Ed25519 (two 32-byte keys and three 64-byte signatures).
```

These 13,831 bytes come before certificate encoding/extensions and any SCTs. Actual chain composition and TCP initial-window configuration determine whether more acknowledgement pacing is needed; an extra full round trip is not automatic. Proposals such as Merkle Tree Certificates aim to shrink this before PQ certificates become mandatory.

## Planning a migration

1. **Inventory.** Find every place you use public-key crypto: TLS endpoints, VPNs, SSH, code signing, JWTs, stored encrypted data, HSMs, embedded devices with 15-year lifetimes. Inventory and dependencies can dominate the migration work.
2. **Prioritise by exposure and lifetime.** Long-lived confidential records need harvest-now-decrypt-later protection. Root CA and software-update keys create a distinct long-lived authentication risk, so include their replacement and device-update durations.
3. **Get crypto-agile.** Hard-coded algorithms, fixed field sizes for keys and signatures, and HSMs without PQ firmware all block migration. Design so algorithms can be swapped by configuration.
4. **Evaluate supported hybrid key exchange** through compatibility testing, library/service upgrades and deployment policy; middleboxes, protocol negotiation and operational constraints may also require changes.
5. **Plan signatures** to follow standards and timelines: the November 2024 draft NIST IR 8547 proposed security-strength-dependent transition dates, including 2030 deprecation and 2035 disallowance for listed classical uses. Treat this as a dated draft proposal, not a universal law or a final rule for every application.

## Key takeaways
- A reviewed hybrid combiner aims to retain secrecy when either component remains secure.
- Larger post-quantum keys and signatures affect handshake size and protocol engineering.
- Inventory dependencies, test interoperability and distinguish dated draft transition guidance from binding application policy.

## Further reading
- [Cryptographic storage guidance — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [NIST post-quantum project](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [NIST releases first three finalised post-quantum encryption standards — NIST](https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards)
- [FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard](https://csrc.nist.gov/pubs/fips/203/final)
- [The state of the post-quantum Internet — Cloudflare blog](https://blog.cloudflare.com/pq-2024/)
- [Nonce-disrespecting adversaries: practical forgery attacks on GCM in TLS](https://eprint.iacr.org/2016/475)
- [Mining your Ps and Qs: weak keys in network devices](https://factorable.net/)
- [Cryptographic Storage Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
