---
id: tcp-performance
title: TCP performance in the real world
level: advanced
minutes: 15
summary: Where the time goes in a TCP transfer, the Mathis formula linking loss to throughput, bufferbloat and active queue management, head-of-line blocking, why TCP is hard to change, and how QUIC rebuilds the transport in user space.
---

The previous lessons explained how TCP works. This one asks why a transfer is slower than the link, and what engineers at CDNs, browser vendors and cloud providers do about it.

There are three usual suspects:

1. **Round trips**: handshakes and slow start, which bound short transfers.
2. **Loss**: which bounds long transfers through congestion control.
3. **Queues**: which add delay that nobody asked for.

Deployment is another constraint: transport changes must work with deployed endpoints and middleboxes. QUIC provides an alternative design over UDP.

## Short transfers are latency-bound

For small responses on a sufficiently fast link, handshake and request round trips can dominate. Serialization, server work, DNS, certificate size and loss can also matter.

Illustrative model: fetch 100,000 payload bytes over a new TCP + TLS 1.3 connection at 100 ms RTT, with MSS 1,460 bytes, initial window 10 segments, ideal doubling per completed flight, negligible serialization/server processing, no DNS delay, no loss, no TLS retry and no other limits. Ignore handshake bytes when modelling the response window:

| Step | Round trips |
|---|---|
| TCP handshake | 1 |
| TLS 1.3 handshake | 1 |
| Request, then slow start: 10, 20, 39 segments | 3 |
| Total | about 5 (500 ms) |

The response needs 69 segments, sent in flights of 10, 20 and 39. The request/first response costs one RTT; each further flight adds one RTT in this ideal model. A conventional full TLS 1.2 handshake adds a round trip relative to TLS 1.3; resumptions differ. The table is an estimate under these assumptions, not a measured or universal HTTPS latency. Connection reuse and closer servers can reduce round-trip costs.

> [!note] TCP Fast Open
> TFO ([RFC 7413](https://www.rfc-editor.org/rfc/rfc7413)) can let a client with a previously obtained cookie send data in its SYN. When supported and accepted, this can save a round trip. Applications must handle replay-related restrictions and implementations need fallback for incompatible paths. This lesson makes no current browser-adoption claim.

## Long transfers are loss-bound: the Mathis formula

The Mathis model approximates a sustained Reno-style congestion-avoidance flow with light/moderate loss, sufficient sender data and receive window, and no retransmission timeouts. The ideal periodic-loss sawtooth, with one ACK per segment, yields:

```
            MSS     C
rate  ~=  ----- x -----
            RTT   sqrt(p)

C ~= 1.22 (sqrt(3/2)), p = loss rate
```

It follows from the sawtooth: with a loss every 1/p packets, the window oscillates between W/2 and W, and solving for W gives a window proportional to 1/√p.

```python
from math import sqrt

def mathis(mss, rtt, p):
    """Reno-model estimate in bits/s."""
    valid = (mss > 0 and rtt > 0
             and 0 < p < 1)
    if not valid:
        raise ValueError("invalid input")
    return mss * 8 / rtt * 1.22 / sqrt(p)

print(mathis(1460, 0.1, 0.0001) / 1e6)
print(mathis(1460, 0.1, 0.01) / 1e6)
```

```
14.2496
1.42496
```

At 100 ms RTT, the formula returns about **14 Mbit/s** for p = 0.0001 and **1.4 Mbit/s** for p = 0.01. These are model outputs, not universal caps or predictions for arbitrary packet-loss patterns. ACK behaviour and loss patterns change the constant; timeouts and other limits can invalidate the approximation. Within the model:

- **Throughput ∝ 1/RTT.** Doubling RTT halves the estimate when all other parameters stay fixed. Geographic distance does not by itself determine RTT.
- **Throughput ∝ 1/√p.** To double throughput you need **four times** less loss.
- **Long fat pipes need tiny loss rates**, which is why CUBIC and BBR exist. This Reno model should not be applied as a general throughput law for CUBIC or BBR.

Use the formula as a teaching comparison, not a unique diagnosis. Matching it does not rule out other bottlenecks. `ss -ti` exposes TCP state and counters on Linux; its retransmission counters are not automatically the model’s loss probability. Compare captures, application demand, receive windows, congestion-control state and link utilisation.

## Bufferbloat

Routers need buffers to absorb bursts. The traditional rule of thumb was one BDP of buffering per link. But memory became cheap, and many home routers, cable modems and mobile base stations were built with **far** more.

A saturated loss-based flow with a large tail-drop queue can sustain substantial queue occupancy. ECN, AQM, competing traffic and sender limits change this behaviour. For a packet joining a FIFO behind the following backlog:

```
   queue delay = buffer / link rate

   256 KiB at a 2 Mbit/s uplink:
   256 x 1024 x 8 / 2e6 = ~1.05 s
```

A packet behind that backlog waits about 1.05 seconds before its own transmission, ignoring overhead and changes in link rate. Other queues or priority classes can see different delays. Sustained excessive queueing is **bufferbloat**: high throughput can coexist with poor latency under load. The following RTTs are illustrative:

```
idle:           RTT  20 ms
upload running: RTT 1,070 ms
```

### Active queue management

Active queue management signals congestion before excessive persistent queues develop. Delay is the signal used by CoDel; other AQM designs use other measurements:

- **CoDel** (Controlled Delay, [RFC 8289](https://www.rfc-editor.org/rfc/rfc8289)) tracks how long packets wait. Its usual target and interval are 5 ms and 100 ms. Persistent excess sojourn time can trigger drops or ECN marks; a remaining-backlog check avoids needlessly starving the link. The target is not a hard upper bound on every packet’s delay, and finite buffers can still drop bursts.
- **fq_codel** ([RFC 8290](https://www.rfc-editor.org/rfc/rfc8290)) adds **flow queueing**: packets are hashed into queues, with modified deficit round-robin scheduling and CoDel. This reduces interference between bulk and sparse traffic; hash collisions and shared bottlenecks mean isolation is not absolute.
- **L4S** ([RFC 9330](https://www.rfc-editor.org/rfc/rfc9330)) describes an architecture using scalable congestion control and compatible ECN/AQM behaviour to target low queueing delay. It is not merely a replacement name for CoDel or a guarantee of one-millisecond end-to-end latency.

**Pacing** spreads transmissions and can reduce bursts; **BBR** uses a path model but can still build queues. Locate the actual bottleneck. When it is an inaccessible modem/ISP queue, suitable shaping on a controlled router can move the bottleneck to a queue where AQM is effective; measure the throughput trade-off.

## Head-of-line blocking

TCP delivers one ordered byte stream. If one segment is lost, later stream bytes cannot be delivered in order until the gap is filled (or the connection fails), even if those bytes belong to an unrelated request.

That matters for **HTTP/2**, which multiplexes many streams over a single TCP connection:

```
TCP stream:  [css][js][img1][img2]
loss in js:        ^
css: delivered
later bytes wait for gap recovery
```

Multiple HTTP/1.1 connections have separate TCP delivery ordering; HTTP/2 multiplexes streams on a connection. A TCP gap blocks later bytes on that connection, not resources already delivered or other connections. Recovery has no fixed one-RTT duration. Which HTTP version is faster depends on the workload, implementation and path.

## Ossification: why TCP is hard to change

TCP commonly runs in OS kernels, although user-space implementations exist. Devices along a path may inspect or rewrite it:

- **NATs and firewalls** track TCP state, rewrite ports and sometimes sequence numbers.
- **Middleboxes** strip unknown options, normalise headers, or drop packets that look unusual. Compatibility therefore needs testing and fallback. Multipath TCP includes fallback to ordinary TCP when its negotiation does not succeed.
- **Deployment dependencies** can include OS updates and peer support, depending on the extension. Sender-only congestion-control changes need not update both endpoints.

These constraints contribute to **ossification**: deployed equipment’s assumptions can restrict protocol evolution. This does not mean every TCP change takes a decade or that extensions have stopped.

## QUIC: the transport in user space

**QUIC** ([RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)), started at Google and standardised in 2021, is the transport under **HTTP/3**. It runs over UDP (lesson 1) and can be implemented in application **libraries** without changing the kernel; the protocol does not mandate an implementation location. Its design answers each of the problems above.

| Problem | QUIC's answer |
|---|---|
| Handshake RTTs | Combined transport/TLS setup; eligible 0-RTT sends early data, with replay restrictions |
| Head-of-line blocking | Per-stream ordering avoids TCP’s connection-wide delivery gap; shared limits remain |
| Ossification | Protected control frames reduce ossification; some fields remain observable |
| Slow deployment | Can ship in application libraries |
| Network changes | Connection IDs support eligible, validated client migration |

A few details worth knowing:

- **Protection.** QUIC protects payloads, including ACK/control frames, and masks selected header bits and packet numbers. Connection IDs and other fields remain observable. Initial packet keys are publicly derivable, so Initial protection does not provide confidentiality against an observer. The optional spin bit can assist RTT estimation.
- **Loss recovery.** A newly transmitted packet uses a new packet number within its packet-number space; stream data may be resent at the same stream offset. This removes TCP's original-versus-retransmission ACK ambiguity. It does not make loss detection infallible: reordering can still cause spurious loss declarations.
- **Migration.** After handshake confirmation, connection IDs can support client migration, subject to negotiated restrictions, address validation and a working new path. A zero-length connection ID constrains migration. Success and seamless latency are not guaranteed.
- **Shared effects.** Loss can reduce a connection's congestion window, and flow control or application dependencies can delay several streams. QUIC removes the requirement to wait for an unrelated stream's missing bytes; it does not promise complete independence.
- **Congestion control.** RFC 9002 gives a NewReno-like example; compatible alternatives can be implemented. A library deployment can update the algorithm without an OS upgrade.

### The costs of QUIC

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
- Round trips can dominate short transfers; longer transfers can be limited by capacity, congestion control, receive windows, endpoints or application demand.
- The Mathis approximation teaches Reno scaling under explicit assumptions; it is not a universal TCP ceiling or a standalone diagnosis.
- Queueing delay depends on queued work and service rate. AQM, scheduling and pacing address different parts of the problem.
- TCP's ordered byte stream can block later HTTP/2 bytes behind a gap.
- QUIC supports per-stream ordering, integrated TLS and eligible migration, while retaining shared resource constraints and deployment trade-offs.

> [!note] Evidence limits
> Universal browser connection counts, current TFO adoption, fixed protocol speedups and CPU costs are omitted because they require versioned deployment data or measurements not established here. The numerical timing and throughput examples are explicitly simplified models. This review did not run a WAN, QUIC migration or AQM performance experiment.

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
