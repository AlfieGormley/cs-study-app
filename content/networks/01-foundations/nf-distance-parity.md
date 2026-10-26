---
id: nf-distance-parity
sourceLesson: nf-error-control
title: Hamming distance and parity
level: advanced
minutes: 3
summary: Separate detection and correction guarantees and test parity’s blind spots.
---

Physical links can introduce errors through noise, interference or equipment faults. Error rates depend on the link, operating conditions and coding; there is no single Ethernet or wireless rate. A reliability design must consider two distinct functions:
1. **Detect** that a frame was damaged, so it isn't delivered as if it were good.
2. **Recover**, either by fixing the error in place (forward error correction) or by sending the data again (**ARQ**, automatic repeat request).

This unit starts with the distance between valid codewords and the simplest detection code, parity. Later units examine stronger checks and retransmission strategies.

## The idea behind every check

The sender computes a few redundant bits from the data and sends them along. The receiver recomputes them from what arrived. A mismatch means something changed.

How good a code is depends on its **Hamming distance**: the minimum number of bit flips needed to turn one valid codeword (a bit pattern the code allows) into another. From the distance you can read off how many flipped bits the code is guaranteed to catch or repair:

```formula reference
t_detect = d − 1
t_correct = ⌊(d − 1) / 2⌋
where
d: the code's minimum Hamming distance, a whole number of bits
t_detect: the largest number of flipped bits that is always detected
t_correct: the largest number of flipped bits that can always be corrected
⌊ ⌋: the floor function: round down to the nearest whole number (⌊1.5⌋ = 1)
In words: detection works while damage cannot turn one valid codeword into another; guaranteed correction requires the damaged word to remain closer to its original than to every alternative.
```

For example, a code with distance 3 detects up to 2 flipped bits, or corrects 1, because one flipped bit still leaves it closer to its original than to any other valid codeword.

For a given worst-case number of bit errors, correction requires a larger minimum distance than detection. These are alternative decoding guarantees; a distance-3 correcting decoder cannot also promise to identify every two-bit error as uncorrectable.

## Parity

One **parity bit** makes the number of 1s even (even parity). Distance is 2, so it catches any single-bit error, and any odd number of flips, but misses every even number. Two flips in a byte cancel out.

A **burst error** spans from the first changed bit to the last; intermediate bits need not all change. Parity misses bursts containing an even number of flips, so it cannot guarantee detection of even a two-bit burst.

## Key takeaways
- Minimum distance bounds alternative detection and correction guarantees.
- Even parity catches odd numbers of flipped bits but misses even numbers.

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
