---
id: crypto-hash-constructions
sourceLesson: crypto-hashes
title: Chaining state, sponges and length extension
level: basic
minutes: 3
summary: Full-state Merkle–Damgård digests permit classic length extension; truncated variants differ.
---

## How the common hashes are built

### Merkle–Damgård (MD5, SHA-1, SHA-2)

Most older hashes split the padded message into blocks and feed them through a **compression function**, carrying a fixed-size internal state from one block to the next. A full-width digest exposes the final chaining state; truncated variants return only part of it.

```
IV -> [f] -> [f] -> [f] -> digest
       ^      ^      ^
       M1     M2     M3 (+ padding)
```

For MD5, SHA-1, SHA-256 and SHA-512, the digest exposes the final chaining state. This does not apply equally to truncated variants such as SHA-384 and SHA-512/256. So anyone who sees the digest can carry on hashing from where it stopped. This is a **length-extension attack**. It doesn't break the hash's three properties, but it breaks naive constructions that hash a secret key followed by the message and use the result as an authentication code. The server's tag is the hash's internal state after the key, the message and the hash's own padding. An attacker who sees it can load it as their starting state, hash some extra data of their choosing, and get a valid tag for a longer message: the original message, then that padding, then the extra data. They never learn the key. The card shows this symbolically.

```formula reference
t = H(k ‖ m)
t′ = H(k ‖ m ‖ p ‖ x)
where
H: a full-state Merkle–Damgård hash such as SHA-256
k: the secret key, which the attacker never learns
m: the message the server authenticated, for example `amount=10`
t: the tag the server sends, which is also the hash's final internal state
p: the padding the hash appended after k ‖ m; it depends only on their total length, which the attacker can guess
x: extra data the attacker chooses, for example `&amount=1000`
t′: a valid tag for the longer message m ‖ p ‖ x, computed by restarting the hash from state t
‖: concatenation: joining byte strings end to end
In words: because the digest is the whole internal state, an attacker holding one valid tag can keep hashing from where the server stopped and get a valid tag for the message followed by the hash's padding and their own extra data, without knowing the key.
```

The attacker only has to guess the length of the key (trying a few values is cheap), and the forged message contains the original padding bytes in the middle, which many parsers ignore. The later HMAC unit shows how a specified keyed construction avoids it.

> [!analogy] Real-world analogy: Continuing a till receipt from its printed total
> A shop's till prints the total so far after a list of items. Suppose the first few items are hidden, but the printed total is visible. Anyone can carry on from that total, add more items and print a valid-looking longer receipt, without ever seeing the hidden items.
>
> **How it maps:** The hidden items are the secret key, the listed items are the message, and the printed total is the digest, which for SHA-256 is the hash's whole internal state. Carrying on from the total is length extension: the attacker resumes hashing from the published state and appends their own data.
>
> **Where it stops:** A hash state is not a sum: you cannot subtract items or work backwards to the hidden ones, and the forged message must include the hash's padding bytes in the middle. A truncated or sponge-based hash prints only part of its state, like a receipt that hides part of the total, so it cannot be continued.

### Sponge (SHA-3)

**SHA-3** (Keccak, standardised in FIPS 202 in 2015) uses a different design called a **sponge construction**. It absorbs input into a large state and squeezes output from only part of it. Because the digest doesn't reveal the whole state, SHA-3 is not vulnerable to length extension. It provides a structurally different standardised alternative to SHA-2; its standardisation does not imply that SHA-2 has been broken.

## Key takeaways
- Full-state Merkle–Damgård digests permit classic length extension; truncated variants differ.
- SHA-3 hides part of its sponge state and avoids classic length extension.

## Further reading
- [NIST FIPS 180-4: secure hashes](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
- [NIST FIPS 202: SHA-3](https://csrc.nist.gov/pubs/fips/202/final)
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
