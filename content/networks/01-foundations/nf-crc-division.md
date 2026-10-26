---
id: nf-crc-division
sourceLesson: nf-error-control
title: Compute a CRC by XOR division
level: advanced
minutes: 3
summary: Explain XOR division, execute a small CRC and distinguish no detected error from proof of correctness.
---

## Cyclic redundancy checks

A **CRC** treats the bits as the coefficients of a polynomial over GF(2), arithmetic where addition and subtraction are both XOR (exclusive or: 1 when exactly one input is 1) and there are no carries. Each bit is a coefficient of a power of a formal polynomial variable. For example, `1001` has a cubic term and a constant term. Sender and receiver agree on a **generator polynomial**. Its degree (highest power) determines the check-bit count. The CRC is a remainder after division:



1. Append as many zero bits as the generator's degree.
2. Divide by the generator using XOR long division.
3. Replace those zero positions with the remainder to form data followed by check bits.
4. The receiver divides the complete received bit pattern by the generator. A remainder of zero means "no detected error" in this unreflected, zero-initialised model. Real protocols can use other initialisation and final-XOR conventions.

### A worked division

Use data bits `101110` and generator bits `1001`. The generator has degree three, so append three zero bits. Wherever the leading bit is 1, XOR the generator in beneath it:

```
 101110000   D + three zeros
^1001
 001010000
^  1001
 000011000
^    1001
 000001010
^     1001
 000000011   remainder R = 011
```

The sender transmits `101110 011`. The receiver divides `101110011` by `1001` and gets `000`. If the fourth bit is flipped on the way (`101010011`), the remainder is `100`, not zero, and the frame is dropped.

The same thing in code:

```python
def crc_remainder(data, gen):
    if not data or set(data) - {"0", "1"}:
        raise ValueError("need binary data")
    if (len(gen) < 2 or gen[0] != "1"
            or gen[-1] != "1"
            or set(gen) - {"0", "1"}):
        raise ValueError("bad generator")
    r = len(gen) - 1
    # Reserve the check-bit positions.
    bits = list(data + "0" * r)
    for i in range(len(data)):
        # Cancel a leading one with XOR.
        if bits[i] == "1":
            for j, g in enumerate(gen):
                b = bits[i + j]
                bits[i + j] = str(
                    int(b) ^ int(g))
    # Only the remainder positions survive.
    return "".join(bits[-r:])

print(crc_remainder("101110", "1001"))
# 011
```

A check can pass even when data changed: some errors turn one valid codeword into another. A zero remainder means only that this particular check detected no error.

## Key takeaways
- GF(2) division uses XOR without carries.
- The simple zero-remainder test uses the stated unreflected, zero-initialised convention.

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
