---
id: tcp-byte-sequence-wrap
sourceLesson: tcp-reliability
title: Byte numbering, wrap and PAWS
level: intermediate
minutes: 3
summary: Why TCP numbers bytes rather than packets, and how timestamps protect fast connections when the numbers wrap.
---

IP makes no promises. Packets are dropped when a router queue overflows, corrupted by a bad link, reordered when they take different paths, and occasionally duplicated. TCP provides an ordered byte stream, suppresses duplicate delivery within a connection and retransmits detected losses. Connections can fail after partial delivery, checksums are not perfect, and an error does not tell the sender exactly what the peer application processed. This is not exactly-once application execution.

The trick is old and simple. Number every byte, have the receiver say what it has, and resend whatever seems to be missing. The hard part is deciding *when* something is missing. Resend prematurely and you waste bandwidth on data that was only delayed; resend too late and the connection stalls. Most of this lesson is about that judgement.

## Numbering bytes, not packets

TCP's sequence numbers count **bytes**. A segment starting at sequence number 1001 and carrying 500 bytes holds bytes 1001 to 1500: the first byte counts, so the last is one less than 1001 + 500. The next segment starts at 1501, and 1501 is also the ACK number the receiver sends once it holds this segment.

Counting bytes rather than packets lets TCP **re-segment**: if a retransmission can be bigger or smaller than the original, the receiver doesn't care, because it only tracks byte ranges.

The sequence number is 32 bits, so it wraps after 4,294,967,296 data bytes (4 GiB). A fast connection gets through that quickly: at an ideal 10 Gbit/s of payload the whole space is used in about 3.4 seconds, and at 40 Gbit/s in under a second.

About 3.4 seconds is shorter than a segment might linger in the network. The **timestamp option** ([RFC 7323](https://www.rfc-editor.org/rfc/rfc7323)) supports **PAWS** (Protection Against Wrapped Sequences): negotiated timestamps and serial-number comparisons against maintained timestamp state help reject old duplicates. Timestamp wrap, idle expiry, segment validation and reset handling mean this is not simply “drop anything older than the largest timestamp ever seen”.

> [!analogy] Real-world analogy: A car odometer that rolls over
> Imagine a car odometer with so few digits that it rolls back to zero every few kilometres on a fast motorway. If someone hands you an old logbook entry reading "1,234", the number alone cannot tell you whether it is from this lap of the dial or an earlier one; you also need the date it was written.
>
> **How it maps:** The odometer is TCP's 32-bit sequence space, which a fast flow reuses within seconds. A delayed old segment can carry a sequence number that looks valid again. The date on the logbook entry is the TCP timestamp: PAWS compares it with recent timestamps to reject the stale segment.
>
> **Where it stops:** TCP timestamps also wrap eventually and are not wall-clock dates, so RFC 7323 adds rules for long idle periods and validation. And unlike a logbook, the receiver keeps only recent timestamp state, not a full history.

## Key takeaways

- TCP numbers byte positions, so retransmitted bytes can be repacketised.
- A segment length advances the next position; its final byte is one position earlier.
- High payload rates can wrap the sequence space quickly; negotiated timestamps support PAWS with additional validation rules.

## Further reading

- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
