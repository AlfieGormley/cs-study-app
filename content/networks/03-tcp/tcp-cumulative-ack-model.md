---
id: tcp-cumulative-ack-model
sourceLesson: tcp-reliability
title: Tracing cumulative acknowledgements
level: intermediate
minutes: 3
summary: What a cumulative ACK says, why a hole produces duplicate ACKs, and a small model receiver that shows it.
---

## Cumulative acknowledgements

The receiver's ACK number means "I have **every byte before this one**". That is a **cumulative** ACK. It has two nice properties:

- A later cumulative ACK can cover data acknowledged by a lost ACK; if no later ACK arrives, loss can still delay progress.
- The receiver can ACK every other segment instead of every one (delayed ACK, taught in the flow-control units).

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

> [!analogy] Real-world analogy: A serial story by post
> A magazine posts you a serial story one chapter at a time, and asks you to tell them which chapter you need next. Chapter 2 goes missing, but chapters 3, 4 and 5 arrive. All you can honestly reply each time is "I've read up to chapter 1; please send chapter 2."
>
> **How it maps:** Your reply is a cumulative ACK: it names the first missing piece, so every chapter after the gap produces the same reply, a duplicate ACK. When chapter 2 finally arrives you can jump straight to "send chapter 6".
>
> **Where it stops:** TCP counts bytes, not chapters, and a sender may resend data in different-sized pieces. With SACK, a TCP receiver can also say which later ranges it holds, which this simple reply cannot.

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
        # Merge overlapping/touching ranges.
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
            # Only close a contiguous gap.
            if lo <= nxt:
                nxt = max(nxt, hi)
            else:
                held.append([lo, hi])
        # Print next missing byte and gaps.
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

## Key takeaways

- A cumulative ACK names the next missing sequence position in the contiguous prefix.
- Out-of-order coverage cannot advance that prefix until its gap fills.
- The toy receiver merges intervals and models coverage only, not a full TCP stack.

## Further reading

- [RFC 2018: TCP Selective Acknowledgment Options](https://www.rfc-editor.org/rfc/rfc2018)
- [RFC 5681: TCP Congestion Control (fast retransmit)](https://www.rfc-editor.org/rfc/rfc5681)
