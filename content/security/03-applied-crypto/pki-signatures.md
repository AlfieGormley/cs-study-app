---
id: pki-signatures
title: Digital signatures
level: basic
minutes: 12
summary: How a private key produces a signature anyone can check, how signature schemes process messages and why textbook RSA is unsafe, how RSA-PSS, ECDSA and Ed25519 differ, and where signatures quietly hold the internet together.
---

A **digital signature** lets a signature verifier with a trusted public key check message integrity and authenticity to the corresponding signing key, under the scheme's security assumptions. It does not identify a human or establish freshness by itself.

The previous module covered message authentication codes (MACs). MACs also prove integrity and origin, but both sides share the same secret key, so either side could have produced the tag. A signature splits the key in two. Holders of the private key can sign; anyone with the public key can verify. That asymmetry is what makes signatures useful between strangers, and it is the foundation of certificates, software updates and TLS.

## What a signature scheme is

Every signature scheme is three algorithms:

1. **KeyGen** produces a key pair: a private signing key `sk` and a public verification key `pk`.
2. **Sign(sk, message)** produces a signature, a short string of bytes.
3. **Verify(pk, message, signature)** returns true or false.

The security goal is called **existential unforgeability under chosen-message attack** (EUF-CMA). Even if an attacker can get you to sign any messages they like, they still cannot produce a valid signature on *any* new message. Not a meaningful one, not a random one, nothing.

| Property | MACs | Signatures |
|---|---|---|
| Keys | One shared secret | Private + public |
| Who can create | Anyone with the key | Private key holder |
| Who can verify | Anyone with the key | Anyone |
| Signature verifier can check without signing power | No (shared key) | Yes |
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

The raw RSA private exponentiation resembles the RSA decryption primitive, but real signature encoding is different from encryption padding. For this arithmetic-only example, the signer raises the message's hash to the private exponent, and the signature verifier raises the signature to the public exponent and checks that the hash comes back:

```formula
s = h^d mod n
h' = s^e mod n
where
s: the signature, a whole number from 0 to n − 1
h: the message's hash, treated as a whole number smaller than n
d: the private exponent, the secret half of the RSA key; only the signer knows it
e: the public exponent, part of the public key; real keys almost always use 65,537
n: the modulus, the product of two secret primes; part of the public key, at least 2,048 bits (about 617 decimal digits) in real keys
h': the value the signature verifier recovers from the signature; the signature is accepted only if h' equals h
mod: modulo: the remainder after dividing by n (for example, 17 mod 5 = 2)
In words: signing raises the hash to the private power and verifying raises the signature to the public power; the two powers undo each other, so a genuine signature gives back the hash.
```

Why do the two powers undo each other? The key is built so that e × d leaves remainder 1 when divided by a number only the key owner can compute:

```formula
n = p × q
φ = (p − 1) × (q − 1)
e × d mod φ = 1
where
n: the public modulus
p: the first secret prime
q: the second secret prime
φ: phi (Euler's totient of n): how many numbers from 1 to n share no factor with n; computing it needs p and q, so it stays secret
e: the public exponent
d: the private exponent
mod: modulo: the remainder after division
In words: d is the number that cancels e when you count in remainders of φ; Euler's theorem (plus a short extra argument for the rare numbers that share a factor with n) then guarantees that raising any number below n to the power e and then to the power d gives the original number back, modulo n.
```

Use the classic small key, with primes 61 and 53, public exponent 17 and private exponent 2753. Suppose the message hashes to 65:

```formula
n = 61 × 53 = 3233
φ = 60 × 52 = 3120
17 × 2753 = 46,801 = 15 × 3120 + 1
s = 65^{2753} mod 3233 = 588
h' = 588^{17} mod 3233 = 65
where
n: the toy public modulus
φ: phi, the secret totient (p − 1) × (q − 1)
s: the signature Alice produces with her private exponent 2753
h': the value Bob recovers with the public exponent 17; it equals the hash 65, so the signature is valid
mod: modulo: the remainder after dividing by 3233
In words: 17 × 2753 is one more than a multiple of 3120, so the exponents cancel; signing 65 gives 588, and raising 588 to the 17th power modulo 3233 gives 65 back.
```

Anyone can break this tiny example by factoring n or testing candidates. Real security requires large keys and a complete specified signature scheme; public verification alone is illustrated here.

### Why textbook RSA signatures are broken

Raw RSA (the formula above, with no padding) has fatal algebraic structure:

- **Raw-message forgery.** If any number below the modulus counts as a message, an attacker can pick the signature first and compute, from the public key alone, which message it verifies for (first formula below). If the scheme instead hashes an external message first, this does not by itself find a message with that hash; do not confuse those two models. Neither observation justifies inventing a signature encoding.
- **Multiplication.** Multiplying two valid signatures gives a valid signature on the product of their messages (second formula below).

The forgery runs verification backwards:

```formula
m = s^e mod n
m = 5^{17} mod 3233 = 3086
where
m: the forged message, a number below n
s: the forged signature: any number the attacker likes; here 5
e: the public exponent; 17 in the toy key
n: the public modulus; 3233 in the toy key
mod: modulo: the remainder after dividing by n
In words: pick the signature, then compute the message it signs; the pair (3086, 5) passes verification although the key owner never signed 3086.
```

The multiplication property follows from the rules of powers:

```formula
sig(x) = x^d mod n
a^d × b^d = (a × b)^d
sig(a) × sig(b) mod n = sig(a × b)
1027 × 1857 mod 3233 = 2902 = sig(6)
where
sig: textbook RSA signing with the private exponent
x: any message, as a number below n
a: a first message the owner signed; here 2, whose signature is 1027
b: a second signed message; here 3, whose signature is 1857
d: the private exponent; 2753 in the toy key
n: the public modulus; 3233 in the toy key
mod: modulo: the remainder after dividing by n
In words: two signatures multiplied together are a signature on the two messages multiplied together, so an attacker holding the signatures on 2 and 3 gets the signature on 6 (2902) without the private key.
```

The forged message 3086 is meaningless, but EUF-CMA counts any new valid pair as a break, and the multiplication trick can produce chosen values.

Real RSA therefore **pads** the hash into a structured, full-width number first:

- **PKCS#1 v1.5** padding: deterministic and used in existing protocols. Secure for signatures if verified strictly, but sloppy parsers have led to forgeries such as Bleichenbacher's 2006 attack on keys with public exponent 3.
- **RSA-PSS**: randomised padding with a security proof. TLS 1.3 requires PSS when RSA signs the handshake.

## ECDSA and the nonce

ECDSA signs using an elliptic-curve key. Each signature needs a secret nonce selected according to the scheme, either securely at random or with a specified deterministic derivation. The signature is a pair of numbers:

```formula
r = x(k × G) mod n
s = k^{−1} × (h + r × d) mod n
where
r: the first half of the signature: the x-coordinate of the point k × G, reduced modulo n
s: the second half of the signature
k: the secret per-signature nonce, a number from 1 to n − 1; it must never repeat, leak or be biased
G: the generator: a fixed, public starting point on the elliptic curve, part of the curve's definition
k × G: elliptic-curve scalar multiplication: adding the point G to itself k times; easy to compute, infeasible to reverse
x: "the x-coordinate of" a point on the curve
h: the message hash, as a number (its leftmost bits if the hash is longer than n)
d: the signer's private key, a secret number; the public key is the point d × G
n: the order of G: how many distinct points you visit by repeatedly adding G before returning to the start; about 2^256 for P-256
k^{−1}: the modular inverse of k: the number that gives remainder 1 when multiplied by k, modulo n
mod: modulo: the remainder after dividing by n
In words: r is a public fingerprint of the secret nonce, and s mixes the nonce, the hash and the private key so that only someone who knows d can produce a pair that verifies against the public key.
```

A signature verifier with the public key checks the pair without learning k or d.

The nonce is the weak point:

- **Reuse `k` for two messages** and anyone can solve two equations for `k`, then for your private key `d`. Sony's PlayStation 3 used a constant `k` for its firmware-signing key; in 2010 the fail0verflow team recovered the key and could sign anything.
- **Certain nonce biases or partial leaks** can enable private-key recovery with enough signatures; exploitability depends on the bias and observations. In 2013 a flaw in Android's `SecureRandom` let attackers steal Bitcoin from wallets that had repeated nonces.

Here is why reuse is fatal. Two signatures with the same k share the same r, and each s gives one equation. Two equations, two unknowns:

```formula
s_1 × k = h_1 + r × d   (mod n)
s_2 × k = h_2 + r × d   (mod n)
k = (h_1 − h_2) / (s_1 − s_2)   (mod n)
d = (s_1 × k − h_1) / r   (mod n)
where
s_1: the s half of the first signature, public
s_2: the s half of the second signature, public
h_1: the hash of the first message, public
h_2: the hash of the second message, public; it must differ from h_1
r: the r half, identical in both signatures because k repeated
k: the reused nonce, secret until this calculation
d: the private key
n: the order of the curve's generator, about 2^256 for P-256
mod: modulo: every step is done in remainders after dividing by n
/: division modulo n: multiplying by the modular inverse of the divisor
In words: subtracting the two equations cancels the private-key term and reveals k; putting k back into either equation reveals d.
```

The first two lines are just the signing formula multiplied through by k. Everything on the right-hand side of the last two lines is public once k is known, so two signatures are enough.

One standard option is **deterministic ECDSA** (RFC 6979), deriving k from the private key and message hash. It removes reliance on fresh signing-time randomness, but is not a mathematical uniqueness guarantee across all messages. Secure randomness is still needed for key generation, and side-channel/fault defenses remain necessary.

## Ed25519: designed to be hard to misuse

**Ed25519** (EdDSA on the Edwards-form edwards25519 curve, RFC 8032) bakes these lessons in:

- The nonce is computed from a secret and the message by a fixed rule. Same key and message, same signature; no fresh per-signature RNG input is required. Key generation still needs secure randomness.
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
| ECDSA P-256 | 65 B uncompressed SEC1; 33 B compressed | 64 B (r then s, 32 B each) | Needs a correctly generated nonce |
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
- ECDSA nonce reuse across suitable distinct message hashes can reveal the private key; exploitable bias can also enable recovery.  RFC 6979 and Ed25519 derive nonces from the key and message instead of fresh randomness.
- Ed25519 is the modern default: small, fast, deterministic and hard to misuse.
- Verify against a pinned algorithm and act only on the exact bytes that were signed.

## Further reading
- [Digital signature — Wikipedia](https://en.wikipedia.org/wiki/Digital_signature)
- [RFC 8032: Edwards-Curve Digital Signature Algorithm (EdDSA)](https://www.rfc-editor.org/rfc/rfc8032)
- [RFC 6979: Deterministic Usage of DSA and ECDSA](https://www.rfc-editor.org/rfc/rfc6979)
- [Ed25519 signing — pyca/cryptography docs](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/)
- [Critical vulnerabilities in JSON Web Token libraries — Auth0](https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/)
