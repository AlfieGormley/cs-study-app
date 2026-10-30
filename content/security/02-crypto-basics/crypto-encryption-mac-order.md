---
id: crypto-encryption-mac-order
sourceLesson: crypto-macs
title: Why encryption and authentication order matters
level: intermediate
minutes: 3
summary: Under suitable assumptions, encrypt-then-MAC checks protected ciphertext before decryption.
---

## Combining encryption and a MAC

Before AEAD modes were common, people combined a cipher and a MAC by hand. There are three orders:

| Scheme | Used by | Verdict |
|---|---|---|
| Encrypt-then-MAC | Traditional encryption-plus-integrity IPsec ESP suites | Sound under suitable primitive, key and encoding assumptions |
| MAC-then-encrypt | Original TLS CBC suites | Difficult to implement without side channels |
| Encrypt-and-MAC | SSH (original) | Fragile |

**Encrypt-then-MAC** computes the MAC over the ciphertext. The receiver checks the tag first and rejects failed authentication before decryption. Under the stated composition assumptions, unauthenticated requests therefore cannot obtain a padding-validity response.

**MAC-then-encrypt** requires decryption before verifying its inner MAC. TLS also defined an encrypt-then-MAC extension (RFC 7366), so this is not the behaviour of every TLS CBC connection. The padding oracle and Lucky Thirteen attacks on TLS CBC suites exploited exactly this. **Encrypt-and-MAC** MACs the plaintext and can leak whether two plaintexts are equal.

> [!analogy] Real-world analogy: A seal outside the box, or inside it
> A depot receives parcels it must not trust. If the tamper seal is on the outside, staff check it and refuse a damaged parcel without opening it. If the seal is packed inside, they must open every parcel first, and anything nasty inside gets handled before anyone knows the parcel was tampered with.
>
> **How it maps:** The outside seal is encrypt-then-MAC: the receiver checks the tag over the ciphertext and rejects forgeries before decrypting. The inside seal is MAC-then-encrypt: the receiver must decrypt and strip padding before it can check the MAC, and differences in how it handles bad padding become a padding oracle.
>
> **Where it stops:** The danger in MAC-then-encrypt is not a harmful payload but information leaking from the decryption steps themselves, through error messages or timing. And checking the seal first only helps if the MAC also covers the IV, headers and anything else the receiver uses.

Today the answer is simpler: use a maintained AEAD implementation such as AES-GCM or ChaCha20-Poly1305, following its nonce, tag and key-usage limits. If you must compose by hand, use encrypt-then-MAC with **separate keys** for encryption and authentication, and include the IV and any headers in the MAC.

## Pitfalls

- **Comparing tags with `==`.** Use `hmac.compare_digest` or your library's constant-time verify.
- **Weak or shared keys.** Use the key format and entropy required by the MAC; 32 random bytes are suitable for HMAC-SHA256. Do not substitute a guessable word such as `"secret"`. Use different keys for different purposes.
- **Forgetting replay.** Add a timestamp or counter to the signed data, and reject stale or repeated values.
- **Authenticating the wrong thing.** If the URL path, HTTP method or a header changes meaning, it must be inside the MAC.
- **Expecting non-repudiation.** If a third party needs to verify who sent something, use signatures.
- **Inventing your own scheme.** Use HMAC or a library's AEAD; don't design MAC constructions.

## Key takeaways
- Under suitable assumptions, encrypt-then-MAC checks protected ciphertext before decryption.
- Prefer a specified AEAD instead of assembling separate primitives.

## Further reading
- [Python cryptography: AEAD APIs](https://cryptography.io/en/latest/hazmat/primitives/aead/)
- [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
