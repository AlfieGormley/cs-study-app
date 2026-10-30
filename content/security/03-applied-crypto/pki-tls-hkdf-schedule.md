---
id: pki-tls-hkdf-schedule
title: TLS key derivation and Finished
level: intermediate
minutes: 4
sourceLesson: pki-tls
summary: HKDF separates client/server and handshake/application secrets with specified labels and contexts.
---

One ECDH result has to become many keys: separate keys for each direction, for the handshake and for application data, plus secrets for resumption and exporters. TLS 1.3 derives all of them with HKDF, the extract-then-expand key derivation function from the crypto basics module.

## Job 3: from one secret to many keys with HKDF

The ECDH output is raw shared keying material, not a set of independently derived traffic keys. It goes through the **TLS 1.3 key schedule**, built entirely from HKDF:

```
PSK or 0 --Extract--> Early Secret
                          |
          derive salt     v
(EC)DHE --Extract--> Handshake Secret
                          |-> c hs traffic
                          |-> s hs traffic
          derive salt     v
0 ------- Extract--> Master Secret
                          |-> c ap traffic
                          |-> s ap traffic
                          |-> resumption
                          |-> exporter
```

**HKDF-Extract** condenses input material into a pseudorandom key. **HKDF-Expand-Label** stretches it into named outputs, each with a label such as `"c hs traffic"` and the transcript hash at that moment as context. Two consequences follow:

- **Keys are separated by purpose and direction.** Distinct labels derive client/server and handshake/application traffic secrets. A leaked key for one direction and phase need not reveal sibling keys, but a parent secret can reveal its derived keys and a current application traffic secret can derive its future updates. Separation prevents simple reflection between directions under the cryptographic assumptions.
- **Traffic secrets bind selected transcript prefixes.** The Early, Handshake and Master Secret extraction steps are not themselves all transcript-dependent. Derived traffic secrets use the appropriate handshake prefix, while signatures and Finished cover later messages. Tampering with a protected transcript is detected.

Under the hood both steps are HMAC, the keyed hash from the previous module. Extract runs HMAC with a salt (zeros at the start, then a secret derived from the previous stage) as the key; Expand runs HMAC again, keyed with that result, over the wanted length, a label and a context value (often a transcript hash), so every purpose gets its own independent-looking key from the same secret. With SHA-256, an output of 32 bytes or fewer needs only one HMAC block.

From each traffic secret, two more expansions produce the actual AEAD key and a 12-byte IV. Here is that last step, checked against the published RFC 8448 example handshake:

```python
import hashlib, hmac

def expand_label(secret, label, n):
    if not 0 < n <= 32:
        raise ValueError("one-block helper")
    # TLS prefixes labels for separation.
    full = b"tls13 " + label
    # Encode length, label and empty
    # context.
    info = (n.to_bytes(2, "big")
            + bytes([len(full)]) + full
            + b"\x00")  # empty context
    # HKDF-Expand: one HMAC block is
    # enough when n <= 32 bytes
    t1 = hmac.new(secret, info + b"\x01",
                  hashlib.sha256).digest()
    # Take only the requested output bytes.
    return t1[:n]

# server handshake traffic secret,
# from the RFC 8448 example trace
s_hs = bytes.fromhex(
    "b67b7d690cc16c4e75e54213cb2d37b4"
    "e9c912bcded9105d42befd59d391ad38")
key = expand_label(s_hs, b"key", 16)
iv = expand_label(s_hs, b"iv", 12)
print(key.hex())
print(iv.hex())
```

This prints `3fce516009c21727d0f2e4e86ee403bc` and `5d313eb2671276ee13000b30`, the same AES-128-GCM key and IV as the RFC.

### Finished: an HMAC over everything

Each side confirms the handshake with a **Finished message**: an HMAC, keyed with a key derived from its handshake traffic secret, over the transcript hash. It proves that this side derived the same keys and saw the same messages. A mismatch aborts the connection. The server may send application data after its own Finished before receiving the client Finished; optional 0-RTT data arrives earlier still and has weaker replay guarantees.

## Key takeaways
- HKDF separates client/server and handshake/application secrets with specified labels and contexts.
- Parent-secret exposure can reveal derived keys; separate labels are not arbitrary compromise recovery.
- Finished authenticates the transcript and confirms possession of the corresponding handshake secret.

## Further reading
- [TLS 1.3 — RFC 9846](https://www.rfc-editor.org/rfc/rfc9846)
- [TLS example traces — RFC 8448](https://www.rfc-editor.org/rfc/rfc8448)
