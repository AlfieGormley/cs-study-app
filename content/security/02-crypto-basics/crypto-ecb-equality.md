---
id: crypto-ecb-equality
sourceLesson: crypto-symmetric
title: ECB exposes equal plaintext blocks
level: basic
minutes: 3
summary: Identical AES blocks expose equality under ECB, allowing patterns and block rearrangement.
---
## ECB: the mode you must not use

**Electronic Codebook (ECB)** is the obvious approach: split the message into 16-byte blocks and encrypt each independently.

```
P1      P2      P3
|       |       |
AES_k   AES_k   AES_k
|       |       |
C1      C2      C3
```

Each ciphertext block depends only on its own plaintext block and the key. Nothing carries over from one block to the next, and nothing changes between messages.

The problem: **identical plaintext blocks give identical ciphertext blocks**. Repeated blocks therefore reveal equality directly to an observer. ECB is deterministic per block, so it leaks structure. The famous demonstration encrypts an uncompressed image of the Linux penguin: the "encrypted" image is still clearly a penguin, because every patch of the same colour encrypts to the same bytes.

> [!example] ECB leaks equality
> Encrypt `YELLOW SUBMARINE` twice in a row (32 bytes) with AES-ECB. The two 16-byte ciphertext blocks are byte-for-byte identical. An observer learns "these blocks are equal" without the key.

> [!analogy] Real-world analogy: A phrasebook code
> Imagine a secret code book that turns every common phrase into a fixed code word: "meet at noon" is always "PELICAN". Someone who cannot read the code book still notices when "PELICAN" turns up in three messages, and can copy a code word from one message into another.
>
> **How it maps:** The code book is AES under one key, each phrase is a 16-byte plaintext block, and each code word is a ciphertext block. ECB's name, Electronic Codebook, comes from exactly this idea: same input, same output, every time.
>
> **Where it stops:** ECB works on fixed 16-byte chunks rather than words, so a repeat is only visible when equal data lines up on the same block boundaries. Collecting known plaintext and ciphertext pairs lets an attacker recognise those exact blocks again, but not decrypt new ones: AES itself stays strong, and the leak is equality and rearrangement.

It also lets an attacker cut and paste blocks between messages. If block 3 of one ciphertext encrypts `role=admin;.....`, it can be spliced into another message. Avoid ECB for directly encrypting structured application data; low-level block operations can also be components of correctly designed standard constructions.

## Key takeaways
- ECB repeats ciphertext for identical plaintext blocks under one key.
- Pattern leakage and block rearrangement make ECB unsuitable for structured application data.

## Further reading
- [NIST block cipher modes](https://csrc.nist.gov/pubs/sp/800/38/a/final)
- [NIST GCM standard](https://csrc.nist.gov/pubs/sp/800/38/d/final)
