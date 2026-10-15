---
id: nf-nyquist-signalling
sourceLesson: nf-physical-layer
title: The ideal Nyquist limit
level: basic
minutes: 3
summary: Apply the real-baseband zero-intersymbol-interference model and state its assumptions.
---

## Two hard limits

### Nyquist: how fast can you send symbols?

A channel's **bandwidth** in this sense is the width of the frequency range it passes, in hertz. For ideal zero-intersymbol-interference signalling (each symbol's pulse is shaped so it does not smear into its neighbours at the sampling instants) over a real low-pass channel with a specified one-sided bandwidth in hertz, Nyquist gives a maximum real symbol rate of twice that bandwidth. With M levels the corresponding uncoded rate is:

```formula
C = 2B log_2(M)
where
C: the maximum bit rate of the noiseless channel, in bits per second (bit/s)
B: the channel's bandwidth, in hertz (Hz): the width of the frequency range it passes, starting from zero (baseband)
M: the number of distinguishable signal levels
log_2: the base-2 logarithm; log_2(M) is the bits per symbol
Hz: hertz, one cycle per second
In words: a channel B hertz wide can carry at most 2 × B symbols per second, each carrying log_2(M) bits. More levels add bits only logarithmically.
```

For a hypothetical noiseless baseband channel 3.1 kHz wide with four levels:

```formula
C = 2 × 3,100 Hz × log_2(4)
C = 2 × 3,100 × 2 = 12,400 bit/s
where
C: the noiseless channel's maximum bit rate
Hz: hertz; 3.1 kHz (kilohertz) is 3,100 Hz
log_2: the base-2 logarithm; log_2(4) = 2 because 2^2 = 4
bit: one binary digit; bit/s is bits per second
s: seconds
In words: 6,200 symbols per second at 2 bits each gives 12.4 kbit/s.
```

In practice noise, not the Nyquist rate, sets how many levels can be told apart. That is Shannon's limit.

## Key takeaways
- The stated Nyquist model bounds real symbols per second by twice one-sided baseband bandwidth.
- More distinguishable levels carry more bits per symbol, but noise constrains usable levels.

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
