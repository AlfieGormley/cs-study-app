---
id: tcp-fast-retransmit-limits
sourceLesson: tcp-reliability
title: Duplicate ACKs and fast retransmit limits
level: intermediate
minutes: 3
summary: Duplicate ACKs and fast retransmit limits, with worked examples and explicit assumptions.
---

## Fast retransmit

Waiting for a timeout is slow. The duplicate ACKs from earlier are a quicker signal: repeated cumulative ACKs can indicate out-of-order arrival, although duplicate packets/ACKs and other events complicate that inference. Classic algorithms apply a specific duplicate-ACK definition, including window/data conditions.

One duplicate could just be **reordering**: two packets swapped places. So the classic rule ([RFC 5681](https://www.rfc-editor.org/rfc/rfc5681)) waits for **three duplicate ACKs**, then retransmits the missing segment straight away, without waiting for the timer. That is **fast retransmit**, usually paired with **TCP fast recovery** (the congestion-control units) to control the congestion window during recovery. Reno’s multiplicative reduction does not promise the application’s measured sending rate is exactly halved.

```
ACK 1001          (new data acked)
ACK 1001  dup #1
ACK 1001  dup #2
ACK 1001  dup #3  -> resend seq=1001
ACK 5001          (hole filled)
```

Fast retransmit needs **enough data after the loss** to generate three duplicates. Without additional mechanisms such as Limited Transmit or loss probes, the simple three-duplicate threshold can fail to trigger in these cases:

- **Small windows**: if only three segments are in flight and one is lost, at most two duplicates come back.
- **Tail loss**: if the **last** segment of a response is lost, nothing follows it, so no duplicates arrive at all. The simple scheme may then need the RTO; other loss-recovery mechanisms can intervene.

## Key takeaways

- Classic fast retransmit requires three qualifying duplicate ACKs rather than reacting to the first reordering hint.
- Small flights and tail losses may lack enough later arrivals to produce that signal.

## Further reading

- [RFC 6298: Computing TCP's Retransmission Timer](https://www.rfc-editor.org/rfc/rfc6298)
- [RFC 2018: TCP Selective Acknowledgment Options](https://www.rfc-editor.org/rfc/rfc2018)
- [RFC 8985: The RACK-TLP Loss Detection Algorithm for TCP](https://www.rfc-editor.org/rfc/rfc8985)
- [RFC 5681: TCP Congestion Control (fast retransmit)](https://www.rfc-editor.org/rfc/rfc5681)
- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
- [Congestion Avoidance and Control — Van Jacobson (1988)](https://ee.lbl.gov/papers/congavoid.pdf)
- [Linux retransmission timer controls](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
