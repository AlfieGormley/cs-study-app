---
id: crypto-hkdf-purpose-labels
sourceLesson: crypto-passwords-kdfs
title: Extract and expand keys with HKDF
level: advanced
minutes: 4
summary: HKDF derives purpose-specific keys from suitable high-entropy input; it does not harden passwords.
---

## Key derivation with HKDF

You often have one strong secret but need several keys. A DH-based handshake can establish shared secret material while needing separate traffic keys and IVs for each direction. TLS 1.3 also has PSK and hybrid profiles; its complete key schedule follows the chosen profile. Re-using one key for multiple purposes is dangerous, and raw DH output isn't uniformly random anyway.

**HKDF** (HMAC-based KDF, RFC 5869) solves this in two steps, Extract and Expand, described below. The exact HMAC chain is in the reference card if you want it.

```formula reference
PRK = HMAC(S, IKM)
T(0) = ε
T(i) = HMAC(PRK, T(i − 1) ‖ ctx ‖ i)
OKM = trunc_L(T(1) ‖ T(2) ‖ … ‖ T(N))
N = ⌈L / H_len⌉ ≤ 255
L ≤ 255 × 32 = 8160 bytes
where
PRK: the pseudorandom key produced by the Extract step, one hash length long
HMAC: HMAC with the chosen hash, here SHA-256; its first argument is the key
S: the optional HKDF salt: a normally non-secret salt; if absent, RFC 5869 uses one hash-output length of zero bytes
IKM: the input keying material: the strong secret you start from, such as a DH shared secret
T(i): the i-th output block of the Expand step, one hash length long
ε: the empty string, so T(1) starts from nothing
i: the block counter 1, 2, 3, …, written as a single byte
ctx: the context label (the `info` parameter), such as `b"client write key"`
OKM: the output keying material: the derived key or keys
trunc_L: keep only the first L bytes
L: the number of output bytes you ask for
N: the number of blocks needed
H_len: the hash output length in bytes: 32 for SHA-256
⌈ ⌉: ceiling: round up to the next whole number
‖: concatenation: joining byte strings end to end
≤: is at most
…: and so on, up to T(N)
bytes: the unit of data, 8 bits each
In words: Extract condenses the input secret into one fixed-length pseudorandom key; Expand then runs HMAC repeatedly under that key, mixing in the purpose label and a one-byte counter, and keeps as many output bytes as you asked for, up to 255 hash lengths.
```

1. **Extract** condenses the input secret into one fixed-length pseudorandom key, called the PRK. A suitable HKDF salt can strengthen extraction under the protocol’s assumptions.
2. **Expand** produces up to 255 hash lengths (8,160 bytes for SHA-256), because its block counter is a single byte. The `info` string binds each output to its purpose, such as `b"client write key"`, so unambiguously distinct purpose labels separate derived keys under HKDF’s assumptions. A KDF cannot manufacture entropy that was absent from its input.

For example, requesting 44 bytes (a 32-byte AES-256 key plus a 12-byte IV) with SHA-256 needs two output blocks and keeps the first 44 of their 64 bytes.

> [!analogy] Real-world analogy: Cutting labelled keys from one master
> A locksmith holds one master blank and cuts a separate key for each door from it, following a label on each order: "front door", "garage", "shed". The same blank and the same label always give the same key, a different label gives an unrelated-looking key, and holding the garage key tells you nothing useful about the front-door key.
>
> **How it maps:** The master blank is the input keying material (after Extract, the pseudorandom key), each label is HKDF's `info` string and each cut key is a derived output. Both sides of a connection follow the same orders with the same labels, so they cut matching keys without ever sending them.
>
> **Where it stops:** A physical key can be copied or decoded from another key; HKDF outputs are designed so that one derived key reveals no feasible information about another or about the master. And HKDF cannot strengthen a weak master: if the input is guessable, such as a password, every derived key is guessable too.

TLS 1.3, the Signal Protocol, WireGuard (via its Noise framework) and the Web Push standard all build their key schedules on HKDF. The earlier X25519 unit demonstrates one use.

> [!warning] HKDF is not a password hash
> HKDF is fast and assumes its input already has high entropy (a random key or a DH secret). It does not deliberately increase password-guessing cost. Actual attack throughput depends on derivation and candidate-verification work. Passwords need the deliberately slow functions below.

## Key takeaways
- HKDF derives purpose-specific keys from suitable high-entropy input; it does not harden passwords.
- Expand chains HMAC blocks and uses a one-byte counter, limiting output to 255 hash lengths.

## Further reading
- [RFC 5869: HKDF](https://www.rfc-editor.org/rfc/rfc5869)
- [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
