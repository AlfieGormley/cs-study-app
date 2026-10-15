---
id: pki-e2ee-symmetric-chain
title: One-way message-key chains
level: advanced
minutes: 2
sourceLesson: pki-e2ee
summary: Separate HMAC labels derive a message key and the next chain key.
---

End-to-end encryption keeps message-content keys at the communicating endpoints. Signal’s protocol family uses uploaded prekeys to start sessions and ratcheting keys to protect ongoing conversations.

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
    # Label 1 makes this message’s key.
    mk = hmac.new(ck, b"\x01",
                  hashlib.sha256).digest()
    # Label 2 advances the secret chain.
    nxt = hmac.new(ck, b"\x02",
                   hashlib.sha256).digest()
    return nxt, mk

ck = bytes(32)  # really: from the root KDF
for n in range(3):
    ck, mk = step(ck)
    # Show an index and 8-byte key prefix.
    print(n, mk.hex()[:16])
    # encrypt message n with mk,
    # then forget mk
```

This prints three unrelated-looking keys: `3d7afb663124ecbf`, `e43cd1fae55cf944`, `7718295d45e4164b` (first 8 bytes of each). HMAC is one-way, so a thief who steals today's chain key cannot run it backwards to yesterday's message keys. That is per-message forward secrecy.

What it does not give is recovery: from the current chain key, the thief can compute every *future* key in this chain.

## Key takeaways
- Separate HMAC labels derive a message key and the next chain key.
- Deleting earlier chain and message keys protects old ciphertext from current chain-key theft.
- A stolen current chain key still reveals later keys in that same chain.

## Further reading
- [X3DH specification — Signal](https://signal.org/docs/specifications/x3dh/)
- [Double Ratchet specification — Signal](https://signal.org/docs/specifications/doubleratchet/)
