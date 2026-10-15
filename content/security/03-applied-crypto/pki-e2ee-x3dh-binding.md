---
id: pki-e2ee-x3dh-binding
title: X3DH key binding and post-quantum starts
level: advanced
minutes: 3
sourceLesson: pki-e2ee
summary: X3DH combines three or four DH results with different identity and ephemeral roles.
---

Alice has Bob’s X3DH prekey bundle: his identity public key, its signed prekey, and an optional one-time prekey. She verifies the signed prekey, creates an ephemeral key pair and computes the DH contributions below. Public bundle keys have private halves retained by their owners.

```formula
DH1 = DH(IK_A, SPK_B)
DH2 = DH(EK_A, IK_B)
DH3 = DH(EK_A, SPK_B)
DH4 = DH(EK_A, OPK_B)
SK = KDF(DH1 ‖ DH2 ‖ DH3 ‖ DH4)
where
DH: one Diffie–Hellman computation (X25519 or X448 in Signal): DH(X, Y) combines the private half of key pair X with the public half of key pair Y; the holder of Y's private half gets the same result (32 bytes with X25519) from X's public half
IK_A: Alice's long-term identity key pair
IK_B: Bob's long-term identity key pair
SPK_B: Bob's signed prekey pair, replaced periodically according to policy
EK_A: Alice's ephemeral key pair, made fresh for this session and deleted afterwards
OPK_B: one of Bob's one-time prekey pairs, used once and deleted
DH1: the shared secret from Alice's identity key and Bob's signed prekey
DH2: the shared secret from Alice's ephemeral key and Bob's identity key
DH3: the shared secret from Alice's ephemeral key and Bob's signed prekey
DH4: the shared secret from Alice's ephemeral key and Bob's one-time prekey; left out if no one-time prekey was available
SK: the 32-byte shared secret key that starts the session
KDF: key derivation function: X3DH uses HKDF, with 32 bytes of 0xFF (for X25519) placed in front of the input to separate it from other uses of the same keys
‖: concatenation: the bytes of one value followed directly by the next
In words: Alice combines four pairings of her keys with Bob's, and hashes all four results into one session key; Bob, holding the matching private halves, computes exactly the same four values later.
```

Each one has a job:

- **DH1 and DH2** each involve one party's identity key, binding the exchange to those identity keys. This provides **mutual authentication of keys** under the protocol’s assumptions; establishing that those keys belong to the intended people requires authenticated key comparison or another trusted binding.
- **DH3 and DH4** involve Alice's ephemeral key, which she deletes afterwards. That gives **forward secrecy**: stealing both identity keys later does not reveal SK.
- **The one-time prekey**, with its private half deleted after successful use, prevents reusing that prekey to accept the initial exchange again and strengthens protection against later compromise of SPK_B. If the server has run out, X3DH works without DH4, with slightly weaker guarantees.

Alice sends her first message encrypted under a key derived from SK, together with IK_A, EK_A and which prekeys she used. When Bob comes online, he computes the same four values and decrypts. No round trip was needed.

> [!note] PQXDH
> Signal announced **PQXDH** in 2023: Bob's bundle adds signed post-quantum prekeys. The published specification uses a parameterised KEM and gives CRYSTALS-Kyber-1024 as an example. NIST's later ML-KEM standard derives from Kyber, but draft Kyber encodings and the final standard cannot be assumed interchangeable. Alice encapsulates to it and mixes the resulting secret into the KDF alongside the DH values. As with hybrid TLS, the hybrid is designed to retain secrecy if either component remains secure under the protocol’s assumptions. This revision’s mutual authentication still relies on classical discrete-log hardness; it does not authenticate against an active quantum attacker.

## Key takeaways
- X3DH combines three or four DH results with different identity and ephemeral roles.
- Authenticated public-key fingerprint comparison is still needed to bind keys to the intended people.
- PQXDH adds a KEM secret under a specified hybrid design; draft Kyber and final ML-KEM are not interchangeable encodings.

## Further reading
- [X3DH specification — Signal](https://signal.org/docs/specifications/x3dh/)
- [Double Ratchet specification — Signal](https://signal.org/docs/specifications/doubleratchet/)
