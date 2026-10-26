---
id: nf-arq-sequence-space
sourceLesson: nf-error-control
title: Loss recovery and sequence-number reuse
level: advanced
minutes: 4
summary: Trace loss recovery and explain why reused sequence numbers must not confuse old frames with new data.
---

### Go-Back-N

- The receiver accepts frames **only in order**. Anything after a gap is discarded.
- ACKs are **cumulative**: "ACK n" means everything up to n arrived.
- On timeout, the sender retransmits the oldest unacknowledged frame and all later **outstanding** frames in its window.

The receiver is trivial (one expected sequence number, no buffer), but a gap can require retransmission of several already received frames.

```
sender:   0 1 2 3 4 5 | 2 3 4 5
               x lost   ^ timeout: go back
receiver: 0 1 - drop drop drop | 2 3 4 5
```

### Selective Repeat

- The receiver **buffers** out-of-order frames within its window and ACKs each one individually.
- The textbook sender keeps a timer per unacknowledged frame and resends frames whose acknowledgements have not arrived before timeout.
- Buffered frames are delivered upwards once the gap is filled.

It costs memory and bookkeeping on both sides, and it avoids retransmitting correctly acknowledged later frames merely because an earlier frame was lost. Lost ACKs or repeated loss can still cause more retransmissions. TCP uses cumulative byte acknowledgements and can negotiate SACK to report non-contiguous received ranges. Its recovery and congestion-control rules are more complex than these textbook models.

### Window size versus sequence numbers

A fixed-width sequence field has a finite number of values, after which counting wraps back to zero. With two bits the numbers go 0, 1, 2, 3, 0, 1, …. In the textbook model used here, assume ordered channels and a bound on how long old duplicates can survive. Under those assumptions, window limits avoid confusing retransmissions from the outstanding window with new data. Finite sequence numbers alone cannot handle packets delayed across arbitrary numbers of wraps. The table assumes equal sender and receiver windows for Selective Repeat.

```formula reference
W_GBN ≤ 2^k − 1
W_SR ≤ 2^(k − 1)
where
W_GBN: the largest safe Go-Back-N window, in frames
W_SR: the largest safe Selective Repeat window, in frames
k: the number of bits in the sequence-number field
≤: less than or equal to
In words: Go-Back-N can use every sequence number but one; Selective Repeat can use only half of them.
```

| Protocol | Maximum window |
|---|---|
| Go-Back-N | One less than the sequence space |
| Selective Repeat | Half the sequence space |

Why Go-Back-N cannot use all four values with a two-bit field (numbers 0–3) and a window of 4:

1. The sender sends 0, 1, 2, 3. All arrive; the receiver now expects 0 (the next lap).
2. All four ACKs are lost. The sender times out and resends the *old* 0.
3. The receiver, expecting a new 0, accepts the duplicate as fresh data. Silent corruption.

With a window of 3 the receiver would be expecting 3 when the old 0 reappears, and would reject it.

Selective Repeat is stricter because the receiver accepts a whole window of numbers. After receiving 0, 1, 2 with window 3, it accepts {3, 0, 1}. If the ACKs are lost and the sender resends the old 0, it falls inside the new window and is wrongly accepted. Keeping the window at no more than half the sequence space separates the old retransmissions from the next receive window in this scenario.

TCP numbers bytes using 32 bits and constrains window sizes; negotiated timestamps support PAWS rejection of old segments. Byte numbering alone does not remove wraparound concerns.

## Key takeaways
- Go-Back-N discards frames after a gap; Selective Repeat buffers them and acknowledges individually.
- Safe sequence windows also require bounded old duplicates and the stated ordered-channel assumptions.

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
