---
id: tcp-reno-round-trace
sourceLesson: tcp-congestion
title: Tracing a simplified Reno sawtooth
level: advanced
minutes: 3
summary: Tracing a simplified Reno sawtooth, with worked examples and explicit assumptions.
---

## A cwnd trace

This illustrative per-round model counts segments, assumes a full flight and ideal ACK clocking, starts with cwnd at 1 segment and ssthresh at 32, and treats each event as a separate recovery episode. It omits temporary recovery inflation, repeated-RTO rules, partial ACKs, retransmission scheduling and receiver limits. Its integer halving and hard threshold cap are teaching choices, not a full Reno implementation:

```python
def reno(n, events, cwnd=1, ssth=32):
    if (type(n) is not int or n < 0
            or type(cwnd) is not int
            or type(ssth) is not int
            or cwnd < 1 or ssth < 2):
        raise ValueError("bad model inputs")
    for when, event in events.items():
        if (type(when) is not int
                or not 0 <= when < n
                or event not in
                ("dupack", "timeout")):
            raise ValueError("bad event")
    for r in range(n):
        ev = events.get(r, "")
        # Report state BEFORE this event.
        print(r, cwnd, ssth, ev)
        # Events model separate episodes.
        if ev == "dupack":
            ssth = max(cwnd // 2, 2)
            cwnd = ssth
        elif ev == "timeout":
            ssth = max(cwnd // 2, 2)
            cwnd = 1
        elif cwnd < ssth:
            # Model a hard threshold cap.
            cwnd = min(cwnd * 2, ssth)
        else:
            cwnd += 1

reno(16, {8: "dupack", 12: "timeout"})
```

| RTT | cwnd | ssthresh | Event |
|---|---|---|---|
| 0–5 | 1, 2, 4, 8, 16, 32 | 32 | slow start |
| 6–8 | 33, 34, 35 | 32 | avoidance |
| 8 | 35 | 32 | 3 dup ACKs |
| 9–12 | 17, 18, 19, 20 | 17 | avoidance |
| 12 | 20 | 17 | timeout |
| 13–15 | 1, 2, 4 | 10 | slow start |

Plotted as bars, one per RTT, this is the famous **sawtooth**:

```
RTT
  0 # 1
  1 ## 2
  2 #### 4
  3 ######## 8
  4 ################ 16
  5 ################################ 32
  6 ################################# 33
  7 ################################## 34
  8 ################################### 35
  9 ################# 17
 10 ################## 18
 11 ################### 19
 12 #################### 20
 13 # 1
 14 ## 2
 15 #### 4
```

A simplified stable sawtooth with linear growth from half the peak to the peak has a time-average window of three quarters of the peak:

```formula
W_avg = ((W / 2) + W) / 2 = 0.75 × W
W_avg = 0.75 × 40 = 30
where
W_avg: the average congestion window over one sawtooth cycle, in segments
W: the peak window just before each loss; here 40 segments
In words: a window that climbs steadily from 20 to 40 averages 30, three quarters of its peak.
```

Timeouts, unequal cycles, variable RTTs and application limits change that model.

## Key takeaways

- The trace is an integer, per-round teaching model with a hard threshold cap.
- Printed state precedes the event update, so the following row reflects a cut.
- A linear half-peak-to-peak sawtooth averages three quarters of the peak only under that model.

## Further reading

- [Congestion Avoidance and Control — Van Jacobson (1988)](https://ee.lbl.gov/papers/congavoid.pdf)
- [RFC 5681: TCP Congestion Control](https://www.rfc-editor.org/rfc/rfc5681)
- [RFC 9438: CUBIC for Fast and Long-Distance Networks](https://www.rfc-editor.org/rfc/rfc9438)
- [BBR: Congestion-Based Congestion Control — Google Research](https://research.google/pubs/bbr-congestion-based-congestion-control-2/)
- [RFC 3168: Explicit Congestion Notification](https://www.rfc-editor.org/rfc/rfc3168)
- [TCP congestion control — Wikipedia](https://en.wikipedia.org/wiki/TCP_congestion_control)
- [Linux v6.12 BBRv1 implementation](https://github.com/torvalds/linux/blob/v6.12/net/ipv4/tcp_bbr.c)
- [BBRv3 IETF draft, July 2026](https://datatracker.ietf.org/doc/html/draft-ietf-ccwg-bbr-06)

- [Chiu and Jain: increase/decrease algorithms, original paper](https://pages.cs.wisc.edu/~suman/courses/740/papers/chiu89isdn.pdf)
