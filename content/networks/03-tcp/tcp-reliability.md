---
id: tcp-reliability
title: Sequence numbers, ACKs and retransmission
level: intermediate
minutes: 14
summary: How TCP turns a lossy packet network into a reliable byte stream: cumulative ACKs, SACK, the RTO calculation from RFC 6298, fast retransmit on duplicate ACKs, and modern loss detection with RACK-TLP.
---

IP makes no promises. Packets are dropped when a router queue overflows, corrupted by a bad link, reordered when they take different paths, and occasionally duplicated. TCP provides an ordered byte stream, suppresses duplicate delivery within a connection and retransmits detected losses. Connections can fail after partial delivery, checksums are not perfect, and an error does not tell the sender exactly what the peer application processed. This is not exactly-once application execution.

The trick is old and simple. Number every byte, have the receiver say what it has, and resend whatever seems to be missing. The hard part is deciding *when* something is missing. Resend prematurely and you waste bandwidth on data that was only delayed; resend too late and the connection stalls. Most of this lesson is about that judgement.

## Numbering bytes, not packets

TCP's sequence numbers count **bytes**. A segment with `seq=1001` carrying 500 bytes holds bytes 1001 to 1500. The next segment starts at 1501. The "− 1" catches people out, so here it is as a formula:

```formula
B_last = S + L − 1
B_last = 1001 + 500 − 1 = 1500
S_next = S + L = 1001 + 500 = 1501
where
B_last: the sequence number of the segment's last data byte
S: the segment's sequence number: the number of its first data byte
L: how many data bytes the segment carries
S_next: where the next new segment starts, and the ACK number the receiver sends once it holds this segment
In words: a segment starting at 1001 with 500 bytes ends at byte 1500, because the first byte counts too; the next one starts at 1501.
```

Counting bytes rather than packets lets TCP **re-segment**: if a retransmission can be bigger or smaller than the original, the receiver doesn't care, because it only tracks byte ranges.

The sequence number is 32 bits, so it wraps after 2^32 bytes (4 GiB). At an ideal TCP payload rate of 10 Gbit/s, ignoring headers and control sequence positions, the wrap time is:

```formula
T_wrap = 2^32 × 8 bit / R
T_wrap = 34,359,738,368 bit / 10^10 bit/s
T_wrap ≈ 3.4 s
where
T_wrap: how long it takes to use every sequence number once, in seconds (s)
R: the payload rate, in bits per second (bit/s); here 10 Gbit/s, which is 10^10 bit/s
bit: binary digit; 8 bits make one byte, so 2^32 bytes (4,294,967,296) are 34,359,738,368 bits
s: seconds
≈: approximately equal to
In words: at 10 Gbit/s the whole 4 GiB sequence space is used up in about 3.4 seconds; four times the rate would make it four times quicker.
```

About 3.4 seconds is shorter than a segment might linger in the network. The **timestamp option** ([RFC 7323](https://www.rfc-editor.org/rfc/rfc7323)) supports **PAWS** (Protection Against Wrapped Sequences): negotiated timestamps and serial-number comparisons against maintained timestamp state help reject old duplicates. Timestamp wrap, idle expiry, segment validation and reset handling mean this is not simply “drop anything older than the largest timestamp ever seen”.

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

## The retransmission timeout (RTO)

The last line of defence is a timer. RFC 6298’s timer starts when outstanding data needs timing, restarts on an ACK acknowledging new data, and stops when all outstanding data is acknowledged. On expiry, the earliest unacknowledged segment is retransmitted. Thus expiry is not always exactly one RTO after that segment’s original send.

The RTO must be somewhat longer than a typical round trip, but RTTs vary from microseconds in a data centre to seconds on a satellite link, and they change during a connection. So TCP **measures** them. [RFC 6298](https://www.rfc-editor.org/rfc/rfc6298) defines the calculation, which Van Jacobson introduced in 1988.

It keeps two running averages: a smoothed RTT (SRTT), its best guess at the typical round trip, and an RTT variation (RTTVAR), how much the samples usually stray from that guess. With no history, the first measurement sets both:

```formula
SRTT = R
RTTVAR = R / 2
where
SRTT: smoothed round-trip time, TCP's running average of the RTT, in milliseconds (ms)
RTTVAR: round-trip time variation, a running average of how far samples stray from SRTT, in ms
R: the first measured RTT sample, in ms
ms: milliseconds, thousandths of a second
In words: with only one measurement, use it as the average and assume it might be off by half its size.
```

Each later sample nudges both averages towards the new evidence. This kind of update is an **exponentially weighted moving average** (EWMA): keep most of the old value and blend in a small share of the new one.

```formula
RTTVAR_new = (1 − β) × RTTVAR
           + β × |SRTT − R|
SRTT_new = (1 − α) × SRTT + α × R
where
RTTVAR_new: the updated variation, in milliseconds (ms)
RTTVAR: the variation before this sample
SRTT_new: the updated smoothed RTT, in ms
SRTT: the smoothed RTT before this sample (the old value, also used in the RTTVAR line)
R: the new RTT sample, in ms
α: alpha, the share of the new sample blended into SRTT; RFC 6298 uses 1/8 = 0.125
β: beta, the share of the new deviation blended into RTTVAR; RFC 6298 uses 1/4 = 0.25
|SRTT − R|: the absolute value of the difference: its size, ignoring the sign, so |100 − 120| = 20
ms: milliseconds
In words: each new sample moves SRTT one eighth of the way towards it, and moves RTTVAR a quarter of the way towards how surprising the sample was.
```

RTTVAR is updated **before** SRTT, using the old SRTT. The timeout then adds a safety margin of four variations to the average:

```formula
RTO = SRTT + max(G, 4 × RTTVAR)
where
RTO: retransmission timeout, how long to wait for an ACK before resending, in milliseconds (ms)
SRTT: the smoothed round-trip time, in ms
RTTVAR: the round-trip time variation, in ms
G: the clock granularity: the tick size of the system's timer, for example 1 ms; it stops the margin rounding down to zero
max: whichever of the two values in brackets is larger
ms: milliseconds
In words: wait for the typical round trip plus four times its usual wobble, so a steady path gets a tight timeout and a jittery one a generous margin.
```

A worked example with two samples, ignoring the minimum RTO floor and assuming the clock granularity is below 4 × RTTVAR:

```formula
SRTT_1 = 100 ms
RTTVAR_1 = 100 / 2 = 50 ms
RTO_1 = 100 + 4 × 50 = 300 ms
RTTVAR_2 = 0.75 × 50 + 0.25 × |100 − 120|
RTTVAR_2 = 37.5 + 5 = 42.5 ms
SRTT_2 = 0.875 × 100 + 0.125 × 120
SRTT_2 = 87.5 + 15 = 102.5 ms
RTO_2 = 102.5 + 4 × 42.5
RTO_2 = 102.5 + 170 = 272.5 ms
where
SRTT_1: the smoothed RTT after the first sample (100 ms), in milliseconds (ms)
RTTVAR_1: the variation after the first sample
RTO_1: the retransmission timeout after the first sample
RTTVAR_2: the variation after the second sample (120 ms); 0.75 is 1 − 1/4, 0.25 is 1/4, and |100 − 120| is the size of the difference ignoring its sign, 20
SRTT_2: the smoothed RTT after the second sample; 0.875 is 1 − 1/8 and 0.125 is 1/8
RTO_2: the retransmission timeout after the second sample
ms: milliseconds
In words: a slightly slower second sample nudges the average up to 102.5 ms but shrinks the variation, so the timeout falls from 300 ms to 272.5 ms.
```

The 4 × RTTVAR term is the important one. A connection with a steady RTT gets a tight timeout; a jittery one gets a generous margin, so it doesn't fire on every delay spike.

Other rules:

- **Minimum RTO.** RFC 6298 says a computed value below one second SHOULD be rounded up to one second. The retrieved Linux documentation lists a **200 ms default**, with route, socket and sysctl overrides; it is not a hard universal lower bound.
- **Initial RTO** before measurement: RFC 6298 recommends one second and permits a more conservative value.
- **Exponential RTO backoff.** Each time the timer fires for the same data, the RTO doubles (an optional RFC 6298 maximum must be at least 60 s; the retrieved Linux default maximum is 120 s and is configurable). This stops a sender hammering a path that is down.
- **Karn's algorithm.** Without a mechanism that disambiguates the measurement, do not take an RTT sample from retransmitted data: when the ACK arrives you can't tell whether it acknowledges the original or the copy. Negotiated timestamp echo rules can remove this ambiguity and permit such samples; the echo is selected by those rules, not invariably from the latest segment that triggered an ACK.

Exponential RTO backoff adds up quickly. If each wait doubles, the total time from the original send to the k-th retransmission is a doubling series:

```formula
T_k = RTO_0 × (1 + 2 + … + 2^{k − 1})
T_k = RTO_0 × (2^k − 1)
T_4 = 0.3 s × (16 − 1) = 4.5 s
where
T_k: the time from the original transmission to the k-th retransmission, in seconds (s)
RTO_0: the timeout before any RTO backoff; here 300 ms = 0.3 s
k: which retransmission we mean: 1, 2, 3 and so on
T_4: the same total for the fourth retransmission
…: and so on, continuing the pattern
s: seconds
In words: with a 300 ms starting timeout, the waits are 0.3, 0.6, 1.2 and 2.4 s, so the fourth retransmission goes out 4.5 s after the original.
```

A timeout delays recovery. Under RFC 5681, the TCP loss window after an RTO is at most one full-sized segment; this is a congestion-window change, not a specified one-segment-per-second rate. Linux documents `tcp_retries2 = 15` using a hypothetical default timeout of 924.6 seconds as a minimum under its stated RTO backoff model. Actual failure time depends on timers, overrides and application policy. An entirely idle connection with no outstanding data need not discover a vanished peer without probes or keepalives.

## Fast retransmit

Waiting for a timeout is slow. The duplicate ACKs from earlier are a quicker signal: repeated cumulative ACKs can indicate out-of-order arrival, although duplicate packets/ACKs and other events complicate that inference. Classic algorithms apply a specific duplicate-ACK definition, including window/data conditions.

One duplicate could just be **reordering**: two packets swapped places. So the classic rule ([RFC 5681](https://www.rfc-editor.org/rfc/rfc5681)) waits for **three duplicate ACKs**, then retransmits the missing segment straight away, without waiting for the timer. That is **fast retransmit**, usually paired with **TCP fast recovery** (lesson 5) to control the congestion window during recovery. Reno’s multiplicative reduction does not promise the application’s measured sending rate is exactly halved.

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
- **TLP** (Tail Loss Probe) schedules a probe timeout (PTO) whose baseline is two smoothed RTTs (see the formula below). Rules account for unavailable RTT estimates, possible delayed ACKs, the RTO deadline and probe eligibility. It prefers new data when available and permitted; otherwise it can retransmit the highest-sequence segment. A probe/ACK exchange may expose earlier tail loss to RACK. It does not guarantee delivery or a fixed total repair time.

The baseline probe timeout, for example on a path with a 40 ms smoothed RTT:

```formula
PTO = 2 × SRTT
PTO = 2 × 40 ms = 80 ms
where
PTO: probe timeout, how long TLP waits after the last send before probing, in milliseconds (ms)
SRTT: the smoothed round-trip time, in ms
ms: milliseconds
In words: if nothing has been acknowledged within about two round trips, send a probe instead of waiting for the much longer RTO.
```

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
- TCP numbers bytes; the 32-bit space wraps quickly at high speed, so timestamps (PAWS) disambiguate old segments.
- A cumulative ACK says "I have everything before N". Out-of-order arrivals produce duplicate ACKs.
- SACK reports selected received ranges (option space limits the count); D-SACK reports duplicate receipt, which can support recovery diagnostics.
- The RTO is the smoothed RTT plus the larger of the clock granularity and four times the RTT variation, subject to timer policy, bounds and RTO backoff; Karn’s rule avoids ambiguous RTT samples.
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
