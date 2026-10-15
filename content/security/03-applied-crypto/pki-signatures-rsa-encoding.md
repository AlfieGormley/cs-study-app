---
id: pki-signatures-rsa-encoding
title: Why RSA signatures need encoding
level: basic
minutes: 3
sourceLesson: pki-signatures
summary: Raw-message RSA permits signature-first forgery and multiplicative manipulation.
---

A signature verifier checks a message and signature against a trusted public key. The preceding units separated that verification authority from private-key signing authority.

### Why textbook RSA signatures are broken

Raw RSA (the preceding unit’s toy private exponentiation, with no padding) has fatal algebraic structure:

- **Raw-message forgery.** If any number below the modulus counts as a message, an attacker can pick the signature first and compute, from the public key alone, which message it verifies for (first formula below). If the scheme instead hashes an external message first, this does not by itself find a message with that hash; do not confuse those two models. Neither observation justifies inventing a signature encoding.
- **Multiplication.** Multiplying two valid signatures gives a valid signature on the product of their messages (second formula below).

The forgery runs verification backwards:

```formula
m = s^e mod n
m = 5^{17} mod 3233 = 3086
where
m: the forged message, a number below n
s: the forged signature: any number the attacker likes; here 5
e: the public exponent; 17 in the toy key
n: the public modulus; 3233 in the toy key
mod: modulo: the remainder after dividing by n
In words: pick the signature, then compute the message it signs; the pair (3086, 5) passes verification although the key owner never signed 3086.
```

The multiplication property follows from the rules of powers:

```formula
sig(x) = x^d mod n
a^d × b^d = (a × b)^d
(sig(a) sig(b)) mod n = sig(a × b)
1027 × 1857 mod 3233 = 2902 = sig(6)
where
sig: textbook RSA signing with the private exponent
x: a raw message representative; signing reduces the exponentiation modulo n
a: a first message the owner signed; here 2, whose signature is 1027
b: a second signed message; here 3, whose signature is 1857
d: the private exponent; 2753 in the toy key
n: the public modulus; 3233 in the toy key
mod: modulo: the remainder after dividing by n
In words: two signatures multiplied together are a signature on the two messages multiplied together, so an attacker holding the signatures on 2 and 3 gets the signature on 6 (2902) without the private key.
```

The forged message 3086 is meaningless, but EUF-CMA counts any new valid pair as a break, and the multiplication trick can produce chosen values.

Real RSA therefore **pads** the hash into a structured, full-width number first:

- **PKCS#1 v1.5** padding: deterministic and used in existing protocols. Secure for signatures if verified strictly, but sloppy parsers have led to forgeries such as Bleichenbacher's 2006 attack on keys with public exponent 3.
- **RSA-PSS**: randomised padding with a security proof. TLS 1.3 requires PSS when RSA signs the handshake.

## Key takeaways
- Raw-message RSA permits signature-first forgery and multiplicative manipulation.
- An attack on raw message representatives is distinct from finding a preimage for an external hash.
- Use a specified scheme: TLS 1.3 requires RSA-PSS for RSA CertificateVerify signatures.

## Further reading
- [RSA signature schemes — RFC 8017](https://www.rfc-editor.org/rfc/rfc8017)
- [EdDSA — RFC 8032](https://www.rfc-editor.org/rfc/rfc8032)
- [Deterministic ECDSA — RFC 6979](https://www.rfc-editor.org/rfc/rfc6979)
