---
id: tcp-quic-transport-tradeoffs
sourceLesson: tcp-performance
title: QUIC streams, migration and deployment
level: advanced
minutes: 3
summary: QUIC streams, migration and deployment, with worked examples and explicit assumptions.
---

## QUIC: the transport in user space

**QUIC** ([RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)), started at Google and standardised in 2021, is the transport under **HTTP/3**. It runs over UDP (the UDP and ports units) and can be implemented in application **libraries** without changing the kernel; the protocol does not mandate an implementation location. Its design answers each of the problems above.

| Problem | QUIC's answer |
|---|---|
| Handshake RTTs | Combined transport/TLS setup; eligible 0-RTT sends early data, with replay restrictions |
| Head-of-line blocking | Per-stream ordering avoids TCP’s connection-wide delivery gap; shared limits remain |
| Ossification | Protected QUIC frames reduce ossification; some fields remain observable |
| Slow deployment | Can ship in application libraries |
| Network changes | Connection IDs support eligible, validated client migration |

A few details worth knowing:

- **Protection.** QUIC protects payloads, including ACK and other QUIC frames, and masks selected header bits and packet numbers. Connection IDs and other fields remain observable. Initial packet keys are publicly derivable, so Initial protection does not provide confidentiality against an observer. The optional spin bit can assist RTT estimation.
- **Loss recovery.** A newly transmitted packet uses a new packet number within its packet-number space; stream data may be resent at the same stream offset. This removes TCP's original-versus-retransmission ACK ambiguity. It does not make loss detection infallible: reordering can still cause spurious loss declarations.
- **Migration.** After handshake confirmation, connection IDs can support client migration, subject to negotiated restrictions, address validation and a working new path. A zero-length connection ID constrains migration. Success and seamless latency are not guaranteed.
- **Shared effects.** Loss can reduce a connection's congestion window, and flow control or application dependencies can delay several streams. QUIC removes the requirement to wait for an unrelated stream's missing bytes; it does not promise complete independence.
- **Congestion control.** RFC 9002 gives a NewReno-like example; compatible alternatives can be implemented. A library deployment can update the algorithm without an OS upgrade.

## The costs of QUIC

- **CPU.** Encryption, packet processing, batching and offload support affect cost. Compare QUIC with the actual alternative, often TCP **plus TLS**, using measurements for the implementations and workload. User-space location alone does not determine performance.
- **UDP blocking.** Some enterprise networks block or rate-limit UDP. Applications that support HTTP/2 or HTTP/1.1 can provide a TCP fallback. QUIC-only applications do not automatically acquire such a fallback.
- **Operational visibility.** Network operators lose the TCP header information they used for troubleshooting.

## A practical tuning checklist

- **Reuse connections.** Reuse can avoid setup while a connection remains valid. Idle periods can change congestion-control state.
- **Watch idle restarts.** Linux documents `tcp_slow_start_after_idle = 1` as enabling window timeout after sufficient idle time. Assess the algorithm, version and burst risk before changing it; there is no universal recommendation to disable it.
- **Check buffer limits against measured BDP** if flow control is limiting throughput. Linux socket-memory accounting and advertised windows differ; blindly raising maxima may waste memory without helping.
- **Compare congestion control and pacing configurations** under representative load, including competing traffic and latency. Do not infer a universal BBR improvement from one test.
- **Measure latency under load**, not just throughput.

## Key takeaways

- QUIC provides per-stream ordering, protected frames and separate packet-number spaces over UDP.
- Connection IDs can support eligible validated migration; shared congestion and resource constraints remain.
- CPU cost, UDP reachability and operational visibility require implementation- and path-specific assessment.

## Further reading

- [The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm — Mathis et al.](https://www.cs.utexas.edu/~lam/395t/papers/Mathis1998.pdf)
- [Introduction to bufferbloat — bufferbloat.net](https://www.bufferbloat.net/projects/bloat/wiki/Introduction/)
- [RFC 8289: Controlled Delay Active Queue Management](https://www.rfc-editor.org/rfc/rfc8289)
- [RFC 9000: QUIC](https://www.rfc-editor.org/rfc/rfc9000)
- [The QUIC Transport Protocol: Design and Internet-Scale Deployment — Google (SIGCOMM 2017)](https://research.google/pubs/the-quic-transport-protocol-design-and-internet-scale-deployment/)
- [RFC 7413: TCP Fast Open](https://www.rfc-editor.org/rfc/rfc7413)
- [RFC 9001: Using TLS to Secure QUIC](https://www.rfc-editor.org/rfc/rfc9001)
- [RFC 9002: QUIC Loss Detection and Congestion Control](https://www.rfc-editor.org/rfc/rfc9002)
- [Mathis and Mahdavi: Deprecating the TCP Macroscopic Model (2019 editorial)](https://ccronline.sigcomm.org/wp-content/uploads/2019/10/acmdl19-323.pdf)

> [!note] Evidence limits
> Universal browser connection counts, current TFO adoption, fixed protocol speedups and CPU costs are omitted because they require versioned deployment data or measurements not established here. The numerical timing and throughput examples are explicitly simplified models. This review did not run a WAN, QUIC migration or AQM performance experiment.
