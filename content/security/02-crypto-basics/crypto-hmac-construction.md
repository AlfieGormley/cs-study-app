---
id: crypto-hmac-construction
sourceLesson: crypto-macs
title: HMAC nesting and tag guessing budgets
level: intermediate
minutes: 4
summary: HMAC applies different inner and outer key-derived prefixes to defeat classic length extension.
---

## HMAC

**HMAC** (RFC 2104, 1997) wraps the hash twice with two derived keys:

```formula
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

RFC 2104 just fixes the two constants without explaining the choice. They provide distinct inner and outer prefixes. This description does not claim that distinct constants alone prove HMAC secure: the proof also needs precise assumptions about the underlying hash construction. The fixed padding bytes differ in four of their eight bit positions:

```formula
0x36 ⊕ 0x5c = 0x6a
where
⊕: bitwise exclusive or
0x36, 0x5c: the specified inner and outer padding bytes, in hexadecimal
0x6a: their XOR, binary 01101010, which has four set bits
In words: applying the same key byte to these two masks leaves four differing bits between the derived prefix bytes.
```

For example, HMAC-SHA256 with key `key` and message `The quick brown fox jumps over the lazy dog` pads the 3-byte key with 61 zero bytes, hashes 64 + 43 bytes on the inside and 64 + 32 bytes on the outside, and gives `f7bc83f4…2d1a3cd8`.

The inner hash processes the message. The outer hash then hashes that result under a different key-derived prefix. An attacker who extends the inner hash still can't produce the outer one, so length extension is defeated.

A collision attack on the unkeyed hash does not automatically forge HMAC. RFC 2104 discusses why HMAC's requirements differ from ordinary collision resistance. Use **HMAC-SHA256** for new work.

> [!note] Content gap: formal HMAC proof
> The full proof paper could not be retrieved reliably during this review (official/archive retrieval failed). Its exact reduction assumptions and bounds are omitted rather than compressed into an unverified one-line theorem.

Some details worth knowing:

- Keys longer than the block size (64 bytes for SHA-256) are first hashed. A uniformly random 32-byte key is an appropriate HMAC-SHA256 choice.
- Tags can be truncated: 128 bits retains 16 bytes from HMAC-SHA256. Choose the length from the protocol, forgery budget and verification limits; 64 bits is not a universal safe minimum.
- Use a specified keyed construction. BLAKE2 has a built-in key parameter, and KMAC is standardised in NIST SP 800-185. Absence of length extension alone does not prove an arbitrary keyed hash construction is a secure MAC.

Why tag length matters: against an ideal MAC, an attacker without the key can only guess, and each guess has the same tiny chance of being right:

```formula
p_forge ≤ q / 2^L
p_forge ≤ 2^20 / 2^64 = 2^−44
where
p_forge: the probability that at least one forged message is accepted
q: the number of forgery attempts the verifier checks under one key; here 2^20, about a million
L: the tag length in bits; here 64, a truncated tag
≤: is at most; this is an upper bound
In words: each extra tag bit halves the attacker's odds, so the safe length depends on how many guesses the verifier will ever check.
```

With a full 128-bit tag the same million guesses give at most 2^−108. A 64-bit tag gives about 5.7 × 10^−14 here, but a system that lets attackers make 2^40 attempts shrinks that margin to 2^−24, which is why the forgery budget, not a fixed minimum, decides the length.

## Key takeaways
- HMAC applies different inner and outer key-derived prefixes to defeat classic length extension.
- Choose a tag length from the protocol and total forgery budget.

## Further reading
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
- [Python hmac API](https://docs.python.org/3/library/hmac.html)
