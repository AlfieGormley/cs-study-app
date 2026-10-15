---
id: pki-mistakes-pq-quantum-effects
title: What Shor and Grover change
level: advanced
minutes: 2
sourceLesson: pki-mistakes-pq
summary: Shor targets factoring and discrete logarithms, including classical RSA and elliptic-curve schemes.
---

Cryptographic security depends on the complete construction and its implementation, including key generation, message authentication and correct nonce handling.

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

```formula
W ≈ √(N) = √(2^k) = 2^{k/2}
W_128 ≈ 2^{128/2} = 2^{64}
W_256 ≈ 2^{256/2} = 2^{128}
where
W: the number of Grover steps (idealised quantum evaluations of the cipher) to find a key
N: the number of possible keys, 2^k
k: the key length in bits
√: square root
≈: approximately equal to (constant factors are ignored)
W_128: the idealised Grover work for AES-128
W_256: the idealised Grover work for AES-256
In words: Grover halves the key length in bits, so AES-128 drops to about 64-bit strength in theory and AES-256 keeps about 128-bit strength, which remains far out of reach.
```

These are idealised counts. Grover's steps must run one after another on a fault-tolerant machine, and splitting the search across many machines saves far less than it does classically, so real costs are much higher.

## Key takeaways
- Shor targets factoring and discrete logarithms, including classical RSA and elliptic-curve schemes.
- Grover gives an idealised square-root key-search improvement with substantial implementation costs.
- Symmetric-key search and hash collision attacks are different security questions.

## Further reading
- [Cryptographic storage guidance — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [NIST post-quantum project](https://csrc.nist.gov/projects/post-quantum-cryptography)
