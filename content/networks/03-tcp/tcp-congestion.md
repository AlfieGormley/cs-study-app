---
id: tcp-congestion
title: Congestion control: Reno, CUBIC and BBR
level: advanced
minutes: 16
summary: Why TCP must slow down for the network's sake, slow start and AIMD traced RTT by RTT, Reno's fast recovery, CUBIC's cubic growth curve, BBR's model-based pacing, ECN, and the fairness trade-offs between them.
---

In October 1986, throughput between Lawrence Berkeley Laboratory and UC Berkeley, 400 yards apart, fell from 32 kbit/s to **40 bit/s**. Jacobson and Karels attributed much of the problem to transport implementations’ response to congestion: when packets were lost, senders retransmitted aggressively, which caused more loss, which caused more retransmissions. The network was busy carrying copies of packets that would be dropped anyway. This was **congestion collapse**.

Van Jacobson's 1988 fix, still at the heart of TCP, is that each sender must **infer** how much the network can take and back off when it is overloaded. Signals include ACK progress, losses, delays and, when deployed, explicit congestion marks from routers.

## The congestion window

The sender keeps a second window alongside the receiver's rwnd: the **congestion window** (cwnd), a sender-side limit on outstanding data derived from its congestion-control policy, not a direct measurement of network storage. In a simplified steady-state model, new-data sending respects `min(cwnd, rwnd)`; recovery, probes, pacing and earlier in-flight data require more detailed accounting.

For a continuously backlogged, window-limited flow under stable conditions:

```
rate ~= cwnd / RTT
```

Congestion control is the set of rules for growing and shrinking cwnd. Every algorithm answers the same three questions:

1. How fast do I grow when things look fine?
2. What counts as a congestion signal?
3. How much do I shrink when I see one?

## Slow start

A new connection knows nothing about the path. Its **initial window** is implementation/configuration dependent. RFC 6928 experimentally permits an upper bound `min(10*MSS, max(2*MSS, 14600))` bytes, giving IW10 for MSS 1,460; it does not require every TCP to start at ten segments. Classic slow start increases cwnd on ACKs of new data, with rules affected by ACK frequency and byte-counting variants.

In the idealised model with an ACK per full segment and enough data/window capacity, cwnd **doubles per round**. Delayed ACKs, pacing, limits and different growth rules alter that approximation. "Slow" is a historical joke: it's slow compared to blasting a full window at once, but it is exponential growth.

Slow start ends when cwnd reaches the **slow start threshold** (ssthresh), or when loss is detected.

> [!example] Why short transfers are latency-bound
> A 100,000-byte response needs 69 payload segments at MSS 1,460. Under ideal round-based IW10 doubling, it uses three flights: 10, 20, then 39 (capacity 40). Ignoring serialization, those flights can start near t=0, RTT and 2×RTT. Last-byte arrival additionally needs forward-path delay; final acknowledgement needs return delay. Three flights do not automatically mean 300 ms of extra transfer time at RTT 100 ms. This is why CDNs place servers near users and why HTTP connection reuse matters.

## Congestion avoidance: AIMD

In classic Reno congestion avoidance, the sender probes with approximately **one MSS of cwnd growth per RTT** under ideal ACK/traffic assumptions. Crossing ssthresh does not prove that the path is currently near capacity. That is **additive increase**.

When loss signals congestion, cwnd is cut by a **fraction**: **multiplicative decrease**. Together, **AIMD** has an important property, shown by Chiu and Jain in 1989: in a simplified synchronous feedback model with comparable flows, rates can converge toward equal shares. Real TCP fairness depends on RTTs, loss/mark patterns, starting times, bottlenecks and algorithm variants. Each increase adds the same amount to both; each decrease takes more from the larger. Over many cycles the difference shrinks.

## Reno: reacting to two kinds of loss

TCP Reno ([RFC 5681](https://www.rfc-editor.org/rfc/rfc5681)) treats the two loss signals from lesson 3 differently:

- **Three qualifying duplicate ACKs**: classic fast retransmit enters fast recovery. The RFC 5681 threshold uses `max(FlightSize/2, 2*SMSS)` as an upper bound, not universally cwnd/2. Reno temporarily inflates cwnd to ssthresh + 3×SMSS, with further duplicate-ACK handling, then deflates on a recovery-completing ACK. The simplified trace below shows only the post-recovery reduction.
- **Retransmission timeout**: on the first RTO retransmission of that data, apply the threshold rule; set the loss window to at most one full-sized segment and resume slow start. A repeated RTO for the same data does not repeatedly halve ssthresh under the RFC rule. Loss/timeout observations do not prove “mild congestion” or “nothing is getting through”.

Its predecessor, Tahoe, reset to one segment on every loss. **NewReno** ([RFC 6582](https://www.rfc-editor.org/rfc/rfc6582)) fixes Reno's handling of several losses in one window; SACK supplies additional received-range information, but limited reports, reordering and receiver reneging still require a loss-recovery algorithm.

### A cwnd trace

This illustrative per-round model counts segments, assumes a full flight and ideal ACK clock, starts at cwnd=1/ssthresh=32, and treats each event as a separate recovery episode. It omits temporary recovery inflation, repeated-RTO rules, partial ACKs, retransmission scheduling and receiver limits. Its integer halving and hard threshold cap are teaching choices, not a full Reno implementation:

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
        print(r, cwnd, ssth, ev)
        if ev == "dupack":
            ssth = max(cwnd // 2, 2)
            cwnd = ssth
        elif ev == "timeout":
            ssth = max(cwnd // 2, 2)
            cwnd = 1
        elif cwnd < ssth:
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

A simplified stable sawtooth with linear growth from W/2 to W has time-average window **0.75 W**. Timeouts, unequal cycles, variable RTTs and application limits change that model.

### Why Reno fails on fast, long paths

Additive increase is one segment per RTT, no matter how big the window. Consider a model counting 1,500 payload bytes per segment, ignoring headers, at 10 Gbit/s and 100 ms RTT:

```
W = 10e9 x 0.1 / (1500 x 8)
  = ~83,333 segments
```

After one loss halves the window, getting back to W takes about 41,667 RTTs: **over an hour**, during which a single further loss starts the climb again. In the distinct average-window model in RFC 3649, sustaining this average rate requires roughly one congestion event per five billion packets ([RFC 3649](https://www.rfc-editor.org/rfc/rfc3649)). This illustrates Reno’s scaling limitation under the stated assumptions, not an absolute impossibility for every fast path or workload.

## CUBIC: grow by the clock, not the ACK

**CUBIC** ([RFC 9438](https://www.rfc-editor.org/rfc/rfc9438)) is widely implemented; the actual default is chosen by the operating system, version and configuration. It makes two changes.

First, a gentler cut: its congestion-event reduction normally uses **β = 0.7**; recovery and RTO handling require additional rules. It does not reduce independently for every lost packet.

Second, after a loss it grows cwnd as a **cubic function of time since the loss**, to define a target, with actual window updates still driven by ACK processing:

```
W(t) = C (t - K)^3 + Wmax

C = 0.4, b = 0.7, Wmax = cwnd at loss
K = cbrt(Wmax (1 - b) / C)
```

In this simplified epoch, `K` is where the pure cubic target reaches Wmax. Actual behaviour also includes the Reno-friendly estimate, fast convergence, ACK updates and exclusion of application-limited periods. The curve is fast when far below Wmax, flattens as it approaches the old limit (where loss happened last time), then accelerates again to probe for new bandwidth.

For example, after a loss at Wmax = 100 segments, cwnd drops to 70 and K = cbrt(100 × 0.3 / 0.4) = cbrt(75) ≈ 4.2 s:

| t (s) | W(t) | Phase |
|---|---|---|
| 0 | 70.0 | just after loss |
| 1 | 86.7 | rapid regrowth |
| 2 | 95.6 | slowing |
| 4.2 | 100.0 | plateau at Wmax |
| 6 | 102.3 | probing |
| 7 | 108.6 | accelerating |

Because growth depends on **elapsed time**, the cubic window target reduces dependence on ACK-round counting outside the Reno-friendly region. Similar windows do not imply equal throughput for different RTTs; CUBIC still has RTT bias. CUBIC also has a **Reno-friendly region**: if a standard Reno flow would have a larger window at this moment (common on short-RTT paths), CUBIC uses the Reno value, to improve coexistence. That model comparison is not a guarantee that every actual CUBIC flow always outperforms an actual Reno flow.

Like Reno, CUBIC is **loss-based**: it responds to congestion events, which can include ECN marks before buffer overflow. Without suitable queue management its probing can build queues. That has two costs. It fills router buffers, adding queueing delay (lesson 6), and it misreads **random** loss (Wi-Fi corruption, policers) as congestion.

## BBR: model the path

Google's **BBR** (Bottleneck Bandwidth and Round-trip propagation time, 2016) takes a different approach: it estimates path properties from delivery feedback and controls pacing/in-flight data from a model. The numerical details below describe **BBRv1 as implemented in Linux v6.12**, not all BBR versions.

- **BtlBw**: the bottleneck bandwidth, estimated using a windowed maximum of delivery-rate samples over ten packet-timed rounds in this version, with safeguards for limited sending and other conditions.
- **RTprop**: the round-trip propagation delay, estimated using a ten-second windowed minimum in this version. The estimate includes endpoint/serialization effects and may include persistent queueing; it is not pure physical propagation delay.

Their product is the BDP. BBR **paces** packets at about BtlBw and caps in-flight data at a small multiple of the BDP (a base gain near 2× in BBRv1, with minimum-window, ACK-aggregation and other adjustments). The ideal operating point is to keep the pipe full without building a queue.

To observe available delivery capacity the sender must offer enough data; probing beyond it can build a queue and obscure the baseline RTT. Reducing in-flight data can help refresh the RTT estimate. These are estimation challenges, not a theorem that full utilisation always requires a queue. So BBR cycles through phases:

| Phase | Behaviour |
|---|---|
| Startup | Pacing gain about 2.89, designed for rapid growth; exits after three qualifying rounds without 25% bandwidth growth |
| Drain | Gain below 1 to empty the queue Startup built |
| ProbeBW | Gains 1.25, 0.75, then six 1.0 phases; transitions use timing/in-flight checks |
| ProbeRTT | On qualifying minimum-RTT expiry, reduce toward 4 packets; duration includes at least 200 ms and a completed round |

BBRv1 aims to keep utilisation high without persistently filling queues and can avoid repeated Reno/CUBIC-style reductions for non-congestion loss. It still performs loss recovery and includes loss-related recovery/policer handling; “ignores all loss” is false. Results depend on the path and competing traffic, so there is no guaranteed speedup or fairness outcome.

Later BBR versions change the model and loss response. The **July 2026 BBRv3 IETF draft** retrieved here remains experimental and explicitly does **not** specify a particular ECN algorithm; if a connection advertises ECN support, however, CE marks must still be treated as congestion. Thus, claims that every BBRv2/v3 implementation has one common ECN algorithm are omitted. Linux BBR uses packet pacing, via `fq` or internal pacing support in the examined implementation.

## ECN: congestion without loss

Loss-oriented controllers can also react to explicit congestion indications. **Explicit Congestion Notification** ([RFC 3168](https://www.rfc-editor.org/rfc/rfc3168)) lets a router **mark** a packet instead of dropping it:

1. In classic TCP ECN (RFC 3168), both sides negotiate ECN capability in the handshake. Later ECN schemes have different feedback details.
2. Packets are sent with an ECN-capable codepoint in the IP header.
3. A capable queue-management algorithm may set **CE** (Congestion Experienced) on eligible packets instead of dropping; overload and policy can still cause drops.
4. The receiver echoes it with **ECE** in its ACKs; the sender reduces cwnd as for a loss and replies with **CWR**.

A delivered CE-marked packet does not need retransmission merely because it was marked. ECN does not prevent unrelated loss or guarantee a one-RTT improvement. Data-centre algorithms such as **DCTCP** go further, scaling the reduction by the **fraction** of marked packets to keep queues tiny.

## Choosing and checking

Example Linux inspection commands (shown output is illustrative, not a guaranteed default):

```
$ sysctl net.ipv4.tcp_congestion_control
net.ipv4.tcp_congestion_control = cubic
$ ss -ti   # per-connection cwnd, rtt
```

An application can choose per socket with the `TCP_CONGESTION` option. Congestion control runs on the **sender**, so a server can change its TCP sender algorithm without requiring the client to use the same controller. Whether performance improves must be measured; receiver feedback and available implementation support still matter.

## Key takeaways
- Congestion control protects the network: both windows constrain ordinary new-data sending. A continuously backlogged, cwnd-limited steady flow has rate ≈ cwnd / RTT.
- Idealised slow start grows exponentially; Reno avoidance grows roughly one segment per RTT. Initial windows and fairness depend on the model and implementation.
- Reno uses flight-size-based threshold and fast-recovery rules; an RTO invokes a much smaller loss window.
- Reno’s linear growth can recover very slowly on high-BDP paths. CUBIC uses a time-based cubic target, a Reno-friendly region and normally a 30% congestion-event reduction.
- BBR versions estimate delivery capacity and baseline RTT to control pacing, with version-specific loss handling and coexistence trade-offs.
- ECN lets routers signal congestion by marking rather than dropping.

## Further reading
- [Congestion Avoidance and Control — Van Jacobson (1988)](https://ee.lbl.gov/papers/congavoid.pdf)
- [RFC 5681: TCP Congestion Control](https://www.rfc-editor.org/rfc/rfc5681)
- [RFC 9438: CUBIC for Fast and Long-Distance Networks](https://www.rfc-editor.org/rfc/rfc9438)
- [BBR: Congestion-Based Congestion Control — Google Research](https://research.google/pubs/bbr-congestion-based-congestion-control-2/)
- [RFC 3168: Explicit Congestion Notification](https://www.rfc-editor.org/rfc/rfc3168)
- [TCP congestion control — Wikipedia](https://en.wikipedia.org/wiki/TCP_congestion_control)

> [!note] Content omitted after review
> Universal operating-system defaults, guaranteed equal-share fairness and fixed BBR speedups are omitted because this review did not establish suitable versioned measurements. Congestion-control traces here are explicit models, not packet-level benchmarks.

- [Linux v6.12 BBRv1 implementation](https://github.com/torvalds/linux/blob/v6.12/net/ipv4/tcp_bbr.c)
- [BBRv3 IETF draft, July 2026](https://datatracker.ietf.org/doc/html/draft-ietf-ccwg-bbr-06)
