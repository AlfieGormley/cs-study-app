---
id: nsec-wifi-wep-reused-ivs
title: Radio exposure and WEP IV reuse
level: advanced
minutes: 3
summary: Radio reception extends the observation boundary beyond a cable.
sourceLesson: nsec-wireless
---

Wired networks have a physical boundary: to sniff a cable you need to reach it. Wi-Fi signals may extend beyond the intended premises. Capture depends on channel, signal, interference and receiver capabilities; being nearby does not guarantee reception of every frame.

So Wi-Fi security has to provide in protocol what walls provide for Ethernet:

- **Access control**: only authorised devices may join.
- **Confidentiality and integrity** for protected data, with separate protection rules for management traffic; many headers and control frames remain exposed.
- **Authentication of the network**, so clients do not join an impostor.

The history of Wi-Fi security is a tour of how to get these wrong, and it is worth studying because the same mistakes recur in other protocols.

## WEP: what not to do

**WEP**, introduced with the original 802.11 standard, encrypted the payloads of protected 802.11 data frames with the RC4 stream cipher, using a key built from a shared 40- or 104-bit secret plus a 24-bit **initialisation vector** (IV) sent in clear. Integrity came from a CRC-32 checksum.

Its flaws compound:

### IV reuse

 Stream ciphers must never reuse a keystream. A 24-bit IV has only about 16.8 million possible values, and repeats come much sooner than that. If each frame picks an IV independently and uniformly at random (repeats allowed), the **birthday approximation** says when the chance that *some* two frames share an IV reaches 50 %:

```formula
N = 2^24 = 16777216
n_50 ≈ √(2 ln(2) N)
n_50 ≈ 1.18√(N) = 1.18 × 4096
n_50 ≈ 4800
where
N: the number of possible IVs: 24 copies of 2 multiplied together, because the IV is 24 bits long
n_50: the number of frames after which the chance of at least one repeated IV reaches 50 %
√: square root
ln: the natural logarithm (logarithm to base e ≈ 2.718); ln(2) ≈ 0.693
≈: approximately equal to (rounded)
In words: because any pair of frames can collide, a repeat becomes an even bet after only about the square root of the number of IVs, roughly 4,800 frames, not after 16.8 million.
```

   This is why it is called the birthday problem: in a room of just 23 people, two probably share a birthday. Counter-based IV choices have different repeat behaviour until wraparound. For equal IVs under the same WEP key, XORing the encrypted payloads cancels their keystream and reveals the XOR of the plaintexts; recovering either plaintext needs further information.

## Key takeaways
- Radio reception extends the observation boundary beyond a cable.
- WEP’s small IV space can repeat keystreams under the same key.
- The birthday estimate assumes independent uniform random IV choices.

## Further reading
- [Key Reinstallation Attacks (KRACK) — Mathy Vanhoef](https://www.krackattacks.com/)
- [Dragonblood: analysing WPA3's Dragonfly handshake](https://wpa3.mathyvanhoef.com/)
- [Wi-Fi Protected Access — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access)
- [Wired Equivalent Privacy — Wikipedia](https://en.wikipedia.org/wiki/Wired_Equivalent_Privacy)
- [IEEE 802.1X — Wikipedia](https://en.wikipedia.org/wiki/IEEE_802.1X)
- [RFC 7664: Dragonfly Key Exchange](https://www.rfc-editor.org/rfc/rfc7664)
