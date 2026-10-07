---
id: crypto-key-exchange
title: Key exchange and Diffie–Hellman
level: advanced
minutes: 14
summary: How two strangers agree a secret over a public channel, Diffie–Hellman worked with small numbers, the man-in-the-middle attack and why key exchange must be authenticated, small-subgroup and Logjam pitfalls, ECDH with X25519, and forward secrecy.
---

Alice and Bob have never met. Every byte they send crosses a network Eve can read. Can they end up with a shared secret key that Eve doesn't know?

It sounds impossible: anything they say, Eve hears. In 1976 Whitfield Diffie and Martin Hellman published a way to do it anyway. **Diffie–Hellman (DH) key exchange** and its elliptic-curve variants are important components of protocols including TLS, SSH, Signal, WireGuard and IPsec. Protocol modes vary; some use pre-shared keys or hybrid post-quantum exchange.

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

The public parameters are a prime `p` and a **generator** `g`. We'll use `p = 23`, `g = 5`.

1. Alice picks a secret `a = 6` and sends `A = g^a mod p`.
2. Bob picks a secret `b = 15` and sends `B = g^b mod p`.
3. Alice computes `s = B^a mod p`. Bob computes `s = A^b mod p`.

Step by step:

```
A = 5^6 mod 23
  5^2 = 25 = 2   (mod 23)
  5^4 = 2^2 = 4
  5^6 = 4 x 2 = 8      -> A = 8

B = 5^15 mod 23 = 19   -> B = 19

Alice: 19^6 mod 23 = 2
Bob:    8^15 mod 23 = 2
```

Both get `s = 2`. Checked in Python:

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

```
B^a = (g^b)^a = g^(ab)
A^b = (g^a)^b = g^(ab)
```

Both equal `g^(ab) = 5^90 mod 23`. Since `5^22 ≡ 1 (mod 23)`, exponents repeat every 22, and `90 mod 22 = 2`, so the answer is `5^2 mod 23 = 2`.

### Why Eve can't

Eve knows `p = 23`, `g = 5`, `A = 8` and `B = 19`. Recovering either exponent by discrete logarithm is one way to compute `s`. Here, testing exponents finds `a = 6`. The **computational Diffie–Hellman assumption** directly assumes that obtaining `g^(ab)` from the public shares is infeasible in the chosen group; it does not assert a general equivalence to solving discrete logs. A prime's bit length alone is insufficient: subgroup order, exponent randomness and known attacks matter. Vetted 2,048-bit finite-field groups target roughly 112-bit classical strength, not 2^2048 work.

### What "generator" means

Powers of 5 mod 23 visit every number from 1 to 22 before repeating, so 5 has **order** 22: it generates the whole group. Not every base does. Powers of 2 mod 23 cycle through only 11 values, so a secret derived from base 2 has half as many possible values. Real parameters are chosen so the generator's order is a large prime.

## Man in the middle: why DH must be authenticated

Plain DH protects against a **passive** eavesdropper. It does nothing against an **active** attacker who can change messages. Mallory sits in the middle and runs a separate exchange with each side, using her own secret `m = 3`:

```
Alice --A=8-->  Mallory  --M=10--> Bob
Alice <-M=10--  Mallory  <-B=19--  Bob

M = 5^3 mod 23 = 10

Alice's key: 10^6 mod 23 = 6
  (Mallory: 8^3 mod 23 = 6)
Bob's key:   10^15 mod 23 = 5
  (Mallory: 19^3 mod 23 = 5)
```

Alice thinks she shares key 6 with Bob; she actually shares it with Mallory. Bob shares key 5 with Mallory. Mallory decrypts each message, reads or alters it, and re-encrypts it for the other side. Neither notices.

DH tells you "I share a key with whoever sent this number". It doesn't tell you *who* sent it. Every real protocol therefore **authenticates** the exchange:

- **Certificate-authenticated TLS 1.3**: `CertificateVerify` signs a context string and the transcript hash up to that point. The client verifies the signature, certificate chain and intended server identity. PSK modes authenticate differently.
- **SSH**: the server signs the exchange with its host key; a correctly configured client verifies a trusted host key, often stored in `known_hosts`, and rejects unexpected changes. Accepting an unverified first key can pin an attacker.
- **Signal**: long-term identity keys are mixed into the exchange, and users can compare "safety numbers" out of band.
- **WireGuard**: each peer is configured with the other's static public key in advance.

> [!warning] Unauthenticated DH is a classic home-made protocol bug
> "We do Diffie–Hellman, so it's secure" is not true. Without authentication, a MITM is trivial. This is one of many reasons to use TLS or a Noise-based library rather than designing a protocol.

## Pitfalls in the parameters

### Small-subgroup and invalid values

What if Mallory replaces Bob's value with `B = 22` (that is, `p − 1`, or −1 mod 23)? Then:

```
22^a mod 23 = 1   if a is even
            = 22  if a is odd
```

Alice's "secret" is now one of only two values, both known to Mallory. Similar tricks with values of small order can leak bits of a long-term private key.

Defences: use a **safe prime** `p = 2q + 1` with `q` prime (23 = 2 × 11 + 1 is one), use a generator of the large prime-order subgroup, and **validate** received values (reject 0, 1 and `p − 1`, and check the value is in the right subgroup). Use the checks required by the protocol and library; not every low-level API enforces all of them.

### Weak or shared groups: Logjam

In 2015 the **Logjam** researchers showed two problems:

1. Many TLS servers still accepted 512-bit "export-grade" DH, a 1990s US export restriction. An active attacker could downgrade connections to it and break them in minutes.
2. Most servers shared a handful of standard 1,024-bit primes. Because most of the work in breaking discrete logs depends only on the prime, a nation-state could plausibly precompute once and then break huge numbers of connections.

The response: at least 2,048-bit groups from vetted lists such as RFC 7919's `ffdhe2048` and up, or, far more commonly now, elliptic curves.

## ECDH and X25519

**Elliptic-curve Diffie–Hellman (ECDH)** is the same protocol with points instead of numbers. Alice sends `aG`, Bob sends `bG`, and both compute `abG`. On the toy curve from the last lesson with `G = (5, 1)`, secrets `a = 3` and `b = 7` give public points `(10, 6)` and `(0, 6)`, and both sides arrive at `21G = 2G = (6, 3)`, because the group has 19 elements.

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

Signal's Double Ratchet evolves message keys and periodically incorporates fresh DH material. Erasure protects older keys; recovery after compromise requires fresh secret contributions no longer visible to the attacker. Continuous endpoint access or retained keys can prevent recovery, so there is no guaranteed short exposure window.

## Beyond classical DH

Shor's algorithm on a large quantum computer would solve discrete logs and break DH and ECDH. Because recorded traffic could be decrypted later, browsers and CDNs have already deployed **hybrid** key exchange, X25519 combined with ML-KEM-768, so a correctly constructed and authenticated hybrid can retain key-establishment secrecy if one component remains secure under its assumptions. This does not protect compromised endpoints or broken authentication.

## Key takeaways
- Diffie–Hellman lets two parties agree a secret over a public channel; with `p = 23, g = 5, a = 6, b = 15` both compute `2`.
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
