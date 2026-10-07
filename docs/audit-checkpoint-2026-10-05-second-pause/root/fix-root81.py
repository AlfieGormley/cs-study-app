from pathlib import Path
p=Path('content/networks/03-tcp/tcp-reliability.md');s=p.read_text()
def r(a,b):
 global s
 assert a in s,a[:90]
 s=s.replace(a,b)
r('TCP\'s promise to the application is the opposite: **every byte, exactly once, in order**, or a clear error.','TCP provides an ordered byte stream, suppresses duplicate delivery within a connection and retransmits detected losses. Connections can fail after partial delivery, checksums are not perfect, and an error does not tell the sender exactly what the peer application processed. This is not exactly-once application execution.')
r('At 10 Gbit/s that takes about 3.4 seconds,','At an ideal TCP payload rate of 10 Gbit/s, ignoring headers and control sequence positions, that takes about 3.4 seconds,')
r('fixes this with **PAWS** (Protection Against Wrapped Sequences): a segment carrying an older timestamp than one already seen is discarded, even if its sequence number looks valid.','supports **PAWS** (Protection Against Wrapped Sequences): negotiated timestamps and serial-number comparisons against maintained timestamp state help reject old duplicates. Timestamp wrap, idle expiry, segment validation and reset handling mean this is not simply “drop anything older than the largest timestamp ever seen”.')
r('A lost ACK doesn\'t matter much; the next one covers it.','A later cumulative ACK can cover data acknowledged by a lost ACK; if no later ACK arrives, loss can still delay progress.')
r('Here is a toy receiver that shows the logic. It delivers in-order data, holds out-of-order segments, and jumps forward when the gap fills:','This sequence-space model merges received byte intervals, including overlap, and advances its cumulative point when gaps fill. It tracks coverage only: no payload comparison, sequence-number wrap, window limits, SYN/FIN, socket delivery, ACK timing or memory bounds. Positive ordinary integer byte positions are required:')
a=s.index('def rx(arrivals, nxt=1):');z=s.index('\nrx([',a)
s=s[:a]+'''def rx(arrivals, nxt=1):
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
                held + [(seq, seq + n)]):
            if merged and lo <= merged[-1][1]:
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
''' +s[z:]
r('ACK 1001 held [2001, 3001]\nACK 1001 held [2001, 3001, 4001]','ACK 1001 held [2001]\nACK 1001 held [2001]')
r('Now the sender knows exactly which hole to fill. SACK is agreed by a `SACK-permitted` option on the SYNs and is on by default in every mainstream stack.','These blocks report received ranges with exclusive right edges. They help identify gaps, but a missing report is not proof of loss: only a limited number of blocks fit, data may still be in flight, and a receiver can discard previously SACKed data before cumulative acknowledgement. Permission to send SACK is advertised directionally with `SACK-permitted` in SYN segments; support and configuration vary.')
r('That tells the sender a retransmission was **spurious** (the original was only delayed or reordered), so it can undo any slowdown it applied.','Duplicate receipt can support inference of a **spurious** retransmission and possible congestion-control undo, but can also result from network duplication. The sender must apply its algorithm’s checks; D-SACK is not unconditional proof of a particular cause or automatic permission to undo every reduction.')
r('When the oldest unacknowledged segment has gone unacknowledged for one **RTO**, the sender retransmits it.','RFC 6298’s timer starts when outstanding data needs timing, restarts on an ACK acknowledging new data, and stops when all outstanding data is acknowledged. On expiry, the earliest unacknowledged segment is retransmitted. Thus expiry is not always exactly one RTO after that segment’s original send.')
r('> First sample 100 ms:','> Ignoring the minimum RTO floor and assuming clock granularity is below 4×RTTVAR:\n> First sample 100 ms:')
r('RFC 6298 says 1 second. Linux uses **200 ms** (`TCP_RTO_MIN`), because 1 s is painfully long on fast networks. Data-centre operators sometimes lower it further per route.','RFC 6298 says a computed value below one second SHOULD be rounded up to one second. The retrieved Linux documentation lists a **200 ms default**, with route, socket and sysctl overrides; it is not a hard universal lower bound.')
r('**Initial RTO** before any measurement: 1 second.','**Initial RTO** before measurement: RFC 6298 recommends one second and permits a more conservative value.')
r('up to at least 60 s; Linux caps it at 120 s','an optional RFC 6298 maximum must be at least 60 s; the retrieved Linux default maximum is 120 s and is configurable')
r('Never take an RTT sample from a retransmitted segment:','Without a mechanism that disambiguates the measurement, do not take an RTT sample from retransmitted data:')
r('Timestamps remove the ambiguity, since the ACK echoes the timestamp of the segment that triggered it.','Negotiated timestamp echo rules can remove this ambiguity and permit such samples; the echo is selected by those rules, not invariably from the latest segment that triggered an ACK.')
a=s.index('A timeout is expensive.');z=s.index('\n## Fast retransmit',a)
s=s[:a]+'''A timeout delays recovery. Under RFC 5681, the loss window after an RTO is at most one full-sized segment; this is a congestion-window change, not a specified one-segment-per-second rate. Linux documents `tcp_retries2 = 15` using a hypothetical default timeout of 924.6 seconds as a lower bound under its stated backoff model. Actual failure time depends on timers, overrides and application policy. An entirely idle connection with no outstanding data need not discover a vanished peer without probes or keepalives.
''' +s[z:]
r('each one means "another segment arrived, but there is still a hole".','repeated cumulative ACKs can indicate out-of-order arrival, although duplicate packets/ACKs and other events complicate that inference. Classic algorithms apply a specific duplicate-ACK definition, including window/data conditions.')
r('so the sender halves its rate rather than collapsing to one segment.','to control the congestion window during recovery. Reno’s multiplicative reduction does not promise the application’s measured sending rate is exactly halved.')
r('It fails in two common cases:','Without additional mechanisms such as Limited Transmit or loss probes, the simple three-duplicate threshold can fail to trigger in these cases:')
r('The sender waits for a full RTO. For short web responses, that is most losses.','The simple scheme may then need the RTO; other loss-recovery mechanisms can intervene.')
r('Linux, Windows and FreeBSD now use **RACK-TLP**','**RACK-TLP**')
r('which reasons about **time** instead.','reasons about transmission and acknowledgement **time**. The retrieved Linux documentation describes RACK support; availability and defaults in other systems require version-specific confirmation.')
a=s.index('- **RACK** (Recent ACKnowledgement):');z=s.index('\n## Pitfalls',a)
s=s[:a]+'''- **RACK** (Recent ACKnowledgement) uses delivery of later-transmitted data, transmission times, an RTT estimate and a reordering window to infer losses of earlier unacknowledged transmissions. ACK/SACK information can provide this evidence; duplicate-ACK count alone is not the trigger. Reordering tolerance can adapt using D-SACK and other state.
- **TLP** (Tail Loss Probe) schedules a probe timeout whose baseline is 2×SRTT. Rules account for unavailable RTT estimates, possible delayed ACKs, the RTO deadline and probe eligibility. It prefers new data when available and permitted; otherwise it can retransmit the highest-sequence segment. A probe/ACK exchange may expose earlier tail loss to RACK. It does not guarantee delivery or a fixed total repair time.

| Mechanism | Main trigger | Timing qualification |
|---|---|---|
| RTO | Retransmission timer expires | Estimator, floor/cap and backoff apply |
| Classic fast retransmit | 3 qualifying duplicate ACKs | Depends on ACK arrivals |
| RACK | Delivery/time evidence of a hole | RTT and reordering state apply |
| TLP | Eligible probe timeout expires | Baseline 2×SRTT, with adjustments |
''' +s[z:]
r('which triggers spurious fast retransmits','which can trigger spurious fast retransmits')
r('whose authentication tag detects any corruption.','whose authenticated records detect alteration with a very small but nonzero forgery probability under their cryptographic assumptions. Neither layer gives a mathematical guarantee against every error.')
r('An ACK means the peer\'s **kernel** has the bytes,','A cumulative ACK means the peer’s **TCP endpoint** accepted the preceding stream positions,')
r('A sustained rate above about 1% usually means congestion or a bad link.','Interpret retransmission counters with their definitions, denominator, traffic pattern and captures; no universal one-percent threshold identifies a cause.')
r('SACK tells the sender exactly which blocks arrived (up to 3–4 blocks); D-SACK reports spurious retransmissions.','SACK reports selected received ranges (option space limits the count); D-SACK reports duplicate receipt, which can support recovery diagnostics.')
r('RTO = SRTT + 4×RTTVAR, minimum 200 ms on Linux, doubled on every repeat timeout; Karn\'s rule bars samples from retransmitted segments.','The RTO estimator is SRTT + max(G, 4×RTTVAR), subject to timer policy, bounds and backoff; Karn’s rule avoids ambiguous RTT samples.')
s+='\n> [!note] Content omitted after review\n> Cross-platform adoption claims, fixed RACK/TLP repair times and a universal retransmission-health threshold are omitted because this review did not establish reliable versioned measurements. The receiver is a byte-coverage model, not a complete TCP stack.\n\n- [Linux retransmission timer controls](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)\n'
p.write_text(s)
