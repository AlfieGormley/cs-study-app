---
id: wm-wifi-modulation
title: Modulation, signal quality and capacity
level: basic
minutes: 3
summary: More constellation points add bits logarithmically and need cleaner signals.
sourceLesson: wm-wifi
---

Each new Wi-Fi generation advertises a denser modulation: 256-QAM, then 1024-QAM, then 4096-QAM. The gain per step is smaller than the numbers suggest, and only clients with a very clean signal can use it.

## Why denser modulation needs a cleaner signal

A QAM symbol is one of a fixed number of possible points (amplitude-and-phase combinations). The receiver measures the incoming wave and decides which point was sent. The number of bits one symbol carries grows with the logarithm of the number of points:

```formula essential
b = log_2(M)
where
b: the number of bits carried by one QAM symbol on one subcarrier
M: the number of distinct points in the QAM constellation, e.g. 256, 1024 or 4096
log_2: the base-2 logarithm: the power you must raise 2 to in order to get the number, so log_2(1024) = 10 because 2^10 = 1024
In words: every doubling of the number of constellation points adds just one bit per symbol.
```

So 256-QAM carries 8 bits, 1024-QAM 10 bits and 4096-QAM 12 bits. Going from 1024 to 4096 points adds only 2 bits (+20%), but squeezes four times as many points into the same space, so neighbouring points sit much closer together. Noise that a 256-QAM receiver shrugs off makes a 4096-QAM receiver pick the wrong point.

That is why **rate adaptation** matters: a client near the access point with little interference may use the densest modulation, while one further away or behind walls drops to a sparser, more robust one. Achievable modulation depends on signal quality, interference and hardware, not a fixed distance boundary.

> [!analogy] Real-world analogy: Reading a finely marked dial through fogged glasses
> A dial marked in tenths tells you more per glance than one marked in halves. But if your glasses are fogged, the fine marks blur together and you misread them, while the coarse marks are still easy.
>
> **How it maps:** Each mark is a constellation point and one glance is one symbol. More marks carry more information per glance (more bits per symbol), but only when the view is clear (high signal-to-noise ratio). Fog is noise and interference; switching to a coarser dial is rate adaptation choosing a lower-order modulation.
>
> **Where it stops:** QAM points are spread over two dimensions (amplitude and phase), not along one scale. Errors are probabilistic, and error-correcting codes repair some misreadings, so a radio does not simply fail at one fog level.

## The ceiling: Shannon capacity

The networks foundations module introduced the **Shannon–Hartley theorem**: for a channel disturbed by random (Gaussian) noise, no modulation or coding can reliably exceed a capacity set by bandwidth and signal-to-noise ratio (SNR).

```formula reference
C = B log_2(1 + (S / N))
where
C: the channel capacity: the highest reliable data rate theoretically possible, in bits per second (bit/s)
B: the channel bandwidth, in hertz (Hz)
S: the received signal power, in watts (W)
N: the noise power in the same channel, in watts (W)
log_2: the base-2 logarithm
In words: capacity grows in proportion to channel width but only with the logarithm of signal quality, so doubling the channel width roughly doubles the ceiling while doubling signal power adds much less once the signal is already well above the noise.
```

For example, a 20 MHz channel at 30 dB SNR (signal 1000 times the noise power) has a theoretical ceiling of about 200 Mbit/s, roughly 10 bits per second per hertz. SNR is quoted in decibels: every extra 10 dB means ten times the power ratio.

The ceiling is not a minimum-SNR specification for 1024-QAM. Coding, error targets, interference and hardware determine a real radio's requirements. Real radios also lose rate to coding and guard intervals, so the rates in the PHY-rate lesson sit below this bound. The practical lesson: wider channels and more spatial streams add capacity roughly in proportion, while denser modulation adds only a little and only where the signal is clean.

## Key takeaways
- More constellation points add bits logarithmically and need cleaner signals.
- Rate adaptation picks the densest modulation the current signal quality supports.
- The Gaussian-noise capacity model is a theoretical bound, not a radio throughput measurement.

## Further reading
- [Shannon: A Mathematical Theory of Communication (original paper)](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)
- [Quadrature amplitude modulation — Wikipedia](https://en.wikipedia.org/wiki/Quadrature_amplitude_modulation)
