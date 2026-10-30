---
id: tcp-rack-tail-probes
sourceLesson: tcp-reliability
title: RACK, tail probes and recovery diagnosis
level: intermediate
minutes: 3
summary: How RACK uses timing instead of duplicate-ACK counts, and how tail loss probes rescue lost final segments.
---

## Modern loss detection: RACK-TLP

Counting duplicate ACKs is crude. **RACK-TLP** ([RFC 8985](https://www.rfc-editor.org/rfc/rfc8985)), reasons about transmission and acknowledgement **time**. The retrieved Linux documentation describes RACK support; availability and defaults in other systems require version-specific confirmation.

- **RACK** (Recent ACKnowledgement) uses delivery of later-transmitted data, transmission times, an RTT estimate and a reordering window to infer losses of earlier unacknowledged transmissions. ACK/SACK information can provide this evidence; duplicate-ACK count alone is not the trigger. Reordering tolerance can adapt using D-SACK and other state.
- **TLP** (Tail Loss Probe) schedules a probe timeout (PTO) whose baseline is two smoothed RTTs: on a path with a 40 ms smoothed RTT, about 80 ms after the last send, far sooner than a typical RTO. Rules account for unavailable RTT estimates, possible delayed ACKs, the RTO deadline and probe eligibility. It prefers new data when available and permitted; otherwise it can retransmit the highest-sequence segment. A probe/ACK exchange may expose earlier tail loss to RACK. It does not guarantee delivery or a fixed total repair time.

The full rules adjust this baseline (for a single outstanding segment, a possible delayed ACK, and the RTO deadline).

| Mechanism | Main trigger | Timing qualification |
|---|---|---|
| RTO | Retransmission timer expires | Estimator, floor/cap and RTO backoff apply |
| Classic fast retransmit | 3 qualifying duplicate ACKs | Depends on ACK arrivals |
| RACK | Delivery/time evidence of a hole | RTT and reordering state apply |
| TLP | Eligible probe timeout expires | Baseline 2 × SRTT, with adjustments |

## Pitfalls and real-world notes

- **Reordering looks like loss.** Links that spread one flow over several paths, and some load balancers reorder packets, which can trigger spurious fast retransmits and needless slowdowns. RACK's adaptive window and D-SACK undo help, and per-flow ECMP hashing can reduce reordering caused by sending each packet down a different route.
- **Checksums are weak.** TCP's 16-bit checksum misses some multi-bit errors. Real systems lean on link-layer CRCs and, increasingly, TLS, whose authenticated records detect alteration with a very small but nonzero forgery probability under their cryptographic assumptions. Neither layer gives a mathematical guarantee against every error.
- **Transport acknowledgement is not application acknowledgement.** A cumulative ACK means the peer’s **TCP endpoint** accepted the preceding stream positions, not that the application processed them. If you need "the server saved it", you need an application-level acknowledgement.
- **Retransmission rate is a health signal.** On Linux, `ss -ti` shows per-connection `rto`, `rtt` and `retrans`, and `nstat` shows `TcpRetransSegs`. Interpret retransmission counters with their definitions, denominator, traffic pattern and captures; no universal one-percent threshold identifies a cause.

## Key takeaways

- RACK uses transmission/delivery times and reordering tolerance to infer a missing earlier transmission.
- TLP probes eligible outstanding data before the RTO, subject to adjustments and deadlines.
- Recovery counters and transport ACKs need careful interpretation; neither proves application-level completion.

## Further reading

- [RFC 8985: The RACK-TLP Loss Detection Algorithm for TCP](https://www.rfc-editor.org/rfc/rfc8985)
- [Linux retransmission timer controls](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
