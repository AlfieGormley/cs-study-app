---
id: pki-signatures-rsa-encoding
title: Why RSA signatures need encoding
level: basic
minutes: 3
sourceLesson: pki-signatures
summary: Raw-message RSA permits signature-first forgery and multiplicative manipulation.
---

The previous unit's toy RSA arithmetic verifies correctly, but used on its own it is not a secure signature scheme. This unit shows the two structural weaknesses and the encodings that remove them.

## Why textbook RSA signatures are broken

Raw RSA (the preceding unit's private exponentiation, with no padding) has fatal algebraic structure:

- **Raw-message forgery.** If any number below the modulus counts as a message, an attacker can pick the signature first and compute, from the public key alone, which message it verifies for. If the scheme instead hashes an external message first, this does not by itself find a message with that hash; do not confuse those two models. Neither observation justifies inventing a signature encoding.
- **Multiplication.** Multiplying two valid signatures gives a valid signature on the product of their messages.

The forgery simply runs verification backwards: choose any number as the "signature", raise it to the public exponent, and the result is a message that the pair verifies for. With the toy key (modulus 3233, public exponent 17), the attacker-chosen signature 5 verifies for the message 3086, although the key owner never signed 3086.

```formula reference
m = s^e mod n
where
m: the forged message, a number below n
s: the forged signature: any number the attacker likes
e: the public exponent
n: the public modulus
mod: modulo: the remainder after dividing by n
In words: an attacker can choose any signature value and compute, using only the public key, the raw message it verifies for, so the pair passes verification although the owner never signed it.
```

The multiplication property is the one that makes chosen values possible, and it follows from the ordinary rule for powers:

```formula essential
sig(x) = x^d mod n
(sig(a) sig(b)) mod n = sig(ab)
where
sig: textbook RSA signing with the private exponent, with no padding
x: a raw message representative, a number below n
a: a first message the owner signed
b: a second message the owner signed
d: the private exponent, unknown to the attacker
n: the public modulus
mod: modulo: the remainder after dividing by n
In words: two raw signatures multiplied together (and reduced modulo n) are a valid signature on the two messages multiplied together, so an attacker who holds signatures can combine them into new ones without the private key.
```

With the toy key, an attacker holding the owner's raw signatures on 2 and 3 obtains a valid signature on 6. A forged message such as 3086 may be meaningless, but the security goal (EUF-CMA) counts any new valid pair as a break, and multiplication can produce values the attacker chose.

## Encoding fixes the structure

Real RSA therefore **pads** the hash into a structured, full-width number first, so the product of two encodings is not the encoding of anything:

- **PKCS#1 v1.5** padding: deterministic and used in existing protocols. Secure for signatures if verified strictly, but sloppy parsers have led to forgeries such as Bleichenbacher's 2006 attack on keys with public exponent 3.
- **RSA-PSS**: randomised padding with a security proof. TLS 1.3 requires PSS when RSA signs the handshake (CertificateVerify); PKCS#1 v1.5 is still allowed for the signatures inside certificates.

The practical rule is to call a library's complete signature scheme (for example RSA-PSS with SHA-256) and never feed raw numbers to an RSA "sign" primitive.

## Key takeaways
- Raw-message RSA permits signature-first forgery and multiplicative manipulation.
- An attack on raw message representatives is distinct from finding a preimage for an external hash.
- Use a specified scheme: TLS 1.3 requires RSA-PSS for RSA CertificateVerify signatures.

## Further reading
- [RSA signature schemes — RFC 8017](https://www.rfc-editor.org/rfc/rfc8017)
- [Probabilistic signature scheme — Wikipedia](https://en.wikipedia.org/wiki/Probabilistic_signature_scheme)
