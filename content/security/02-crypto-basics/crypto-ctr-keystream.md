---
id: crypto-ctr-keystream
sourceLesson: crypto-symmetric
title: CTR counters and repeated keystreams
level: basic
minutes: 3
summary: CTR XORs a counter-derived keystream with data and must never repeat counter blocks under one key.
---

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

The key cancels out. If the ciphertext XOR begins with byte 0x15 and the known first plaintext starts with `A`, recover the other first byte:

```formula
P_2 = 0x15 ⊕ 0x41 = 0x54
where
P_2: the first byte of the other plaintext; 0x54 is ASCII T
0x15: the observed XOR of the first ciphertext bytes
0x41: the known first plaintext byte, ASCII A
⊕: bitwise exclusive or, cancelling the repeated keystream
In words: combine the observed ciphertext XOR with the known A byte to recover T in the other message.
```

Known or correctly guessed plaintext reveals corresponding bytes of the other message. The XOR alone does not determine both complete messages. This repeated-keystream failure is called the "two-time pad".

## Key takeaways
- CTR XORs a counter-derived keystream with data and must never repeat counter blocks under one key.
- Repeated keystream exposes plaintext XOR; known plaintext reveals corresponding other bytes.

## Further reading
- [NIST SP 800-38A: block cipher modes](https://csrc.nist.gov/pubs/sp/800/38/a/final)
- [NIST SP 800-38D: GCM](https://csrc.nist.gov/pubs/sp/800/38/d/final)
