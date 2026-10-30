---
id: pki-mistakes-pq-quantum-effects
title: What Shor and Grover change
level: advanced
minutes: 2
sourceLesson: pki-mistakes-pq
summary: Shor targets factoring and discrete logarithms, including classical RSA and elliptic-curve schemes.
---

Everything so far has assumed the algorithms themselves are sound. A large quantum computer would break some of them outright, and only weaken others.

## Post-quantum: what breaks

A large, fault-tolerant quantum computer, which nobody has yet built, would change the picture for public-key cryptography:

| Algorithm | Quantum attack | Effect |
|---|---|---|
| RSA, DH, ECDH | Shor | Broken |
| ECDSA, Ed25519 | Shor | Broken |
| AES-128 | Grover | ~64-bit, in theory |
| AES-256 | Grover key search | Idealised ~two to the power 128 oracle queries; practical costs are higher |
| SHA-256 | Quantum search/collision algorithms | Preimage and collision security differ; do not assign one universal bit strength |

**Shor's algorithm** solves factoring and discrete logarithms in polynomial time, so the classical factoring/discrete-log public-key schemes discussed earlier are vulnerable. The post-quantum schemes below rely on different assumptions. **Grover's algorithm** only gives a square-root speed-up on brute-force search, and it parallelises badly, so symmetric crypto survives with large enough keys. Guidance such as the NSA's CNSA 2.0 suite calls for AES-256.

In idealised terms, Grover's algorithm needs about the square root of the number of possible keys, which halves the key length measured in bits: AES-128 would fall to about 64-bit strength in theory, while AES-256 keeps about 128-bit strength, which remains far out of reach.

These are idealised step counts that ignore constant factors. Grover's steps must run one after another on a fault-tolerant machine, and splitting the search across many machines saves far less than it does classically, so real costs are much higher.

## Key takeaways
- Shor targets factoring and discrete logarithms, including classical RSA and elliptic-curve schemes.
- Grover gives an idealised square-root key-search improvement with substantial implementation costs.
- Symmetric-key search and hash collision attacks are different security questions.

## Further reading
- [Shor's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Shor%27s_algorithm)
- [NIST post-quantum cryptography project](https://csrc.nist.gov/projects/post-quantum-cryptography)
