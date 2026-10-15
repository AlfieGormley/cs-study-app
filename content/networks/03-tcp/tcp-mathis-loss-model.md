---
id: tcp-mathis-loss-model
sourceLesson: tcp-performance
title: The Mathis model and its limits
level: advanced
minutes: 5
summary: The Mathis model and its limits, with worked examples and explicit assumptions.
---

## Long transfers are loss-bound: the Mathis formula

The Mathis model approximates a sustained Reno-style congestion-avoidance flow with light/moderate loss, sufficient sender data and receive window, and no retransmission timeouts. Use it to estimate how much throughput a given loss rate allows on a given path. The ideal periodic-loss sawtooth, with one ACK per segment, yields:

```formula
X ≈ (MSS / RTT) × (C / √p)
C = √(3 / 2) ≈ 1.22
where
X: the estimated throughput, in bytes per second (multiply by 8 for bits per second)
MSS: maximum segment size, the payload bytes per segment, for example 1,460 bytes
RTT: round-trip time, in seconds
C: a constant from the sawtooth shape, about 1.22 for one ACK per segment and periodic loss
p: the loss rate: the fraction of packets lost, for example 0.0001 for one in ten thousand
√: square root: the number that, multiplied by itself, gives the value inside; √0.0001 = 0.01
≈: approximately equal to
In words: throughput is one segment per round trip, scaled up by 1.22 divided by the square root of the loss rate.
```

Where does it come from? The sawtooth. With one loss in every 1/p packets, the window climbs from half its peak back to its peak at one segment per round trip, and the packets sent in one such cycle must equal 1/p. Solving for the peak window shows it grows with one over the square root of p:

```formula
N_cycle = (W / 2) × (3 × W / 4) = 1 / p
W = √(8 / (3 × p))
X = (3 × W / 4) × MSS / RTT
X = √(3 / 2) × MSS / (RTT √p)
where
N_cycle: the packets sent in one sawtooth cycle: W / 2 round trips at an average window of 3W/4
W: the peak window just before each loss, in segments
p: the loss rate, so one packet in every 1/p is lost
X: the average throughput, in bytes per second
MSS: maximum segment size, in bytes
RTT: round-trip time, in seconds
√: square root
In words: rarer losses let the window climb higher, but because the packets per cycle grow with the square of the window, the window only grows with one over the square root of the loss rate.
```

The worked example below is the first of the two results the code prints:

```formula
X ≈ ((1,460 × 8 bit) / (0.1 s))
    × (1.22 / 0.01)
X ≈ 116,800 bit/s × 122
X ≈ 14,249,600 bit/s ≈ 14 Mbit/s
where
X: the estimated throughput, in bits per second (bit/s)
bit: binary digit; 1,460 bytes × 8 = 11,680 bits per segment
s: seconds; the RTT is 100 ms = 0.1 s
Mbit/s: megabits per second, millions of bits per second
≈: approximately equal to
In words: with 1,460-byte segments, a 100 ms RTT and a 0.01 % loss rate (p = 0.0001, √p = 0.01), Reno-style TCP manages about 14 Mbit/s.
```

```python
from math import sqrt

def mathis(mss, rtt, p):
    """Reno-model estimate in bits/s."""
    valid = (mss > 0 and rtt > 0
             and 0 < p < 1)
    if not valid:
        raise ValueError("invalid input")
    # Convert payload bytes to bits.
    return mss * 8 / rtt * 1.22 / sqrt(p)

# Divide by a million to print Mbit/s.
print(mathis(1460, 0.1, 0.0001) / 1e6)
print(mathis(1460, 0.1, 0.01) / 1e6)
```

Rounded output:

```
14.2496
1.42496
```

At 100 ms RTT, the formula returns about **14 Mbit/s** for a 0.01% loss rate and **1.4 Mbit/s** for a 1% loss rate. These are model outputs, not universal caps or predictions for arbitrary packet-loss patterns. ACK behaviour and loss patterns change the constant; timeouts and other limits can invalidate the approximation. Within the model, two proportionalities matter:

```formula
X ∝ 1 / RTT
X ∝ 1 / √p
where
X: the estimated throughput
RTT: round-trip time
p: the loss rate
√: square root
∝: is proportional to: the left side changes by the same factor as the right side when everything else stays fixed
In words: double the round trip and throughput halves; quadruple the loss rate and throughput also halves.
```

- **Throughput falls in proportion to RTT.** Doubling RTT halves the estimate when all other parameters stay fixed. Geographic distance does not by itself determine RTT.
- **Throughput falls with the square root of loss.** To double throughput you need **four times** less loss.
- **Long fat pipes need tiny loss rates**, which is why CUBIC and BBR exist. This Reno model is not a general throughput law for CUBIC or BBR.

Use the formula as a teaching comparison, not a unique diagnosis. Matching it does not rule out other bottlenecks. `ss -ti` exposes TCP state and counters on Linux; its retransmission counters are not automatically the model’s loss probability. Compare captures, application demand, receive windows, congestion-control state and link utilisation.

## Key takeaways

- The Mathis approximation describes a qualified Reno-style loss/RTT model without retransmission timeouts.
- Its square-root dependence follows from the ideal sawtooth packet count.
- The formula is a comparison tool rather than a universal TCP ceiling or a unique bottleneck diagnosis.

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
