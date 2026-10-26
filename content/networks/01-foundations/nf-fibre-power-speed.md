---
id: nf-fibre-power-speed
sourceLesson: nf-physical-layer
title: Fibre reach, loss and pulse speed
level: basic
minutes: 3
summary: Compare fibre modes, interpret optical loss and explain how group index affects pulse speed.
---

## Fibre

An optical fibre is a glass **core** surrounded by **cladding** of slightly lower refractive index. The refractive-index structure guides optical modes; **total internal reflection** is a useful ray-model explanation, particularly for multimode fibre. A laser or LED switches on and off (or modulates phase and amplitude) to encode symbols.

- **Multi-mode fibre** has a wide core (50 or 62.5 µm). Light takes many paths ("modes") of slightly different length, so pulses spread out (modal dispersion). It is cheap with 850 nm optics and good for a few hundred metres: 10GBASE-SR reaches about 300 m on OM3 and 400 m on OM4.
- **Single-mode fibre** supports one spatial mode over its specified wavelength range; it is not literally one geometrical ray. Core diameter and mode-field diameter are distinct properties. With 1310 or 1550 nm lasers it reaches tens of kilometres directly, and thousands with amplifiers.
- For a hypothetical fibre loss of **0.2 dB/km**, an 80 km span loses 16 dB before connectors/splices. Actual loss is product- and wavelength-dependent; amplifier spacing also depends on the optical power/noise budget, not a universal distance.
- **Wavelength-division multiplexing** (DWDM) sends dozens of wavelengths through one fibre, each its own channel. Total capacity depends on channel count, modulation, coding, equipment and reach; no universal capacity figure is implied.
- The optical signal is not subject to electromagnetic pickup like copper wiring, but fibre can still be tapped or physically damaged. Fibre is not a substitute for encryption. Both optical and copper links are used in data centres.

Fibre loss is quoted in decibels because losses along a route then simply add. The surviving power fraction changes multiplicatively.

The hypothetical 80 km span has 16 dB loss, leaving about 2.5% of its launched optical power before connector and splice losses. A fixed number of decibels represents a multiplicative power change, rather than a fixed percentage of the original launch power.

```formula reference
A = αd
P_out / P_in = 10^(−A / 10)
where
A: total distributed attenuation in decibels
α: loss per kilometre, in decibels per kilometre, for the specified fibre and wavelength
d: span length in kilometres
P_out: received optical power in watts after the modelled span loss
P_in: launched optical power in watts
In words: distributed loss adds in decibels as the span gets longer; each additional ten decibels leaves one tenth of the power that would otherwise remain.
```

### Why pulses travel slower in glass

For pulse propagation, use the fibre’s **effective group index**, not simply the bulk phase refractive index. Corning’s July 2025 SMF-28 Ultra data sheet lists a typical group index of 1.4682 at 1550 nm. Rounding to 1.47 means that the pulse speed is the vacuum speed of light divided by 1.47.

Pulses therefore travel at about 68% of the vacuum speed of light in this example, taking about 4.9 microseconds per kilometre. A higher group index means slower pulse propagation.

Wavelength and fibre construction matter.

On copper, the signal is an electromagnetic wave guided by the conductors and dielectric. Its speed is not the electron drift velocity. **Velocity factor** depends on cable construction: copper is not universally slower than glass. For example, Belden 2433 specifies a nominal 72% of c, above the roughly 68% used in the glass-fibre example. Compare complete link latency, including PHY electronics, when choosing a medium.

> [!note] Lower propagation delay
> Radio in air travels close to c. Hollow-core fibre can also reduce propagation delay because much of its optical field travels through an air-filled region. Microsoft has reported Azure deployment. Exact universal hollow-core velocity and trading-route latency figures are omitted because they require a specific fibre, wavelength, route and measurement source.

## Key takeaways
- Fibre reach depends on mode, optics, attenuation and the optical budget.
- Group index determines pulse delay; copper velocity is construction-dependent.

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
