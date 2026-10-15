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

 A message authentication code (keyed MAC) is a checksum computed with a secret key, so only key holders can produce a valid one. CRC-32 has no key, and its algebraic structure permits predictable checksum adjustments when chosen bits are modified. For two messages of the same length:

```formula
CRC(a ⊕ b) = CRC(a) ⊕ CRC(b) ⊕ C_0
where
CRC: the CRC-32 checksum function, which turns a message into a 32-bit value
a: one message, as a string of bits
b: another message of the same length; in an attack, a pattern of bits to flip
⊕: XOR (exclusive OR), bit by bit: 1 where the two inputs differ, 0 where they match
C_0: the CRC-32 of an all-zero message of that length; it appears because CRC-32 uses fixed initial and final values, which makes the relation affine rather than purely linear
In words: the checksum of a message with flipped bits can be calculated from the old checksum and the flip pattern alone, without knowing the message.
```

   So an attacker who flips chosen bits of a WEP frame (RC4 encryption is XOR with a keystream, so flipping ciphertext bits flips the same plaintext bits) can also fix up the encrypted checksum. CRC-32 has no key, so it cannot prove that the frame is genuine.
**Shared-key management** makes individual revocation and safe rotation difficult; WEP does not require that operators literally never change keys.

WEP is obsolete; never use it. The lessons: never reuse a nonce, use a keyed MAC, and derive fresh per-session keys.

## Key takeaways
- WEP’s weak RC4 key scheduling enabled practical key-recovery attacks.
- CRC-32 detects accidental errors; it does not authenticate a sender.
- The equal-length CRC relation includes the affine correction term.

## Further reading
- [Key Reinstallation Attacks (KRACK) — Mathy Vanhoef](https://www.krackattacks.com/)
- [Dragonblood: analysing WPA3's Dragonfly handshake](https://wpa3.mathyvanhoef.com/)
- [Wi-Fi Protected Access — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access)
- [Wired Equivalent Privacy — Wikipedia](https://en.wikipedia.org/wiki/Wired_Equivalent_Privacy)
- [IEEE 802.1X — Wikipedia](https://en.wikipedia.org/wiki/IEEE_802.1X)
- [RFC 7664: Dragonfly Key Exchange](https://www.rfc-editor.org/rfc/rfc7664)
