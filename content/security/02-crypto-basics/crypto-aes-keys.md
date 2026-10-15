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

Symmetric encryption is used for bulk data; public-key operations commonly establish or protect its keys. Hardware AES instructions can accelerate it.

> [!note] Content gap: throughput
> No reproducible machine, library or benchmark record supports the former per-core throughput figure, so that measurement is omitted. Performance depends on the mode, the implementation and the size and pattern of the data being encrypted.

One principle runs through the whole field. **Kerckhoffs's principle** says a system must stay secure even if the attacker knows everything about it except the key. So the algorithm is public, and all the secrecy lives in the key. "Nobody knows how our cipher works" is not security.

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

AES starts with a round-key addition. Its rounds apply byte substitution, row shifts and round-key addition; all but the final round also mix columns. AES-128 and AES-256 are standardized choices. AES-256 offers a larger key-search margin.

How large is that margin? For an ideal block cipher, generic classical key search tries keys one by one (brute force). This is a baseline work model, not a proof that no cryptanalytic shortcut exists for a concrete algorithm. The number of possible keys doubles with every extra key bit:

```formula
N_keys = 2^k
N_keys = 2^128 ≈ 3.4 × 10^38
T_avg ≈ N_keys / 2 = 2^(k − 1)
Q_Grover ≈ √(N_keys) = 2^(k/2)
where
N_keys: the number of possible keys (the keyspace)
k: the key length in bits: 128, 192 or 256 for AES
2^k: k copies of 2 multiplied together, because each extra bit doubles the number of possible keys
T_avg: the average number of keys a classical brute-force search tries before hitting the right one (half the keyspace)
Q_Grover: roughly how many queries Grover's algorithm, an idealised quantum search, would need: on the order of the square root of the keyspace
√: square root: √(x) is the number that multiplied by itself gives x
≈: approximately equal to
In words: every key bit doubles a classical attacker's work, while an ideal quantum search only gets the square root of it, so a 128-bit key gives about 2^64 quantum queries and a 256-bit key about 2^128.
```

For scale, assume an entirely hypothetical trillion guesses per second:

```formula
T = 2^(128 − 1) / r
T ≈ 1.70 × 10^26 s
T ≈ 5.39 × 10^18 yr
where
T: the average classical search time under the assumed rate
r: the hypothetical rate, 10^12 guesses per second
s: seconds
yr: years, using 365.25 days or 31,557,600 seconds per year
≈: approximately equal to
In words: even this assumed rate gives an astronomical average search time for a uniformly chosen 128-bit key.
```

The Grover figure is a query count only; it is not a practical quantum runtime estimate, which is why AES-256 is described as a margin rather than a necessity.

One AES block operation processes exactly 16 bytes. Real messages are longer, so you need a **mode of operation** that says how to chain blocks together. The mode is where most real-world mistakes happen.

## Key takeaways
- AES maps 128-bit blocks under a shared secret key; its key length sets a generic search margin.
- Public algorithms and secret keys follow Kerckhoffs’s principle.

## Further reading
- [NIST FIPS 197: AES](https://csrc.nist.gov/pubs/fips/197/final)
- [Python cryptography: AEAD APIs](https://cryptography.io/en/latest/hazmat/primitives/aead/)
