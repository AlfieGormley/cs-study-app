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

No further contact with the network is needed, so there is no lockout. The 4,096 PBKDF2 iterations add work per guess, but the rate an attacker achieves depends on their hardware and software. In some configurations, a captured **PMKID**, derived using the PMK, a fixed label and both MAC addresses, supplies another offline verifier without a victim client handshake:

```formula reference
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

**How long does a passphrase last?** That depends on how many candidates the attacker must try and how fast they can try them. The number of candidates grows exponentially with length: each extra random character multiplies it by the size of the character set.

```formula reference
K = c^L
where
K: the number of possible passphrases (the keyspace)
c: the number of possible characters per position, for example 26 for lowercase letters only
L: the passphrase length in characters
^: "to the power of": c^L is L copies of c multiplied together
In words: the search space is the number of choices per position multiplied by itself once for every position, so length matters enormously.
```

For example, eight random lowercase letters give about 209 billion candidates. At a hypothetical constant million guesses per second, trying them all takes about 58 hours, and on average a randomly chosen one is found in about half that time. Five words chosen at random from a 7,776-word list give roughly a hundred million times more candidates. These figures assume the passphrase was chosen uniformly at random. Human choices are often not, and a dictionary ordered by popularity finds them far sooner; security also depends on the attacker's hardware and budget.

> [!analogy] Real-world analogy: a copy of the lock taken home
> Guessing a door code at the door is slow and noisy: there are cameras, and the keypad locks after a few wrong tries. Now imagine the thief could make an exact copy of the lock and take it home. They could try codes all night, as fast as they like, and nobody would ever know.
>
> **How it maps:** Guessing at the door is online guessing against the access point, which can rate-limit. The copied lock is the captured handshake or PMKID: it contains enough to check each guess, so the attack moves offline with no lockout. The difficulty of each try is PBKDF2's 4,096 iterations, and the number of codes is the passphrase's search space.
>
> **Where it stops:** A copied lock never tells you the code directly; the captured handshake does not contain the passphrase either, only a way to test it. And a thief at home is limited by patience, while an offline attacker's speed scales with how many GPUs they can rent. WPA3's SAE, correctly implemented, is designed so that a captured exchange gives no such copy.

WPA2-Personal's resistance to this offline guessing attack depends on passphrase strength. An observer who knows the shared passphrase and captures the needed WPA2-Personal handshake can derive that client's link-layer keys; application TLS can still protect the application payload. Implementation and management-frame security also matter.

## Key takeaways
- Captured handshake data can verify passphrase guesses without a live login.
- SSID salting restricts reuse of precomputed tables to the same salt.
- A long, randomly chosen passphrase is the main defence against offline guessing.

## Further reading
- [Wi-Fi Protected Access — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access)
- [Dictionary attack — Wikipedia](https://en.wikipedia.org/wiki/Dictionary_attack)
- [Dragonblood: analysing WPA3's Dragonfly handshake](https://wpa3.mathyvanhoef.com/)
