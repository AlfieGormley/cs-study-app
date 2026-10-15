---
id: nf-shannon-capacity
sourceLesson: nf-physical-layer
title: Noise, SNR and Shannon capacity
level: basic
minutes: 3
summary: Convert decibels into a power ratio and calculate the capacity of a specified AWGN channel.
---

### Shannon: how much can noise allow?

For the band-limited additive white Gaussian noise (AWGN) model (random noise spread evenly over all frequencies and simply added to the signal), Shannon capacity is:

```formula
C = B log_2(1 + S / N)
where
C: the channel capacity: the highest bit rate that can be carried with arbitrarily few errors, in bits per second (bit/s)
B: the channel bandwidth, in hertz (Hz)
S: the average received signal power, in watts (W)
N: the average noise power in the channel, in watts (W)
log_2: the base-2 logarithm
Hz: hertz, cycles per second
W: watts, the unit of power; only the ratio S / N matters here
In words: capacity grows in direct proportion to bandwidth, but only logarithmically with signal-to-noise ratio: doubling B doubles C, while doubling S / N adds only about one bit per second per hertz once the signal is well above the noise.
```

Below capacity, suitable coding can make error probability arbitrarily small in the asymptotic model; this is not a promise of zero errors with finite packets. The signal-to-noise quantity in the capacity formula is a power ratio. Engineers quote the signal-to-noise ratio (**SNR**) in decibels:

```formula
SNR_dB = 10 × log_10(S / N)
S / N = 10^(SNR_dB / 10)
S / N = 10^(30 / 10) = 1000
where
SNR_dB: the signal-to-noise ratio in decibels (dB)
dB: decibels, ten times the base-10 logarithm of a power ratio
S: the signal power
N: the noise power
log_10: the base-10 logarithm: the power 10 must be raised to in order to give the number (log_10(1000) = 3)
In words: every 10 dB multiplies the power ratio by 10, so 30 dB means the signal is 1000 times stronger than the noise.
```

> [!example] A simplified single-channel capacity model
> Assume one flat AWGN channel (not a complete Wi-Fi/MIMO model): a 20 MHz channel with 30 dB SNR. The calculation below gives about **199 Mbit/s**. No modulation scheme, however clever, can beat that on that channel. To go faster you need more bandwidth (wider channels), more SNR, or more independent channels (more antennas, MIMO).

```formula
C = 20 × 10⁶ Hz × log_2(1 + 1000)
C ≈ 20 × 10⁶ × 9.97 bit/s
C ≈ 1.99 × 10⁸ bit/s ≈ 199 Mbit/s
where
C: the Shannon capacity of the channel
Hz: hertz; 20 MHz (megahertz) is 20 × 10⁶ Hz
log_2: the base-2 logarithm; log_2(1001) ≈ 9.97 because 2^10 = 1024
bit: one binary digit; bit/s is bits per second
s: seconds
Mbit/s: megabits per second (millions of bits per second)
≈: approximately equal to
In words: 20 million hertz times about 10 bits per second per hertz gives a limit of about 199 Mbit/s.
```

The model helps explain why attenuation can reduce achievable rate when transmit power, noise and other conditions are held fixed. Actual distance-to-rate behaviour also depends on interference, propagation paths, equipment and adaptation.

## Key takeaways
- Shannon capacity depends on bandwidth and signal-to-noise power ratio.
- The asymptotic coding theorem does not promise zero errors in finite packets or model an entire Wi-Fi system.

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
