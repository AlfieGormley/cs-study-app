---
id: crypto-dh-agreement
sourceLesson: crypto-key-exchange
title: Agree a toy secret over a public channel
level: advanced
minutes: 4
summary: Each DH participant combines the other public value with its own secret exponent.
---

Alice and Bob have never met. Every byte they send crosses a network Eve can read. Can they end up with a DH shared secret key that Eve doesn't know?

It sounds impossible: anything they say, Eve hears. In 1976 Whitfield Diffie and Martin Hellman published a way to do it anyway. **Diffie–Hellman (DH) key exchange** and its elliptic-curve variants are important components of protocols including TLS, SSH, the Signal Protocol, WireGuard and IPsec. Protocol modes vary; some use pre-shared keys or hybrid post-quantum exchange.

## The paint analogy

```
Alice           public          Bob
secret: red     yellow       secret: blue

red+yellow  ---orange--->
            <---green---  blue+yellow

orange + blue: brown
green + red: brown
```

1. They publicly agree a common colour, yellow.
2. Each mixes in a secret colour and sends the mixture.
3. Each adds their own secret to the other's mixture. Both end up with the same brown.

Eve sees yellow, orange and green. The analogy imagines unmixing to be hard; it is not a proof about paint or cryptography. In DH, mixing is modular exponentiation and unmixing is the **discrete logarithm problem**.

## Diffie–Hellman with small numbers

The public parameters are a prime and a **DH generator**. Each side also picks a secret exponent, sends one public value, and combines the other side's value with its own secret:

```formula
A = g^a mod p
B = g^b mod p
s = B^a mod p = A^b mod p
where
p: the public prime modulus; here 23 (real finite-field groups use 2,048 bits or more)
g: the public generator, here 5
a: Alice's secret exponent, here 6; never sent
b: Bob's secret exponent, here 15; never sent
A: Alice's public value, sent in the clear
B: Bob's public value, sent in the clear
s: the DH shared secret both of them compute
g^a: a copies of g multiplied together
mod: "modulo": x mod p is the remainder left after dividing x by p
In words: each side raises the generator to its secret and publishes the result, then raises the other side's result to its own secret; both end up with the same number.
```

1. Alice picks secret exponent 6 and sends her public value.
2. Bob picks secret exponent 15 and sends his public value.
3. Each computes the shared value from the received value and their own exponent.

Step by step, working with remainders so the numbers stay small:

```formula
5^2 = 25 ≡ 2 (mod 23)
5^4 ≡ 2^2 = 4 (mod 23)
5^6 = 5^4 × 5^2 ≡ 4 × 2 = 8 (mod 23)
A = 8
B = 5^15 mod 23 = 19
s_Alice = 19^6 mod 23 = 2
s_Bob = 8^15 mod 23 = 2
where
A, B: the public values Alice and Bob send
s_Alice, s_Bob: the secret each of them computes
mod: "modulo": x mod 23 is the remainder left after dividing x by 23
≡: "is congruent to": both sides leave the same remainder after dividing by 23
In words: 5^6 is 15625, but by reducing after every multiplication Alice only ever handles small numbers; both sides finish with 2.
```

Both get shared value 2. Checked in Python:

```python
p, g = 23, 5          # public
a, b = 6, 15          # private

# Publish powers, keeping exponents secret.
A = pow(g, a, p)      # Alice sends 8
B = pow(g, b, p)      # Bob sends 19

# Combine the peer value with our secret.
print(pow(B, a, p))   # Alice: 2
print(pow(A, b, p))   # Bob:   2
```

## Key takeaways
- Each DH participant combines the other public value with its own secret exponent.
- The toy exchange reaches the same shared value but does not authenticate either peer.

## Further reading
- [Diffie and Hellman: New Directions in Cryptography](https://ee.stanford.edu/~hellman/publications/24.pdf)
- [RFC 7919: vetted finite-field groups](https://www.rfc-editor.org/rfc/rfc7919)
