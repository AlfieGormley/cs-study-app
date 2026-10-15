---
id: nsec-wpa2-offline-guesses
title: WPA2 offline guessing and search budgets
level: advanced
minutes: 4
summary: Captured handshake data can verify passphrase guesses without a live login.
sourceLesson: nsec-wireless
---

The WPA2 handshake does not send the passphrase, yet it can give an observer enough information to check a guessed passphrase. Trace that distinction before estimating the work of a search.

### The offline cracking problem

Look at what an eavesdropper captures: ANonce, SNonce, both MAC addresses, and a MIC computed from a PTK that depends only on those values and the PMK. So they can mount an **offline guessing** attack, testing passphrase guesses on their own hardware:

```pseudocode
for guess in wordlist:
    p = pmk(guess, ssid)
    if mic(ptk(p, nonces), M2) == seen:
        found!
```

No further contact with the network is needed, so there is no lockout. The 4,096 PBKDF2 iterations add work per guess. The rate depends on hardware and implementation; the next example uses a hypothetical rate. In some configurations, a captured **PMKID**, derived using the PMK, a fixed label and both MAC addresses, supplies another offline verifier without a victim client handshake:

```formula
PMKID = HMAC-SHA1-128(PMK,
          L ‖ MAC_AP ‖ MAC_C)
where
PMKID: PMK identifier, a 128-bit value an AP may send in the first handshake message
HMAC-SHA1-128: HMAC using SHA-1, cut down to its first 128 bits
PMK: Pairwise Master Key, derived from the passphrase
L: the fixed text label "PMK Name"
‖: concatenation: joining byte strings end to end
MAC_AP: the AP's MAC address
MAC_C: the client's MAC address
In words: the PMKID is a fingerprint of the PMK and the two addresses, so an attacker can test a guessed passphrase by recomputing it.
```

**How long does a password last?** The search space is the number of choices per position raised to the number of positions, and the time to search it all is that space divided by the guessing rate:

```formula
K = c^L
K = 26^8 ≈ 2.1 × 10^11
t_full = K / r
t_full = (2.1 × 10^11) / (10^6 s^−1)
t_full ≈ 2.1 × 10^5 s ≈ 58 h
t_avg ≈ t_full / 2 ≈ 29 h
where
K: the number of possible passphrases (the keyspace)
c: the number of possible characters per position; 26 for lowercase letters only
L: the passphrase length in characters; here 8
r: the guessing rate; an assumed constant 10^6 (one million) guesses per second
t_full: the time to try every possibility
t_avg: the average search time, approximately half the full search for this large uniformly chosen keyspace and enumeration without repetition
s: seconds; s^−1 means "per second"
h: hours; 1 h = 3,600 s
^: "to the power of": 26^8 is 8 copies of 26 multiplied together, and 10^11 is 1 followed by 11 zeros
≈: approximately equal to (rounded)
In words: an 8-letter lowercase passphrase has about 210 billion possibilities, which a million guesses a second exhausts in about 58 hours, finding it on average in about 29.
```

This assumes the passphrase was chosen uniformly at random. Human choices are often not, and a dictionary ordered by popularity finds them far sooner. Uniformly choosing five words from a specified large list gives a much larger finite search space (calculated in the quiz); security still depends on the list, selection process and attacker resources.

WPA2-Personal's resistance to this offline guessing attack depends on passphrase strength. An observer who knows the shared passphrase and captures the needed WPA2-Personal handshake can derive that client's link-layer keys; application TLS can still protect the application payload. Implementation and management-frame security also matter.

## Key takeaways
- Captured handshake data can verify passphrase guesses without a live login.
- SSID salting restricts reuse of precomputed tables to the same salt.
- The worked duration is a hypothetical uniform-search model, not a hardware benchmark.

## Further reading
- [Key Reinstallation Attacks (KRACK) — Mathy Vanhoef](https://www.krackattacks.com/)
- [Dragonblood: analysing WPA3's Dragonfly handshake](https://wpa3.mathyvanhoef.com/)
- [Wi-Fi Protected Access — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access)
- [Wired Equivalent Privacy — Wikipedia](https://en.wikipedia.org/wiki/Wired_Equivalent_Privacy)
- [IEEE 802.1X — Wikipedia](https://en.wikipedia.org/wiki/IEEE_802.1X)
- [RFC 7664: Dragonfly Key Exchange](https://www.rfc-editor.org/rfc/rfc7664)
