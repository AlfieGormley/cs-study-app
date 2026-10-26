---
id: nf-nyquist-signalling
sourceLesson: nf-physical-layer
title: The ideal Nyquist limit
level: basic
minutes: 3
summary: Explain the ideal symbol-rate limit, bandwidth conventions and limits of adding levels.
---

A physical channel passes a limited range of frequencies. Here **bandwidth** means that frequency range in hertz, rather than a network's advertised bit rate.

## Symbols must remain distinguishable

Pulses can spread into neighbouring symbol intervals, causing **intersymbol interference**. Ideal pulse shaping can arrange for neighbouring pulses to contribute zero at the receiver's sampling instants.

For a noiseless real low-pass channel, one-sided bandwidth is measured from zero frequency to the upper limit. The ideal Nyquist zero-intersymbol-interference model supports a maximum real symbol rate of twice that bandwidth. This is a model with particular bandwidth and signalling conventions, not a universal factor to apply to every radio rate.

More distinguishable levels allow more bits in each symbol. Four levels carry two bits per symbol; increasing the number of levels does not increase bits per symbol in direct proportion.

```formula reference
C = 2B log_2(M)
where
C: maximum uncoded bit rate in the stated noiseless real-baseband model, in bits per second
B: one-sided low-pass bandwidth in hertz, measured from zero frequency to the upper limit
M: number of distinguishable signal levels; a power of two for a fixed whole-bit mapping
log_2: base-two logarithm; it gives bits per symbol for this mapping
In words: the stated ideal model limits the symbol rate through bandwidth, while the number of distinguishable levels determines how many bits each symbol carries.
```

For example, a hypothetical noiseless 3.1 kHz baseband channel with four levels permits 6,200 real symbols per second, each carrying two bits, for 12.4 kbit/s. These values illustrate the assumptions; finite implementations and overhead require separate accounting.

## Noise changes the problem

The noiseless model does not decide how many closely spaced levels a real receiver can reliably distinguish. Noise can blur them together. Shannon's noisy-channel limit addresses that additional constraint.

Increasing the number of levels on an unchanged noisy channel therefore does not guarantee a usable rate increase. Both bandwidth and reliable distinction matter.

## Key takeaways
- The Nyquist zero-ISI model constrains real symbol rate for its stated one-sided baseband bandwidth.
- More levels carry more bits per symbol, but noise constrains usable signalling.

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
