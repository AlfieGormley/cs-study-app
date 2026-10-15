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

For MD5, SHA-1, SHA-256 and SHA-512, the digest exposes the final chaining state. This does not apply equally to truncated variants such as SHA-384 and SHA-512/256. So anyone who sees the digest can carry on hashing from where it stopped. This is a **length-extension attack**. It doesn't break the hash's three properties, but it breaks naive constructions that hash a secret key followed by the message and use the result as an authentication code:

```formula
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
In words: because the digest is the whole internal state, an attacker holding t can keep hashing from where the server stopped and get a valid tag for an extended message, without knowing k.
```

The attacker only has to guess the length of k (trying a few values is cheap), and the forged message contains the padding bytes p in the middle, which many parsers ignore. The later HMAC unit shows how a specified keyed construction avoids it.

### Sponge (SHA-3)

**SHA-3** (Keccak, standardised in FIPS 202 in 2015) uses a different design called a **sponge construction**. It absorbs input into a large state and squeezes output from only part of it. Because the digest doesn't reveal the whole state, SHA-3 is not vulnerable to length extension. It provides a structurally different standardised alternative to SHA-2; its standardisation does not imply that SHA-2 has been broken.

## Key takeaways
- Full-state Merkle–Damgård digests permit classic length extension; truncated variants differ.
- SHA-3 hides part of its sponge state and avoids classic length extension.

## Further reading
- [NIST FIPS 180-4: secure hashes](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
- [NIST FIPS 202: SHA-3](https://csrc.nist.gov/pubs/fips/202/final)
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
