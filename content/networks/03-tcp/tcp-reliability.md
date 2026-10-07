---
id: tcp-reliability
title: Sequence numbers, ACKs and retransmission
level: intermediate
minutes: 14
summary: How TCP turns a lossy packet network into a reliable byte stream: cumulative ACKs, SACK, the RTO calculation from RFC 6298, fast retransmit on duplicate ACKs, and modern loss detection with RACK-TLP.
---

IP makes no promises. Packets are dropped when a router queue overflows, corrupted by a bad link, reordered when they take different paths, and occasionally duplicated. TCP provides an ordered byte stream, suppresses duplicate delivery within a connection and retransmits detected losses. Connections can fail after partial delivery, checksums are not perfect, and an error does not tell the sender exactly what the peer application processed. This is not exactly-once application execution.

The trick is old and simple. Number every byte, have the receiver say what it has, and resend whatever seems to be missing. The hard part is deciding *when* something is missing. Resend too early and you waste bandwidth on data that was only delayed; resend too late and the connection stalls. Most of this lesson is about that judgement.

## Numbering bytes, not packets

TCP's sequence numbers count **bytes**. A segment with `seq=1001` carrying 500 bytes holds bytes 1001 to 1500. The next segment starts at 1501.

Counting bytes rather than packets lets TCP **re-segment**: if a retransmission can be bigger or smaller than the original, the receiver doesn't care, because it only tracks byte ranges.

The sequence number is 32 bits, so it wraps after 4 GiB. At an ideal TCP payload rate of 10 Gbit/s, ignoring headers and control sequence positions, that takes about 3.4 seconds, which is shorter than a segment might linger in the network. The **timestamp option** ([RFC 7323](https://www.rfc-editor.org/rfc/rfc7323)) supports **PAWS** (Protection Against Wrapped Sequences): negotiated timestamps and serial-number comparisons against maintained timestamp state help reject old duplicates. Timestamp wrap, idle expiry, segment validation and reset handling mean this is not simply “drop anything older than the largest timestamp ever seen”.

## Cumulative acknowledgements

The receiver's ACK number means "I have **every byte before this one**". That is a **cumulative** ACK. It has two nice properties:

- A later cumulative ACK can cover data acknowledged by a lost ACK; if no later ACK arrives, loss can still delay progress.
- The receiver can ACK every other segment instead of every one (delayed ACK, lesson 4).

Its weakness shows when something in the middle is lost. Suppose the sender sends five 1,000-byte segments and the second is dropped:

```
Sender                     Receiver
seq=1    ------------->    ACK 1001
seq=1001 ----X (lost)
seq=2001 ------------->    ACK 1001
seq=3001 ------------->    ACK 1001
seq=4001 ------------->    ACK 1001
```

The receiver has bytes 2001–5000, but a cumulative ACK can only say "I'm still waiting for 1001". Those repeated ACKs are **duplicate ACKs**.

This sequence-space model merges received byte intervals, including overlap, and advances its cumulative point when gaps fill. It tracks coverage only: no payload comparison, sequence-number wrap, window limits, SYN/FIN, socket delivery, ACK timing or memory bounds. Nonnegative ordinary integer byte positions and positive interval lengths are required:

```python
def rx(arrivals, nxt=1):
    if type(nxt) is not int or nxt < 0:
        raise ValueError("bad start")
    held = []  # half-open intervals
    for seq, n in arrivals:
        if (type(seq) is not int
                or type(n) is not int
                or seq < 0 or n <= 0):
            raise ValueError("bad interval")
        merged = []
        for lo, hi in sorted(
                held + [[seq, seq + n]]):
            joins = (merged and
                     lo <= merged[-1][1])
            if joins:
                merged[-1][1] = max(
                    merged[-1][1], hi)
            else:
                merged.append([lo, hi])
        held = []
        for lo, hi in merged:
            if lo <= nxt:
                nxt = max(nxt, hi)
            else:
                held.append([lo, hi])
        print("ACK", nxt, "held",
              [lo for lo, hi in held])

rx([(1, 1000), (2001, 1000), (3001, 1000),
    (4001, 1000), (1001, 1000)])
```

Output:

```
ACK 1001 held []
ACK 1001 held [2001]
ACK 1001 held [2001]
ACK 1001 held [2001]
ACK 5001 held []
```

When the retransmitted 1001 arrives, the ACK leaps from 1001 to 5001: the receiver had the rest all along.

## Selective acknowledgement (SACK)

Cumulative ACKs leave the sender guessing. Was only 1001 lost, or 1001 and 3001? A cautious sender (**Go-Back-N** style) resends everything from 1001; an optimistic one resends 1001 and waits a round trip to learn more.

**SACK** ([RFC 2018](https://www.rfc-editor.org/rfc/rfc2018)) lets the receiver list the blocks it holds beyond the cumulative point:

```
ACK 1001  SACK 2001-5001
```

These blocks report received ranges with exclusive right edges. They help identify gaps, but a missing report is not proof of loss: only a limited number of blocks fit, data may still be in flight, and a receiver can discard previously SACKed data before cumulative acknowledgement. Permission to send SACK is advertised directionally with `SACK-permitted` in SYN segments; support and configuration vary. A SACK option fits at most **four** blocks, or **three** alongside the timestamp option, because TCP options are limited to 40 bytes.

A related extension, **D-SACK** ([RFC 2883](https://www.rfc-editor.org/rfc/rfc2883)), uses the first SACK block to report a segment received **twice**. Duplicate receipt can support inference of a **spurious** retransmission and possible congestion-control undo, but can also result from network duplication. The sender must apply its algorithm’s checks; D-SACK is not unconditional proof of a particular cause or automatic permission to undo every reduction.

## The retransmission timeout (RTO)

The safety net is a timer. RFC 6298’s timer starts when outstanding data needs timing, restarts on an ACK acknowledging new data, and stops when all outstanding data is acknowledged. On expiry, the earliest unacknowledged segment is retransmitted. Thus expiry is not always exactly one RTO after that segment’s original send.

The RTO must be a bit longer than a typical round trip, but RTTs vary from microseconds in a data centre to seconds on a satellite link, and they change during a connection. So TCP **measures** them. [RFC 6298](https://www.rfc-editor.org/rfc/rfc6298) defines the calculation, which Van Jacobson introduced in 1988.

It keeps a smoothed RTT (SRTT) and a smoothed mean deviation (RTTVAR), with α = 1/8 and β = 1/4:

```
first sample R:
  SRTT   = R
  RTTVAR = R / 2

each later sample R:
  RTTVAR = (1-b)*RTTVAR + b*|SRTT - R|
  SRTT   = (1-a)*SRTT   + a*R

RTO = SRTT + max(G, 4 * RTTVAR)
```

`G` is the clock granularity. RTTVAR is updated **before** SRTT, using the old SRTT.

> [!example] Two samples
> Ignoring the minimum RTO floor and assuming clock granularity is below 4×RTTVAR:
> First sample 100 ms: SRTT = 100, RTTVAR = 50, RTO = 100 + 200 = 300 ms.
>
> Second sample 120 ms: RTTVAR = 0.75 × 50 + 0.25 × 20 = 42.5. SRTT = 0.875 × 100 + 0.125 × 120 = 102.5. RTO = 102.5 + 170 = 272.5 ms.

The `4 × RTTVAR` term is the important one. A connection with a steady RTT gets a tight timeout; a jittery one gets a generous margin, so it doesn't fire on every delay spike.

Other rules:

- **Minimum RTO.** RFC 6298 says a computed value below one second SHOULD be rounded up to one second. The retrieved Linux documentation lists a **200 ms default**, with route, socket and sysctl overrides; it is not a hard universal lower bound.
- **Initial RTO** before measurement: RFC 6298 recommends one second and permits a more conservative value.
- **Exponential backoff.** Each time the timer fires for the same data, the RTO doubles (an optional RFC 6298 maximum must be at least 60 s; the retrieved Linux default maximum is 120 s and is configurable). This stops a sender hammering a path that is down.
- **Karn's algorithm.** Without a mechanism that disambiguates the measurement, do not take an RTT sample from retransmitted data: when the ACK arrives you can't tell whether it acknowledges the original or the copy. Negotiated timestamp echo rules can remove this ambiguity and permit such samples; the echo is selected by those rules, not invariably from the latest segment that triggered an ACK.

A timeout delays recovery. Under RFC 5681, the loss window after an RTO is at most one full-sized segment; this is a congestion-window change, not a specified one-segment-per-second rate. Linux documents `tcp_retries2 = 15` using a hypothetical default timeout of 924.6 seconds as a lower bound under its stated backoff model. Actual failure time depends on timers, overrides and application policy. An entirely idle connection with no outstanding data need not discover a vanished peer without probes or keepalives.

## Fast retransmit

Waiting for a timeout is slow. The duplicate ACKs from earlier are a quicker signal: repeated cumulative ACKs can indicate out-of-order arrival, although duplicate packets/ACKs and other events complicate that inference. Classic algorithms apply a specific duplicate-ACK definition, including window/data conditions.

One duplicate could just be **reordering**: two packets swapped places. So the classic rule ([RFC 5681](https://www.rfc-editor.org/rfc/rfc5681)) waits for **three duplicate ACKs**, then retransmits the missing segment straight away, without waiting for the timer. That is **fast retransmit**, usually paired with **fast recovery** (lesson 5) to control the congestion window during recovery. Reno’s multiplicative reduction does not promise the application’s measured sending rate is exactly halved.

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

## Modern loss detection: RACK-TLP

Counting duplicate ACKs is crude. **RACK-TLP** ([RFC 8985](https://www.rfc-editor.org/rfc/rfc8985)), reasons about transmission and acknowledgement **time**. The retrieved Linux documentation describes RACK support; availability and defaults in other systems require version-specific confirmation.

- **RACK** (Recent ACKnowledgement) uses delivery of later-transmitted data, transmission times, an RTT estimate and a reordering window to infer losses of earlier unacknowledged transmissions. ACK/SACK information can provide this evidence; duplicate-ACK count alone is not the trigger. Reordering tolerance can adapt using D-SACK and other state.
- **TLP** (Tail Loss Probe) schedules a probe timeout whose baseline is 2×SRTT. Rules account for unavailable RTT estimates, possible delayed ACKs, the RTO deadline and probe eligibility. It prefers new data when available and permitted; otherwise it can retransmit the highest-sequence segment. A probe/ACK exchange may expose earlier tail loss to RACK. It does not guarantee delivery or a fixed total repair time.

| Mechanism | Main trigger | Timing qualification |
|---|---|---|
| RTO | Retransmission timer expires | Estimator, floor/cap and backoff apply |
| Classic fast retransmit | 3 qualifying duplicate ACKs | Depends on ACK arrivals |
| RACK | Delivery/time evidence of a hole | RTT and reordering state apply |
| TLP | Eligible probe timeout expires | Baseline 2×SRTT, with adjustments |

## Pitfalls and real-world notes

- **Reordering looks like loss.** Multipath links and some load balancers reorder packets, which can trigger spurious fast retransmits and needless slowdowns. RACK's adaptive window and D-SACK undo help, and per-flow ECMP hashing can reduce reordering caused by per-packet path changes.
- **Checksums are weak.** TCP's 16-bit checksum misses some multi-bit errors. Real systems lean on link-layer CRCs and, increasingly, TLS, whose authenticated records detect alteration with a very small but nonzero forgery probability under their cryptographic assumptions. Neither layer gives a mathematical guarantee against every error.
- **Transport acknowledgement is not application acknowledgement.** A cumulative ACK means the peer’s **TCP endpoint** accepted the preceding stream positions, not that the application processed them. If you need "the server saved it", you need an application-level acknowledgement.
- **Retransmission rate is a health signal.** On Linux, `ss -ti` shows per-connection `rto`, `rtt` and `retrans`, and `nstat` shows `TcpRetransSegs`. Interpret retransmission counters with their definitions, denominator, traffic pattern and captures; no universal one-percent threshold identifies a cause.

## Key takeaways
- TCP numbers bytes; the 32-bit space wraps quickly at high speed, so timestamps (PAWS) disambiguate old segments.
- A cumulative ACK says "I have everything before N". Out-of-order arrivals produce duplicate ACKs.
- SACK reports selected received ranges (option space limits the count); D-SACK reports duplicate receipt, which can support recovery diagnostics.
- The RTO estimator is SRTT + max(G, 4×RTTVAR), subject to timer policy, bounds and backoff; Karn’s rule avoids ambiguous RTT samples.
- Classic fast retransmit uses three qualifying duplicate ACKs; without additional mechanisms, insufficient following data can leave tail losses or small flights waiting for the timer.
- RACK-TLP detects loss by time and probes the tail, turning many timeouts into quick repairs.

## Further reading
- [RFC 6298: Computing TCP's Retransmission Timer](https://www.rfc-editor.org/rfc/rfc6298)
- [RFC 2018: TCP Selective Acknowledgment Options](https://www.rfc-editor.org/rfc/rfc2018)
- [RFC 8985: The RACK-TLP Loss Detection Algorithm for TCP](https://www.rfc-editor.org/rfc/rfc8985)
- [RFC 5681: TCP Congestion Control (fast retransmit)](https://www.rfc-editor.org/rfc/rfc5681)
- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
- [Congestion Avoidance and Control — Van Jacobson (1988)](https://ee.lbl.gov/papers/congavoid.pdf)

> [!note] Content omitted after review
> Cross-platform adoption claims, fixed RACK/TLP repair times and a universal retransmission-health threshold are omitted because this review did not establish reliable versioned measurements. The receiver is a byte-coverage model, not a complete TCP stack.

- [Linux retransmission timer controls](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
