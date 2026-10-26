---
id: nf-shannon-capacity
sourceLesson: nf-physical-layer
title: Noise, SNR and Shannon capacity
level: basic
minutes: 3
summary: Explain noisy-channel capacity, decibel power ratios and bandwidth-versus-power trade-offs.
---

A receiver must distinguish signal from noise. Choosing more modulation states cannot create unlimited reliable capacity when noise blurs those states.

## A limit for a specified noisy channel

For a band-limited **additive white Gaussian noise (AWGN)** channel, noise is modelled as random Gaussian variation added to the signal, with equal average noise power in equal-width frequency bands across the channel. Shannon capacity gives the highest reliable information rate in this model under its average-power constraint.

At rates below capacity, suitable coding can make error probability arbitrarily small as coding length grows. This is not a promise of zero errors for finite packets.

```formula reference
C = B log_2(1 + S / N)
where
C: Shannon capacity of the stated AWGN model, in bits per second
B: channel bandwidth in hertz
S: average received signal power in watts
N: average noise power in the channel bandwidth, in watts
log_2: base-two logarithm
In words: holding the signal-to-noise power ratio fixed, more bandwidth raises capacity in direct proportion; at high signal-to-noise ratios, increasing signal power gives progressively smaller proportional gains.
```

The **signal-to-noise ratio (SNR)** compares signal power with noise power. Engineers often express it in **decibels (dB)**: every additional 10 dB multiplies the power ratio by ten. Thus 30 dB represents a signal power 1000 times the noise power. A dB value is not itself the power ratio.

```formula reference
SNR_dB = 10 log_10(S / N)
S / N = 10^(SNR_dB / 10)
where
SNR_dB: signal-to-noise ratio in decibels
S: signal power in watts
N: noise power in watts, measured over the same channel
log_10: base-ten logarithm
In words: decibels describe a power ratio logarithmically; an increase of ten decibels means ten times the ratio, rather than ten more units of signal power.
```

## What can improve capacity?

For a hypothetical single flat AWGN channel, 20 MHz at 30 dB SNR has about 199 Mbit/s capacity. At the same SNR, doubling bandwidth doubles capacity. Doubling signal power while holding noise and bandwidth fixed gives a much smaller proportional improvement at this high SNR.

Keeping SNR fixed while widening a channel is an explicit assumption. If total signal power stays fixed and noise spectral density stays constant, a wider channel admits more noise and reduces SNR.

Actual Wi-Fi systems also involve multiple spatial channels, contention, pilots, coding and protocol overhead. Independent spatial channels can add capacity, but simply adding antennas does not guarantee independence. Attenuation, interference, propagation paths and equipment affect achievable rates.

## Key takeaways
- Capacity depends on channel bandwidth and signal-to-noise power ratio.
- More modulation levels cannot defeat the stated channel limit.
- The asymptotic theorem does not promise error-free finite packets or model a complete Wi-Fi network.

## Further reading
- [Shannon–Hartley theorem — Wikipedia](https://en.wikipedia.org/wiki/Shannon%E2%80%93Hartley_theorem)
- [Line code — Wikipedia](https://en.wikipedia.org/wiki/Line_code)
- [Optical fiber — Wikipedia](https://en.wikipedia.org/wiki/Optical_fiber)
- [Velocity factor — Wikipedia](https://en.wikipedia.org/wiki/Velocity_factor)
- [Ethernet physical layer — Wikipedia](https://en.wikipedia.org/wiki/Ethernet_physical_layer)
- [Hollow-core optical fiber — Wikipedia](https://en.wikipedia.org/wiki/Hollow-core_optical_fiber)

- [Corning SMF-28 Ultra data sheet (July 2025)](https://www.corning.com/content/dam/corning/media/worldwide/coc/documents/Fiber/product-information-sheets/PI-1424-AEN.pdf)
- [Cisco 10GBASE transceiver specifications](https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/data_sheet_c78-455693.html)
- [Texas Instruments DP83825I PHY data sheet](https://www.ti.com/lit/ds/symlink/dp83825i.pdf)
- [Shannon: A Mathematical Theory of Communication](https://web.mit.edu/6.976/www/handout/shannon.pdf)

- [Belden 2433 cable specifications](https://catalog.belden.com/techdata/EN/2433_techdata.pdf)
