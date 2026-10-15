---
id: crypto-hash-algorithm-choices
sourceLesson: crypto-hashes
title: Hash families and historical collision attacks
level: basic
minutes: 3
summary: MD5 and SHA-1 lack collision resistance; choose a specified modern hash for its intended purpose.
---

## The hash family tree

| Hash | Output | Status |
|---|---|---|
| MD5 | 128 bits | Broken collision resistance; do not use for new cryptographic designs |
| SHA-1 | 160 bits | Broken (practical collisions) |
| SHA-256 / SHA-512 | 256 / 512 | Secure, the default |
| SHA-3-256 | 256 bits | Secure |
| BLAKE2b / BLAKE2s | up to 512 / 256 bits | Configurable digest length |
| BLAKE3 | 256-bit default; extensible output | Longer output does not imply proportionally greater security |

**MD5** collisions were found in 2004 and became cheap enough to weaponise. In 2012 the Flame malware used an MD5 collision to forge a code-signing certificate that Windows Update trusted.

**SHA-1** fell in 2017, when Google and CWI Amsterdam published **SHAttered**: two different PDF files with the same SHA-1 hash. It took around 2^63 SHA-1 computations, about 6,500 CPU-years plus 110 GPU-years. Later "chosen-prefix" attacks made it cheaper still. Browser vendors phased out SHA-1-signed public TLS certificates; the 2017 collision is a historical result, not a new benchmark.

**SHA-2** (SHA-224, SHA-256, SHA-384, SHA-512 and the truncated variants SHA-512/224 and SHA-512/256) is the workhorse: TLS certificates, code signing, Bitcoin, package managers. **BLAKE2** and **BLAKE3** provide modern alternatives. WireGuard specifies BLAKE2s; do not infer that each named product uses both families.

> [!tip] What to pick
> Use **SHA-256** when you need a general-purpose hash. Use SHA-512/256, SHA-3 or BLAKE2 if you want immunity to length extension. Do not choose MD5 or SHA-1 for new cryptographic designs; collision attacks do not automatically break every legacy HMAC use.

## Key takeaways
- MD5 and SHA-1 lack collision resistance; choose a specified modern hash for its intended purpose.
- A collision attack on an unkeyed hash is not automatically an HMAC forgery.

## Further reading
- [NIST FIPS 180-4: secure hashes](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
- [NIST FIPS 202: SHA-3](https://csrc.nist.gov/pubs/fips/202/final)
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
