---
id: tcp-byte-sequence-wrap
sourceLesson: tcp-reliability
title: Byte numbering, wrap and PAWS
level: intermediate
minutes: 3
summary: Byte numbering, wrap and PAWS, with worked examples and explicit assumptions.
---

IP makes no promises. Packets are dropped when a router queue overflows, corrupted by a bad link, reordered when they take different paths, and occasionally duplicated. TCP provides an ordered byte stream, suppresses duplicate delivery within a connection and retransmits detected losses. Connections can fail after partial delivery, checksums are not perfect, and an error does not tell the sender exactly what the peer application processed. This is not exactly-once application execution.

The trick is old and simple. Number every byte, have the receiver say what it has, and resend whatever seems to be missing. The hard part is deciding *when* something is missing. Resend prematurely and you waste bandwidth on data that was only delayed; resend too late and the connection stalls. Most of this lesson is about that judgement.

## Numbering bytes, not packets

TCP's sequence numbers count **bytes**. A segment starting at sequence number 1001 and carrying 500 bytes holds bytes 1001 to 1500. The next segment starts at 1501. The "− 1" catches people out, so here it is as a formula:

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

The sequence number is 32 bits, so it wraps after 4,294,967,296 data bytes (4 GiB). At an ideal TCP payload rate of 10 Gbit/s, ignoring headers and control sequence positions, the wrap time is:

```formula
T_wrap = 2^32 × 8 bit / R
T_wrap = 34,359,738,368 bit / (10^10 bit/s)
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

## Key takeaways

- TCP numbers byte positions, so retransmitted bytes can be repacketised.
- A segment length advances the next position; its final byte is one position earlier.
- High payload rates can wrap the sequence space quickly; negotiated timestamps support PAWS with additional validation rules.

## Further reading

- [RFC 6298: Computing TCP's Retransmission Timer](https://www.rfc-editor.org/rfc/rfc6298)
- [RFC 2018: TCP Selective Acknowledgment Options](https://www.rfc-editor.org/rfc/rfc2018)
- [RFC 8985: The RACK-TLP Loss Detection Algorithm for TCP](https://www.rfc-editor.org/rfc/rfc8985)
- [RFC 5681: TCP Congestion Control (fast retransmit)](https://www.rfc-editor.org/rfc/rfc5681)
- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
- [Congestion Avoidance and Control — Van Jacobson (1988)](https://ee.lbl.gov/papers/congavoid.pdf)
- [Linux retransmission timer controls](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
