---
id: crypto-cbc-padding
sourceLesson: crypto-symmetric
title: CBC IVs, padding and authentication
level: basic
minutes: 5
summary: Trace CBC chaining, choose unpredictable IVs and recognise padding-oracle and integrity failures.
---
CBC combines each block with the previous ciphertext, using an unpredictable IV to start. Understanding that chain explains why padding errors and unauthenticated changes are dangerous.

## CBC: chaining with an IV

**Cipher Block Chaining (CBC)** XORs each plaintext block with the previous ciphertext block before encrypting. The first block is XORed with an **initialisation vector (IV)**.

**XOR** (exclusive or, written ⊕) is the workhorse of symmetric cryptography. It compares two bit strings position by position:

```formula essential
x ⊕ y ⊕ y = x
where
⊕: XOR (exclusive or): combines two bit strings bit by bit; each output bit is 1 where the inputs differ and 0 where they match
x, y: any two bit strings of the same length, for example two 16-byte blocks
In words: XORing the same value in twice cancels it out, so one operation both applies a mask and removes it. This is why a single XOR can both encrypt and decrypt, and why repeated masks cancel.
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

Put simply: before encryption, each plaintext block is XORed with the previous ciphertext block (the IV for the first block). Decryption runs AES backwards on a block and then XORs the previous ciphertext block back out. That last step matters later: whatever an attacker does to one ciphertext block lands, bit for bit, in the next decrypted plaintext block (and scrambles the block it sits in).

```formula reference
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
In words: encryption mixes each plaintext block with the previous ciphertext block before AES; decryption undoes AES and then XORs the previous ciphertext block back out, so a change to one ciphertext block flips the same bits in the next plaintext block.
```

If the first two plaintext blocks are both `YELLOW SUBMARINE`, each is mixed with a different chaining value in the usual case. Repeated plaintext no longer forces repeated ciphertext, although accidental block equality remains possible. Use a fresh **random and unpredictable** IV for each CBC message; also authenticate it with the ciphertext. This prevents the deterministic equality pattern of ECB under the scheme’s assumptions. A predictable IV broke TLS 1.0 (the BEAST attack, 2011).

CBC has two big weaknesses:

- **Padding.** Messages must be padded to a multiple of 16 bytes (usually PKCS#7). If a server reveals whether the padding was valid, through an error message or even response timing, an attacker can decrypt the whole message one byte at a time. These are **padding oracle** attacks; Lucky Thirteen and POODLE exploit particular TLS/SSL CBC constructions and observable differences. Exploitation depends on obtaining a usable oracle and enough queries.
- **No integrity.** CBC hides the content but does not stop tampering.

PKCS#7 padding always adds between 1 and 16 bytes, and every padding byte holds the number of bytes added, so the receiver knows how many to strip. A message that already fills whole blocks gets a whole extra block of sixteen `0x10` bytes, so the last byte can always be read as a count. A 10-byte message gets six bytes of `0x06`. A padding oracle works by tweaking the previous ciphertext block until the server says the last byte decrypted to a valid padding value such as `0x01`.

> [!analogy] Real-world analogy: A clerk with two rejection stamps
> A clerk checks sealed forms you cannot read. Forms with a badly filled-in last box get stamped "bad ending"; everything else that fails gets "rejected". By submitting many slightly altered copies and watching which stamp comes back, you can work out what was written in the last box, one character at a time.
>
> **How it maps:** The clerk is the server decrypting CBC; the "bad ending" stamp is a distinguishable padding error (an error message, status code or timing difference). Each altered copy is a ciphertext whose previous block the attacker has tweaked, and each answer reveals whether the decrypted last byte formed valid padding.
>
> **Where it stops:** A real clerk's answer would not let you calculate hidden text. The attack works because CBC decryption XORs the previous ciphertext block into the plaintext, so the attacker's tweak and the padding rule together pin down each byte exactly. Without that XOR structure, two stamps would leak far less.

## Key takeaways
- CBC uses an unpredictable IV, block chaining and unambiguous padding.
- CBC alone lacks integrity; observable padding differences can become an attack oracle.

## Further reading
- [NIST block cipher modes](https://csrc.nist.gov/pubs/sp/800/38/a/final)
- [NIST GCM standard](https://csrc.nist.gov/pubs/sp/800/38/d/final)
