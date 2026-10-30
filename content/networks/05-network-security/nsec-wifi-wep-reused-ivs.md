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

Stream ciphers must never reuse a keystream. WEP's keystream depends only on the shared key and the 24-bit IV, so two frames with the same IV under the same key use the same keystream. A 24-bit IV has only about 16.8 million possible values, and if IVs are chosen at random, a repeat arrives much sooner than that, because every pair of frames is a chance to collide. This is the **birthday problem**: in a room of just 23 people, two probably share a birthday, although there are 365 possible days.

```formula reference
n_50 ≈ 1.18√(N)
where
n_50: the number of randomly chosen IVs after which the chance that at least two are equal reaches 50 %
N: the number of possible IVs; 2^24 = 16,777,216 for WEP's 24-bit IV
√: square root
≈: approximately equal to
1.18: the constant √(2 ln 2) from the birthday approximation; ln is the natural logarithm
In words: with random choices, a repeat becomes an even bet after only about the square root of the number of possible values, which for WEP is about 4,800 frames rather than 16.8 million.
```

So with independent, uniformly random IVs a repeated IV is an even bet after about 4,800 frames: a few seconds on a busy network. Counter-based IV choices behave differently until the counter wraps round, but a 24-bit counter still wraps after 16.8 million frames, and every device using the same shared key draws from the same small space.

For equal IVs under the same WEP key, XORing the two encrypted payloads cancels the keystream and reveals the XOR of the two plaintexts; recovering either plaintext needs further information, such as predictable headers.

> [!analogy] Real-world analogy: a one-time pad used twice
> Two spies share a pad of random pages and are meant to use each page once. If one page is used for two messages, an interceptor who lines the two ciphertexts up can cancel the page out and is left with the two messages mixed together, which predictable phrases ("Dear Sir") can then untangle.
>
> **How it maps:** The page is the RC4 keystream chosen by the key and IV, and using a page twice is IV reuse. Lining up and cancelling is XORing the two ciphertexts. WEP's 24-bit IV is like a pad with too few pages: with random page choices, a repeat comes after a few thousand messages.
>
> **Where it stops:** A real one-time pad is perfectly secure if never reused; RC4 in WEP had further weaknesses (the next unit) that allowed recovery of the key itself, not just individual messages.

## Key takeaways
- Radio reception extends the observation boundary beyond a cable.
- WEP’s small IV space can repeat keystreams under the same key.
- With random IVs, a repeat is likely after only a few thousand frames (the birthday problem).

## Further reading
- [Wired Equivalent Privacy — Wikipedia](https://en.wikipedia.org/wiki/Wired_Equivalent_Privacy)
- [Birthday problem — Wikipedia](https://en.wikipedia.org/wiki/Birthday_problem)
- [Wi-Fi Protected Access — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access)
