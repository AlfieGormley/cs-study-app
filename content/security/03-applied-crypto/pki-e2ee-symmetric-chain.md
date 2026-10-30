---
id: pki-e2ee-symmetric-chain
title: One-way message-key chains
level: advanced
minutes: 2
sourceLesson: pki-e2ee
summary: Separate HMAC labels derive a message key and the next chain key.
---

X3DH gives Alice and Bob one shared secret at the start of a conversation. If every message were encrypted under that one key, stealing it once would expose the whole history. The Double Ratchet keeps changing the key instead.

## The Double Ratchet

The **Double Ratchet** updates the keys continuously, with two interlocking mechanisms. This unit covers the first.

### The symmetric ratchet: a key per message

Each direction has a **chain key**. Every message turns the chain once with a KDF, producing a fresh **message key** and the next chain key, and the old chain key is deleted. Signal's specification recommends HMAC with two different one-byte inputs:

```formula essential
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

Each message key encrypts one message and is then deleted. Because HMAC cannot be run backwards, a thief who steals today's chain key cannot compute yesterday's message keys or chain keys. That is per-message forward secrecy.

> [!analogy] Real-world analogy: A ratchet spanner
> A ratchet spanner turns a bolt in one direction only; the mechanism clicks forward and will not turn back.
>
> **How it maps:** Each message turns the chain forward one click: the current chain key produces this message's key and the next chain key, and the old chain key is deleted. Like the spanner, the chain moves only forwards, so the current position does not reveal earlier ones.
>
> **Where it stops:** A spanner can be taken off and turned back by hand. A KDF chain cannot be reversed at all, because going back would mean inverting HMAC. But anyone who copies the current position can keep clicking forwards, which is exactly the weakness below.

What it does not give is healing: from the current chain key, the thief can compute every *future* key in this chain. The next unit adds the second ratchet to fix that.

## Key takeaways
- Separate HMAC labels derive a message key and the next chain key.
- Deleting earlier chain and message keys protects old ciphertext from current chain-key theft.
- A stolen current chain key still reveals later keys in that same chain.

## Further reading
- [X3DH specification — Signal](https://signal.org/docs/specifications/x3dh/)
- [Double Ratchet specification — Signal](https://signal.org/docs/specifications/doubleratchet/)
