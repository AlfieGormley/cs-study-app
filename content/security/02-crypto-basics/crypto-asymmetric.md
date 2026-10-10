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

RSA works in **modular arithmetic**, "clock arithmetic" where numbers wrap around at a fixed number called the modulus. A 12-hour clock is arithmetic modulo 12: 5 hours after 9 o'clock is 2 o'clock.

```formula
r = a mod n
17 mod 5 = 2
17 ≡ 2 (mod 5)
where
a: any whole number
n: the modulus: the positive whole number the arithmetic wraps around at
r: the remainder, always from 0 to n − 1
mod: "modulo": a mod n is the remainder left after dividing a by n
≡: "is congruent to": both sides leave the same remainder after dividing by the number named in (mod …)
In words: 17 divided by 5 is 3 remainder 2, so 17 mod 5 is 2, and 17 and 2 count as the same number when you only care about remainders after dividing by 5.
```

## RSA with small numbers

Real keys use primes of around 1,024 bits or more each. With tiny primes we can do every step by hand. (This example is checked in Python below.)

### 1. Key generation

1. Pick two secret primes, here 61 and 53.
2. Multiply them to get the **modulus**. This is public.
3. Compute **Euler's totient** of the modulus from the two primes. Keep it secret.
4. Choose a **public exponent** that shares no factor with the totient. Take 17.
5. Compute the **private exponent**: the number that, multiplied by the public exponent, leaves remainder 1 after dividing by the totient. The **extended Euclidean algorithm** finds it quickly.

```formula
n = p × q = 61 × 53 = 3233
φ(n) = (p − 1) × (q − 1)
φ(n) = 60 × 52 = 3120
gcd(e, φ(n)) = gcd(17, 3120) = 1
e × d ≡ 1 (mod φ(n))
17 × 2753 = 46801 = 15 × 3120 + 1
where
p, q: the two secret primes, here 61 and 53 (real ones are about 1,024 bits or more each)
n: the modulus, the product of the primes; part of the public key
φ: Euler's totient function: φ(n) counts the whole numbers from 1 to n that share no factor with n; for a product of two distinct primes it equals (p − 1) × (q − 1)
e: the public exponent, here 17
gcd: greatest common divisor: the largest whole number that divides both inputs; 1 means they share no factor
d: the private exponent, here 2753: the modular inverse of e
mod: "modulo": arithmetic on remainders after dividing by the number that follows
≡: "is congruent to": both sides leave the same remainder after dividing by φ(n)
In words: multiply two primes to get the public modulus, and pick d so that e × d is exactly one more than a multiple of φ(n); here 17 × 2753 is 15 × 3120 plus 1.
```

That gives the two keys:

```
Public key:  (n = 3233, e = 17)
Private key: (n = 3233, d = 2753)
```

Why keep φ(n) secret? Expanding the totient shows that it hands over the sum of the primes:

```formula
φ(n) = (p − 1) × (q − 1)
φ(n) = n − (p + q) + 1
p + q = n − φ(n) + 1
p + q = 3233 − 3120 + 1 = 114
where
φ(n): Euler's totient of the modulus, 3120 in the toy key
n: the public modulus, p × q = 3233
p, q: the secret primes
In words: anyone who knows n and φ(n) learns p + q, and two numbers whose sum is 114 and product is 3233 can only be 61 and 53 (solve the quadratic), so the factorisation falls out.
```

Why do real systems almost always use e = 65537? It is prime, so it is very likely to share no factor with φ(n). It equals 2^16 + 1, whose binary form `1 0000 0000 0000 0001` has only two 1 bits, so encryption needs just 16 squarings and one extra multiplication. And it is far larger than tiny exponents such as 3, which make some textbook-RSA mistakes (below) easier to exploit.

### 2. Encryption

To encrypt a message, first encode it as a whole number smaller than the modulus, then raise it to the public exponent and keep the remainder:

```formula
0 ≤ m < n
c = m^e mod n
c = 65^17 mod 3233 = 2790
where
m: the message, encoded as a whole number; here 65 (the ASCII code for the letter A)
n: the public modulus, 3233
e: the public exponent, 17
c: the ciphertext, a whole number from 0 to n − 1
m^e: m multiplied by itself e times
mod: "modulo": x mod n is the remainder left after dividing x by n
≤: is less than or equal to
<: is less than
In words: raise the message to the power e, divide by n and keep the remainder; that remainder is the ciphertext, and anyone with the public key can compute it.
```

### 3. Decryption

Raise the ciphertext to the private exponent instead:

```formula
m = c^d mod n
m = 2790^2753 mod 3233 = 65
where
c: the ciphertext, 2790
d: the private exponent, 2753, known only to the key owner
n: the modulus, 3233
m: the recovered message
c^d: c multiplied by itself d times (computed step by step with remainders, never as one giant number)
mod: "modulo": x mod n is the remainder left after dividing x by n
In words: only the holder of d can undo the encryption: raising 2790 to the power 2753 and keeping the remainder after dividing by 3233 gives back 65.
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

Decryption undoes encryption because of how d was chosen. **Euler's theorem** supplies the key step:

```formula
e × d = 1 + k × φ(n)
c^d ≡ (m^e)^d = m^(e × d) (mod n)
c^d ≡ m^(1 + k × φ(n)) (mod n)
c^d ≡ m × (m^φ(n))^k (mod n)
m^φ(n) ≡ 1 (mod n) if gcd(m, n) = 1
c^d ≡ m × 1^k = m (mod n)
where
e, d: the public and private exponents
k: some whole number; e × d ≡ 1 (mod φ(n)) means e × d is a multiple of φ(n) plus one (in the toy key 46801 = 1 + 15 × 3120, so k = 15)
φ: Euler's totient function; φ(n) = (p − 1) × (q − 1) for an RSA modulus
n: the modulus
m: the message, a whole number from 0 to n − 1
c: the ciphertext, m^e mod n
gcd: greatest common divisor; gcd(m, n) = 1 means m and n share no factor
mod: "modulo": arithmetic on remainders after dividing by n
≡: "is congruent to": both sides leave the same remainder after dividing by n
In words: e × d is one more than a multiple of φ(n), and Euler's theorem says any power of m that is a multiple of φ(n) is congruent to 1, so all that survives is m itself.
```

Euler's theorem (the line ending "if gcd(m, n) = 1") does **not** give 1 for messages that share a factor with n. RSA decryption still works for those representatives: prove `m^(ed) ≡ m` separately modulo each prime (zero is immediate; nonzero uses Fermat), then combine by the Chinese Remainder Theorem.

### Why it's secure

An attacker sees the public key, 3233 and 17. Factoring the modulus is sufficient to derive a valid private exponent:

```formula
n = 3233 = 61 × 53
φ(n) = 60 × 52 = 3120
d = e^(−1) mod φ(n)
d = 17^(−1) mod 3120 = 2753
where
n: the public modulus
φ: Euler's totient function, computable once the primes are known: φ(n) = (p − 1) × (q − 1)
e: the public exponent, 17
d: the private exponent
e^(−1) mod φ(n): the modular inverse of e: the number that multiplied by e leaves remainder 1 after dividing by φ(n)
mod: "modulo": arithmetic on remainders after dividing by φ(n)
In words: once the modulus is split into its primes, the attacker repeats the owner's key generation and gets the same private exponent.
```

It is not proved that every way of inverting RSA must factor `n`. Here `3233 = 61 × 53` is trivial; properly generated 2,048-bit moduli resist known practical classical factoring methods. A 2,048-bit integer has 617 decimal digits.

## Textbook RSA is not secure

What we just did is **textbook RSA**, and you must never use it directly. It has serious problems:

- **It is deterministic.** Encrypting 65 always gives 2790. An attacker who suspects the message is "yes" or "no" encrypts both with your public key and compares.
- **It is malleable.** Multiply the ciphertext by the encryption of 2 (which anyone can compute with the public key) and the plaintext doubles. In our example, 65 becomes 130. An attacker can change your message in a predictable way without decrypting it.
- **Small messages leak.** With a public exponent of 3 and a message whose cube is smaller than the modulus, no wrap-around happens at all. The attacker takes an ordinary cube root of the ciphertext and reads the message.

The malleability, worked through with the toy key:

```formula
c′ = c × 2^e mod n
c′^d ≡ m^(e × d) × 2^(e × d) (mod n)
c′^d ≡ m × 2 (mod n)
c′ = 2790 × 2^17 mod 3233 = 3017
3017^2753 mod 3233 = 130
where
c: the original ciphertext, 2790 (the encryption of 65)
c′: the attacker's altered ciphertext
e, d: the public and private exponents, 17 and 2753
n: the modulus, 3233
m: the original message, 65
mod: "modulo": arithmetic on remainders after dividing by n
≡: "is congruent to": both sides leave the same remainder after dividing by n
In words: multiplying ciphertexts multiplies the hidden plaintexts, so the attacker doubles the message without ever seeing it.
```

The small-message leak:

```formula
c = m^3 mod n = m^3  when m^3 < n
m = ∛(c)
c = 125  gives  m = ∛(125) = 5
where
m: the message as a whole number, for example a PIN
n: the modulus, about 2^2048 for a 2,048-bit key
c: the ciphertext
m^3: m multiplied by itself three times (the public exponent here is 3)
∛: the ordinary cube root: ∛(c) is the number whose cube is c
mod: "modulo": the remainder after dividing by n
<: is less than
In words: if the cube never reaches the modulus there is no remainder to hide anything, so the ciphertext is just the cube of the message and an ordinary cube root undoes it.
```

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

OAEP's structure also caps the message size:

```formula
L_max = L_n − 2 × L_h − 2
L_max = 384 − 2 × 32 − 2 = 318 bytes
where
L_max: the longest message RSA-OAEP can encrypt in one operation, in bytes
L_n: the modulus length in bytes: 3,072 bits / 8 = 384
L_h: the hash output length in bytes: 32 for SHA-256
2 × L_h: room for OAEP's random seed and the hash of its label, one hash length each
2: one leading 0x00 byte and one 0x01 byte that marks where the message starts
bytes: the unit of data, 8 bits each
In words: a 3,072-bit RSA-OAEP key with SHA-256 can carry at most 318 bytes, which is plenty for a 32-byte symmetric key but useless for a file.
```

So RSA-OAEP with a 3,072-bit modulus and SHA-256 allows at most 318 message bytes per encryption. Bulk data is therefore usually handled with symmetric encryption. Instead, systems use **hybrid encryption**:

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

An elliptic curve is the set of points satisfying an equation of a particular shape. Over a **finite field** (whole numbers modulo a prime) the "curve" is just a scattered set of points. Here is the general shape and a toy curve:

```formula
y^2 = x^3 + a × x + b
y^2 ≡ x^3 + 2 × x + 2 (mod 17)
1^2 ≡ 5^3 + 2 × 5 + 2 = 137 (mod 17)
137 = 8 × 17 + 1 ≡ 1 (mod 17)
where
x, y: the coordinates of a point; on the toy curve, whole numbers from 0 to 16
a, b: constants that choose the curve; here a = 2 and b = 2
mod: "modulo": all arithmetic is on remainders after dividing by the prime 17
≡: "is congruent to": both sides leave the same remainder after dividing by 17
In words: a point is on the curve when its coordinates satisfy the equation; checking (5, 1) gives 1 on the left and 137, which leaves remainder 1, on the right, so it is on the curve.
```

The magic is a rule for **adding** two points to get a third point on the curve (geometrically: draw a line through them, find where it hits the curve again, reflect). Adding a starting point to itself repeatedly is called **scalar multiplication**:

```formula
k × G = G + G + … + G
1 × G = (5, 1)
2 × G = (6, 3)
3 × G = (10, 6)
4 × G = (3, 1)
5 × G = (9, 16)
18 × G = (5, 16)
19 × G = O
where
G: the generator point, here (5, 1)
k: a whole number, the scalar: how many copies of G are added
+: point addition, the curve's chord-and-tangent rule; not ordinary addition of coordinates
×: scalar multiplication: k × G means G added to itself k times (the sum has k terms)
…: and so on, up to k copies of G
O: the point at infinity: the "zero" of point addition, so adding O to any point leaves it unchanged
In words: repeatedly adding G walks through the curve's points one by one until, after 19 steps, it reaches the point at infinity and the cycle starts again.
```

This curve has 19 points **including the point at infinity**, and G generates the group: its multiples visit every point.

- **Easy direction.** Given the scalar and G, compute the multiple. With "double-and-add" this takes only a few hundred point operations even for a 256-bit scalar.
- **Hard direction.** Given G and the result, find the scalar. This is the **elliptic-curve discrete logarithm problem (ECDLP)**. Curves with special weaknesses can be easier.

In numbers:

```formula
P = k × G
D ≈ log_2(k) ≤ 256
W ≈ √(N) ≈ √(2^256) = 2^128
where
P: the result point (in ECC, the public key)
k: the scalar (in ECC, the private key), a random number up to about 2^256
G: the generator point, fixed by the curve standard
D: the number of point doublings in double-and-add (plus at most as many point additions)
log_2: the base-2 logarithm: log_2(k) is about the number of bits in k
N: the order of G: how many distinct points its multiples visit, about 2^256 for a well-chosen curve
W: the work for the best generic classical attack (Pollard's rho) to recover k from P, in group operations; the exact expected count carries a small constant factor (roughly 0.9 to 1.3 × √(N), depending on the variant), which doesn't change the order of magnitude
√: square root
≈: approximately equal to
≤: is at most
In words: computing P from k takes a few hundred point operations, while recovering k from P takes about 2^128, which is why a 256-bit curve gives roughly 128-bit security.
```

So in ECC, the private key is a random number k and the public key is the point P = k × G. Unlike general factoring, no sub-exponential classical attack is known on appropriately selected prime-field curves, which is why the keys can be so short.

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
- RSA's security rests on factoring: with primes 61 and 53 and public exponent 17 we get private exponent 2753, and 65 encrypts to 2790.
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
