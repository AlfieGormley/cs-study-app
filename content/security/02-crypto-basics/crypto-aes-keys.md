---
id: crypto-aes-keys
sourceLesson: crypto-symmetric
title: Shared keys and the AES block cipher
level: basic
minutes: 5
summary: AES maps 128-bit blocks under a shared secret key; its key length sets a generic search margin.
---

With symmetric encryption, two parties share one secret **key**, and the same key both locks (encrypts) and unlocks (decrypts) the data.

```
 plaintext --[ Enc(key) ]--> ciphertext
ciphertext --[ Dec(key) ]--> plaintext
```

Symmetric encryption is used for bulk data; public-key operations commonly establish or protect its keys. Hardware AES instructions can accelerate it; actual speed depends on the mode, the implementation and the size and pattern of the data.

One principle runs through the whole field. **Kerckhoffs's principle** says a system must stay secure even if the attacker knows everything about it except the key. So the algorithm is public, and all the secrecy lives in the key. "Nobody knows how our cipher works" is not security.

> [!analogy] Real-world analogy: A padlock model anyone can buy
> A well-known padlock model is sold in every hardware shop. Anyone can buy one, take it apart and study the mechanism, yet your particular lock is still safe because only you have its key.
>
> **How it maps:** The published padlock design is the public cipher (AES, its rounds and its mode). The individual key is the secret key. Kerckhoffs's principle says security must survive full knowledge of the design, just as a good padlock model stays useful after its blueprint is public.
>
> **Where it stops:** Physical locks fail to picking, cutting and wear, and a key can be copied from a photograph. A cipher's key cannot be guessed from its design, and the attacker's cost is measured in guesses: each extra key bit doubles the work, which has no padlock equivalent.

> [!warning] Never roll your own
> Everything in this lesson is here so you understand what your library does and can spot misuse. In real code, use a vetted, high-level library (Python's `cryptography`, libsodium, Google Tink, your platform's crypto API). Do not design ciphers, modes or protocols yourself, and do not hand-assemble low-level primitives.

## Block ciphers and AES

A **block cipher** is a keyed permutation on fixed-size blocks. For AES, a given key maps each possible 128-bit input to a unique 128-bit output, and it should look like a random permutation to anyone without the key.

**AES** (the Advanced Encryption Standard, originally Rijndael) is the block cipher you will use:

| Property | Value |
|---|---|
| Block size | 128 bits (16 bytes) |
| Key sizes | 128, 192, 256 bits |
| Rounds | 10, 12, 14 |
| Standard | NIST FIPS 197 (2001) |

AES starts with a round-key addition. Its rounds apply byte substitution, row shifts and round-key addition; all but the final round also mix columns. AES-128 and AES-256 are standardised choices. AES-256 offers a larger key-search margin.

How large is that margin? For an ideal block cipher, generic classical key search tries keys one by one (brute force). This is a baseline work model, not a proof that no cryptanalytic shortcut exists for a concrete algorithm. The relationship to keep in mind is that every extra key bit doubles the number of possible keys:

```formula essential
N_keys = 2^k
where
N_keys: the number of possible keys (the keyspace)
k: the key length in bits: 128, 192 or 256 for AES
In words: each extra key bit doubles the keyspace, so a 129-bit key has twice as many possibilities as a 128-bit key, and a 256-bit key has 2^128 times as many as a 128-bit key.
```

On average a classical search finds the key after trying about half the keyspace. For scale, even an entirely hypothetical trillion guesses per second would need about five billion billion years on average for one uniformly chosen 128-bit key. That is why practical attacks go after how keys are generated, stored and used rather than the key length itself.

Quantum computers change the generic estimate less than many people expect. Grover's algorithm, an idealised quantum search, needs on the order of the square root of the keyspace in queries: about 2^64 for a 128-bit key and about 2^128 for a 256-bit key. That is a query count, not a practical quantum runtime estimate, which is why AES-256 is described as an extra margin rather than a necessity.

One AES block operation processes exactly 16 bytes. Real messages are longer, so you need a **mode of operation** that says how to chain blocks together. The mode is where most real-world mistakes happen.

## Key takeaways
- AES maps 128-bit blocks under a shared secret key; its key length sets a generic search margin.
- Public algorithms and secret keys follow Kerckhoffs’s principle.

## Further reading
- [NIST FIPS 197: AES](https://csrc.nist.gov/pubs/fips/197/final)
- [Python cryptography: AEAD APIs](https://cryptography.io/en/latest/hazmat/primitives/aead/)
