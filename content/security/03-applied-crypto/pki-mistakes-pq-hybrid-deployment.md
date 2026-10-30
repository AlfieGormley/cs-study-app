---
id: pki-mistakes-pq-hybrid-deployment
title: Hybrid deployment and migration engineering
level: advanced
minutes: 3
sourceLesson: pki-mistakes-pq
summary: A reviewed hybrid combiner aims to retain secrecy when either component remains secure.
---

The post-quantum algorithms are standardised, but they are young and large. Real deployments therefore combine them with classical algorithms and plan a long, careful migration.

## Hybrids and deployment

Because the new schemes are young, several prominent deployments use **hybrid key exchange**: run classical and post-quantum algorithms together and combine the secrets, so a correctly analysed combiner can preserve security if either component holds; whole-process compromise is outside that guarantee.

- **TLS**: Chrome introduced `X25519MLKEM768` in version 131. Relative to X25519 alone, its key-share payload adds 1,184 bytes client-to-server and 1,088 bytes server-to-client; deployment policies vary.
- **SSH**: OpenSSH made a hybrid with Streamlined NTRU Prime the default in 2022, and moved to `mlkem768x25519-sha256` by default in version 10.0 in 2025.
- **Messaging**: Signal's PQXDH (2023) and SPQR ratchet (2025); Apple's iMessage PQ3 (2024).

Signatures are harder. Consider a server sending a leaf and one intermediate certificate, both with ML-DSA-65 keys and signatures, and signing CertificateVerify with ML-DSA-65. The client receives two public keys and three signatures: about 13.8 KB of keys and signatures alone, before names, extensions and SCTs, against 256 bytes for the same items with Ed25519. That is close to a typical TCP initial congestion window of about 14.6 KB (ten segments), so a real chain can push the server's first flight past it. Whether that costs an extra round trip depends on the actual window, chain and acknowledgement timing. Proposals such as Merkle Tree Certificates aim to shrink this before PQ certificates become mandatory.

> [!analogy] Real-world analogy: Two different locks on one door
> When you are unsure whether a new lock design is as good as it claims, you fit it alongside the old lock you trust. A burglar now has to defeat both.
>
> **How it maps:** Hybrid key exchange runs a classical algorithm (X25519) and a post-quantum one (ML-KEM) and feeds both secrets into one key derivation. If the new algorithm turns out to have a flaw, the classical one still protects the session, and if a quantum computer breaks the classical one, ML-KEM still does.
>
> **Where it stops:** Two physical locks work independently, so fitting a second one can never weaken the first. In a hybrid, the two secrets are mixed by a specified combiner whose security has to be analysed, and both algorithms run in the same software on the same device: a bug that leaks memory can expose both secrets at once. A hybrid also protects only the key exchange; the certificate signatures still need their own migration.

## Planning a migration

1. **Inventory.** Find every place you use public-key crypto: TLS endpoints, VPNs, SSH, code signing, JWTs, stored encrypted data, HSMs, embedded devices with 15-year lifetimes. Inventory and dependencies can dominate the migration work.
2. **Prioritise by exposure and lifetime.** Long-lived confidential records need harvest-now-decrypt-later protection. Root CA and software-update keys create a distinct long-lived authentication risk, so include their replacement and device-update durations.
3. **Get crypto-agile.** Hard-coded algorithms, fixed field sizes for keys and signatures, and HSMs without PQ firmware all block migration. Design so algorithms can be swapped by configuration.
4. **Evaluate supported hybrid key exchange** through compatibility testing, library/service upgrades and deployment policy; middleboxes, protocol negotiation and operational constraints may also require changes.
5. **Plan signatures** to follow standards and timelines. NIST IR 8547, finalised on 27 October 2026, says NIST will deprecate quantum-vulnerable public-key cryptography after 2030 and disallow it under NIST standards and guidelines after 2035, while US federal directives require the most sensitive systems to move earlier. These dates bind organisations that follow NIST rules; other sectors and countries set their own, so check the policy that applies to you.

## Key takeaways
- A reviewed hybrid combiner aims to retain secrecy when either component remains secure.
- Larger post-quantum keys and signatures affect handshake size and protocol engineering.
- Inventory dependencies, test interoperability and check which dated transition policy actually applies to your systems.

## Further reading
- [NIST IR 8547: Transition to Post-Quantum Cryptography Standards](https://csrc.nist.gov/pubs/ir/8547/final)
- [NIST releases first three finalised post-quantum encryption standards — NIST](https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards)
- [The state of the post-quantum Internet — Cloudflare blog](https://blog.cloudflare.com/pq-2024/)
- [OpenSSH 10.0 release notes](https://www.openssh.com/txt/release-10.0)
