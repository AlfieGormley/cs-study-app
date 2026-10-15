---
id: crypto-ciphertext-malleability
sourceLesson: crypto-symmetric
title: How unauthenticated ciphertext can change
level: basic
minutes: 3
summary: CTR ciphertext bit changes become the same plaintext bit changes.
---

CTR decryption removes its keystream with XOR. That reversibility also lets an active attacker apply chosen differences without learning the key.

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

## Key takeaways
- CTR ciphertext bit changes become the same plaintext bit changes.
- Confidentiality alone does not provide integrity; authenticate before using decrypted data.

## Further reading
- [NIST SP 800-38A: block cipher modes](https://csrc.nist.gov/pubs/sp/800/38/a/final)
- [Python cryptography: AEAD APIs](https://cryptography.io/en/latest/hazmat/primitives/aead/)
