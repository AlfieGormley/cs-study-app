---
id: nf-physical-layer
title: The physical layer in brief
level: basic
minutes: 12
summary: How bits become signals, why line codes exist, the Nyquist and Shannon limits, and how copper, fibre and radio differ, including why signals in fibre travel at about two-thirds of the speed of light.
---

Everything above the physical layer assumes it can hand over a string of bits and have the same bits appear at the other end. The physical layer makes that true, most of the time, by turning bits into something that can travel: voltages on copper, pulses of light in glass, or radio waves.

Software engineers rarely touch this layer. It still shapes everything above it: the fastest possible RTT, how far a cable can run, why Wi-Fi is flaky and why data centres are full of fibre. This lesson covers just enough to reason about those effects.

## Signals, symbols and bits

A link sends **symbols**, chosen from a signal alphabet for successive symbol intervals: for example, voltage levels or combinations of amplitude and phase. Pulse shaping means the physical waveform need not remain constant throughout an interval. The number of symbols per second is the **baud rate** (symbol rate).

Each symbol can carry more than one bit. For an uncoded fixed mapping with M = 2^k distinguishable states, each symbol labels k = log₂ M bits. Coding, pilots and framing reduce payload rate:

| Scheme | States | Bits/symbol |
|---|---|---|
| Two voltage levels | 2 | 1 |
| PAM-4 | 4 | 2 |
| 16-QAM | 16 | 4 |
| 1024-QAM (Wi-Fi 6) | 1024 | 10 |

So **bit rate = baud rate × bits per symbol**. A 1 Gbaud PAM-4 link carries 2 Gbit/s.

Why not use millions of levels? Because noise blurs them. The closer together the levels are, the more likely noise pushes a symbol across a boundary and the receiver decodes the wrong one.

## Two hard limits

### Nyquist: how fast can you send symbols?

For ideal zero-intersymbol-interference signalling over a real low-pass channel with one-sided bandwidth B hertz, Nyquist gives **2B real symbols per second**. With M levels the corresponding uncoded rate is:

`C = 2B × log₂ M`

For a hypothetical noiseless baseband channel with B = 3.1 kHz and four levels: 2 × 3,100 × 2 = 12.4 kbit/s.

### Shannon: how much can noise allow?

For the band-limited additive white Gaussian noise (AWGN) model with average signal/noise powers S and N, Shannon capacity is:

`C = B × log₂(1 + S/N)`

Below capacity, suitable coding can make error probability arbitrarily small in the asymptotic model; this is not a promise of zero errors with finite packets. Here S/N is a power ratio. Engineers quote SNR in decibels: SNR_dB = 10 × log₁₀(S/N), so 30 dB means S/N = 1000.

> [!example] A simplified single-channel capacity model
> Assume one flat AWGN channel (not a complete Wi-Fi/MIMO model). A 20 MHz channel with 30 dB SNR: C = 20 × 10⁶ × log₂(1001) ≈ 20 × 10⁶ × 9.97 ≈ **199 Mbit/s**. No modulation scheme, however clever, can beat that on that channel. To go faster you need more bandwidth (wider channels), more SNR, or more independent channels (more antennas, MIMO).

The model helps explain why attenuation can reduce achievable rate when transmit power, noise and other conditions are held fixed. Actual distance-to-rate behaviour also depends on interference, propagation paths, equipment and adaptation.

## Line coding: why not just send the bits?

The simplest scheme, **NRZ** (non-return-to-zero), maps 1 to high and 0 to low. It has two problems:

1. **Clock recovery.** Assume the receiver has no separate clock and must recover timing from the data. It finds bit boundaries by watching for transitions. A sufficiently long transition-free run can exceed the receiver’s clock-recovery tolerance; not every finite run necessarily causes an error.
2. **Baseline wander (DC balance).** Many links are AC-coupled through transformers or capacitors. A long run of 1s looks like a constant DC level, which the coupling blocks, so the receiver's idea of "zero" drifts.

**Line coding and scrambling** address transition density and baseline wander, but different schemes provide different guarantees.

**Manchester** coding (used by 10 Mbit/s Ethernet) puts a transition in the middle of every bit. In IEEE 802.3's convention, 0 is high-to-low and 1 is low-to-high:

```
bit:        1    0    1    1
NRZ:        HH   LL   HH   HH
Manchester: LH   HL   LH   LH
```

```python
def manchester(bits):
    # IEEE 802.3: 0 -> high,low
    #             1 -> low,high
    out = []
    for b in bits:
        if b not in "01":
            raise ValueError("not binary")
        if b == "1":
            out += [0, 1]
        else:
            out += [1, 0]
    return out

print(manchester("1011"))
# [0, 1, 1, 0, 0, 1, 0, 1]
```

Manchester is self-clocking and DC-balanced, but it **doubles the signalling rate**: two half-bit signal levels per bit. Other Ethernet PHYs use different tradeoffs.

Some faster links use **block codes**, sometimes combined with scrambling and a separate line modulation. They provide different transition-density and DC-balance guarantees:

| Code | Used by | Overhead |
|---|---|---|
| 4B/5B | 100BASE-TX, FDDI | 25% |
| 8b/10b | 1000BASE-X, SATA, PCIe 1–2 | 25% |
| 64b/66b | 10GBASE-R | 3.125% |

Specifically, 100BASE-TX maps its 4B/5B-coded stream to MLT-3 at 125 million symbol intervals/s. Serial binary 10GBASE-R uses 10.3125 Gbaud. Other Fast/Gigabit Ethernet PHYs need not use those rates. Good line codes also leave unused code words that can be used for control, such as marking the start of a frame.

## Copper

**Twisted pair** (Cat5e, Cat6, Cat6a) is the familiar Ethernet cable. Each pair carries a signal as a voltage *difference* between two wires. Twisting them means external interference hits both wires almost equally, and the receiver, looking only at the difference, rejects its common-mode component to the extent allowed by cable balance and receiver performance. Twisting also reduces **crosstalk** between neighbouring pairs.

- Common four-pair building-cabling Ethernet standards support **100 m** channels with the required cable category and installation quality. Other Ethernet PHYs and products have different reach limits. Signals attenuate and pick up noise with length, and higher frequencies attenuate faster.
- **1000BASE-T** sends PAM-5 on all four pairs at 125 Mbaud, in both directions at once, using echo cancellation to separate its own transmit signal from the incoming one.
- **10GBASE-T** can support 100 m on compliant Cat6a channels with suitable endpoints. Reach on other cable categories and power relative to optical alternatives require the specific cable and transceiver specifications; universal figures are omitted.
- **Coaxial cable** (a centre conductor in a shield) carried early Ethernet and still carries cable broadband (DOCSIS).

## Fibre

An optical fibre is a glass **core** surrounded by **cladding** of slightly lower refractive index. The refractive-index structure guides optical modes; **total internal reflection** is a useful ray-model explanation, particularly for multimode fibre. A laser or LED switches on and off (or modulates phase and amplitude) to encode symbols.

- **Multi-mode fibre** has a wide core (50 or 62.5 µm). Light takes many paths ("modes") of slightly different length, so pulses spread out (modal dispersion). It is cheap with 850 nm optics and good for a few hundred metres: 10GBASE-SR reaches about 300 m on OM3 and 400 m on OM4.
- **Single-mode fibre** supports one spatial mode over its specified wavelength range; it is not literally one geometrical ray. Core diameter and mode-field diameter are distinct properties. With 1310 or 1550 nm lasers it reaches tens of kilometres directly, and thousands with amplifiers.
- For a hypothetical fibre loss of **0.2 dB/km**, an 80 km span loses 16 dB before connectors/splices. Actual loss is product- and wavelength-dependent; amplifier spacing also depends on the optical power/noise budget, not a universal distance.
- **Wavelength-division multiplexing** (DWDM) sends dozens of wavelengths through one fibre, each its own channel. Total capacity depends on channel count, modulation, coding, equipment and reach; no universal capacity figure is implied.
- The optical signal is not subject to electromagnetic pickup like copper wiring, but fibre can still be tapped or physically damaged. Fibre is not a substitute for encryption. Both optical and copper links are used in data centres.

### Why fibre is only about two-thirds of c

For pulse propagation, use the fibre’s **effective group index**, not simply the bulk phase refractive index. Corning’s July 2025 SMF-28 Ultra data sheet lists a typical group index of 1.4682 at 1550 nm. Rounding to 1.47 gives:

`v_group ≈ c / n_group ≈ 3 × 10⁸ / 1.47 ≈ 2.04 × 10⁸ m/s`

That is approximately 0.68c, or 4.9 µs/km. Wavelength and fibre construction matter.

On copper, the signal is an electromagnetic wave guided by the conductors and dielectric. Its speed is not the electron drift velocity. **Velocity factor** depends on cable construction: copper is not universally slower than glass. For example, Belden 2433 specifies a nominal 72% of c, above the roughly 68% used in the glass-fibre example. Compare complete link latency, including PHY electronics, when choosing a medium.

> [!note] Lower propagation delay
> Radio in air travels close to c. Hollow-core fibre can also reduce propagation delay because much of its optical field travels through an air-filled region. Microsoft has reported Azure deployment. Exact universal hollow-core velocity and trading-route latency figures are omitted because they require a specific fibre, wavelength, route and measurement source.

## Wireless

Radio has no cable at all, which brings great convenience and a long list of problems:

- **Shared medium.** Devices share radio resources, but hidden nodes, distance and obstacles mean not every transmitter can hear every other. Transmissions collide and must be coordinated (Wi-Fi uses CSMA/CA, covered in a later module).
- **Attenuation.** For the far-field free-space model with fixed transmit power, frequency and antenna gains, received power scales as inverse distance squared: about 6 dB per doubling. Walls, antenna patterns, regulations and multipath alter actual coverage. Higher frequency is not by itself a universal range guarantee.
- **Multipath.** Signals bounce off walls and arrive several times with different delays, interfering with each other. OFDM (splitting a channel into many narrow subcarriers) and MIMO make multipath manageable, even useful.
- **Variable SNR.** Moving a few metres can change SNR a lot, so Wi-Fi and 4G/5G constantly adapt their modulation: higher-order modulation when conditions permit, more robust modulation/coding when needed; distance alone does not determine the mode.
- **Half duplex.** A radio cannot easily hear a faint incoming signal while it transmits a strong one on the same frequency, so it generally takes turns. This is also why Wi-Fi cannot detect collisions the way early Ethernet did.
- **High error rates.** Wireless errors depend on interference, fading and link design. Many systems use error correction and link retries; not every wireless frame is acknowledged, and no universal wired/wireless loss ratio is given here.

## Comparing the media

| Medium | Typical reach | Signal speed |
|---|---|---|
| Four-pair building Ethernet | often 100 m | cable-specific |
| OM3/OM4 with 10GBASE-SR | 300/400 m | fibre-specific |
| Single-mode with 10GBASE-LR | 10 km | fibre-specific |
| Radio (Wi-Fi) | installation-specific | ~c |

## Key takeaways
- Bit rate = baud rate × bits per symbol; more levels per symbol need more SNR.
- Nyquist’s 2B result assumes the stated real baseband/zero-ISI model; B log₂(1 + S/N) is capacity for the stated AWGN model.
- Line coding trades overhead for clock recovery and signal properties. Manchester and 8b/10b provide strict balance properties; 64b/66b uses scrambling for statistical balance, while 4B/5B alone does not guarantee DC balance.
- Reach depends on the PHY and cable: the examples include 100 m Cat6a/10GBASE-T, hundreds of metres for 10GBASE-SR on appropriate multimode fibre, and 10 km for 10GBASE-LR.
- Pulse speed in the specified glass fibre is about c / n_group ≈ 0.68c. Copper velocity depends on construction; radio in air is nearly c.
- Wi-Fi shares radio resources and normally operates half duplex on a channel; interference and fading influence error control and scheduling. These are not universal properties of all wireless systems.

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
