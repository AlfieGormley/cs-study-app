---
id: pki-e2ee
title: End-to-end encryption and the Signal protocol
level: advanced
minutes: 15
summary: What end-to-end encryption promises beyond TLS, how Signal's X3DH/PQXDH handshake works with an offline recipient, how the Double Ratchet gives forward secrecy and break-in recovery, and where E2EE still leaks (keys, groups, devices, metadata, backups).
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

- **IK_B**: his long-term **identity public key**; private keys stay on endpoints.
- **SPK_B**: a **signed prekey**, a medium-term DH key, signed with IK_B and replaced every week or month.
- **OPK_B**: a stack of **one-time prekeys**, each handed out once.

When Alice wants to talk, the server gives her Bob's bundle, including one OPK, which it then deletes. Alice checks the signature on SPK_B, generates a fresh **ephemeral key** EK_A, and computes four Diffie–Hellman values:

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
SPK_B: Bob's signed prekey pair, replaced every week or month
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

- **DH1 and DH2** each involve one party's identity key, binding the exchange to those identity keys. This provides **mutual authentication of keys**; establishing that those keys belong to the intended people requires authenticated key comparison or another trusted binding.
- **DH3 and DH4** involve Alice's ephemeral key, which she deletes afterwards. That gives **forward secrecy**: stealing both identity keys later does not reveal SK.
- **The one-time prekey**, with its private half deleted after successful use, prevents reusing that prekey to accept the initial exchange again and strengthens protection against later compromise of SPK_B. If the server has run out, X3DH works without DH4, with slightly weaker guarantees.

Alice sends her first message encrypted under a key derived from SK, together with IK_A, EK_A and which prekeys she used. When Bob comes online, he computes the same four values and decrypts. No round trip was needed.

> [!note] PQXDH
> Signal announced **PQXDH** in 2023: Bob's bundle adds signed post-quantum prekeys. The published specification uses a parameterised KEM and gives CRYSTALS-Kyber-1024 as an example. NIST's later ML-KEM standard derives from Kyber, but draft Kyber encodings and the final standard cannot be assumed interchangeable. Alice encapsulates to it and mixes the resulting secret into the KDF alongside the DH values. As with hybrid TLS, the hybrid is designed to retain secrecy if either component remains secure under the protocol's assumptions.

## The Double Ratchet

X3DH gives a shared secret once. The **Double Ratchet** then updates the keys continuously, with two interlocking mechanisms.

### The symmetric ratchet: a key per message

Each direction has a **chain key**. Every message turns the chain once with a KDF, producing a fresh **message key** and the next chain key, and the old chain key is deleted. Signal's specification recommends HMAC with two different one-byte inputs:

```formula
mk_i = HMAC(ck_i, 0x01)
ck_{i+1} = HMAC(ck_i, 0x02)
where
mk_i: the message key for message number i in this chain, 32 bytes; it encrypts that one message
ck_i: the chain key before message i, 32 bytes, used as the HMAC key
ck_{i+1}: the next chain key, which replaces ck_i
HMAC: hash-based message authentication code, here with SHA-256: a keyed hash whose output cannot be run backwards to find the key
0x01: the single byte 1, the constant input that labels "make a message key"
0x02: the single byte 2, the constant input that labels "make the next chain key"
In words: the same chain key is hashed with two different labels, giving one key to use now and one to carry forward; because HMAC is one-way, neither output reveals the chain key that made it.
```

In code:

```python
import hmac, hashlib

def step(ck):
    # one turn of the symmetric ratchet
    mk = hmac.new(ck, b"\x01",
                  hashlib.sha256).digest()
    nxt = hmac.new(ck, b"\x02",
                   hashlib.sha256).digest()
    return nxt, mk

ck = bytes(32)  # really: from the root KDF
for n in range(3):
    ck, mk = step(ck)
    print(n, mk.hex()[:16])
    # encrypt message n with mk,
    # then forget mk
```

This prints three unrelated-looking keys: `3d7afb663124ecbf`, `e43cd1fae55cf944`, `7718295d45e4164b` (first 8 bytes of each). HMAC is one-way, so a thief who steals today's chain key cannot run it backwards to yesterday's message keys. That is per-message forward secrecy.

What it does not give is recovery: from the current chain key, the thief can compute every *future* key in this chain.

### The DH ratchet: healing after compromise

So every message also carries the sender's current **ratchet public key**. On receiving a new peer ratchet key, it first combines that key with its existing private ratchet key to derive the receiving chain, then generates a new local key pair and combines it with the peer key to derive the sending chain. The output is mixed into a **root key**, which produces brand-new chain keys:

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

```formula
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

The combination is why it is called the *double* ratchet: a DH ratchet on receipt of a new peer ratchet public key, and a symmetric ratchet for each message in between.

### Out-of-order messages

Mobile networks reorder and delay messages. Each header carries the ratchet public key, the message number in the current chain, and the length of the previous chain. A receiver can skip ahead, derive and store the keys of skipped messages, and use them when the stragglers arrive. Implementations cap how many skipped keys they keep, both to bound memory and because stored keys weaken forward secrecy.

In October 2025 Signal announced a **post-quantum ratchet** (SPQR), whose output is mixed with the Double Ratchet's in what it calls a Triple Ratchet, to add post-quantum forward secrecy and post-compromise recovery under its assumptions. Recovery depends on successful delivery of the needed ratchet contributions.

## Deniability

For the pairwise shared-key authentication illustrated here, a valid tag authenticates the message to a peer who knows they did not create it, assuming uncompromised keys. Either holder could compute the tag, so it alone is not transferable proof of authorship. This is narrower than a claim about all messaging transcripts, group-signature schemes or legal evidence.

> [!note] Content gap
> Legal conclusions about screenshots or deniability are omitted because no jurisdiction-specific legal review was performed.

## Who is Bob, really?

All of this protects Alice's conversation with the holder of IK_B. The server decides what IK_B is. A malicious or compelled server could hand Alice its own key and sit in the middle.

- **Safety numbers**: Signal and WhatsApp show a fingerprint derived from both identity keys. Compare it in person or scan a QR code, and a substituted key shows up as a mismatch.
- **Key-change warnings**: when a contact's identity key changes (new phone, or an attack), the app warns.
- **Key transparency**: auditable key directories can expose inconsistent key views when clients verify proofs and the design's monitoring/witness assumptions hold. WhatsApp described its deployment in 2023. Transparency does not by itself prove the real-world owner of a first-seen key or make all substitutions impossible.

## Groups and multiple devices

**Multiple devices**: devices need authenticated membership and protected sessions. Designs differ: Sesame supports per-user or per-device identity keys, and fan-out encrypts for relevant recipient devices. Adding a device need not change the account's identity fingerprint; device enrolment needs its own controls and visibility.

**Small groups**: pairwise sessions for every message would cost O(n) encryptions per message, where n is the number of group members (one for each other member's device session). **Sender Keys** (used by WhatsApp and Signal groups) give each sender a chain key, distributed once over pairwise sessions; messages are encrypted once and fanned out by the server. It has forward secrecy, but weaker post-compromise security: healing requires distributing new sender keys.

**Large groups**: **MLS** (Messaging Layer Security, RFC 9420, 2023) arranges members' keys in a tree (TreeKEM), so a balanced populated tree can refresh a path of O(log n) nodes. For a balanced tree:

```formula
L = ⌈log_2(N)⌉
L = ⌈log_2(10,000)⌉ = ⌈13.29⌉ = 14
where
L: the number of levels above a member's leaf in a balanced binary tree: how many path nodes one update refreshes
N: the number of members, one per leaf
log_2: logarithm base 2: the power 2 must be raised to (log_2(1,024) = 10)
⌈ ⌉: ceiling: round up to the next whole number
In words: each doubling of the group adds only one level, so 10,000 members need about 14 refreshed nodes instead of 9,999 pairwise messages.
```

Actual update size/work also depends on blank nodes, resolution sizes and members joining or leaving; the tree-depth example is not an unconditional total-cost bound.

## What E2EE does not protect

- **Endpoints.** Spyware like Pegasus reads messages on the phone after decryption. E2EE moves the target to the device.
- **Metadata.** The server still sees who talks to whom, when, from which IP and how often. Signal's **sealed sender** reduces explicit sender identity exposed to the delivery service. Timing, recipient addressing and network observations can still reveal metadata; it is not guaranteed anonymity.
- **Backups.** A chat history backed up to the cloud unencrypted is a copy outside E2EE. WhatsApp added optional end-to-end encrypted backups in 2021.
- **The other person.** A recipient can screenshot or forward anything.
- **Abuse reporting and moderation** have to work without the server seeing content, usually by having the reporting user send messages in themselves.

## Key takeaways
- E2EE means only endpoints hold the keys; the server relays ciphertext, unlike TLS where the server sees plaintext.
- X3DH uses uploaded prekeys and three or four DH computations; PQXDH adds a post-quantum KEM to agree a mutually authenticated, forward-secret key with an offline recipient.
- The symmetric ratchet gives every message its own key, so current chain-state theft does not recover erased older keys; retained plaintext and skipped keys are separate exposures.
- The DH ratchet mixes fresh DH outputs into the root key, supporting recovery after attacker access ends and fresh unknown contributions arrive.
- The server chooses which keys you receive; authenticated safety-number comparison and verified transparency mechanisms help detect substitution under their respective assumptions.
- Sender Keys and MLS scale E2EE to groups with different trade-offs; metadata, endpoints and backups remain outside its protection.

## Further reading
- [The X3DH Key Agreement Protocol — Signal](https://signal.org/docs/specifications/x3dh/)
- [The Double Ratchet Algorithm — Signal](https://signal.org/docs/specifications/doubleratchet/)
- [Quantum Resistance and the Signal Protocol — Signal blog](https://signal.org/blog/pqxdh/)
- [Signal Protocol and Post-Quantum Ratchets — Signal blog](https://signal.org/blog/spqr/)
- [Deploying key transparency at WhatsApp — Meta Engineering](https://engineering.fb.com/2023/04/13/security/whatsapp-key-transparency/)
- [RFC 9420: The Messaging Layer Security (MLS) Protocol](https://www.rfc-editor.org/rfc/rfc9420)
