---
id: wm-wifi-modulation
title: Modulation, signal quality and capacity
level: basic
minutes: 4
summary: More constellation points add bits logarithmically and need cleaner signals.
sourceLesson: wm-wifi
---

This unit focuses on modulation, signal quality and capacity. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Why denser modulation needs a cleaner signal

A QAM symbol is one of a fixed number of possible points (amplitude-and-phase combinations). The number of bits one symbol carries is the base-2 logarithm of the number of points:

```formula
b = log_2(M)
b = log_2(1024) = 10
where
b: the number of bits carried by one QAM symbol on one subcarrier
M: the number of distinct points in the QAM constellation, e.g. 256, 1024 or 4096
log_2: the base-2 logarithm: the power you must raise 2 to in order to get the number, so log_2(1024) = 10 because 2^10 = 1024
In words: every doubling of the number of constellation points adds just one bit per symbol.
```

So 256-QAM carries 8 bits (eight doublings of 1 give 256), 1024-QAM 10 bits and 4096-QAM 12 bits. Going from 1024 to 4096 points adds only 2 bits (+20%), but squeezes four times as many points into the same space, so the receiver must tell apart points that sit much closer together. Noise that a 256-QAM receiver shrugs off makes a 4096-QAM receiver pick the wrong point.

The **Shannon–Hartley theorem** sets the theoretical ceiling on any channel, whatever the modulation. It applies to a channel disturbed by random (Gaussian) noise:

```formula
C = B log_2(1 + (S / N))
C = 20 MHz × log_2(1 + 1000)
C ≈ 20 MHz × 9.97 ≈ 199 Mbit/s
where
C: the channel capacity: the highest error-free data rate theoretically possible, in bits per second (bit/s)
B: the channel bandwidth, in hertz (Hz); here a 20 MHz Wi-Fi channel
S: the received signal power, in watts (W)
N: the noise power in the same channel, in watts (W)
S / N: the signal-to-noise ratio (SNR) as a plain ratio; 1000 here, which is 30 dB
log_2: the base-2 logarithm (log_2(1024) = 10)
MHz: megahertz, one million hertz
Hz: hertz, cycles per second
Mbit/s: megabits per second, one million bits per second
≈: approximately equal to
In words: capacity grows in proportion to bandwidth, but only with the logarithm of signal quality, so doubling channel width roughly doubles capacity while doubling signal power adds only about 1 bit/s per hertz once the signal is already well above the noise.
```

At 30 dB SNR this ideal Gaussian-noise ceiling is about 10 bits per second per hertz. It is not a minimum SNR specification for 1024-QAM: modulation, coding, error targets, interference and hardware determine an actual radio’s requirements and usable locations. SNR is usually quoted in decibels:

```formula
SNR_dB = 10 × log_10(S / N)
SNR_dB = 10 × log_10(1000) = 30 dB
where
SNR_dB: the signal-to-noise ratio expressed in decibels (dB)
S: the received signal power, in watts (W)
N: the noise power, in watts (W)
log_10: the base-10 logarithm, so log_10(1000) = 3 because 10^3 = 1000
dB: decibel, a logarithmic unit for a power ratio: +10 dB means ten times the power, +3 dB about double
In words: every extra 10 dB of SNR means the signal is ten times stronger relative to the noise.
```

Real radios fall short of the Shannon limit and also lose rate to coding and guard intervals, so the later PHY-rate unit’s table sits below it.

## Key takeaways
- More constellation points add bits logarithmically and need cleaner signals.
- The Gaussian-noise capacity model is a theoretical bound, not a radio throughput measurement.

## Further reading
- [Shannon: A Mathematical Theory of Communication (original paper)](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)
