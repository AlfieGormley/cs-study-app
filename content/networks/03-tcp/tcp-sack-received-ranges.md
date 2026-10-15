---
id: tcp-sack-received-ranges
sourceLesson: tcp-reliability
title: Selective ACK ranges and duplicate receipt
level: intermediate
minutes: 3
summary: Selective ACK ranges and duplicate receipt, with worked examples and explicit assumptions.
---

## Selective acknowledgement (SACK)

Cumulative ACKs leave the sender guessing. Was only 1001 lost, or 1001 and 3001? A cautious sender (**Go-Back-N** style) resends everything from 1001; an optimistic one resends 1001 and waits a round trip to learn more.

**SACK** ([RFC 2018](https://www.rfc-editor.org/rfc/rfc2018)) lets the receiver list the blocks it holds beyond the cumulative point:

```
ACK 1001  SACK 2001-5001
```

These blocks report received ranges with exclusive right edges. They help identify gaps, but a missing report is not proof of loss: only a limited number of blocks fit, data may still be in flight, and a receiver can discard previously SACKed data before cumulative acknowledgement. Permission to send SACK is advertised directionally with `SACK-permitted` in SYN segments; support and configuration vary.

A SACK option fits at most **four** blocks, or **three** alongside the timestamp option, because TCP options are limited to 40 bytes. Each block is two 32-bit sequence numbers (8 bytes), plus 2 bytes for the option's kind and length:

```formula
L_SACK = 2 B + n × 8 B
2 B + 4 × 8 B = 34 B ≤ 40 B
2 B + 3 × 8 B = 26 B ≤ 40 B − 12 B
where
L_SACK: the length of a SACK option, in bytes (B)
n: the number of blocks it carries
B: bytes
≤: is at most
In words: four blocks need 34 bytes, which fits in the 40 option bytes, but five would need 42; once the timestamp option takes 12 bytes (10 plus 2 of padding), only three blocks fit in the 28 that remain.
```

A related extension, **D-SACK** ([RFC 2883](https://www.rfc-editor.org/rfc/rfc2883)), uses the first SACK block to report a segment received **twice**. Duplicate receipt can support inference of a **spurious retransmission** and possible congestion-control undo, but can also result from network duplication. The sender must apply its algorithm’s checks; D-SACK is not unconditional proof of a particular cause or automatic permission to undo every reduction.

## Key takeaways

- SACK blocks describe received ranges using exclusive right edges.
- Limited option space and receiver reneging prevent treating every SACK report as a complete permanent delivery record.
- D-SACK reports duplicate receipt; its cause and any recovery undo require further inference.

## Further reading

- [RFC 6298: Computing TCP's Retransmission Timer](https://www.rfc-editor.org/rfc/rfc6298)
- [RFC 2018: TCP Selective Acknowledgment Options](https://www.rfc-editor.org/rfc/rfc2018)
- [RFC 8985: The RACK-TLP Loss Detection Algorithm for TCP](https://www.rfc-editor.org/rfc/rfc8985)
- [RFC 5681: TCP Congestion Control (fast retransmit)](https://www.rfc-editor.org/rfc/rfc5681)
- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
- [Congestion Avoidance and Control — Van Jacobson (1988)](https://ee.lbl.gov/papers/congavoid.pdf)
- [Linux retransmission timer controls](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
