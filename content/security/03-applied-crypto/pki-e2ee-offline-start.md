---
id: pki-e2ee-offline-start
title: E2EE and offline recipient prekeys
level: advanced
minutes: 2
sourceLesson: pki-e2ee
summary: Hop-by-hop TLS exposes that layer’s plaintext at each terminating server; inner E2EE keeps content keys at endpoints.
---

In a messaging service that uses only hop-by-hop TLS, the server decrypts the application messages and can read them before forwarding them over another TLS connection. TLS can also carry already end-to-end encrypted content; in that case terminating TLS does not reveal the inner message.

**End-to-end encryption** (E2EE) removes the server from the circle of trust for content. Only the sender's and recipient's devices hold the keys; the server relays ciphertext it cannot read. The Signal protocol family is used in Signal and other messaging products. Product deployment scope and defaults can change; this lesson explains the protocol rather than claiming every feature or conversation in another product uses the same design.

## Why messaging is a hard case

E2EE for a phone call is relatively easy: both parties are online, so they can run a Diffie–Hellman handshake like TLS. Messaging is harder:

- **Asynchronous**: Alice wants to send a message while Bob's phone is off. There is no chance for a two-way handshake.
- **Long-lived**: a conversation may last years. One stolen key should not expose all of it.
- **Devices get compromised**: phones are lost, seized or infected. Ideally a conversation should heal once the attacker loses access.
- **The server distributes keys**: you are trusting it to give you Bob's real public key, not its own.

Signal's goals, beyond confidentiality and integrity:

| Property | Meaning |
|---|---|
| Forward secrecy | Old messages stay safe after a key leak |
| Post-compromise security | Future messages can recover after fresh unknown secrets enter the ratchet and attacker access ends |
| Asynchronous start | Bob can be offline |
| Deniability | Shared-key tags alone are not transferable proof of authorship |

## Starting a session: X3DH and prekeys

Bob's phone uploads a **prekey bundle** to the server in advance:

- **IK_B**: his long-term **identity public key**; the corresponding private key stays on his endpoint.
- **SPK_B**: a **signed prekey**, a medium-term DH public key, signed using the private half of Bob's identity key pair and replaced periodically according to policy.
- **OPK_B**: a stack of **one-time prekeys**, each handed out once.

When Alice wants to talk, the server gives her Bob's bundle, including one OPK, which it then deletes from its public inventory. Alice checks the signed prekey’s signature and generates a fresh ephemeral key pair, called EK_A. The next unit combines those public keys with her private keys to derive the shared secret.

## Key takeaways
- Hop-by-hop TLS exposes that layer’s plaintext at each terminating server; inner E2EE keeps content keys at endpoints.
- Offline recipients publish authenticated public prekeys so senders can start without a live round trip.
- Endpoint compromise, long conversations and key-directory authenticity are separate design challenges.

## Further reading
- [X3DH specification — Signal](https://signal.org/docs/specifications/x3dh/)
- [Double Ratchet specification — Signal](https://signal.org/docs/specifications/doubleratchet/)
