---
id: pki-tls-record-nonces
title: TLS record encryption and sequence nonces
level: intermediate
minutes: 3
sourceLesson: pki-tls
summary: AEAD protects record contents and authenticates the visible header.
---

In a certificate-authenticated TLS 1.3 connection, ephemeral key agreement, signatures, HKDF and AEAD have separate jobs. This unit examines one part of that composition. The preceding HKDF unit derived the server handshake IV `5d313eb2671276ee13000b30`; the nonce example below uses that value.

## Job 4: protecting records with AEAD

After the handshake, data travels in **TLS records** of up to 16 KiB of content. Each record is sealed with the negotiated AEAD:

```formula
N = IV ⊕ S
C = Seal(K, N, P ‖ T_ct ‖ Z, A)
where
N: the per-record nonce, 12 bytes; it is computed by both sides and never sent
IV: the static 12-byte IV derived from the traffic secret with HKDF
⊕: XOR (exclusive OR), byte by byte: each output bit is 1 when the two input bits differ
S: the 64-bit record sequence number (0 for the first record under a key, then 1, 2, …), written as a 12-byte number with zero bytes on the left
C: the protected record body: ciphertext plus a 16-byte authentication tag
Seal: AEAD encryption: encrypts and authenticates in one operation
K: the traffic key, for example 16 bytes for AES-128-GCM
P: the plaintext record content, up to 16 KiB (16,384 bytes)
T_ct: one byte giving the real record type: handshake, alert or application data
Z: optional zero-byte padding that obscures content length while keeping the full inner plaintext within 16,385 bytes and respecting ciphertext expansion limits
A: the associated data: the 5-byte record header, authenticated but not encrypted
‖: concatenation: one value's bytes followed by the next
In words: each record's nonce is the fixed IV with the record number mixed into its last bytes, and the AEAD encrypts the content plus its true type while also authenticating the visible header.
```

- **The nonce is never sent.** Both sides keep a 64-bit record **sequence number**, starting at 0 for each key, and XOR it into the static IV. Each record gets a unique nonce without spending bytes on the wire, and deletion, reordering or replay within the delivered TLS byte stream causes subsequent authentication failure. Ordinary packet loss is repaired by TCP.
- **The header is authenticated** as associated data, so its length and type cannot be altered.
- **The real record type is inside the encryption**, along with optional padding, so an observer cannot easily tell handshake messages from alerts or application data.

Here the IV is the published value from the previous HKDF unit. The function accepts it as an argument; this is a nonce derivation illustration, not a complete record implementation:

```python
def nonce(iv, seq):
    if not 0 <= seq < 2**64:
        raise ValueError("64-bit sequence")
    # Left-pad the sequence with zero bytes.
    s = seq.to_bytes(len(iv), "big")
    # XOR pairs; neither input is mutated.
    return bytes(a ^ b for a, b in
                 zip(iv, s))

# Reuse the published RFC 8448 IV.
iv = bytes.fromhex(
    "5d313eb2671276ee13000b30")
print(nonce(iv, 0).hex())
print(nonce(iv, 1).hex())
print(nonce(iv, 256).hex())
```

Output: `...13000b30` (the IV itself), `...13000b31`, then `...13000a30`. Record 256 is the sequence number 0x0100, so it changes bits in the last two bytes: 0x0b XOR 0x01 is 0x0a, and 0x30 XOR 0x00 stays 0x30. Only the low bytes change, and no two records under one key share a nonce.

## Key takeaways
- AEAD protects record contents and authenticates the visible header.
- A static IV XOR the implicit sequence number gives unique per-key nonces without transmitting them.
- Removing a record from the delivered byte stream disrupts authentication on the next record.

## Further reading
- [TLS 1.3 — RFC 9846](https://www.rfc-editor.org/rfc/rfc9846)
- [TLS example traces — RFC 8448](https://www.rfc-editor.org/rfc/rfc8448)
