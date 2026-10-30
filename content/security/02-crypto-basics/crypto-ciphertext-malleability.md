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

Why it works: decryption just XORs the keystream back off, so any difference the attacker XORs into a ciphertext byte passes straight through into the decrypted byte. The keystream cancels as usual and the attacker's change survives, so a guessed plaintext byte can be turned into any byte they like.

In the example, the difference is the XOR of the characters `1` and `9` (`0x31` and `0x39`), which is `0x08`. The attacker needs only two things: a guess at the plaintext in that position (message formats are rarely secret) and the ability to change data in transit or in storage. They never need the key.

The same weakness affects CBC in a block-shaped form: flipping bits in one ciphertext block flips the same bits in the next plaintext block. Adding more encryption does not help. What is missing is a check that the ciphertext is exactly what the sender produced.

The lesson: **unauthenticated encryption is almost never what you want**. You need a way to detect any change before you act on decrypted data.

## Key takeaways
- CTR ciphertext bit changes become the same plaintext bit changes.
- Confidentiality alone does not provide integrity; authenticate before using decrypted data.

## Further reading
- [NIST SP 800-38A: block cipher modes](https://csrc.nist.gov/pubs/sp/800/38/a/final)
- [Python cryptography: AEAD APIs](https://cryptography.io/en/latest/hazmat/primitives/aead/)
