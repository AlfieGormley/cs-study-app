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

## The idea

Each side keeps one secret and publishes a "mixed" value made from a public starting point and that secret. Each side then mixes its own secret into the other side's published value. Both arrive at the same result, but an eavesdropper who saw only the published values cannot easily do the same.

> [!analogy] Real-world analogy: Mixing paint
> Alice and Bob publicly agree a common colour, yellow. Alice secretly picks red and Bob secretly picks blue. Each mixes their secret colour into the yellow and sends the mixture: Alice sends orange, Bob sends green. Each then adds their own secret colour to the mixture they received, and both end up with the same brown. Eve sees yellow, orange and green, but separating a mixture back into its colours is hard.
>
> **How it maps:** Yellow is the public parameters (prime and generator), the secret colours are the secret exponents, the sent mixtures are the public values and the brown is the shared secret. "Unmixing" corresponds to solving the discrete logarithm problem.
>
> **Where it stops:** Unmixing paint is just practically awkward; the cryptographic version rests on a precise hardness assumption in a well-chosen group. And the picture hides the biggest real-world weakness: nothing in it tells Alice that the green really came from Bob, which is why plain DH must be authenticated.

## Diffie–Hellman with small numbers

The public parameters are a prime and a **DH generator**. Each side also picks a secret exponent, sends one public value, and combines the other side's value with its own secret. These relationships are the whole protocol:

```formula essential
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

With the toy numbers, Alice's secret exponent is 6 and Bob's is 15. Alice sends 8 and Bob sends 19. Each combines the received value with their own secret exponent, and both get the shared value 2. Real implementations never compute the huge power first: they reduce after every multiplication, so the numbers stay no larger than the modulus. Checked in Python:

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

Eve sees the prime, the generator and both public values (23, 5, 8 and 19). The obvious way for her to get the shared value is to recover a secret exponent from its public value, the **discrete logarithm problem**. That is trivial at toy size but believed infeasible in a well-chosen large group; the next unit covers why.

## Key takeaways
- Each DH participant combines the other public value with its own secret exponent.
- The toy exchange reaches the same shared value but does not authenticate either peer.

## Further reading
- [Diffie and Hellman: New Directions in Cryptography](https://ee.stanford.edu/~hellman/publications/24.pdf)
- [RFC 7919: vetted finite-field groups](https://www.rfc-editor.org/rfc/rfc7919)
