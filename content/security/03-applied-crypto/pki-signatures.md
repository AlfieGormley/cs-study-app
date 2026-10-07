---
id: pki-signatures
title: Digital signatures
level: basic
minutes: 12
summary: How a private key produces a signature anyone can check, how signature schemes process messages and why textbook RSA is unsafe, how RSA-PSS, ECDSA and Ed25519 differ, and where signatures quietly hold the internet together.
---

A **digital signature** lets a verifier with a trusted public key check message integrity and authenticity to the corresponding signing key, under the scheme's security assumptions. It does not identify a human or establish freshness by itself.

The previous module covered MACs. A MAC also proves integrity and origin, but both sides share the same secret key, so either side could have produced the tag. A signature splits the key in two. Holders of the private key can sign; anyone with the public key can verify. That asymmetry is what makes signatures useful between strangers, and it is the foundation of certificates, software updates and TLS.

## What a signature scheme is

Every signature scheme is three algorithms:

1. **KeyGen** produces a key pair: a private signing key `sk` and a public verification key `pk`.
2. **Sign(sk, message)** produces a signature, a short string of bytes.
3. **Verify(pk, message, signature)** returns true or false.

The security goal is called **existential unforgeability under chosen-message attack** (EUF-CMA). Even if an attacker can get you to sign any messages they like, they still cannot produce a valid signature on *any* new message. Not a meaningful one, not a random one, nothing.

| Property | MAC | Signature |
|---|---|---|
| Keys | One shared secret | Private + public |
| Who can create | Anyone with the key | Private key holder |
| Who can verify | Anyone with the key | Anyone |
| Verifier can check without signing power | No (shared MAC key) | Yes |
| Speed | Very fast | Much slower |

Signatures can support evidence of origin because verification need not grant signing authority. Attribution also needs trustworthy identity binding, key custody and protocol context.

> [!note] Content gap: legal effect
> This lesson supplies no jurisdiction-specific legal assessment. It does not claim a signature alone proves a person acted, guarantees admissibility or determines a dispute.

> [!warning] Signing is not encrypting
> A signature does nothing for confidentiality. The message is sent alongside it in the clear. If both are needed, use a suitable authenticated-encryption protocol. TLS certificate handshakes use signatures for authentication; Signal's message protection is not simply a publicly verifiable signature on every message.

## Hash, then sign

Many signature schemes hash messages as part of their encoding, but the construction is scheme-specific. For example, pure Ed25519 hashes the message together with secret-derived material and signature/public-key data; it is not simply Sign(SHA256(message)). Follow the API's message or prehash interface. The diagram is only a simplified hash-then-sign construction.

```
simplified hash-then-sign example
message
     |
  SHA-256
     |
 32-byte digest --Sign(sk)--> signature
```

This is why hash **collision resistance** matters so much. If an attacker can find two documents with the same hash, a signature on the harmless one is also a valid signature on the harmful one. That is exactly how researchers forged a rogue CA certificate using MD5 collisions in 2008, and why SHA-1 was retired from certificates, a decision vindicated by the SHAttered collision in 2017.

## A toy RSA signature

The raw RSA private exponentiation resembles the RSA decryption primitive, but real signature encoding is different from encryption padding. For this arithmetic-only example, `s = h^d mod n`. Verification raises it back: `s^e mod n` should give `h`.

Use the classic small key: `p = 61`, `q = 53`, `n = 3233`, `e = 17`, `d = 2753`. Suppose the message hashes to `h = 65`.

```
sign:   s = 65^2753 mod 3233 = 588
verify: 588^17 mod 3233     = 65  ✓
```

Anyone can break this tiny example by factoring n or testing candidates. Real security requires large keys and a complete specified signature scheme; public verification alone is illustrated here.

### Why textbook RSA signatures are broken

Raw `h^d mod n` has fatal algebraic structure:

- **Raw-message forgery.** If the message space is the integers modulo n, pick s and compute m = s^e mod n. The pair verifies. If the scheme instead hashes an external message first, this does not by itself find a message with hash m; do not confuse those two models. Neither observation justifies inventing a signature encoding.
- **Multiplication.** `sig(a) × sig(b) mod n = sig(a × b)`. With the toy key, `sig(2) × sig(3)` is a valid signature on 6.

Real RSA therefore **pads** the hash into a structured, full-width number first:

- **PKCS#1 v1.5** padding: deterministic and used in existing protocols. Secure for signatures if verified strictly, but sloppy parsers have led to forgeries such as Bleichenbacher's 2006 "e = 3" attack.
- **RSA-PSS**: randomised padding with a security proof. TLS 1.3 requires PSS when RSA signs the handshake.

## ECDSA and the nonce

ECDSA signs using an elliptic-curve key. Each signature needs a secret nonce k selected according to the scheme, either securely at random or with a specified deterministic derivation. The signature is a pair `(r, s)` where `r` comes from `k·G` and `s = k⁻¹(h + r·d) mod n`.

The nonce is the weak point:

- **Reuse `k` for two messages** and anyone can solve two equations for `k`, then for your private key `d`. Sony's PlayStation 3 used a constant `k` for its firmware-signing key; in 2010 the fail0verflow team recovered the key and could sign anything.
- **Certain nonce biases or partial leaks** can enable private-key recovery with enough signatures; exploitability depends on the bias and observations. In 2013 a flaw in Android's `SecureRandom` let attackers steal Bitcoin from wallets that had repeated nonces.

One standard option is **deterministic ECDSA** (RFC 6979), deriving k from the private key and message hash. It removes reliance on fresh signing-time randomness, but is not a mathematical uniqueness guarantee across all messages. Secure randomness is still needed for key generation, and side-channel/fault defenses remain necessary.

## Ed25519: designed to be hard to misuse

**Ed25519** (EdDSA on the Edwards-form edwards25519 curve, RFC 8032) bakes these lessons in:

- The nonce is derived deterministically from a secret and the message. Same key and message, same signature; no fresh per-signature RNG input is required. Key generation still needs secure randomness.
- It is fast, constant-time by design, and has small keys and signatures.
- There are fewer parameters to get wrong. You do not pick a hash or a padding scheme.

```python
from cryptography.hazmat.primitives \
    .asymmetric import ed25519
from cryptography import exceptions

sk = ed25519.Ed25519PrivateKey.generate()
pk = sk.public_key()

msg = b"pay alice 10 GBP"
sig = sk.sign(msg)
print(len(sig))          # 64

pk.verify(sig, msg)      # no exception
try:
    pk.verify(sig, b"pay alice 99 GBP")
except exceptions.InvalidSignature:
    print("rejected")
print(sk.sign(msg) == sig)  # True
```

The last line prints `True` because Ed25519 is deterministic. ECDSA with independently random nonces would normally print False; deterministic ECDSA can instead repeat the signature for the same key and message.

## Choosing an algorithm

| Scheme | Public key | Signature | Notes |
|---|---|---|---|
| RSA-2048 | 256 B modulus plus exponent/encoding | 256 B | Cost depends on exponent and implementation |
| ECDSA P-256 | 65 B uncompressed SEC1; 33 B compressed | 64 B fixed-width r||s | Needs a correctly generated nonce |
| Ed25519 | 32 B | 64 B | Deterministic, fast |
| ML-DSA-44 | 1,312 B | 2,420 B | Post-quantum |

Sizes depend on encoding: DER ECDSA signatures vary, commonly around 70–72 bytes for P-256; smaller encodings can occur. Ed25519 is a useful choice when the protocol supports it. ECDSA P-256 is widely interoperable, but FIPS 186-5 also specifies EdDSA; compliance depends on a validated implementation and applicable policy. WebAuthn support depends on negotiated algorithms and authenticators. Post-quantum signatures are covered later.

## Where signatures are used

- **TLS**: a CA signs the server's certificate, and the server signs the handshake (next two lessons).
- **Software updates and packages**: apt, Windows Authenticode, Apple code signing, Android APKs, and Sigstore for open-source artefacts.
- **Git**: signed commits and tags, with GPG or SSH keys.
- **Tokens**: JWTs signed with RS256, ES256 or EdDSA, so any service can verify without the issuer's secret.
- **Email**: DKIM validates selected headers and body content against a signing domain's key. The signing domain need not match the visible From address; DMARC alignment is a separate check.
- **Passkeys**: WebAuthn assertions sign authenticator data plus a client-data hash that binds the challenge and origin. Some passkeys synchronize between devices; device-bound and backed-up credentials have different custody models.

## Pitfalls

- **Check what was actually signed.** XML Signature "wrapping" attacks moved the signed element and inserted an unsigned one that the application then read. Sign canonical bytes, and act only on the bytes you verified.
- **Do not let the message choose the algorithm.** Early JWT libraries trusted the token's `alg` header, so `alg: none` or switching RS256 to HS256 (using the public key as an HMAC secret) bypassed verification. Pin the expected algorithm.
- **A signature proves the key, not the person.** Binding a public key to an identity is a separate problem, solved by certificates.
- **Compromised keys can create new forgeries.** Trusted timestamps or other reliable prior records can help distinguish older signatures. Whether an old artifact remains acceptable depends on the earliest plausible compromise, trust-chain validation and policy, not a universal timestamp rule.

## Key takeaways
- A signature is created with a private key and verified with the public key, so anyone with the public key can check it, while producing signatures requires the private key under the scheme's security assumptions.
- Message hashing and encoding are scheme-specific; follow the scheme's API rather than inventing a hash-then-sign construction.
- Textbook RSA signatures are forgeable; real RSA uses PKCS#1 v1.5 or, better, PSS padding.
- ECDSA nonce reuse across suitable distinct message hashes can reveal the private key; exploitable bias can also enable recovery.  RFC 6979 and Ed25519 derive nonces deterministically.
- Ed25519 is the modern default: small, fast, deterministic and hard to misuse.
- Verify against a pinned algorithm and act only on the exact bytes that were signed.

## Further reading
- [Digital signature — Wikipedia](https://en.wikipedia.org/wiki/Digital_signature)
- [RFC 8032: Edwards-Curve Digital Signature Algorithm (EdDSA)](https://www.rfc-editor.org/rfc/rfc8032)
- [RFC 6979: Deterministic Usage of DSA and ECDSA](https://www.rfc-editor.org/rfc/rfc6979)
- [Ed25519 signing — pyca/cryptography docs](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/)
- [Critical vulnerabilities in JSON Web Token libraries — Auth0](https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/)
