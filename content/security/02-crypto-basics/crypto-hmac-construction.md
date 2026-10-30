---
id: crypto-hmac-construction
sourceLesson: crypto-macs
title: HMAC nesting and tag guessing budgets
level: intermediate
minutes: 4
summary: HMAC applies different inner and outer key-derived prefixes to defeat classic length extension.
---

## HMAC

**HMAC** (RFC 2104, 1997) wraps the hash twice, each time with a different version of the key. The inner hash processes the key-derived inner prefix and the message. The outer hash then hashes that inner result under a second key-derived prefix. An attacker who extends the inner hash still cannot produce the outer one, so length extension is defeated.

```formula reference
HMAC(K, m) = H((K′ ⊕ opad) ‖
             H((K′ ⊕ ipad) ‖ m))
where
HMAC(K, m): the tag for message m under key K
H: the underlying hash function, for example SHA-256
K: the secret key
K′: the key fitted to the hash's block size B: hashed first if it is longer than B, then padded with zero bytes up to B
B: the hash's block size: 64 bytes for SHA-256, 128 bytes for SHA-512
m: the message
ipad: the inner padding constant: the byte 0x36 repeated B times
opad: the outer padding constant: the byte 0x5c repeated B times
⊕: XOR (exclusive or): each output bit is 1 where the two inputs differ and 0 where they match
‖: concatenation: joining byte strings end to end
In words: hash the message under one version of the key, then hash that result again under a second, different version of the key.
```

RFC 2104 just fixes the two padding constants (bytes 0x36 and 0x5c, which differ in four of their eight bit positions) without explaining the choice. They provide distinct inner and outer prefixes. This description does not claim that distinct constants alone prove HMAC secure: the proof also needs precise assumptions about the underlying hash construction.

For example, HMAC-SHA256 with key `key` and message `The quick brown fox jumps over the lazy dog` pads the 3-byte key with 61 zero bytes, hashes 64 + 43 bytes on the inside and 64 + 32 bytes on the outside, and gives `f7bc83f4…2d1a3cd8`.

A collision attack on the unkeyed hash does not automatically forge HMAC. RFC 2104 discusses why HMAC's requirements differ from ordinary collision resistance. Use **HMAC-SHA256** for new work.

Some details worth knowing:

- Keys longer than the block size (64 bytes for SHA-256) are first hashed. A uniformly random 32-byte key is an appropriate HMAC-SHA256 choice.
- Tags can be truncated: 128 bits retains 16 bytes from HMAC-SHA256. Choose the length from the protocol, forgery budget and verification limits; 64 bits is not a universal safe minimum.
- Use a specified keyed construction. BLAKE2 has a built-in key parameter, and KMAC is standardised in NIST SP 800-185. Absence of length extension alone does not prove an arbitrary keyed hash construction is a secure MAC.

Why tag length matters: against an ideal MAC, an attacker without the key can only guess, and each guess has the same tiny chance of being right. Every extra tag bit halves that chance, and every verification attempt the system allows is another chance. So the safe length depends on how many guesses the verifier will ever check under one key, not on a fixed minimum. A full 128-bit or 256-bit tag leaves an enormous margin; a 32-bit tag on an endpoint with no rate limit and no expiry can fall to blind guessing: at a thousand guesses per second, trying every possible tag takes about seven weeks, and a hit comes after about half that on average.

```formula reference
p_forge ≤ q / 2^L
where
p_forge: the probability that at least one forged message is accepted
q: the number of forgery attempts the verifier checks under one key
L: the tag length in bits
≤: is at most; this is an upper bound
In words: the forgery chance is at most the number of attempts divided by the number of possible tags, so a million guesses against a 64-bit tag succeed with probability at most about 1 in 18 trillion, while against a 32-bit tag the same bound is about 1 in 4,300.
```

## Key takeaways
- HMAC applies different inner and outer key-derived prefixes to defeat classic length extension.
- Choose a tag length from the protocol and total forgery budget.

## Further reading
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
- [Python hmac API](https://docs.python.org/3/library/hmac.html)
