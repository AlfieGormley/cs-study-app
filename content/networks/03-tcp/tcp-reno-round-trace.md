---
id: tcp-reno-round-trace
sourceLesson: tcp-congestion
title: Tracing a simplified Reno sawtooth
level: advanced
minutes: 3
summary: Reading a Reno congestion-window trace: slow start, the sawtooth, and the difference a timeout makes.
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

How to read the trace:

- **Doubling** (rounds 0–5) is slow start. It stops at ssthresh, not at a loss.
- **Steady +1 per round** (rounds 6–8 and 9–12) is congestion avoidance.
- **A drop to about half** (round 9) is the duplicate-ACK response: ssthresh and cwnd both become half the window at the loss.
- **A drop to one segment followed by doubling** (round 13 onward) is the timeout response: ssthresh becomes half the window at the loss, cwnd restarts at one, and slow start runs again until the new threshold.

In a long run with only duplicate-ACK losses, the window climbs steadily from half its peak to its peak and is then halved again: the sawtooth. Under that simplified model the window averages about three quarters of its peak. Timeouts, unequal cycles, variable RTTs and application limits change that model.

## Key takeaways

- The trace is an integer, per-round teaching model with a hard threshold cap.
- Printed state precedes the event update, so the following row reflects a cut.
- A linear half-peak-to-peak sawtooth averages three quarters of the peak only under that model.

## Further reading

- [RFC 5681: TCP Congestion Control](https://www.rfc-editor.org/rfc/rfc5681)
