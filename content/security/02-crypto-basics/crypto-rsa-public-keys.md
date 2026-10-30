---
id: crypto-rsa-public-keys
sourceLesson: crypto-asymmetric
title: Public keys, trapdoors and factoring
level: intermediate
minutes: 3
summary: Authenticate the recipient’s public key before encrypting to it.
---

Symmetric encryption has a chicken-and-egg problem. To talk securely, you and a server must share a key. But how do you get the key to them securely in the first place, over a network an attacker is watching?

**Asymmetric cryptography** (public-key cryptography) uses a mathematically related pair of keys:

- A **public key** you can publish to the world.
- A **private key** you never share.

```
Anyone:   Enc(public, msg) -> ciphertext
Only you: Dec(private, ct) -> msg
```

Anyone can encrypt to you with your public key; only your private key decrypts.

> [!analogy] Real-world analogy: Handing out open padlocks
> You hand out open padlocks to anyone who asks and keep the only key on your keyring. Anyone can put a message in a box and snap one of your padlocks shut; only you can open it.
>
> **How it maps:** The open padlock is the public key, snapping it shut is encryption, and your key is the private key. No secret ever had to travel to the sender.
>
> **Where it stops:** Anyone can also hand out padlocks *claiming* to be yours. Unless the sender checks that the padlock really came from you (certificates, pinned keys), an attacker can substitute their own. Real public-key encryption is also slow and size-limited, so in practice it protects a small symmetric key rather than the whole message.

RSA illustrates a **trapdoor function**: reversing it is intended to be hard without secret information. Other public-key constructions use different mathematical structures. Public-key encryption also needs an authenticated public key: if an attacker substitutes their own, secrecy from that attacker is lost.

## RSA: the idea

RSA (1977) is built on one asymmetry in arithmetic:

- Multiplication is efficient compared with known classical factoring methods for appropriately generated RSA-sized semiprimes.
- **Factoring** the product back into its primes is hard. The best known classical algorithm, the general number field sieve, has a heuristic expected cost that grows faster than any polynomial in the input length. In 2020, researchers factored RSA-250 (829 bits). Their report lists about 2,450 core-years for sieving and 250 for linear algebra, plus 114 for polynomial selection. These are reported historical costs, not a current universal benchmark or claim about the latest record.

RSA works in **modular arithmetic**, "clock arithmetic" where numbers wrap around at a fixed number called the modulus. A 12-hour clock is arithmetic modulo 12: 5 hours after 9 o'clock is 2 o'clock. Likewise 17 divided by 5 leaves remainder 2, so 17 and 2 count as the same number "modulo 5". RSA's public modulus is a huge number of this kind, the product of two secret primes.

## Key takeaways
- Authenticate the recipient’s public key before encrypting to it.
- Factoring an RSA modulus is sufficient to recover private-key information.

## Further reading
- [RFC 8017: RSA and OAEP](https://www.rfc-editor.org/rfc/rfc8017)
- [Python cryptography: RSA API](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/)
