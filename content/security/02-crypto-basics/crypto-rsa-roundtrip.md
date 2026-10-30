---
id: crypto-rsa-roundtrip
sourceLesson: crypto-asymmetric
title: Trace RSA encryption and why it decrypts
level: intermediate
minutes: 5
summary: RSA exponentiation recovers every valid message representative under the generated key.
---

Use the toy public modulus 3233, public exponent 17 and private exponent 2753. A plaintext representative must be a nonnegative integer smaller than the modulus.

### Encryption and decryption

To encrypt, encode the message as a whole number smaller than the modulus, raise it to the public exponent and keep the remainder after dividing by the modulus. To decrypt, do the same with the private exponent. These two relationships are the whole of textbook RSA:

```formula essential
c = m^e mod n
m = c^d mod n
where
m: the message, encoded as a whole number from 0 to n − 1; here 65 (the ASCII code for the letter A)
c: the ciphertext, a whole number from 0 to n − 1
e: the public exponent, 17
d: the private exponent, 2753, known only to the key owner
n: the public modulus, 3233
m^e: e copies of m multiplied together (computed step by step with remainders, never as one giant number)
mod: "modulo": x mod n is the remainder left after dividing x by n
In words: anyone with the public key can raise the message to the public exponent to encrypt it; only the key owner can raise the ciphertext to the private exponent and get the message back. With the toy key, 65 encrypts to 2790, and 2790 decrypts to 65.
```

Checked in Python:

```python
p, q = 61, 53
n = p * q              # 3233
phi = (p - 1) * (q - 1)  # 3120
e = 17
# Invert the public exponent modulo phi.
d = pow(e, -1, phi)    # 2753

m = 65
# Reductions avoid forming the full power.
c = pow(m, e, n)       # 2790
# Print ciphertext, then recovered message.
print(c, pow(c, d, n)) # 2790 65
```

Python's three-argument `pow` performs modular exponentiation without constructing the huge unreduced power. It is an arithmetic teaching tool, not a constant-time RSA implementation. `pow(e, -1, phi)` (Python 3.8+) computes the modular inverse.

### Why it works

Decryption undoes encryption because of how the private exponent was chosen: the two exponents multiply to one more than a multiple of the totient, and raising a message that shares no factor with the modulus to a multiple of the totient leaves remainder 1 (Euler's theorem). So encrypting and then decrypting is the same as raising the message to the power 1. With the toy key, 17 × 2753 = 46,801, which is 15 × 3120 + 1, and every one of the 3,233 possible messages comes back unchanged after encrypting and decrypting. [RFC 8017](https://www.rfc-editor.org/rfc/rfc8017) gives the full specification.

Euler's theorem needs the message and modulus to share no factor. RSA decryption still works for the rare messages that do: check the result separately modulo each prime and combine the two with the Chinese Remainder Theorem.

### Why it's secure

An attacker sees only the public key, 3233 and 17. Factoring the modulus into 61 and 53 would let them repeat the owner's key generation and compute 2753, so factoring is sufficient to break a key. It is not proved that every way of inverting RSA must factor the modulus. Factoring 3233 is trivial; properly generated 2,048-bit moduli (617 decimal digits) resist all known practical classical factoring methods.

## Key takeaways
- RSA exponentiation recovers every valid message representative under the generated key.
- Euler’s theorem handles coprime messages; prime-wise reasoning covers the remaining representatives.

## Further reading
- [RFC 8017: RSA and OAEP](https://www.rfc-editor.org/rfc/rfc8017)
- [Python cryptography: RSA API](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/)
