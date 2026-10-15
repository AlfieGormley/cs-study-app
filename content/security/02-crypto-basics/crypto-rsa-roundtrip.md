---
id: crypto-rsa-roundtrip
sourceLesson: crypto-asymmetric
title: Trace RSA encryption and why it decrypts
level: intermediate
minutes: 5
summary: RSA exponentiation recovers every valid message representative under the generated key.
---

Use the toy public modulus 3233, public exponent 17 and private exponent 2753. A plaintext representative must be a nonnegative integer smaller than the modulus.

### 2. Encryption

To encrypt a message, first encode it as a whole number smaller than the modulus, then raise it to the public exponent and keep the remainder:

```formula
0 ≤ m < n
c = m^e mod n
c = 65^17 mod 3233 = 2790
where
m: the message, encoded as a whole number; here 65 (the ASCII code for the letter A)
n: the public modulus, 3233
e: the public exponent, 17
c: the ciphertext, a whole number from 0 to n − 1
m^e: e copies of m multiplied together
mod: "modulo": x mod n is the remainder left after dividing x by n
≤: is less than or equal to
<: is less than
In words: raise the message to the power e, divide by n and keep the remainder; that remainder is the ciphertext, and anyone with the public key can compute it.
```

### 3. Decryption

Raise the ciphertext to the private exponent instead:

```formula
m = c^d mod n
m = 2790^2753 mod 3233 = 65
where
c: the ciphertext, 2790
d: the private exponent, 2753, known only to the key owner
n: the modulus, 3233
m: the recovered message
c^d: d copies of c multiplied together (computed step by step with remainders, never as one giant number)
mod: "modulo": x mod n is the remainder left after dividing x by n
In words: applying the private exponent recovers the message: raising 2790 to the power 2753 and keeping the remainder after dividing by 3233 gives back 65. The tiny toy key itself offers no secrecy.
```

We get the original message back.

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

Python's three-argument `pow` performs modular exponentiation without constructing the huge unreduced power. It is an arithmetic teaching tool, not a constant-time RSA implementation.

> [!note] Content gap: timings
> No reproducible benchmark supports the former multiplication and exponentiation timings or fixed CRT speed-up, so those figures are omitted.

 `pow(e, -1, phi)` (Python 3.8+) computes the modular inverse.

### Why it works

Decryption undoes encryption because of how d was chosen. **Euler's theorem** supplies the key step:

```formula
ed = 1 + kφ(n)
c^d ≡ (m^e)^d = m^(ed) (mod n)
c^d ≡ m^(1 + kφ(n)) (mod n)
c^d ≡ m(m^φ(n))^k (mod n)
m^φ(n) ≡ 1 (mod n) if gcd(m, n) = 1
c^d ≡ m × 1^k = m (mod n)
where
e, d: the public and private exponents
k: some whole number; e × d ≡ 1 (mod φ(n)) means e × d is a multiple of φ(n) plus one (in the toy key 46801 = 1 + 15 × 3120, so k = 15)
φ: Euler's totient function; φ(n) = (p − 1) × (q − 1) for an RSA modulus
n: the modulus
m: the message, a whole number from 0 to n − 1
c: the ciphertext, m^e mod n
gcd: greatest common divisor; gcd(m, n) = 1 means m and n share no factor
mod: "modulo": arithmetic on remainders after dividing by n
≡: "is congruent to": both sides leave the same remainder after dividing by n
In words: e × d is one more than a multiple of φ(n), and for m coprime to n, Euler's theorem says any power of m whose exponent is a multiple of φ(n) is congruent to 1, so all that survives is m itself.
```

Euler's theorem requires the message and modulus to be coprime. It does not give remainder 1 for messages sharing a factor with the modulus. RSA decryption still works for those representatives: prove that decrypting the encrypted representative recovers the same remainder separately modulo each prime (zero is immediate; nonzero uses Fermat), then combine by the Chinese Remainder Theorem.

### Why it's secure

An attacker sees the public key, 3233 and 17. Factoring the modulus is sufficient to derive a valid private exponent:

```formula
n = 3233 = 61 × 53
φ(n) = 60 × 52 = 3120
d = e^(−1) mod φ(n)
d = 17^(−1) mod 3120 = 2753
where
n: the public modulus
φ: Euler's totient function, computable once the primes are known: φ(n) = (p − 1) × (q − 1)
e: the public exponent, 17
d: the private exponent
e^(−1) mod φ(n): the modular inverse of e: the number that multiplied by e leaves remainder 1 after dividing by φ(n)
mod: "modulo": arithmetic on remainders after dividing by φ(n)
In words: once the modulus is split into its primes, the attacker repeats the owner's key generation and gets the same private exponent.
```

It is not proved that every way of inverting RSA must factor `n`. Factoring the toy modulus 3233 is trivial; properly generated 2,048-bit moduli resist known practical classical factoring methods. A 2,048-bit integer has 617 decimal digits.

## Key takeaways
- RSA exponentiation recovers every valid message representative under the generated key.
- Euler’s theorem handles coprime messages; prime-wise reasoning covers the remaining representatives.

## Further reading
- [RFC 8017: RSA and OAEP](https://www.rfc-editor.org/rfc/rfc8017)
- [Python cryptography: RSA API](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/)
