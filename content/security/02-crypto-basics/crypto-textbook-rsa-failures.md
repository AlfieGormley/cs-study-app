---
id: crypto-textbook-rsa-failures
sourceLesson: crypto-asymmetric
title: Determinism and malleability in textbook RSA
level: intermediate
minutes: 3
summary: Textbook RSA leaks guesses, permits multiplicative changes and can expose small cubes.
---

The toy key has public modulus 3233 and exponent 17, with private exponent 2753. Its encryption of message representative 65 is 2790; the following attacks need only public information.

## Textbook RSA is not secure

What we just did is **textbook RSA**, and you must never use it directly. It has serious problems:

- **It is deterministic.** Encrypting 65 always gives 2790. An attacker who suspects the message is "yes" or "no" encrypts both with your public key and compares.
- **It is malleable.** Multiply the ciphertext by the encryption of 2 (which anyone can compute with the public key) and the plaintext doubles. In our example, 65 becomes 130. An attacker can change your message in a predictable way without decrypting it.
- **Small messages leak.** With a public exponent of 3 and a message whose cube is smaller than the modulus, no wrap-around happens at all. The attacker takes an ordinary cube root of the ciphertext and reads the message.

The malleability, worked through with the toy key:

```formula
c′ = (c × 2^e) mod n
c′^d ≡ m^(ed) × 2^(ed) (mod n)
c′^d ≡ m × 2 (mod n)
c′ = (2790 × 2^17) mod 3233 = 3017
3017^2753 mod 3233 = 130
where
c: the original ciphertext, 2790 (the encryption of 65)
c′: the attacker's altered ciphertext
e, d: the public and private exponents, 17 and 2753
n: the modulus, 3233
m: the original message, 65
mod: "modulo": arithmetic on remainders after dividing by n
≡: "is congruent to": both sides leave the same remainder after dividing by n
In words: multiplying ciphertexts multiplies the hidden plaintexts, so the attacker doubles the message without ever seeing it.
```

The small-message leak:

```formula
c = m^3 mod n = m^3  when m^3 < n
m = ∛(c)
c = 125  gives  m = ∛(125) = 5
where
m: the message as a whole number, for example a PIN
n: the modulus, about 2^2048 for a 2,048-bit key
c: the ciphertext
m^3: three copies of m multiplied together (the public exponent here is 3)
∛: the ordinary cube root: ∛(c) is the number whose cube is c
mod: "modulo": the remainder after dividing by n
<: is less than
In words: if the cube never reaches the modulus there is no remainder to hide anything, so the ciphertext is just the cube of the message and an ordinary cube root undoes it.
```

## Key takeaways
- Textbook RSA leaks guesses, permits multiplicative changes and can expose small cubes.
- A trapdoor arithmetic operation alone is not a secure encryption scheme.

## Further reading
- [RFC 8017: RSA and OAEP](https://www.rfc-editor.org/rfc/rfc8017)
- [Python cryptography: RSA API](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/)
