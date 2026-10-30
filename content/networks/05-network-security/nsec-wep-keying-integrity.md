---
id: nsec-wep-keying-integrity
title: Why WEP keying and CRC integrity fail
level: advanced
minutes: 3
summary: WEP’s weak RC4 key scheduling enabled practical key-recovery attacks.
sourceLesson: nsec-wireless
---

WEP combines a shared secret and a public 24-bit IV for RC4 data encryption. The previous unit explained IV reuse. This unit examines two additional problems: weak key scheduling and an unkeyed integrity check.

### Weak RC4 key scheduling

The Fluhrer–Mantin–Shamir attack (2001), and the much faster PTW attack (2007), recover the key from captured traffic. The 2007 PTW paper reports recovery of a 104-bit WEP key with fewer than 40,000 frames in half its cases, using an active attack. Its sub-minute collection result involved reinjection on an 802.11g network; this is an experiment-specific result, not a guarantee for any busy network.

### CRC-32 is not a keyed MAC

A message authentication code (keyed MAC) is a checksum computed with a secret key, so only key holders can produce a valid one. CRC-32 has no key, and its algebraic structure lets anyone predict how the checksum changes when chosen bits of a message are flipped, without knowing the message itself:

```formula reference
CRC(a ⊕ b) = CRC(a) ⊕ CRC(b) ⊕ C_0
where
CRC: the CRC-32 checksum function, which turns a message into a 32-bit value
a: one message, as a string of bits
b: another message of the same length; in an attack, a pattern of bits to flip
⊕: XOR (exclusive OR), bit by bit: 1 where the two inputs differ, 0 where they match
C_0: the CRC-32 of an all-zero message of that length; it appears because CRC-32 uses fixed initial and final values, which makes the relation affine rather than purely linear
In words: the checksum of a message with flipped bits can be calculated from the old checksum and the flip pattern alone.
```

WEP's RC4 encryption is an XOR with a keystream, so flipping a ciphertext bit flips the same plaintext bit after decryption. An attacker can therefore flip chosen bits of an encrypted frame and also flip the matching bits of the encrypted checksum, and the receiver's CRC check still passes. CRC-32 detects accidental errors; it cannot prove a frame is genuine.

> [!analogy] Real-world analogy: a tamper seal anyone can buy
> A shop seals its boxes with a printed sticker that says "if this seal is broken, the box was opened". Anyone can buy identical stickers, so a thief can open a box, swap the contents and stick a fresh seal on. A wax seal pressed with the shop's private signet ring is different: nobody else can make that mark.
>
> **How it maps:** The shop-bought sticker is CRC-32: it catches accidental damage but anyone can recompute it. The signet seal is a keyed MAC, such as the one in CCMP, which only key holders can produce. Swapping contents and resealing is flipping ciphertext bits and fixing the encrypted checksum.
>
> **Where it stops:** The WEP attacker does not even need to read the contents: XOR lets them change chosen bits blind and adjust the checksum to match. A physical thief usually has to open the box.

**Shared-key management** makes individual revocation and safe rotation difficult; WEP does not require that operators literally never change keys.

WEP is obsolete; never use it. The lessons: never reuse a nonce, use a keyed MAC, and derive fresh per-session keys.

## Key takeaways
- WEP’s weak RC4 key scheduling enabled practical key-recovery attacks.
- CRC-32 detects accidental errors; it does not authenticate a sender.
- The equal-length CRC relation includes the affine correction term.

## Further reading
- [Wired Equivalent Privacy — Wikipedia](https://en.wikipedia.org/wiki/Wired_Equivalent_Privacy)
- [Cyclic redundancy check — Wikipedia](https://en.wikipedia.org/wiki/Cyclic_redundancy_check)
- [Wi-Fi Protected Access — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access)
