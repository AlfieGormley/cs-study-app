---
id: crypto-symmetric
title: Symmetric encryption
level: basic
minutes: 12
summary: How AES and its modes work, why ECB leaks patterns and CTR without a MAC is malleable, and why modern code uses AEAD (AES-GCM or ChaCha20-Poly1305) from a vetted library.
---

With symmetric encryption, two parties share one secret **key**, and the same key both locks (encrypts) and unlocks (decrypts) the data.

```
 plaintext --[ Enc(key) ]--> ciphertext
ciphertext --[ Dec(key) ]--> plaintext
```

Symmetric encryption is used for bulk data; public-key operations commonly establish or protect its keys. Hardware AES instructions can accelerate it.

> [!note] Content gap: throughput
> No reproducible machine, library or benchmark record supports the former per-core throughput figure, so that measurement is omitted. Performance depends on the mode, implementation and workload.

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

AES starts with a round-key addition. Its rounds apply byte substitution, row shifts and round-key addition; all but the final round also mix columns. AES-128 and AES-256 are standardized choices. AES-256 offers a larger key-search margin. Grover's ideal quantum search has square-root query complexity; this is not a practical quantum runtime estimate.

One AES block operation processes exactly 16 bytes. Real messages are longer, so you need a **mode of operation** that says how to chain blocks together. The mode is where most real-world mistakes happen.

## ECB: the mode you must not use

**Electronic Codebook (ECB)** is the obvious approach: split the message into 16-byte blocks and encrypt each independently.

```
P1      P2      P3
|       |       |
AES_k   AES_k   AES_k
|       |       |
C1      C2      C3
```

The problem: **identical plaintext blocks give identical ciphertext blocks**. ECB is deterministic per block, so it leaks structure. The famous demonstration encrypts a bitmap of the Linux penguin: the "encrypted" image is still clearly a penguin, because every patch of the same colour encrypts to the same bytes.

> [!example] ECB leaks equality
> Encrypt `YELLOW SUBMARINE` twice in a row (32 bytes) with AES-ECB. The two 16-byte ciphertext blocks are byte-for-byte identical. An observer learns "these blocks are equal" without the key.

It also lets an attacker cut and paste blocks between messages. If block 3 of one ciphertext encrypts `role=admin;.....`, it can be spliced into another message. Avoid ECB for directly encrypting structured application data; low-level block operations can also be components of correctly designed standard constructions.

## CBC: chaining with an IV

**Cipher Block Chaining (CBC)** XORs each plaintext block with the previous ciphertext block before encrypting. The first block is XORed with an **initialisation vector (IV)**.

```
IV --XOR      +----XOR      +----XOR
     |        |     |       |     |
     P1       |     P2      |     P3
     |        |     |       |     |
   AES_k      |   AES_k     |   AES_k
     |        |     |       |     |
     C1 ------+     C2 -----+     C3
```

Now equal plaintext blocks encrypt differently, and the same message encrypted twice looks different, as long as the IV is **random and unpredictable** for every message. A predictable IV broke TLS 1.0 (the BEAST attack, 2011).

CBC has two big weaknesses:

- **Padding.** Messages must be padded to a multiple of 16 bytes (usually PKCS#7). If a server reveals whether the padding was valid, through an error message or even response timing, an attacker can decrypt the whole message one byte at a time. These are **padding oracle** attacks; Lucky Thirteen and POODLE exploit particular TLS/SSL CBC constructions and observable differences. Exploitation depends on obtaining a usable oracle and enough queries.
- **No integrity.** CBC hides the content but does not stop tampering.

## CTR: turning a block cipher into a stream cipher

**Counter mode (CTR)** encrypts a counter, `nonce || 0`, `nonce || 1`, `nonce || 2`... to produce a **keystream**, then XORs the keystream with the plaintext.

```
nonce||0  nonce||1  nonce||2
   |         |         |
 AES_k     AES_k     AES_k
   |         |         |
  K1        K2        K3   keystream
   XOR P1    XOR P2    XOR P3
   =C1       =C2       =C3
```

CTR needs no padding, blocks can be processed in parallel, and you can decrypt from the middle. But it has one absolute rule: **never repeat a counter block with the same key**. Use non-overlapping nonce/counter ranges, and prevent counter wraparound.

If two messages share a keystream K, then `C1 XOR C2 = (P1 XOR K) XOR (P2 XOR K) = P1 XOR P2`. The key cancels out. Known or correctly guessed plaintext reveals corresponding bytes of the other message. The XOR alone does not determine both complete messages. This repeated-keystream failure is called the "two-time pad".

## The missing piece: integrity

Properly used encryption can provide **confidentiality** against its intended attacker model; unauthenticated modes can fail under active attacks. It does not give **integrity**: an attacker may still change it. With CTR (or any stream cipher), flipping a bit in the ciphertext flips exactly that bit in the plaintext.

> [!example] Malleability in practice
> A server encrypts `pay Bob 10` with AES-CTR. The attacker doesn't know the key but guesses the format. They XOR byte 8 of the ciphertext with `'1' XOR '9'` (that's `0x08`). The server decrypts `pay Bob 90` without complaint.

The lesson: **unauthenticated encryption is almost never what you want**. You need a way to detect any change before you act on decrypted data.

## AEAD: what you should actually use

**Authenticated Encryption with Associated Data (AEAD)** does both jobs in one primitive. It encrypts the plaintext and computes an authentication **tag** over the ciphertext plus optional **associated data** (headers that must not be changed but needn't be secret, such as a record ID or protocol version). A safe API returns plaintext only after successful authentication. Internal decryption may happen before verification; callers must not use unauthenticated output.

Two common AEAD configurations (GCM also defines other permitted tag lengths):

| AEAD | Nonce | Tag | Notes |
|---|---|---|---|
| AES-256-GCM | 96 bits | 128 bits | Fast with AES-NI |
| ChaCha20-Poly1305 | 96 bits | 128 bits | Fast in software |

**AES-GCM** combines CTR encryption with a tag formed from the GHASH polynomial authenticator and a nonce-dependent AES mask. GHASH alone is not a secure standalone MAC. **ChaCha20-Poly1305** (RFC 8439) pairs a stream cipher with the Poly1305 MAC; it is quick on phones and devices without AES instructions. TLS 1.3 only allows AEAD cipher suites, and these two are the common choices.

Here is what it looks like with Python's `cryptography` library:

```python
import os
from cryptography.hazmat.primitives \
    .ciphers.aead import AESGCM

key = AESGCM.generate_key(bit_length=256)
aead = AESGCM(key)

nonce = os.urandom(12)  # random
aad = b"order-id:4711"  # authed, not secret
ct = aead.encrypt(nonce, b"pay Bob 10", aad)

print(len(ct))           # 10 + 16-byte tag
print(aead.decrypt(nonce, ct, aad))
```

This prints `26` and then `b'pay Bob 10'`. Flip any bit of `ct`, the nonce or `aad`, and `decrypt` raises `InvalidTag` instead of returning tampered data. You store or send the nonce alongside the ciphertext; it doesn't need to be secret, only unique.

Python `cryptography`'s **Fernet** manages a random IV and token format for authenticated encryption, but has no associated-data interface. Libsodium's low-level `secretbox` requires the caller to supply a nonce; some wrappers manage it. Check the specific API rather than assuming automatic nonce generation.

## GCM's sharp edge: nonce reuse

GCM inherits CTR's nonce rule, and the consequences are worse. Reusing a nonce under the same key:

1. Leaks `P1 XOR P2`, exactly as in CTR.
2. Can expose equations for GCM's authentication key and enable **forgeries**. Distinct messages, tag length and available observations affect whether the key is uniquely recovered.

With random 96-bit nonces, NIST SP 800-38D limits you to 2^32 messages per key to keep the collision chance acceptably small. Apply the limit across all devices using that key, plus message-length and tag-dependent limits. A counter requires coordinated uniqueness across restarts and workers. **AES-GCM-SIV** tolerates accidental nonce repetition better, though repetition can still leak equality and usage limits remain. **XChaCha20-Poly1305** has a 192-bit nonce that makes random collisions negligible at practical volumes; it is **not** nonce-misuse resistant and must not repeat a nonce under a key.

## Common mistakes

- **ECB for application data.** Select the intended authenticated scheme explicitly.
- **Hard-coded or reused IVs and nonces**, such as a zero IV "for simplicity".
- **Encryption without authentication**, such as AES-CBC with no MAC, which invites padding oracles and tampering.
- **Using a password as the key.** Keys must be random bytes; derive a key from a password with a password KDF (lesson 6).
- **Ignoring decryption failures** or showing different errors for "bad padding" and "bad MAC", which builds an oracle.
- **Keys in source code.** Use a key management service or secrets manager.

## Key takeaways
- Symmetric ciphers use one shared key; they are fast and protect nearly all bulk data.
- AES is a 128-bit block cipher; the mode of operation decides how secure it is in practice.
- ECB leaks patterns. CBC needs random IVs and is vulnerable to padding oracles. CTR is malleable and breaks completely on nonce reuse.
- Use an AEAD (AES-GCM or ChaCha20-Poly1305) so tampering is detected, and never reuse a nonce with the same key.
- Use a vetted high-level library and never design your own scheme.

## Further reading
- [Block cipher mode of operation — Wikipedia](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation)
- [Authenticated encryption (AEAD) — cryptography.io](https://cryptography.io/en/latest/hazmat/primitives/aead/)
- [NIST SP 800-38D: GCM and GMAC](https://csrc.nist.gov/pubs/sp/800/38/d/final)
- [RFC 8439: ChaCha20 and Poly1305](https://www.rfc-editor.org/rfc/rfc8439)
- [Padding oracle attack — Wikipedia](https://en.wikipedia.org/wiki/Padding_oracle_attack)
- [Cryptographic Right Answers — Latacora](https://www.latacora.com/blog/2018/04/03/cryptographic-right-answers/)
