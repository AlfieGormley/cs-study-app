---
id: nf-internet-checksum
sourceLesson: nf-error-control
title: The Internet checksum and end-to-end checks
level: advanced
minutes: 3
summary: Calculate a one’s-complement checksum and explain aligned-word reordering and internal corruption.
---

## The Internet checksum

IPv4 headers, UDP and TCP use a **16-bit one's complement sum** (RFC 1071): add the data as 16-bit words, fold any carry back into the bottom, and invert.

```python
def inet_checksum(data: bytes) -> int:
    # Zero-pad an odd final byte for
    # summing.
    if len(data) % 2:
        data += b"\x00"
    total = 0
    for i in range(0, len(data), 2):
        # Assemble a big-endian 16-bit word.
        word = (data[i] << 8) | data[i + 1]
        total += word
        # fold the carry back in
        total = (total & 0xFFFF) + (
            total >> 16)
    # Invert within the 16-bit result width.
    return ~total & 0xFFFF

hdr = bytes.fromhex(
    "4500 0073 0000 4000 4011 0000"
    "c0a8 0001 c0a8 00c7")
print(hex(inet_checksum(hdr)))  # 0xb861

a = bytes.fromhex("4500 0073 0000 4000")
b = bytes.fromhex("0000 4500 4000 0073")

# Aligned-word swaps leave the sum
# unchanged.
print(inet_checksum(a) == inet_checksum(b))
# True
```

The checksum field (bytes 10–11 here) is zero while computing; the sender then writes `b861` into it. The receiver sums the whole header including the checksum, and a correct header gives zero after inversion.

It was chosen because it is **fast in software**: just additions, which can be done 32 or 64 bits at a time and updated incrementally when a router changes the TTL. Its weaknesses follow from addition being commutative:

- **Reordered 16-bit words** give the same sum, as the second example shows.
- Some multi-bit errors cancel, such as one word going up by some amount and another going down by the same amount.
- A roughly uniform random checksum result suggests an undetected-error probability on the order of 2⁻¹⁶. Structured corruptions, such as word reordering, do not follow that model.

> [!note] Errors the CRC never sees
> Stone and Partridge's study of real traffic (SIGCOMM 2000) found that TCP checksum failures happen far more often than link bit error rates predict. The authors inferred causes including memory and software errors, but could not explain every observed pattern. Corruption introduced after an incoming CRC check and before a new outgoing CRC is computed can pass both link checks. This is the **end-to-end argument**: only a check from source to destination covers the whole path, which is why storage systems and protocols like TLS add their own stronger integrity checks.

## Key takeaways
- One’s-complement sums use end-around carry and inversion.
- A link CRC cannot cover corruption introduced after its check and before a later link’s generation.

## Further reading
- [Cyclic redundancy check — Wikipedia](https://en.wikipedia.org/wiki/Cyclic_redundancy_check)
- [RFC 1071: Computing the Internet Checksum](https://www.rfc-editor.org/rfc/rfc1071)
- [Koopman: Best CRC polynomials](https://users.ece.cmu.edu/~koopman/crc/)
- [Sliding window protocol — Wikipedia](https://en.wikipedia.org/wiki/Sliding_window_protocol)
- [Selective Repeat ARQ — Wikipedia](https://en.wikipedia.org/wiki/Selective_Repeat_ARQ)
- [End-to-end principle — Wikipedia](https://en.wikipedia.org/wiki/End-to-end_principle)

- [Koopman: CRC-32 distance table](https://users.ece.cmu.edu/~koopman/crc/crc32.html)
- [Stone and Partridge: When the CRC and TCP Checksum Disagree](https://conferences.sigcomm.org/sigcomm/2000/conf/paper/sigcomm2000-9-1.pdf)
- [RFC 3366: Advice to Link Designers on Link ARQ](https://www.rfc-editor.org/rfc/rfc3366.html)
- [MIT: ARQ protocols](https://ocw.mit.edu/courses/16-36-communication-systems-engineering-spring-2009/resources/mit16_36s09_lec18/)
