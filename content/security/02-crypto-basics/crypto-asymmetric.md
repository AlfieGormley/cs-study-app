---
id: crypto-asymmetric
title: Asymmetric encryption
level: intermediate
minutes: 14
summary: Public and private keys, a full small-number RSA walkthrough, why textbook RSA is insecure and OAEP is needed, key sizes, hybrid encryption, and the intuition behind elliptic-curve cryptography.
---

Symmetric encryption has a chicken-and-egg problem. To talk securely, you and a server must share a key. But how do you get the key to them securely in the first place, over a network an attacker is watching?

**Asymmetric** (public-key) cryptography uses a mathematically related pair of keys:

- A **public key** you can publish to the world.
- A **private key** you never share.

```
Anyone:   Enc(public, msg) -> ciphertext
Only you: Dec(private, ct) -> msg
```

Anyone can lock a box with your public key; only your private key opens it. It is like a padlock you hand out freely, with the one key on your keyring.

RSA illustrates a **trapdoor** operation: reversing it is intended to be hard without secret information. Other public-key constructions use different mathematical structures. Public-key encryption also needs an authenticated public key: if an attacker substitutes their own, secrecy from that attacker is lost.

## RSA: the idea

RSA (1977) is built on one asymmetry in arithmetic:

- Multiplication is efficient compared with known classical factoring methods for appropriately generated RSA-sized semiprimes.
- **Factoring** the product back into its primes is hard. The best known classical algorithm, the general number field sieve, takes time that grows faster than any polynomial in the number of digits. In 2020, researchers factored RSA-250 (829 bits). Their report lists about 2,450 core-years for sieving and 250 for linear algebra, plus 114 for polynomial selection. These are reported historical costs, not a current universal benchmark or claim about the latest record.

RSA works in **modular arithmetic**, "clock arithmetic" where numbers wrap around at a modulus `n`. For example, `17 mod 5 = 2`.

## RSA with small numbers

Real keys use primes of around 1,024 bits or more each. With tiny primes we can do every step by hand. (This example is checked in Python below.)

### 1. Key generation

1. Pick two primes: `p = 61`, `q = 53`.
2. Compute the modulus: `n = p × q = 3233`. This is public.
3. Compute Euler's totient: `φ(n) = (p − 1)(q − 1) = 60 × 52 = 3120`. Keep it secret: for a two-prime modulus, knowing `n` and `φ(n)` lets an attacker recover `p` and `q`.
4. Choose a public exponent `e` with `gcd(e, φ) = 1`. Take `e = 17`. (Real systems almost always use `e = 65537`.)
5. Compute the private exponent `d`, the inverse of `e` modulo `φ`: the number with `e × d ≡ 1 (mod 3120)`. The extended Euclidean algorithm gives `d = 2753`. Check: `17 × 2753 = 46801 = 15 × 3120 + 1`.

```
Public key:  (n = 3233, e = 17)
Private key: (n = 3233, d = 2753)
```

### 2. Encryption

To encrypt a message, first encoded as an integer `0 ≤ m < n`, compute `c = m^e mod n`. Take `m = 65`:

```
c = 65^17 mod 3233 = 2790
```

### 3. Decryption

Compute `m = c^d mod n`:

```
m = 2790^2753 mod 3233 = 65
```

We get the original message back.

```python
p, q = 61, 53
n = p * q              # 3233
phi = (p - 1) * (q - 1)  # 3120
e = 17
d = pow(e, -1, phi)    # 2753

m = 65
c = pow(m, e, n)       # 2790
print(c, pow(c, d, n)) # 2790 65
```

Python's three-argument `pow` performs modular exponentiation without constructing the huge unreduced power. It is an arithmetic teaching tool, not a constant-time RSA implementation.

> [!note] Content gap: timings
> No reproducible benchmark supports the former multiplication and exponentiation timings or fixed CRT speed-up, so those figures are omitted.

 `pow(e, -1, phi)` (Python 3.8+) computes the modular inverse.

### Why it works

Because `e × d = 1 + k × φ(n)` for some integer `k`, decryption computes:

```
c^d = (m^e)^d = m^(ed) = m^(1 + k·φ(n))
    = m × (m^φ(n))^k
```

For `gcd(m,n)=1`, Euler's theorem gives `m^φ(n) ≡ 1 (mod n)`, proving the displayed reduction. That theorem does **not** give 1 for non-coprime `m`. RSA decryption still works for those representatives: prove `m^(ed) ≡ m` separately modulo each prime (zero is immediate; nonzero uses Fermat), then combine by the Chinese Remainder Theorem.

### Why it's secure

An attacker sees `n = 3233` and `e = 17`. Factoring `n` is sufficient to derive a valid private exponent. It is not proved that every way of inverting RSA must factor `n`. Here `3233 = 61 × 53` is trivial; properly generated 2,048-bit moduli resist known practical classical factoring methods. A 2,048-bit integer has 617 or 618 decimal digits.

## Textbook RSA is not secure

What we just did is **textbook RSA**, and you must never use it directly. It has serious problems:

- **It is deterministic.** Encrypting 65 always gives 2790. An attacker who suspects the message is "yes" or "no" encrypts both with your public key and compares.
- **It is malleable.** Multiply the ciphertext by `2^e mod n` and the plaintext doubles. In our example, decrypting `2790 × 2^17 mod 3233` gives `130`. An attacker can change your message in a predictable way without decrypting it.
- **Small messages leak.** With `e = 3` and a short message where `m^3 < n`, no wrap-around happens at all. The attacker takes an ordinary cube root of `c` and reads `m`.

The fix is **padding**: a randomised encoding applied to the message before exponentiation. The modern scheme is **OAEP** (Optimal Asymmetric Encryption Padding, in PKCS #1 v2). It mixes in fresh random bytes so the same message encrypts differently every time, and its structure makes tampered ciphertexts fail to decode.

> [!warning] Avoid PKCS #1 v1.5 encryption
> The older v1.5 encryption padding is vulnerable to **Bleichenbacher's attack** (1998). If a server reveals whether decrypted padding was valid, an attacker can decrypt ciphertexts with many queries. It kept coming back: the ROBOT study in 2017 found major vendors' TLS stacks still vulnerable. TLS 1.3 removed RSA key transport entirely.

Here is RSA done properly with Python's `cryptography` library:

```python
from cryptography.hazmat.primitives \
    .asymmetric import rsa, padding
from cryptography.hazmat.primitives \
    import hashes

priv = rsa.generate_private_key(
    public_exponent=65537,
    key_size=3072)
pub = priv.public_key()

oaep = padding.OAEP(
    mgf=padding.MGF1(hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None)

ct = pub.encrypt(b"session key", oaep)
print(len(ct))
print(priv.decrypt(ct, oaep))
```

This prints `384` (a 3,072-bit ciphertext is 384 bytes, however short the message) then `b'session key'`. Run it twice and the ciphertext differs each time, because OAEP is randomised. Implementations commonly use CRT acceleration and blinding as part of their defenses. Exact performance and side-channel behavior depend on the library and platform. OAEP encryption alone does not authenticate the sender: anyone with the public key can create a fresh valid ciphertext.

## Key sizes and performance

The classical RSA and ECC schemes below use larger key parameters than symmetric schemes for comparable estimated classical security. NIST SP 800-57 gives these rough equivalents:

| Security | Symmetric | RSA | ECC |
|---|---|---|---|
| 112-bit | 3-key TDEA (historical comparison, not new use) | 2048 | 224 |
| 128-bit | AES-128 | 3072 | 256 |
| 192-bit | AES-192 | 7680 | 384 |
| 256-bit | AES-256 | 15360 | 512+ |

NIST SP 800-57 Part 1 Rev. 5 maps RSA-2048 to about 112-bit classical strength and RSA-3072 to 128 bits, with at least 128 bits for applying protection from 2031. Algorithm suitability also depends on the protocol, policy and post-quantum transition; larger RSA is not quantum resistant.

RSA-OAEP with a 3,072-bit modulus and SHA-256 allows at most `384 − 2×32 − 2 = 318` message bytes per encryption. Bulk data is therefore usually handled with symmetric encryption. Instead, systems use **hybrid encryption**:

```
1. Generate random AES key K
2. Encrypt data with AES-GCM under K
3. Encrypt (wrap) K with recipient's
   public key
4. Send wrapped K + ciphertext
```

This is one hybrid design. HPKE instead combines a key-encapsulation mechanism, key derivation and AEAD. Key size and wrapping method vary; cloud envelope encryption may use a symmetric wrapping key rather than a public-key operation.

## Elliptic-curve cryptography: the intuition

**Elliptic-curve cryptography (ECC)** gets the same security with far smaller keys: a 256-bit ECC key is roughly as strong as a 3,072-bit RSA key. Smaller public-key encodings can reduce protocol overhead; performance and certificate size also depend on the scheme and protocol.

An elliptic curve is the set of points satisfying an equation like `y² = x³ + ax + b`. Over a finite field (integers mod a prime) the "curve" is just a scattered set of points. Here is a toy curve: `y² = x³ + 2x + 2 (mod 17)`.

The magic is a rule for **adding** two points to get a third point on the curve (geometrically: draw a line through them, find where it hits the curve again, reflect). Adding a point `G` to itself repeatedly gives:

```
1G = (5, 1)    2G = (6, 3)
3G = (10, 6)   4G = (3, 1)
5G = (9, 16)   ...
18G = (5, 16)  19G = point at infinity
```

This curve has 19 points **including the point at infinity**, and `G` generates the group.

- **Easy direction.** Given `k` and `G`, compute `kG`. With "double-and-add" this takes about log₂(k) steps, so even a 256-bit `k` needs only a few hundred point operations.
- **Hard direction.** Given `G` and `P = kG`, find `k`. This is the **elliptic-curve discrete logarithm problem (ECDLP)**. For a well-chosen subgroup of roughly 2^256 prime order, generic classical attacks take roughly 2^128 group operations. Curves with special weaknesses can be easier.

So in ECC, the private key is a random number `k` and the public key is the point `kG`. Unlike general factoring, no sub-exponential classical attack is known on appropriately selected prime-field curves, which is why the keys can be so short.

In practice you meet a few named curves:

- **X25519** uses the Montgomery Curve25519 form for key agreement. **Ed25519** is a signature scheme on a related Edwards curve; these names are not interchangeable algorithms. Both have standardized encodings and requirements.
- **NIST P-256** (secp256r1). Widely used in TLS, required in many government and FIPS settings.
- **secp256k1**. Used by Bitcoin and Ethereum.

ECC isn't usually used to "encrypt" directly the way RSA is. It is used for key exchange (ECDH, next lesson) and signatures (ECDSA, EdDSA). Encryption to an ECC public key is done with a hybrid scheme such as ECIES or HPKE (RFC 9180).

## Quantum computers

Shor's algorithm, run on a large enough quantum computer, would factor numbers and solve discrete logs efficiently. That would break RSA and ECC alike. No publicly demonstrated cryptographically relevant machine is established by the sources used here; recorded ciphertext can nevertheless create a future decryption risk ("harvest now, decrypt later"). NIST standardised **ML-KEM** (FIPS 203) in 2024 as a post-quantum replacement for key establishment, and Google reported deploying a hybrid with X25519 in Chrome 131. The applied cryptography module covers this.

## Pitfalls

- **Textbook RSA or PKCS #1 v1.5 encryption.** Use RSA-OAEP, or better, ECDH or HPKE via a library.
- **Short keys.** RSA-1024 offers only about 80-bit classical strength and is unsuitable for new protection under the cited NIST guidance. This is not evidence of a demonstrated general 1,024-bit factorization.
- **Bad randomness in key generation.** In 2012, researchers scanning the internet found tens of thousands of RSA keys sharing a prime factor, because embedded devices generated keys with little entropy at boot. Anyone could factor them with a GCD.
- **Implementing curve arithmetic yourself.** Real ECC implementations must resist side channels and perform the validation required by the specific scheme; X25519 processing rules differ from conventional Weierstrass point validation. These are notoriously hard to get right.
- **Using the same key pair for encryption and signing.** Keep separate keys for separate purposes.

## Key takeaways
- Public-key cryptography uses a public key to encrypt and a private key to decrypt, built on trapdoor problems.
- RSA's security rests on factoring: with `p = 61, q = 53, e = 17` we get `d = 2753`, and `65` encrypts to `2790`.
- Textbook RSA is deterministic and malleable. Always use OAEP padding, never PKCS #1 v1.5 for encryption.
- Asymmetric crypto is slow and limited in size, so real systems use hybrid encryption: wrap a random AES key.
- ECC gives the same security with much smaller keys (256-bit ECC ≈ 3072-bit RSA). Prefer Curve25519 and vetted libraries.

## Further reading
- [RSA (cryptosystem) — Wikipedia](https://en.wikipedia.org/wiki/RSA_(cryptosystem))
- [RFC 8017: PKCS #1 v2.2 (RSA, OAEP)](https://www.rfc-editor.org/rfc/rfc8017)
- [RSA — cryptography.io](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/)
- [Elliptic-curve cryptography — Wikipedia](https://en.wikipedia.org/wiki/Elliptic-curve_cryptography)
- [A (relatively easy to understand) primer on elliptic curve cryptography — Cloudflare](https://blog.cloudflare.com/a-relatively-easy-to-understand-primer-on-elliptic-curve-cryptography/)
- [NIST SP 800-57 Part 1 Rev. 5: Key management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [The ROBOT attack](https://robotattack.org/)
