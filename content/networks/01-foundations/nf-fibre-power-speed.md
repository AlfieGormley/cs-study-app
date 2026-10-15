---
id: nf-fibre-power-speed
sourceLesson: nf-physical-layer
title: Fibre reach, loss and pulse speed
level: basic
minutes: 4
summary: Compare fibre modes, calculate attenuation and use group index for pulse propagation.
---

## Fibre

An optical fibre is a glass **core** surrounded by **cladding** of slightly lower refractive index. The refractive-index structure guides optical modes; **total internal reflection** is a useful ray-model explanation, particularly for multimode fibre. A laser or LED switches on and off (or modulates phase and amplitude) to encode symbols.

- **Multi-mode fibre** has a wide core (50 or 62.5 µm). Light takes many paths ("modes") of slightly different length, so pulses spread out (modal dispersion). It is cheap with 850 nm optics and good for a few hundred metres: 10GBASE-SR reaches about 300 m on OM3 and 400 m on OM4.
- **Single-mode fibre** supports one spatial mode over its specified wavelength range; it is not literally one geometrical ray. Core diameter and mode-field diameter are distinct properties. With 1310 or 1550 nm lasers it reaches tens of kilometres directly, and thousands with amplifiers.
- For a hypothetical fibre loss of **0.2 dB/km**, an 80 km span loses 0.2 × 80 = 16 dB before connectors/splices (the calculation below turns that into a fraction of the power). Actual loss is product- and wavelength-dependent; amplifier spacing also depends on the optical power/noise budget, not a universal distance.
- **Wavelength-division multiplexing** (DWDM) sends dozens of wavelengths through one fibre, each its own channel. Total capacity depends on channel count, modulation, coding, equipment and reach; no universal capacity figure is implied.
- The optical signal is not subject to electromagnetic pickup like copper wiring, but fibre can still be tapped or physically damaged. Fibre is not a substitute for encryption. Both optical and copper links are used in data centres.

Fibre loss is quoted in decibels because losses along a route then simply add. To turn a loss in dB back into the fraction of power that survives:

```formula
A = αd
A = 0.2 dB/km × 80 km = 16 dB
P_out / P_in = 10^(−A / 10)
P_out / P_in = 10^(−1.6) ≈ 0.025
where
A: the total attenuation (loss) along the span, in decibels (dB)
α: alpha, the fibre's loss per kilometre, in dB per kilometre (dB/km); 0.2 here
d: the span length, in kilometres (km)
dB: decibels, a logarithmic measure of a power ratio: every 10 dB is a factor of 10
km: kilometres
P_out: the optical power arriving at the far end
P_in: the optical power launched into the fibre
≈: approximately equal to
In words: 16 dB of loss leaves about 2.5% of the launched light, roughly a fortieth, at the far end of the 80 km span.
```

### Why fibre is only about two-thirds of c

For pulse propagation, use the fibre’s **effective group index**, not simply the bulk phase refractive index. Corning’s July 2025 SMF-28 Ultra data sheet lists a typical group index of 1.4682 at 1550 nm. Rounding to 1.47 gives:

```formula
v_group = c / n_group
v_group ≈ (3 × 10⁸ m/s) / 1.47
v_group ≈ 2.04 × 10⁸ m/s ≈ 0.68 × c
t_km = 1000 m / v_group ≈ 4.9 µs
where
v_group: the group velocity: the speed at which a pulse (and so the data) travels along the fibre, in metres per second (m/s)
c: the speed of light in a vacuum, about 3 × 10⁸ m/s
n_group: the fibre's effective group index: how many times slower than c a pulse travels; about 1.47 at 1550 nm (no unit)
t_km: the time a pulse takes to cross one kilometre of this fibre
m: metres; m/s is metres per second
s: seconds
µs: microseconds, millionths of a second
≈: approximately equal to
In words: dividing the speed of light by about 1.47 gives about two-thirds of it, so light in this fibre needs about 4.9 µs per kilometre.
```

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
