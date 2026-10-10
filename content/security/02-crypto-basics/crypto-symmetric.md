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

How large is that margin? Without the key, the only generic attack is to try keys one by one (brute force). The number of possible keys doubles with every extra key bit:

```formula
N_keys = 2^k
N_keys = 2^128 ≈ 3.4 × 10^38
T_avg ≈ N_keys / 2 = 2^(k−1)
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

For scale: even at a trillion (10^12) guesses per second, 2^127 guesses take about 1.7 × 10^26 seconds, roughly 5 × 10^18 years. The Grover figure is a query count only; it is not a practical quantum runtime estimate, which is why AES-256 is described as a margin rather than a necessity.

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

Written as a formula, each ciphertext block depends only on its own plaintext block and the key:

```formula
C_i = E_k(P_i)
where
C_i: the i-th ciphertext block, 16 bytes (128 bits)
P_i: the i-th plaintext block, 16 bytes
i: the block number: 1 for the first block, 2 for the second, and so on
E_k: one AES block encryption under the secret key k (drawn as AES_k in the diagram)
k: the secret key, 128, 192 or 256 bits long
In words: ECB encrypts every 16-byte block on its own with the same key, so it has no memory of the blocks around it.
```

The problem: **identical plaintext blocks give identical ciphertext blocks**: if P_1 = P_3 then E_k(P_1) = E_k(P_3), so C_1 = C_3. ECB is deterministic per block, so it leaks structure. The famous demonstration encrypts an uncompressed image of the Linux penguin: the "encrypted" image is still clearly a penguin, because every patch of the same colour encrypts to the same bytes.

> [!example] ECB leaks equality
> Encrypt `YELLOW SUBMARINE` twice in a row (32 bytes) with AES-ECB. The two 16-byte ciphertext blocks are byte-for-byte identical. An observer learns "these blocks are equal" without the key.

It also lets an attacker cut and paste blocks between messages. If block 3 of one ciphertext encrypts `role=admin;.....`, it can be spliced into another message. Avoid ECB for directly encrypting structured application data; low-level block operations can also be components of correctly designed standard constructions.

## CBC: chaining with an IV

**Cipher Block Chaining (CBC)** XORs each plaintext block with the previous ciphertext block before encrypting. The first block is XORed with an **initialisation vector (IV)**.

**XOR** (exclusive or, written ⊕) is the workhorse of symmetric cryptography. It compares two bit strings position by position:

```formula
0 ⊕ 0 = 0
0 ⊕ 1 = 1
1 ⊕ 0 = 1
1 ⊕ 1 = 0
x ⊕ y ⊕ y = x
where
⊕: XOR (exclusive or): combines two bit strings bit by bit; each output bit is 1 where the inputs differ and 0 where they match
x, y: any two bit strings of the same length, for example two 16-byte blocks
In words: XOR gives 1 exactly where the two inputs differ, and XORing the same value in twice cancels it out, so one operation both applies and removes a mask.
```

For example, the bytes 0x31 (`0011 0001`) and 0x37 (`0011 0111`) XOR to 0x06 (`0000 0110`): only the two positions that differ come out as 1.

```
IV --XOR      +----XOR      +----XOR
     |        |     |       |     |
     P1       |     P2      |     P3
     |        |     |       |     |
   AES_k      |   AES_k     |   AES_k
     |        |     |       |     |
     C1 ------+     C2 -----+     C3
```

As formulas, encryption and decryption are:

```formula
C_0 = IV
C_i = E_k(P_i ⊕ C_{i−1})
P_i = D_k(C_i) ⊕ C_{i−1}
where
C_i: the i-th ciphertext block, 16 bytes
C_{i−1}: the ciphertext block just before it
C_0: the starting value, set to the IV
IV: the initialisation vector, a random 16-byte block sent along with the ciphertext
P_i: the i-th plaintext block, 16 bytes
i: the block number, counting from 1
E_k: one AES block encryption under the secret key k
D_k: one AES block decryption under k, which undoes E_k
k: the secret key
⊕: XOR (exclusive or): each output bit is 1 where the two inputs differ and 0 where they match
In words: each plaintext block is first mixed with the previous ciphertext block (the IV for the first one) and then encrypted; decryption decrypts the block and XORs the previous ciphertext block back out.
```

So if P_1 and P_2 are both `YELLOW SUBMARINE`, the cipher sees P_1 ⊕ IV and P_2 ⊕ C_1, which are different inputs, and C_1 and C_2 come out unrelated. Now equal plaintext blocks encrypt differently, and the same message encrypted twice looks different, as long as the IV is **random and unpredictable** for every message. A predictable IV broke TLS 1.0 (the BEAST attack, 2011).

CBC has two big weaknesses:

- **Padding.** Messages must be padded to a multiple of 16 bytes (usually PKCS#7). If a server reveals whether the padding was valid, through an error message or even response timing, an attacker can decrypt the whole message one byte at a time. These are **padding oracle** attacks; Lucky Thirteen and POODLE exploit particular TLS/SSL CBC constructions and observable differences. Exploitation depends on obtaining a usable oracle and enough queries.
- **No integrity.** CBC hides the content but does not stop tampering.

PKCS#7 padding always adds between 1 and 16 bytes, and each padding byte holds the number of bytes added, so the receiver knows how many to strip:

```formula
n_pad = 16 − (L mod 16)
L = 10:  n_pad = 16 − 10 = 6
L = 32:  n_pad = 16 − 0 = 16
where
n_pad: the number of padding bytes added, from 1 to 16; each of them has the value n_pad
L: the message length before padding, in bytes
16: the AES block size in bytes
mod: "modulo": L mod 16 is the remainder after dividing L by 16
In words: pad up to the next multiple of 16 bytes, and if the message already fills whole blocks, add a whole extra block of padding so the last byte can always be read as a count.
```

A 10-byte message gets six bytes of `0x06`. A padding oracle works by tweaking the previous ciphertext block until the server says the last byte decrypted to a valid padding value such as `0x01`.

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

As formulas:

```formula
K_i = E_k(N ‖ i)
C_i = P_i ⊕ K_i
P_i = C_i ⊕ K_i
where
K_i: the i-th 16-byte keystream block (K1, K2, … in the diagram)
E_k: one AES block encryption under the secret key k
k: the secret key
N: the nonce, a number used only once per key (96 bits in GCM)
i: the block counter: 0, 1, 2, … (GCM starts its data blocks at 2)
‖: concatenation: the bits of N followed by the bits of i, filling one 16-byte counter block
C_i: the i-th ciphertext block
P_i: the i-th plaintext block (the last block may be shorter; the extra keystream is thrown away)
⊕: XOR (exclusive or): each output bit is 1 where the two inputs differ and 0 where they match
In words: AES only ever encrypts the counter blocks; the message is hidden by XORing it with that keystream, and XORing the same keystream again recovers it.
```

CTR needs no padding, blocks can be processed in parallel, and you can decrypt from the middle. But it has one absolute rule: **never repeat a counter block with the same key**. Use non-overlapping nonce/counter ranges, and prevent counter wraparound.

If two messages share a keystream K, XOR their ciphertexts together:

```formula
C_1 ⊕ C_2 = (P_1 ⊕ K) ⊕ (P_2 ⊕ K)
C_1 ⊕ C_2 = P_1 ⊕ P_2
where
C_1, C_2: the two ciphertexts, which the attacker can see
P_1, P_2: the two plaintexts
K: the keystream that both were XORed with, because the key and nonce were the same
⊕: XOR (exclusive or): each output bit is 1 where the two inputs differ and 0 where they match
In words: the keystream appears twice, and anything XORed with itself vanishes, so the attacker gets the XOR of the two plaintexts without ever touching the key.
```

The key cancels out. If the first bytes of the ciphertexts XOR to 0x15 and the attacker knows P_1 starts with `A` (0x41), then P_2 starts with 0x15 ⊕ 0x41 = 0x54, the letter `T`. Known or correctly guessed plaintext reveals corresponding bytes of the other message. The XOR alone does not determine both complete messages. This repeated-keystream failure is called the "two-time pad".

## The missing piece: integrity

Properly used encryption can provide **confidentiality** against its intended attacker model; unauthenticated modes can fail under active attacks. It does not give **integrity**: an attacker may still change it. With CTR (or any stream cipher), flipping a bit in the ciphertext flips exactly that bit in the plaintext.

> [!example] Malleability in practice
> A server encrypts `pay Bob 10` with AES-CTR. The attacker doesn't know the key but guesses the format. They XOR byte 8 of the ciphertext with `'1' XOR '9'` (that's `0x08`). The server decrypts `pay Bob 90` without complaint.

Why it works: the attacker XORs a difference D into the ciphertext, and decryption carries it straight into the plaintext.

```formula
P′ = (C ⊕ D) ⊕ K
P′ = (C ⊕ K) ⊕ D = P ⊕ D
D = '1' ⊕ '9' = 0x31 ⊕ 0x39 = 0x08
where
C: the ciphertext byte the attacker changes (byte 8, counting from 0)
K: the keystream byte at that position, which the attacker never learns
P: the original plaintext byte, the character '1'
D: the difference the attacker chooses: the XOR of the old and wanted characters
P′: the byte the server gets after decrypting the altered ciphertext: here the character '9'
0x31, 0x39, 0x08: byte values in hexadecimal (base 16, marked by 0x); 0x31 is the character '1' and 0x39 is '9' in ASCII
⊕: XOR (exclusive or): each output bit is 1 where the two inputs differ and 0 where they match
In words: XORing D into the ciphertext XORs exactly D into the plaintext, so an attacker who can guess one plaintext byte can turn it into any byte they like.
```

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

This prints `26` and then `b'pay Bob 10'`. GCM adds no padding, so the output length is simple:

```formula
L_out = L_in + 16
L_out = 10 + 16 = 26 bytes
where
L_out: the length of what encrypt() returns (ciphertext with the tag appended), in bytes
L_in: the length of the plaintext, in bytes (`pay Bob 10` is 10)
16: the tag length: 128 bits = 16 bytes
bytes: the unit; one byte is 8 bits
In words: the ciphertext is exactly as long as the plaintext, plus a 16-byte authentication tag on the end; the 12-byte nonce is stored separately.
```

Flip any bit of `ct`, the nonce or `aad`, and `decrypt` raises `InvalidTag` instead of returning tampered data. You store or send the nonce alongside the ciphertext; it doesn't need to be secret, only unique.

Python `cryptography`'s **Fernet** manages a random IV and token format for authenticated encryption, but has no associated-data interface. Libsodium's low-level `secretbox` requires the caller to supply a nonce; some wrappers manage it. Check the specific API rather than assuming automatic nonce generation.

## GCM's sharp edge: nonce reuse

GCM inherits CTR's nonce rule, and the consequences are worse. Reusing a nonce under the same key:

1. Leaks `P1 XOR P2`, exactly as in CTR.
2. Can expose equations for GCM's authentication key and enable **forgeries**. Distinct messages, tag length and available observations affect whether the key is uniquely recovered.

Random nonces can collide by chance. The **birthday bound** estimates how likely it is that any two of q messages drew the same nonce:

```formula
p_coll ≈ q^2 / 2^(b+1)
p_coll ≈ (2^32)^2 / 2^97
p_coll ≈ 2^64 / 2^97 = 2^−33
where
p_coll: the probability that at least two of the q messages got the same nonce, from 0 (never) to 1 (certain)
q: the number of messages encrypted under one key
b: the nonce length in bits, 96 for standard GCM
2^(b+1): the number of possible nonces, 2^b, doubled (the 2 comes from counting each pair of messages once)
≈: approximately equal to; the approximation is good while p_coll is small
In words: the collision chance grows with the square of the number of messages, so it is tiny at 2^32 messages (about 1 in 8.6 billion) but approaches a coin-flip once q nears 2^(b/2) = 2^48.
```

NIST SP 800-38D requires the chance that one key is ever used with a repeated IV on different data to be at most 2^−32, and for random 96-bit nonces it caps each key at 2^32 (about 4.3 billion) encryptions. The estimate above gives about 2^−33 at that cap, inside the requirement. Apply the limit across all devices using that key, plus message-length and tag-dependent limits. A counter requires coordinated uniqueness across restarts and workers. **AES-GCM-SIV** tolerates accidental nonce repetition better, though repetition can still leak equality and usage limits remain. **XChaCha20-Poly1305** has a 192-bit nonce that makes random collisions negligible at practical volumes; it is **not** nonce-misuse resistant and must not repeat a nonce under a key.

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
