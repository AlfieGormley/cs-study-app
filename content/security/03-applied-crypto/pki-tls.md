---
id: pki-tls
title: How TLS uses all of it
level: intermediate
minutes: 14
summary: TLS 1.3 seen as a composition of primitives: ephemeral Diffie–Hellman for keys, signatures and certificates for identity, HKDF and a transcript hash to bind it together, and AEAD with counter nonces for the records.
---

TLS is widely deployed to protect network connections. It takes the primitives from the previous module and the last two lessons, Diffie–Hellman, signatures, certificates, hashes, HMAC, HKDF and AEAD, and wires them together so each one covers a gap the others leave.

The Networks subject walks through the TLS 1.3 handshake message by message (see *TLS 1.3, certificates, ECH and mTLS*). This lesson takes the opposite view: for each primitive, what job does it do, exactly which bytes does it touch, and what goes wrong without it?

## Four jobs, four primitives

This example uses certificate authentication and X25519. TLS 1.3 also supports other groups and PSK authentication; PSK-only mode does not provide forward secrecy. The example has four jobs:

| Job | Primitive in TLS 1.3 |
|---|---|
| Agree a secret | Ephemeral ECDH (X25519) |
| Prove who the server is | Certificate + signature |
| Turn secrets into keys | HKDF + transcript hash |
| Protect the data | AEAD (AES-GCM, ChaCha20) |

Take any one away and the channel breaks:

- **No key agreement**: nothing to encrypt with.
- **No authentication**: Diffie–Hellman with an unauthenticated peer is Diffie–Hellman with whoever is in the middle. An attacker runs one exchange with you and another with the server and relays.
- **No transcript binding**: an attacker can tamper with negotiation (strip strong options) and nobody notices.
- **No AEAD**: records can be read or modified.

## Job 1: key agreement with ephemeral ECDH

In its first message the client sends a fresh X25519 public key; the server replies with its own. Each side combines its private key with the other's public key and gets the same 32-byte shared secret. Both key pairs are thrown away after the handshake.

That "thrown away" is the point. TLS 1.2 also allowed **RSA key transport**: the client picked a secret, encrypted it with the server's long-term RSA public key, and sent it. Anyone who later obtained that RSA private key, through a breach or a court order, could decrypt every recorded session. RSA decryption on the server was also an oracle: the 2017 ROBOT attack showed many servers still leaked Bleichenbacher-style padding errors, nearly 20 years after the original attack.

TLS 1.3 removed RSA key transport entirely. Certificate-authenticated handshakes use ephemeral (EC)DH, providing **forward secrecy** when ephemeral secrets are securely erased: stealing the certificate key tomorrow does not decrypt today's traffic.

> [!note] Hybrid post-quantum key exchange
> A future quantum computer could solve the discrete-log problem behind X25519, and traffic recorded now could be decrypted then ("harvest now, decrypt later"). Chrome introduced **X25519MLKEM768** in version 131: an X25519 share and an ML-KEM-768 share in one key-share entry (about 1.2 KB from the client). Both shared secrets feed the key schedule. With the specified combiner and correct implementations, either component remaining secure protects the combined exchange. Chrome announced the transition from its earlier Kyber draft to ML-KEM in September 2024.

## Job 2: proving identity with a signature

ECDH gives a secret shared with *someone*. The server proves it is the right someone in two steps:

1. **Certificate**: the chain from the last lesson, binding `shop.example.com` to a public key.
2. **CertificateVerify**: a signature, with that key's private half, over the handshake so far.

What exactly is signed matters. The server signs:

```
64 bytes of 0x20 (spaces)
"TLS 1.3, server CertificateVerify"
0x00
Transcript-Hash(ClientHello ...
                Certificate)
```

The **transcript hash** covers both key shares, the client's random value and the negotiated parameters. So the signature says: "I, the owner of this certificate, took part in *this* handshake, with *these* DH values." An attacker who substitutes their own key share cannot produce a matching signature.

The odd prefix is there for **domain separation**. The 64 spaces and context string separate this signature input from other TLS roles and versions, reducing cross-protocol confusion; arbitrary external protocols must still avoid overlapping signed formats. In TLS 1.2 the server signed only the random values and its DH parameters, not the negotiated cipher suite, and that gap helped make the 2015 Logjam downgrade to 512-bit "export" Diffie–Hellman possible.

The signature algorithm is negotiated through the `signature_algorithms` extension. If the server's key is RSA, TLS 1.3 requires RSA-PSS here, even though the CA's signature *on* the certificate may still be PKCS#1 v1.5.

## Job 3: from one secret to many keys with HKDF

The ECDH output is a single group element, not a set of uniformly random keys. TLS 1.3 runs it through a **key schedule** built entirely from HKDF:

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

- **Keys are separated by purpose and direction.** Distinct labels derive client/server and handshake/application traffic secrets. A record key leak need not reveal sibling keys, but a parent secret can reveal its derived keys and a current application traffic secret can derive its future updates. Separation prevents simple reflection between directions under the cryptographic assumptions.
- **Traffic secrets bind selected transcript prefixes.** The Early, Handshake and Master Secret extraction steps are not themselves all transcript-dependent. Derived traffic secrets use the appropriate handshake prefix, while signatures and Finished cover later messages. Tampering with a protected transcript is detected.

From each traffic secret, two more expansions produce the actual AEAD key and a 12-byte IV. Here is that last step, checked against the published RFC 8448 example handshake:

```python
import hashlib, hmac

def expand_label(secret, label, n):
    if not 0 < n <= 32:
        raise ValueError("one-block helper")
    full = b"tls13 " + label
    info = (n.to_bytes(2, "big")
            + bytes([len(full)]) + full
            + b"\x00")  # empty context
    # HKDF-Expand: one HMAC block is
    # enough when n <= 32 bytes
    t1 = hmac.new(secret, info + b"\x01",
                  hashlib.sha256).digest()
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

Each side ends its flight with a **Finished** message: an HMAC, keyed with a key derived from its handshake traffic secret, over the transcript hash. It proves that this side derived the same keys and saw the same messages. A mismatch aborts the connection. The server may send application data after its own Finished before receiving the client Finished; optional 0-RTT data arrives earlier still and has weaker replay guarantees.

## Job 4: protecting records with AEAD

After the handshake, data travels in **records** of up to 16 KiB of content. Each record is sealed with the negotiated AEAD:

```
nonce = iv XOR seq (64-bit, padded)
aad   = 5-byte record header
ct    = AEAD-Seal(key, nonce,
                  data + type + pad,
                  aad)
```

- **The nonce is never sent.** Both sides keep a 64-bit record **sequence number**, starting at 0 for each key, and XOR it into the static IV. Each record gets a unique nonce without spending bytes on the wire, and deletion, reordering or replay within the delivered TLS byte stream causes subsequent authentication failure. Ordinary packet loss is repaired by TCP.
- **The header is authenticated** as associated data, so its length and type cannot be altered.
- **The real content type is inside the encryption**, along with optional padding, so an observer cannot easily tell handshake messages from alerts or application data.

Continuing the code above:

```python
def nonce(iv, seq):
    if not 0 <= seq < 2**64:
        raise ValueError("64-bit sequence")
    s = seq.to_bytes(len(iv), "big")
    return bytes(a ^ b for a, b in
                 zip(iv, s))

print(nonce(iv, 0).hex())
print(nonce(iv, 1).hex())
print(nonce(iv, 256).hex())
```

Output: `...13000b30` (the IV itself), `...13000b31`, then `...13000a30`. Only the low bytes change, and no two records under one key share a nonce.

AEAD keys also have **usage limits**. RFC 8446 says to send no more than about 2^24.5 full-size records (roughly 24 million records, close to 400 GB) under one AES-GCM key. Long-lived connections send a **KeyUpdate** message, which updates the sender's write secret and receiver's corresponding read secret with HKDF, giving a new key and resetting that direction's sequence number. Updating the opposite direction requires its own KeyUpdate.

Older TLS suites permitted CBC with a separate HMAC, traditionally MAC-then-encrypt; RFC 7366 later defined an encrypt-then-MAC extension. BEAST targeted predictable IVs in TLS 1.0, Lucky 13 exploited timing in CBC processing, and the original POODLE targeted SSL 3.0 padding. TLS 1.3 allows only AEAD.

## Resumption and its trade-offs

The **resumption master secret** derives a PSK for each ticket. The ticket is an opaque identity: implementations may encrypt resumption state into it or use it to look up server-side state. NewSessionTicket is sent encrypted; a subsequent ordinary ClientHello exposes the ticket identity unless protected by ECH. A resumed handshake can skip the certificate and signature.

- With `psk_dhe_ke` mode, a fresh ECDH exchange is still mixed in, so forward secrecy is kept.
- With `psk_ke`, there is no ECDH. Anyone who later gets the PSK, or a **ticket encryption key** that recovers sufficient resumption state, can decrypt those sessions.

For stateless tickets, compromise of a key that exposes PSKs breaks recorded PSK-only resumed sessions. Fresh DH in `psk_dhe_ke` protects its 1-RTT traffic, but 0-RTT traffic still depends only on the PSK. Limit ticket lifetime and key exposure according to the implementation and threat model.

> [!note] Content gap
> Fleet-wide ticket-key reuse measurements and a universal hourly rotation rule are omitted: no reproducible deployment evidence or universally applicable policy was available for this review.

## Putting it together

```
X25519 share ---------+
                      v
        HKDF key schedule <-- transcript
            |      |            hash
   hs keys  |      | app keys    ^
            v      v             |
  {Cert, CertVerify, Finished}   |
     signature + HMAC over ------+
            |
            v
     AEAD records, seq nonces
```

Each piece protects another: the signature authenticates the ECDH values, transcript-dependent derivations and authentication bind the negotiation, HKDF separates keys by purpose and direction, and AEAD with sequence-number nonces protects every byte afterwards.

## Pitfalls in practice

- **Turning off verification.** The cryptography is useless if the client skips certificate or hostname checks; ECDH then happily agrees a key with the attacker.
- **Re-enabling old versions.** TLS 1.0 and 1.1 are deprecated. Enabling them exposes clients that permit those versions; it does not automatically downgrade clients that enforce a newer minimum. Keep TLS 1.2 as the floor and prefer ECDHE with AEAD suites there.
- **Long-lived ticket keys** and **0-RTT without application-level replay safety** both trade away guarantees for speed.
- **Terminating TLS early.** TLS protects only hop to hop. Traffic decrypted at a load balancer and forwarded in plaintext is exposed on that internal hop. A historical intelligence-programme attribution is omitted here because the review did not obtain a reliable primary record supporting the specific claim.

## Key takeaways
- TLS 1.3 composes ephemeral ECDH, certificate-based signatures, an HKDF key schedule over a transcript hash, and AEAD.
- Ephemeral key exchange gives forward secrecy; TLS 1.3 removed RSA key transport, which had none.
- CertificateVerify signs the transcript, binding the server's identity to this handshake's key shares; a context prefix gives domain separation.
- HKDF derives separate keys per direction and phase, using transcript context at the specified derivation stages, while signatures and Finished authenticate the handshake.
- Record nonces are the static IV XOR a sequence number, so they are unique and never sent; KeyUpdate refreshes keys before AEAD limits.
- Hybrid X25519MLKEM768 is designed to protect recorded traffic if its post-quantum component remains secure; it does not make classical certificate signatures quantum-resistant.

## Further reading
- [RFC 8446: The Transport Layer Security (TLS) Protocol Version 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [RFC 8448: Example Handshake Traces for TLS 1.3](https://www.rfc-editor.org/rfc/rfc8448)
- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/)
- [RFC 5869: HMAC-based Extract-and-Expand Key Derivation Function (HKDF)](https://www.rfc-editor.org/rfc/rfc5869)
- [The ROBOT Attack](https://robotattack.org/)
- [Chrome transition to ML-KEM](https://security.googleblog.com/2024/09/a-new-path-for-kyber-on-web.html)
