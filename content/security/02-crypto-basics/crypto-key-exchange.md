---
id: crypto-key-exchange
title: Key exchange and Diffie–Hellman
level: advanced
minutes: 14
summary: How two strangers agree a secret over a public channel, Diffie–Hellman worked with small numbers, the man-in-the-middle attack and why key exchange must be authenticated, small-subgroup and Logjam pitfalls, ECDH with X25519, and forward secrecy.
---

Alice and Bob have never met. Every byte they send crosses a network Eve can read. Can they end up with a shared secret key that Eve doesn't know?

It sounds impossible: anything they say, Eve hears. In 1976 Whitfield Diffie and Martin Hellman published a way to do it anyway. **Diffie–Hellman (DH) key exchange** and its elliptic-curve variants are important components of protocols including TLS, SSH, the Signal Protocol, WireGuard and IPsec. Protocol modes vary; some use pre-shared keys or hybrid post-quantum exchange.

## The paint analogy

```
Alice           public          Bob
secret: red     yellow       secret: blue

red+yellow  ---orange--->
            <---green---  blue+yellow

orange+blue = brown = green+red
```

1. They publicly agree a common colour, yellow.
2. Each mixes in a secret colour and sends the mixture.
3. Each adds their own secret to the other's mixture. Both end up with the same brown.

Eve sees yellow, orange and green. The analogy imagines unmixing to be hard; it is not a proof about paint or cryptography. In DH, mixing is modular exponentiation and unmixing is the **discrete logarithm problem**.

## Diffie–Hellman with small numbers

The public parameters are a prime and a **generator**. Each side also picks a secret exponent, sends one public value, and combines the other side's value with its own secret:

```formula
A = g^a mod p
B = g^b mod p
s = B^a mod p = A^b mod p
where
p: the public prime modulus; here 23 (real finite-field groups use 2,048 bits or more)
g: the public generator, here 5
a: Alice's secret exponent, here 6; never sent
b: Bob's secret exponent, here 15; never sent
A: Alice's public value, sent in the clear
B: Bob's public value, sent in the clear
s: the shared secret both of them compute
g^a: g multiplied by itself a times
mod: "modulo": x mod p is the remainder left after dividing x by p
In words: each side raises the generator to its secret and publishes the result, then raises the other side's result to its own secret; both end up with the same number.
```

1. Alice picks a = 6 and sends A.
2. Bob picks b = 15 and sends B.
3. Alice computes s from B and a. Bob computes s from A and b.

Step by step, working with remainders so the numbers stay small:

```formula
5^2 = 25 ≡ 2 (mod 23)
5^4 ≡ 2^2 = 4 (mod 23)
5^6 = 5^4 × 5^2 ≡ 4 × 2 = 8 (mod 23)
A = 8
B = 5^15 mod 23 = 19
s_Alice = 19^6 mod 23 = 2
s_Bob = 8^15 mod 23 = 2
where
A, B: the public values Alice and Bob send
s_Alice, s_Bob: the secret each of them computes
mod: "modulo": x mod 23 is the remainder left after dividing x by 23
≡: "is congruent to": both sides leave the same remainder after dividing by 23
In words: 5^6 is 15625, but by reducing after every multiplication Alice only ever handles small numbers; both sides finish with 2.
```

Both get s = 2. Checked in Python:

```python
p, g = 23, 5          # public
a, b = 6, 15          # private

A = pow(g, a, p)      # Alice sends 8
B = pow(g, b, p)      # Bob sends 19

print(pow(B, a, p))   # Alice: 2
print(pow(A, b, p))   # Bob:   2
```

### Why they agree

Exponents multiply, and the order doesn't matter:

```formula
B^a = (g^b)^a = g^(b × a)
A^b = (g^a)^b = g^(a × b)
g^(a × b) = 5^(6 × 15) = 5^90
5^22 ≡ 1 (mod 23)
90 = 4 × 22 + 2
5^90 ≡ 1^4 × 5^2 = 25 ≡ 2 (mod 23)
where
g: the generator, 5
a, b: Alice's and Bob's secret exponents, 6 and 15
A, B: the public values g^a and g^b (mod 23)
mod: "modulo": arithmetic on remainders after dividing by 23
≡: "is congruent to": both sides leave the same remainder after dividing by 23
In words: both sides compute g raised to a × b, just in a different order; and because 5^22 leaves remainder 1, only the remainder of the exponent after dividing by 22 matters.
```

The fact that 5^22 leaves remainder 1 is an instance of **Fermat's little theorem**:

```formula
x^(p − 1) ≡ 1 (mod p)
5^(23 − 1) = 5^22 ≡ 1 (mod 23)
where
p: a prime
x: any whole number not divisible by p
mod: "modulo": arithmetic on remainders after dividing by p
≡: "is congruent to": both sides leave the same remainder after dividing by p
In words: modulo a prime p, raising any number not divisible by p to the power p − 1 gives remainder 1, so exponents can be reduced modulo p − 1.
```

### Why Eve can't

Eve sees everything public: 23, 5, 8 and 19. Recovering either secret exponent is one way to compute the shared secret, and that is the **discrete logarithm problem**:

```formula
g^a ≡ A (mod p)
5^a ≡ 8 (mod 23)
5^6 = 15625 = 679 × 23 + 8
where
g: the public generator, 5
p: the public prime, 23
A: Alice's public value, 8
a: the secret exponent Eve wants: the discrete logarithm of A to base g
mod: "modulo": arithmetic on remainders after dividing by p
≡: "is congruent to": both sides leave the same remainder after dividing by p
In words: given g, p and A, find the exponent a; with only 22 possible exponents Eve tries them all and finds 6, but for a well-chosen 2,048-bit group no known method is practical.
```

The **computational Diffie–Hellman assumption** directly assumes that obtaining the shared secret from the public values is infeasible in the chosen group; it does not assert a general equivalence to solving discrete logs. A prime's bit length alone is insufficient: subgroup order, exponent randomness and known attacks matter. Vetted 2,048-bit finite-field groups target roughly 112-bit classical strength, not 2^2048 work.

### What "generator" means

The **order** of a number is how many steps its powers take to get back to 1:

```formula
g^k ≡ 1 (mod p)
5^22 ≡ 1 (mod 23), 5^11 ≡ 22 (mod 23)
2^11 ≡ 1 (mod 23)
where
g: a base, such as 5 or 2
k: the order of g: the smallest positive exponent for which the first line holds
p: the prime modulus, 23
mod: "modulo": arithmetic on remainders after dividing by p
≡: "is congruent to": both sides leave the same remainder after dividing by p
In words: 5 needs all 22 steps to return to 1, but 2 is back at 1 after only 11, so its powers can only ever reach half the values.
```

Powers of 5 mod 23 visit every number from 1 to 22 before repeating, so 5 has order 22: it generates the whole group. Not every base does. Powers of 2 mod 23 cycle through only 11 values, so a secret derived from base 2 has half as many possible values. Real parameters are chosen so the generator's order is a large prime.

## Man in the middle: why DH must be authenticated

Plain DH protects against a **passive** eavesdropper. It does nothing against an **active** attacker who can change messages. Mallory sits in the middle and runs a separate exchange with each side, using her own secret exponent, 3:

```
Alice --A=8-->  Mallory  --M=10--> Bob
Alice <-M=10--  Mallory  <-B=19--  Bob

M = 5^3 mod 23 = 10

Alice's key: 10^6 mod 23 = 6
  (Mallory: 8^3 mod 23 = 6)
Bob's key:   10^15 mod 23 = 5
  (Mallory: 19^3 mod 23 = 5)
```

The arithmetic, with the same public prime and generator:

```formula
M = g^m mod p = 5^3 mod 23 = 10
K_A = M^a mod p = 10^6 mod 23 = 6
K_A = A^m mod p = 8^3 mod 23 = 6
K_B = M^b mod p = 10^15 mod 23 = 5
K_B = B^m mod p = 19^3 mod 23 = 5
where
g, p: the public generator 5 and prime 23
m: Mallory's secret exponent, 3
M: Mallory's public value, which she sends to both sides
a, b: Alice's and Bob's secret exponents, 6 and 15
A, B: Alice's and Bob's public values, 8 and 19, which Mallory intercepts
K_A: the key Alice ends up sharing, which Mallory computes too
K_B: the key Bob ends up sharing, which Mallory computes too
mod: "modulo": x mod p is the remainder left after dividing x by p
In words: each victim does a normal exchange with Mallory, and Mallory can compute both resulting keys because she holds m and sees A and B.
```

Alice thinks she shares key 6 with Bob; she actually shares it with Mallory. Bob shares key 5 with Mallory. Mallory decrypts each message, reads or alters it, and re-encrypts it for the other side. Neither notices.

DH tells you "I share a key with whoever sent this number". It doesn't tell you *who* sent it. Every real protocol therefore **authenticates** the exchange:

- **Certificate-authenticated TLS 1.3**: `CertificateVerify` signs a context string and the transcript hash up to that point. The client verifies the signature, certificate chain and intended server identity. PSK modes authenticate differently.
- **SSH**: the server signs the exchange with its host key; a correctly configured client verifies a trusted host key, often stored in `known_hosts`, and rejects unexpected changes. Accepting an unverified first key can pin an attacker.
- **Signal Protocol**: long-term identity keys are mixed into the exchange, and users can compare "safety numbers" out of band.
- **WireGuard**: each peer is configured with the other's static public key in advance.

> [!warning] Unauthenticated DH is a classic home-made protocol bug
> "We do Diffie–Hellman, so it's secure" is not true. Without authentication, a MITM is trivial. This is one of many reasons to use TLS or a Noise-based library rather than designing a protocol.

## Pitfalls in the parameters

### Small-subgroup and invalid values

What if Mallory replaces Bob's value with 22, one less than the prime, which behaves like −1? Then:

```formula
B′ = p − 1 = 22 ≡ −1 (mod 23)
s = B′^a mod p
s = 1 if a mod 2 = 0
s = 22 if a mod 2 = 1
where
p: the public prime, 23
B′: the value Mallory substitutes for Bob's
a: Alice's secret exponent
s: the "shared secret" Alice computes
mod: "modulo": x mod n is the remainder after dividing x by n (n is 23 or 2 here)
≡: "is congruent to": both sides leave the same remainder after dividing by 23
In words: −1 raised to any power is 1 or −1, depending only on whether the exponent is even or odd, so Alice's secret collapses to one of two values.
```

Alice's "secret" is now one of only two values, both known to Mallory. Similar tricks with values of small order can leak bits of a long-term private key.

Defences: use a **safe prime**, use a generator of the large prime-order subgroup, and **validate** received values:

```formula
p = 2 × q + 1
23 = 2 × 11 + 1
2 ≤ B ≤ p − 2
B^q ≡ 1 (mod p)
where
p: the public prime modulus
q: a second prime; p is a safe prime when q is also prime, which leaves a large subgroup of prime order q
B: a public value received from the other side
≤: is less than or equal to
mod: "modulo": arithmetic on remainders after dividing by p
≡: "is congruent to": both sides leave the same remainder after dividing by p
In words: choose p so that p − 1 is twice a prime, reject the trivial values 0, 1 and p − 1, and check that the received value lies in the order-q subgroup.
```

For p = 23, the value 22 fails the range check, and 5 fails the subgroup check (5^11 leaves remainder 22, not 1). Use the checks required by the protocol and library; not every low-level API enforces all of them.

### Weak or shared groups: Logjam

In 2015 the **Logjam** researchers showed two problems:

1. Many TLS servers still accepted 512-bit "export-grade" DH, a 1990s US export restriction. An active attacker could downgrade connections to it and break them in minutes.
2. Most servers shared a handful of standard 1,024-bit primes. Because most of the work in breaking discrete logs depends only on the prime, a nation-state could plausibly precompute once and then break huge numbers of connections.

The response: at least 2,048-bit groups from vetted lists such as RFC 7919's `ffdhe2048` and up, or, far more commonly now, elliptic curves.

## ECDH and X25519

**Elliptic-curve Diffie–Hellman (ECDH)** is the same protocol with points instead of numbers: exponentiation becomes scalar multiplication. On the toy curve from the last lesson:

```formula
A = a × G, B = b × G
s = a × B = b × A = (a × b) × G
A = 3 × G = (10, 6)
B = 7 × G = (0, 6)
s = 21 × G = 2 × G = (6, 3)
where
G: the public generator point, (5, 1) on the toy curve y^2 ≡ x^3 + 2 × x + 2 (mod 17)
a, b: Alice's and Bob's secret scalars, 3 and 7
A, B: the public points they send
s: the shared point both compute
×: scalar multiplication: k × G means G added to itself k times with the curve's point-addition rule
In words: each side multiplies the other's public point by its own secret, and both arrive at (a × b) × G; since the toy group has 19 elements, 21 × G wraps round to 2 × G.
```


**X25519** (RFC 7748) uses Curve25519 with 32-byte public encodings and roughly 128-bit classical strength. Its arithmetic supports constant-time implementations and specifies handling of non-canonical encodings, but safe implementations still need side-channel care. Some inputs yield an all-zero shared secret. TLS 1.3 requires aborting in that case, and Python cryptography rejects a null shared key. Accepting bytes as an encoding does not guarantee a usable authenticated exchange.

```python
from cryptography.hazmat.primitives \
    .asymmetric import x25519
from cryptography.hazmat.primitives \
    .kdf.hkdf import HKDF
from cryptography.hazmat.primitives \
    import hashes

alice = x25519.X25519PrivateKey.generate()
bob = x25519.X25519PrivateKey.generate()

# swap public keys (32 bytes each)
s1 = alice.exchange(bob.public_key())
s2 = bob.exchange(alice.public_key())
print(s1 == s2, len(s1))   # True 32

key = HKDF(algorithm=hashes.SHA256(),
           length=32, salt=None,
           info=b"demo v1 enc key"
          ).derive(s1)
```

This snippet demonstrates agreement and derivation only: it does not authenticate either peer and is not a deployable handshake.

Note the last step. The raw shared secret is not a uniformly random key, so you should never use it directly as an AES key. Pass it through a **key derivation function** such as HKDF (lesson 6), ideally with the handshake transcript mixed in, to derive separate keys for each direction and purpose. TLS 1.3's key schedule does exactly this.

## Ephemeral keys and forward secrecy

Compare two historical TLS handshake families (this table omits PSK and resumption modes):

| Approach | If server key leaks later |
|---|---|
| RSA key transport | All recorded sessions exposed |
| Ephemeral (EC)DHE | Past sessions stay safe |

With **RSA key transport** (TLS 1.2 and earlier), the client encrypts a premaster secret to the server's long-term RSA key; the protocol derives traffic keys from it. A passive recording containing the required handshake and traffic can then be decrypted if that RSA private key is later compromised.

With **ephemeral** Diffie–Hellman (DHE or ECDHE), both sides generate a fresh key pair for every connection and delete it afterwards. The long-term key only *signs* the exchange. Stealing it later lets an attacker impersonate the server in future, but past session keys are gone. This property is **forward secrecy** (or perfect forward secrecy). TLS 1.3 made ephemeral key exchange mandatory for certificate-based handshakes and removed RSA key transport.

The Signal Protocol's Double Ratchet evolves message keys and periodically incorporates fresh DH material. Erasure protects older keys; recovery after compromise requires fresh secret contributions no longer visible to the attacker. Continuous endpoint access or retained keys can prevent recovery, so there is no guaranteed short exposure window.

## Beyond classical DH

Shor's algorithm on a large quantum computer would solve discrete logs and break DH and ECDH. Because recorded traffic could be decrypted later, browsers and CDNs have already deployed **hybrid** key exchange, X25519 combined with ML-KEM-768, so a correctly constructed and authenticated hybrid can retain key-establishment secrecy if one component remains secure under its assumptions. This does not protect compromised endpoints or broken authentication.

## Key takeaways
- Diffie–Hellman lets two parties agree a secret over a public channel; with prime 23, generator 5 and secrets 6 and 15, both compute 2.
- Small examples are breakable. Real DH requires suitable groups, unpredictable secrets, authenticated peers and an appropriate computational hardness assumption.
- Unauthenticated DH is defeated by a man in the middle. Real protocols sign the exchange or pin known public keys.
- Use vetted parameters (≥2,048-bit safe-prime groups or, better, X25519), validate inputs, and derive keys with HKDF rather than using the raw secret.
- Fresh, erased ephemeral (EC)DHE secrets provide forward secrecy for certificate-authenticated TLS 1.3 handshakes; PSK-only and early-data cases have different guarantees.

## Further reading
- [Diffie–Hellman key exchange — Wikipedia](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange)
- [RFC 7748: Elliptic Curves for Security (X25519)](https://www.rfc-editor.org/rfc/rfc7748)
- [Imperfect Forward Secrecy: the Logjam attack](https://weakdh.org/)
- [RFC 7919: Negotiated FFDHE groups for TLS](https://www.rfc-editor.org/rfc/rfc7919)
- [X25519 key exchange — cryptography.io](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/x25519/)
- [Forward secrecy — Wikipedia](https://en.wikipedia.org/wiki/Forward_secrecy)
