---
id: pki-mistakes-pq
title: Common crypto mistakes and post-quantum cryptography
level: advanced
minutes: 15
summary: Common mistakes that cause cryptographic failures (nonce reuse, unauthenticated modes, bad randomness, timing leaks, hand-rolled constructions) and the coming migration to post-quantum algorithms: what Shor and Grover break, the NIST standards, sizes, hybrids and how to plan the move.
---

Broken ciphers are rare. Broken *uses* of good ciphers are everywhere. Common causes of production cryptographic failure include a repeated nonce, a missing message authentication code, a predictable random number, a comparison that leaks time.

The second half of this lesson covers the one change in the field that does involve breaking the algorithms themselves: quantum computers, and the migration already under way to replace RSA and elliptic curves.

## Mistake 1: reusing a nonce

Stream-like modes (CTR, GCM, ChaCha20) turn the key and nonce into a **keystream** and XOR it with the plaintext. Use the same key and nonce twice and both messages are XORed with the same keystream:

```formula
c_1 = p_1 ⊕ KS
c_2 = p_2 ⊕ KS
c_1 ⊕ c_2 = p_1 ⊕ p_2
p_2 = c_1 ⊕ c_2 ⊕ p_1
where
c_1: the first ciphertext, seen by the attacker
c_2: the second ciphertext, encrypted under the same key and nonce
p_1: the first plaintext
p_2: the second plaintext
KS: the keystream: the pseudorandom bytes the cipher generates from the key and nonce; the same key and nonce always give the same keystream
⊕: XOR (exclusive OR), bit by bit: 1 where the bits differ; anything XORed with itself gives 0, so the keystream cancels
In words: XORing the two ciphertexts removes the keystream and leaves the two plaintexts XORed together; knowing either plaintext then reveals the other, with no key needed.
```

Know or guess one plaintext and you get the other:

```python
import os
from cryptography.hazmat.primitives \
    .ciphers.aead import AESGCM

g = AESGCM(AESGCM.generate_key(128))
n = os.urandom(12)  # BUG: used twice
p1 = b"attack at dawn!"
p2 = b"retreat at ten!"
c1 = g.encrypt(n, p1, None)
c2 = g.encrypt(n, p2, None)

def xor(a, b):
    pairs = zip(a, b)
    return bytes(x ^ y for x, y in pairs)

# attacker knows (or guesses) p1
print(xor(xor(c1, c2), p1))
```

This prints `b'retreat at ten!'`. With GCM it is worse still: nonce reuse creates equations in the authentication subkey and can enable tag forgery. The exact recovery and forgery depend on message structure and available observations; this does not reveal the AES key or automatically provide the mask for every unused nonce.

Real cases: the 2017 **KRACK** attacks tricked WPA2 devices into reinstalling a key and resetting its nonce counter. In 2016 researchers scanning the internet found 184 HTTPS servers repeating GCM nonces, some of them belonging to large organisations, and tens of thousands more using random nonces in ways that risked collisions.

Fixes: use a counter you can guarantee never repeats, random 96-bit nonces only well below 2^32 messages per key, or a nonce-misuse-resistant mode such as **AES-GCM-SIV**, where a repeated nonce leaks only whether two messages are identical.

## Mistake 2: encryption without authentication

ECB mode encrypts each block independently (16 bytes for AES, 8 for 3DES), so equal blocks give equal ciphertext. The famous "ECB penguin" image stays recognisable when encrypted. For password verification, deterministic encryption would reveal repeated values; store salted password hashes instead.

> [!note] Content gap
> Exact Adobe breach counts, its cipher attribution, generic GPU cracking rates and attack-runtime estimates are omitted where this review did not obtain adequate primary evidence. The examples below describe the cryptographic mechanisms without those unsupported specifics.

CBC hides patterns, but without a message authentication code an attacker can still flip bits, and if the server reveals whether padding was valid, the **padding oracle** attack (Vaudenay, 2002) decrypts whole messages one byte at a time. It broke ASP.NET in 2010, and the same family produced POODLE and Lucky 13 in TLS.

Fix: use an **AEAD** (AES-GCM, ChaCha20-Poly1305). If you must combine a cipher and a message authentication code yourself, encrypt-then-MAC, and verify the tag before decrypting or releasing plaintext.

## Mistake 3: weak randomness

Keys, nonces and tokens need a **cryptographically secure** RNG.

- Python's `random` module is a Mersenne Twister. After obtaining a suitable consecutive sequence of 624 full 32-bit MT outputs, an attacker can reconstruct state and predict later generator outputs. Tokens produced through rejection sampling or truncated outputs require a different observation/recovery analysis. Use `secrets` or `os.urandom`.
- In 2008 it emerged that a 2006 Debian patch had removed nearly all entropy from OpenSSL's RNG, leaving the process ID as the only variable input. Affected OpenSSL-generated keys became predictable; the key space depended on process IDs, architecture and generation details. It was not one universal list of 32,768 keys across every key type and platform.
- In 2012, researchers computing GCDs across millions of public RSA keys could factor the keys of about 0.5% of the HTTPS hosts they scanned. Headless devices had generated keys at first boot, before collecting entropy, so different devices shared primes.

Why does a shared prime matter so much? Factoring one 2,048-bit modulus is infeasible, but finding a common factor of two is fast, using Euclid's algorithm:

```formula
n_1 = p × q_1
n_2 = p × q_2
gcd(n_1, n_2) = p
where
n_1: the first device's public RSA modulus
n_2: the second device's public RSA modulus
p: the prime both devices happened to generate
q_1: the first device's other prime
q_2: the second device's other prime
gcd: greatest common divisor: the largest number that divides both exactly; Euclid's algorithm finds it in a fraction of a second even for 2,048-bit numbers
In words: two public keys that share a prime give that prime away, and dividing each modulus by it reveals the other prime, so both private keys follow.
```

With toy numbers, 3233 = 61 × 53 and 3599 = 61 × 59, so the GCD of 3233 and 3599 is 61, and both moduli factor at once. With truly random 1,024-bit primes, two devices picking the same one is practically impossible; it happened only because the devices started from nearly the same RNG state.

## Mistake 4: leaking secrets through time

Ordinary equality has no constant-time security guarantee. An early-exit comparison can reveal prefix information in suitable timing conditions, but Python byte equality is not a guaranteed one-byte-at-a-time oracle. Use the dedicated comparison API and validate expected types and lengths.

```python
import hmac

def check(tag, expected):
    # avoids content-based short circuit
    return hmac.compare_digest(
        tag, expected)
```

The same principle applies inside primitives: table-lookup AES and naive RSA leak keys through cache timing, which is why libraries use constant-time code. Even post-quantum code is not immune: the **KyberSlash** timing bugs (a division that took secret-dependent time), disclosed around the start of 2024, affected several Kyber implementations.

## Mistake 5: hand-rolled constructions

- **Hash as MAC.** Hashing the key followed by the message with SHA-256 looks like a message authentication code but allows **length extension**: from the tag of one message, an attacker can compute a valid tag for that message with extra data appended, without the key (formulas below). Flickr's API signatures fell to this in 2009. Use HMAC.
- **Fast hashes for passwords.** Fast hashes built for general use make offline guessing cheap relative to purpose-built password hashing. Use appropriately configured Argon2id or scrypt; bcrypt is a legacy option with input-length constraints.
- **Custom protocols.** Every handshake in the earlier lessons has subtle bindings (transcripts, domain separation, key separation). A homemade protocol almost certainly misses one.
- **Letting attackers choose algorithms.** Trusting an unvalidated JWT algorithm field can bypass verification. Enforce the expected algorithm and key type. TLS negotiation is normal; downgrade vulnerabilities arise when version/suite policy and transcript binding fail.

Length extension works because SHA-256 (like MD5 and SHA-1) is a Merkle–Damgård hash: its output is its entire internal state after the last block. HMAC fixes this by hashing twice with two derived keys:

```formula
t = H(K ‖ m)
H(K ‖ m ‖ P_m ‖ x) = H_t(x)
HMAC(K, m) = H(K_o ‖ H(K_i ‖ m))
K_o = K ⊕ opad
K_i = K ⊕ ipad
where
t: the tag of the naive hash-as-MAC construction
H: the hash function, here SHA-256
K: the secret key (for HMAC, first padded with zeros to SHA-256's 64-byte block size)
m: the message
P_m: the padding SHA-256 appends after K ‖ m (a 1 bit, zeros and the total length); the attacker can compute it if they know or guess the key's length
x: the attacker's extra data, such as "&amount=1000000"
H_t: SHA-256 restarted from the internal state t instead of its standard starting values, then run over x (with final padding computed for the full, longer length)
HMAC: hash-based message authentication code
K_o: the outer key
K_i: the inner key
opad: the outer pad, the byte 0x5c repeated 64 times
ipad: the inner pad, the byte 0x36 repeated 64 times
⊕: XOR (exclusive OR), byte by byte
‖: concatenation: one value's bytes followed by the next
In words: a plain hash's tag is a saved game the attacker can resume, so they can extend the message and get a valid tag; in HMAC the inner hash's result is hidden inside a second keyed hash, so there is nothing useful to resume.
```

The second line is the attack: the attacker never learns K, but the hash of key, message, padding and extra data equals what they compute by resuming from t.

> [!tip] Choose libraries that make mistakes hard
> High-level APIs can reduce misuse, but responsibilities differ. libsodium's `crypto_secretbox` and `crypto_box` require caller-supplied unique nonces; `secretstream` manages stream nonce/state. Tink AEAD APIs and Fernet manage their own encryption randomness. Fernet is authenticated encryption but has no caller-provided AAD interface. Reach for low-level primitives only when you must, and get the design reviewed.

## Post-quantum: what breaks

A large, fault-tolerant quantum computer, which nobody has yet built, would change the picture for public-key cryptography:

| Algorithm | Quantum attack | Effect |
|---|---|---|
| RSA, DH, ECDH | Shor | Broken |
| ECDSA, Ed25519 | Shor | Broken |
| AES-128 | Grover | ~64-bit, in theory |
| AES-256 | Grover key search | Idealised ~2^128 oracle queries; practical costs are higher |
| SHA-256 | Quantum search/collision algorithms | Preimage and collision security differ; do not assign one universal bit strength |

**Shor's algorithm** solves factoring and discrete logarithms in polynomial time, so the classical factoring/discrete-log public-key schemes discussed earlier are vulnerable. The post-quantum schemes below rely on different assumptions. **Grover's algorithm** only gives a square-root speed-up on brute-force search, and it parallelises badly, so symmetric crypto survives with large enough keys. Guidance such as the NSA's CNSA 2.0 suite calls for AES-256.

```formula
W ≈ √(N) = √(2^k) = 2^{k/2}
W_128 ≈ 2^{128/2} = 2^{64}
W_256 ≈ 2^{256/2} = 2^{128}
where
W: the number of Grover steps (idealised quantum evaluations of the cipher) to find a key
N: the number of possible keys, 2^k
k: the key length in bits
√: square root
≈: approximately equal to (constant factors are ignored)
W_128: the idealised Grover work for AES-128
W_256: the idealised Grover work for AES-256
In words: Grover halves the key length in bits, so AES-128 drops to about 64-bit strength in theory and AES-256 keeps about 128-bit strength, which remains far out of reach.
```

These are idealised counts. Grover's steps must run one after another on a fault-tolerant machine, and splitting the search across many machines saves far less than it does classically, so real costs are much higher.

### When to care: harvest now, decrypt later

Nobody knows when, or whether, a cryptographically relevant quantum computer will arrive. A reliable arrival date cannot be supplied here; planning uses explicit scenarios rather than a forecast. The decision rule, often called **Mosca's inequality**, is:

```formula
x + y > z
where
x: how many years the data must stay secret (its shelf life)
y: how many years it will take to migrate your systems to post-quantum cryptography
z: how many years until a cryptographically relevant quantum computer exists; an estimate, since nobody knows
>: is greater than
In words: if the data's secrecy period plus your migration time is longer than the time until quantum computers arrive, data encrypted near the end of your migration will still need to be secret when it can be broken, so you are already late.
```

For example, with a hypothetical planning scenario of records that must stay secret for 10 years, a 5-year migration and a 12-year quantum estimate:

```formula
x + y = 10 + 5 = 15
15 > 12 = z
where
x: the secrecy period, 10 years
y: the migration time, 5 years
z: the assumed time until a quantum computer, 12 years
>: is greater than
In words: 15 years of exposure against 12 years of safety means traffic recorded in the last few years could still be sensitive when it becomes decryptable.
```

The inequality is a planning model, not a forecast: all three numbers are estimates, and z is the most uncertain.

Encrypted traffic recorded today can be decrypted the day such a machine exists, so **key exchange** must move first. **Signatures** also need early migration planning: long-lived devices, software-update trust anchors and archived signatures can outlast a transition. Recorded-traffic confidentiality and future authentication are distinct risks; one universal priority order is inappropriate.

## The new standards

NIST ran a public competition from 2016 and published the first standards in August 2024:

- **ML-KEM** (FIPS 203, from Kyber): a lattice-based key encapsulation mechanism for key exchange.
- **ML-DSA** (FIPS 204, from Dilithium): lattice-based signatures, the default choice for most uses.
- **SLH-DSA** (FIPS 205, from SPHINCS+): hash-based signatures, relying only on hash functions. Very conservative, but slow and large.

A further lattice signature (FN-DSA, from Falcon) is being standardised, and in 2025 NIST picked **HQC**, a code-based KEM, as a backup to ML-KEM in case lattices fall. The competition showed why hedging matters: two leading candidates, the signature finalist Rainbow and the KEM SIKE, were broken in 2022, the SIKEp434 parameter set in about an hour on a single core in the original attack authors' reported implementation.

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
2. **Prioritise by secrecy lifetime.** Long-lived secrets (health records, state secrets, root CA keys) first.
3. **Get crypto-agile.** Hard-coded algorithms, fixed field sizes for keys and signatures, and HSMs without PQ firmware all block migration. Design so algorithms can be swapped by configuration.
4. **Evaluate supported hybrid key exchange** through compatibility testing, library/service upgrades and deployment policy; middleboxes, protocol negotiation and operational constraints may also require changes.
5. **Plan signatures** to follow standards and timelines: the November 2024 draft NIST IR 8547 proposed security-strength-dependent transition dates, including 2030 deprecation and 2035 disallowance for listed classical uses. Treat this as a dated draft proposal, not a universal law or a final rule for every application.

## Key takeaways
- Common cryptographic misuse includes repeated nonces, unauthenticated modes, weak RNGs, timing leaks and hand-rolled constructions.
- Nonce reuse in CTR/GCM reveals plaintext XORs, and in GCM enables forgeries; use counters, bounded random nonces or GCM-SIV.
- Use AEAD, a CSPRNG (`secrets`), constant-time comparison, HMAC and real password hashes, ideally through misuse-resistant libraries.
- Shor's algorithm would break RSA, DH and elliptic curves; Grover only weakens symmetric keys, so AES-256 is fine.
- Harvest-now-decrypt-later makes post-quantum key exchange urgent; hybrid X25519MLKEM768 is already widely deployed.
- ML-KEM, ML-DSA and SLH-DSA are standardised; their larger sizes, especially for signatures in certificate chains, are the main engineering challenge.

## Further reading
- [NIST releases first three finalised post-quantum encryption standards — NIST](https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards)
- [FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard](https://csrc.nist.gov/pubs/fips/203/final)
- [The state of the post-quantum Internet — Cloudflare blog](https://blog.cloudflare.com/pq-2024/)
- [Nonce-disrespecting adversaries: practical forgery attacks on GCM in TLS](https://eprint.iacr.org/2016/475)
- [Mining your Ps and Qs: weak keys in network devices](https://factorable.net/)
- [Cryptographic Storage Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
