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

The malleability comes from one property of RSA arithmetic: multiplying two ciphertexts gives the ciphertext of the product of their messages, because raising a product to the public exponent is the same as raising each factor and multiplying. Anyone can encrypt a chosen factor with the public key, so anyone can multiply a hidden message by it. The algebra is in the card if you want it.

```formula reference
c′ = (c × s^e) mod n
(c′)^d mod n = (m × s) mod n
where
c: the original ciphertext of the hidden message m
m: the hidden message, as a whole number below n
s: any factor the attacker chooses, for example 2
c′: the attacker's altered ciphertext
e, d: the public and private exponents
n: the public modulus
mod: "modulo": the remainder after dividing by n
In words: multiplying a textbook RSA ciphertext by the public-key encryption of a chosen factor makes it decrypt to the original message times that factor, without the attacker ever learning the message or the key.
```

With the toy key, multiplying 2790 by the encryption of 2 gives a ciphertext that decrypts to 130, twice the original 65.

The small-message leak needs no key either. With public exponent 3 and a 2,048-bit modulus, any message below about 2^682 cubes to less than the modulus, so the remainder step never happens: the ciphertext is just the ordinary cube. If the ciphertext is 125, the message is 5, found with an ordinary cube root.

All three problems come from using the raw arithmetic directly. Real RSA encryption first applies a randomised encoding (OAEP, next unit), which makes encryption non-deterministic, destroys the useful multiplicative structure and pads short messages up to nearly the size of the modulus.

## Key takeaways
- Textbook RSA leaks guesses, permits multiplicative changes and can expose small cubes.
- A trapdoor arithmetic operation alone is not a secure encryption scheme.

## Further reading
- [RFC 8017: RSA and OAEP](https://www.rfc-editor.org/rfc/rfc8017)
- [Python cryptography: RSA API](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/)
