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

AES never touches the message itself. It only encrypts the counter blocks, and the output (the keystream) is XORed with the plaintext. Decryption regenerates the same keystream from the key, nonce and counter and XORs it off again.

```formula reference
K_i = E_k(N ‖ i)
C_i = P_i ⊕ K_i
where
K_i: the i-th 16-byte keystream block (K1, K2, … in the diagram)
E_k: one AES block encryption under the secret key k
k: the secret key
N: the nonce, a value used only once per key (96 bits in GCM)
i: the block counter: 0, 1, 2, … (GCM starts its data blocks at 2)
‖: concatenation: the bits of N followed by the bits of i, filling one 16-byte counter block
C_i: the i-th ciphertext block
P_i: the i-th plaintext block (the last block may be shorter; the extra keystream is thrown away)
⊕: XOR (exclusive or): each output bit is 1 where the two inputs differ and 0 where they match
In words: the keystream depends only on the key, the nonce and the block number, never on the message, so the same key and nonce always produce the same keystream.
```

CTR needs no padding, blocks can be processed in parallel, and you can decrypt from the middle. But it has one absolute rule: **never repeat a counter block with the same key**. Use non-overlapping nonce/counter ranges, and prevent counter wraparound.

## What goes wrong when a keystream repeats

Because the keystream ignores the message, reusing a key and nonce gives two messages the *same* keystream. An eavesdropper who XORs the two ciphertexts together makes that shared keystream cancel:

```formula essential
C_1 ⊕ C_2 = P_1 ⊕ P_2
where
C_1, C_2: two ciphertexts encrypted under the same key and nonce, which the attacker can see
P_1, P_2: the two plaintexts
⊕: XOR (exclusive or): each output bit is 1 where the two inputs differ and 0 where they match
In words: the shared keystream appears in both ciphertexts and cancels, so the attacker gets the XOR of the two plaintexts without ever touching the key.
```

That alone is not both messages, but real messages are rarely random. Wherever the attacker knows or can guess one plaintext (a fixed JSON header, an HTTP request line, a file signature), XORing it into the result reveals the other message's bytes at the same positions. Guesses for one message can be checked against the other until both read sensibly. This repeated-keystream failure is called the "two-time pad".

Typical ways it happens in real systems:

- a nonce hard-coded as all zeros "for now";
- a counter stored in memory that restarts at zero after a reboot or redeploy;
- several servers or devices sharing one key, each starting its own counter at zero;
- a random nonce that is too short for the number of messages, so repeats become likely.

> [!analogy] Real-world analogy: The same noise track under two recordings
> Imagine two private phone calls, each disguised by mixing in an identical recorded noise track. Line the two disguised recordings up and subtract one from the other: the noise cancels exactly, and what remains is the difference between the two conversations. If you know what was said in one call, you can recover the other.
>
> **How it maps:** The noise track is the keystream, each call is a plaintext, and subtracting recordings is XORing ciphertexts. Using the same noise track twice is reusing a key and nonce.
>
> **Where it stops:** Audio subtraction is approximate, while XOR cancellation is exact for every bit. And the leftover is not a muddled mix you can hear through: it is the bitwise XOR of the plaintexts, which needs known or guessed text from one message before the other becomes readable.

## Key takeaways
- CTR XORs a counter-derived keystream with data and must never repeat counter blocks under one key.
- Reusing a key and nonce makes the keystream cancel, exposing the XOR of the plaintexts; known or guessed text then reveals the other message.

## Further reading
- [NIST SP 800-38A: block cipher modes](https://csrc.nist.gov/pubs/sp/800/38/a/final)
- [NIST SP 800-38D: GCM](https://csrc.nist.gov/pubs/sp/800/38/d/final)
