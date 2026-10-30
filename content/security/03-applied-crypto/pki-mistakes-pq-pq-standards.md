---
id: pki-mistakes-pq-pq-standards
title: Post-quantum standards and wire sizes
level: advanced
minutes: 2
sourceLesson: pki-mistakes-pq
summary: ML-KEM, ML-DSA and SLH-DSA have different jobs and mathematical foundations.
---

If quantum computers break today's public-key algorithms, something has to replace them. NIST has now standardised the first replacements, and their practical cost is mostly size.

## The new standards

NIST ran a public competition from 2016 and published the first standards in August 2024:

- **ML-KEM** (FIPS 203, from Kyber): a lattice-based key encapsulation mechanism for key exchange.
- **ML-DSA** (FIPS 204, from Dilithium): a general-purpose lattice-based signature standard.
- **SLH-DSA** (FIPS 205, from SPHINCS+): hash-based signatures, relying only on hash functions. This offers different mathematical assumptions from lattice schemes, with larger signatures and parameter-dependent performance.

A further lattice signature (FN-DSA, from Falcon) is being standardised, and in March 2025 NIST picked **HQC**, a code-based KEM, as a backup to ML-KEM in case lattices fall; as of October 2026 NIST describes both standards as still under development. The competition showed why hedging matters: two leading candidates, the signature finalist Rainbow and the KEM SIKE, were broken in 2022, the SIKEp434 parameter set in about an hour on a single core in the original attack authors' reported implementation.

The big practical difference is size:

| Scheme | Public key | Ciphertext/sig |
|---|---|---|
| X25519 | 32 B | 32 B peer public share (not a ciphertext/signature) |
| ML-KEM-768 | 1,184 B | 1,088 B |
| Ed25519 | 32 B | 64 B |
| ML-DSA-44 | 1,312 B | 2,420 B |
| ML-DSA-65 | 1,952 B | 3,309 B |
| SLH-DSA-128s | 32 B | 7,856 B |

ML-KEM can be computationally efficient, but relative CPU cost depends on implementation, platform and operation. Key and ciphertext size are additional deployment costs, not the only ones.

## Key takeaways
- ML-KEM, ML-DSA and SLH-DSA have different jobs and mathematical foundations.
- HQC was selected for standardisation to diversify KEM assumptions.
- Wire sizes differ substantially; CPU costs still depend on implementation and platform.

## Further reading
- [FIPS 203: ML-KEM](https://csrc.nist.gov/pubs/fips/203/final)
- [FIPS 204: ML-DSA](https://csrc.nist.gov/pubs/fips/204/final)
- [FIPS 205: SLH-DSA](https://csrc.nist.gov/pubs/fips/205/final)
- [NIST post-quantum cryptography project](https://csrc.nist.gov/projects/post-quantum-cryptography)
