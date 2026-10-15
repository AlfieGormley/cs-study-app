---
id: nf-crc-guarantees
sourceLesson: nf-error-control
title: CRC guarantees and secure integrity
level: advanced
minutes: 3
summary: Distinguish bounded error guarantees, random-pattern estimates and protection against deliberate tampering.
---

### What a CRC guarantees

For a generator with degree at least one and leading and constant coefficients 1, the CRC detects:

- **All single-bit errors**.
- **All bursts no longer than the generator degree**: count the span from the first flipped bit through the last.
- **All odd numbers of bit errors**, if the generator has the factor consisting of its formal variable plus one. A quick test: that is true exactly when the generator's bit pattern has an even number of 1s.
- For suitably random long error patterns, the random-pattern miss fraction decreases exponentially with the number of check bits (formula below). This is not a guarantee for arbitrary or adversarial errors.

```formula
P_miss ≈ 2^(−r)
P_miss ≈ 2^(−32) ≈ 2.3 × 10⁻¹⁰
where
P_miss: the fraction of random error patterns that happen to leave a zero remainder and go undetected
r: the number of CRC bits (the generator's degree); 32 for CRC-32
≈: approximately equal to
In words: a random corruption has about a one-in-2^r chance of producing a valid-looking frame; for CRC-32 that is about one in 4.3 billion.
```

Ethernet's **CRC-32** uses generator `0x04C11DB7` with its degree-32 leading term implicit. It detects every burst of up to 32 bits within the protected codeword. Koopman's table gives distance at least 4 through 91,607 data bits (excluding the 32 check bits), and at least 5 through 2,974 data bits. Thus all 1–3-bit errors within the FCS-protected region of ordinary 1518-byte or 9000-byte frames are detected. This excludes preamble/SFD and assumes fixed framing, rather than inserted or deleted bits. Other generators, including CRC-32C, have different guarantees.

### Fast in hardware, fine in software

The division is just a shift register with XOR taps, so NICs can compute CRCs at line rate using hardware resources and power. Software uses a 256-entry lookup table to process a byte at a time, and some CPU instruction sets accelerate particular CRC polynomials; the supported polynomial must match the protocol. Real CRC-32 also has bit-reflection and initial and final XOR conventions, which is why a straight bitwise version looks like this:

```python
import zlib

def crc32(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        # Feed each byte least-significant
        # first.
        crc ^= byte
        for _ in range(8):
            lsb = crc & 1
            crc >>= 1
            # Apply the reflected polynomial
            # tap.
            if lsb:
                crc ^= 0xEDB88320
    return crc ^ 0xFFFFFFFF


# Compare a published test vector with zlib.
msg = b"123456789"
print(hex(crc32(msg)))       # 0xcbf43926
print(crc32(msg) == zlib.crc32(msg))  # True
```

`0xEDB88320` is `0x04C11DB7` bit-reversed, and `0xCBF43926` is the standard check value for CRC-32.

> [!warning] A CRC is not a message authentication code
> A CRC is linear: an attacker who flips some bits can compute exactly how the CRC changes and fix it up, without knowing anything secret. WEP's integrity check was a CRC-32, which is one reason WEP fell. For tamper resistance you need a keyed cryptographic check, a message authentication code, such as the authentication tag in TLS.

## Key takeaways
- Generator choice and protected length determine guaranteed detection.
- CRC-32 is not a keyed authentication mechanism, even when implemented correctly.

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
