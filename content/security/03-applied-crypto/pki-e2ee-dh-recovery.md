---
id: pki-e2ee-dh-recovery
title: DH ratcheting and out-of-order messages
level: advanced
minutes: 3
sourceLesson: pki-e2ee
summary: New peer ratchet keys trigger root-key updates for receiving and sending chains.
---

The symmetric ratchet protects old messages, but a thief who copies the current chain key can follow every later message in that chain. The second ratchet brings in fresh Diffie–Hellman secrets so the conversation can heal.

### The DH ratchet: healing after compromise

Every message also carries the sender's current **ratchet public key**. On receiving a new peer ratchet key, a device first combines that key with its existing private ratchet key to derive the receiving chain, then generates a new local key pair and combines it with the peer key to derive the sending chain. The output is mixed into a **root key**, which produces brand-new chain keys:

```
Alice's view, root key chain:
 DH(a1, B0) -> send chain 1
 DH(a1, B1) -> recv chain 1
 DH(a2, B1) -> send chain 2
 DH(a2, B2) -> recv chain 2
 ...
a1, a2 = Alice's ratchet keys
B1, B2 = Bob's ratchet keys
B0 = Bob's signed prekey
```

Each arrow is a root-KDF step: the DH output and the current root key go in, and a new root key and chain key come out:

```formula reference
RK', CK = KDF_RK(RK, DH(a, B))
where
RK: the current root key, 32 bytes
RK': the new root key that replaces it
CK: the new chain key that starts a sending or receiving chain
KDF_RK: the root-key KDF: Signal recommends HKDF with RK as the salt and the DH output as the input keying material, producing 64 bytes split into RK' and CK
DH: one Diffie–Hellman computation
a: the private half of Alice's current ratchet key pair (a1, a2 in the diagram)
B: Bob's current ratchet public key (B0, B1, B2 in the diagram)
In words: every new DH result is stirred into the root key, which then hands out a fresh chain key; an attacker who does not know the new DH result cannot follow the step.
```

An attacker who stole the state at one point, but is not actively intercepting, does not know the private half of the next fresh ratchet key. Security recovers once fresh DH contributions unknown to the attacker are mixed in and delivered. The exact moment of recovery depends on whose state was stolen and which messages arrive; it is not an unconditional one-round-trip promise. That is **post-compromise security**, also called break-in recovery.

> [!analogy] Real-world analogy: Changing the locks after a break-in
> A burglar copied your house key. Changing the locks does not undo what they already saw, but once the new locks are in and the burglar no longer has access, their copied key is useless.
>
> **How it maps:** The copied key is stolen ratchet state. Each DH ratchet step is a lock change: both sides mix a fresh Diffie–Hellman secret, which the attacker could not compute, into the root key, so later chains are out of the attacker's reach.
>
> **Where it stops:** You change your locks once, deliberately. The DH ratchet changes them automatically, every time the conversation turns round. And it works only if the burglar is truly out: malware still on the phone sees each new key as it is made, and an attacker who actively impersonates both sides with the stolen keys can keep up.

The combination is why it is called the *double* ratchet: a DH ratchet on receipt of a new peer ratchet public key, and a symmetric ratchet for each message in between.

### Out-of-order messages

Mobile networks reorder and delay messages. Each header carries the ratchet public key, the message number in the current chain, and the length of the previous chain. A receiver can skip ahead, derive and store the keys of skipped messages, and use them when the stragglers arrive. Implementations cap how many skipped keys they keep, both to bound memory and because stored keys weaken forward secrecy.

In October 2025 Signal announced a **post-quantum ratchet** (SPQR), whose output is mixed with the Double Ratchet's in what it calls a Triple Ratchet, to add post-quantum forward secrecy and post-compromise recovery under its assumptions. Recovery depends on successful delivery of the needed ratchet contributions.

## Key takeaways
- New peer ratchet keys trigger root-key updates for receiving and sending chains.
- Recovery requires attacker access to end and fresh unknown contributions to arrive.
- Skipped-key storage enables late delivery but retains decrypting capability and needs a bound.

## Further reading
- [X3DH specification — Signal](https://signal.org/docs/specifications/x3dh/)
- [Double Ratchet specification — Signal](https://signal.org/docs/specifications/doubleratchet/)
