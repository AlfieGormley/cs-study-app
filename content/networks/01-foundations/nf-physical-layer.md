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

Each symbol can carry more than one bit. With two possible states a symbol can say 0 or 1; with four states it can say 00, 01, 10 or 11. Each extra bit doubles the number of states needed. For an uncoded fixed mapping:

```formula
M = 2^k
k = log_2(M)
where
M: the number of distinguishable symbol states (levels, or amplitude-and-phase combinations)
k: the number of bits each symbol carries
log_2: the base-2 logarithm: the power 2 must be raised to in order to give M (log_2(16) = 4 because 2^4 = 16)
In words: a symbol with M states carries log_2(M) bits, so 4 states carry 2 bits, 16 carry 4 and 1024 carry 10.
```

Coding, pilots (known reference symbols for the receiver) and framing reduce the payload rate below this:

| Scheme | States | Bits/symbol |
|---|---|---|
| Two voltage levels | 2 | 1 |
| PAM-4 | 4 | 2 |
| 16-QAM | 16 | 4 |
| 1024-QAM (Wi-Fi 6) | 1024 | 10 |

So the bit rate is the symbol rate times the bits each symbol carries:

```formula
R_b = R_s × k
R_b = 10⁹ baud × 2 bit = 2 × 10⁹ bit/s
where
R_b: the bit rate, in bits per second (bit/s)
R_s: the symbol rate (baud rate), in baud: symbols per second
k: the bits carried per symbol, log_2 of the number of states; 2 for PAM-4
baud: one symbol per second; 1 Gbaud is 10⁹ symbols per second
bit: one binary digit; bit/s is bits per second
s: seconds
In words: a 1 Gbaud PAM-4 link sends a billion symbols a second, each carrying 2 bits, so it carries 2 Gbit/s.
```

Why not use millions of levels? Because noise blurs them. The closer together the levels are, the more likely noise pushes a symbol across a boundary and the receiver decodes the wrong one.

## Two hard limits

### Nyquist: how fast can you send symbols?

A channel's **bandwidth** in this sense is the width of the frequency range it passes, in hertz. For ideal zero-intersymbol-interference signalling (each symbol's pulse is shaped so it does not smear into its neighbours at the sampling instants) over a real low-pass channel with one-sided bandwidth B hertz, Nyquist gives **2B real symbols per second**. With M levels the corresponding uncoded rate is:

```formula
C = 2 × B × log_2(M)
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

### Shannon: how much can noise allow?

For the band-limited additive white Gaussian noise (AWGN) model (random noise spread evenly over all frequencies and simply added to the signal), Shannon capacity is:

```formula
C = B × log_2(1 + S / N)
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

Below capacity, suitable coding can make error probability arbitrarily small in the asymptotic model; this is not a promise of zero errors with finite packets. Here S/N is a power ratio. Engineers quote the signal-to-noise ratio (**SNR**) in decibels:

```formula
SNR_dB = 10 × log_10(S / N)
S / N = 10^(SNR_dB / 10)
S / N = 10^(30 / 10) = 1000
where
SNR_dB: the signal-to-noise ratio in decibels (dB)
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

The name says how many line bits replace how many data bits: 8b/10b sends 10 bits on the line for every 8 bits of data. The line must therefore run faster than the data rate:

```formula
R_line = R_data × n / m
R_line = 10 Gbit/s × 66 / 64
R_line = 10.3125 Gbit/s
where
R_line: the rate of coded bits on the line, in bits per second
R_data: the rate of data bits before coding, in bits per second
m: the data bits in each block (the first number in the name, 64 for 64b/66b)
n: the coded bits sent for each block (the second number, 66 for 64b/66b)
Gbit/s: gigabits per second; 1 Gbit is 10⁹ bits
In words: the overhead is (n − m) / m: 2/64 = 3.125% for 64b/66b, and 2/8 = 25% for 8b/10b, so 10 Gbit/s of data needs 10.3125 Gbit/s on the line.
```

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
- For a hypothetical fibre loss of **0.2 dB/km**, an 80 km span loses 0.2 × 80 = 16 dB before connectors/splices (the calculation below turns that into a fraction of the power). Actual loss is product- and wavelength-dependent; amplifier spacing also depends on the optical power/noise budget, not a universal distance.
- **Wavelength-division multiplexing** (DWDM) sends dozens of wavelengths through one fibre, each its own channel. Total capacity depends on channel count, modulation, coding, equipment and reach; no universal capacity figure is implied.
- The optical signal is not subject to electromagnetic pickup like copper wiring, but fibre can still be tapped or physically damaged. Fibre is not a substitute for encryption. Both optical and copper links are used in data centres.

Fibre loss is quoted in decibels because losses along a route then simply add. To turn a loss in dB back into the fraction of power that survives:

```formula
A = α × d
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

## Wireless

Radio has no cable at all, which brings great convenience and a long list of problems:

- **Shared medium.** Devices share radio resources, but hidden nodes, distance and obstacles mean not every transmitter can hear every other. Transmissions collide and must be coordinated (Wi-Fi uses CSMA/CA, covered in a later module).
- **Attenuation.** For the far-field free-space model with fixed transmit power, frequency and antenna gains, received power scales as inverse distance squared: doubling the distance quarters the power, a drop of about 6 dB (since 3 dB is a factor of 2, 6 dB is a factor of 4). Walls, antenna patterns, regulations and multipath alter actual coverage. Higher frequency is not by itself a universal range guarantee.
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
- Bit rate is baud rate times bits per symbol; more levels per symbol need more SNR.
- Nyquist’s limit of two symbols per second per hertz assumes the stated real baseband/zero-ISI model; Shannon's formula gives capacity for the stated AWGN model, linear in bandwidth and logarithmic in SNR.
- Line coding trades overhead for clock recovery and signal properties. Manchester and 8b/10b provide strict balance properties; 64b/66b uses scrambling for statistical balance, while 4B/5B alone does not guarantee DC balance.
- Reach depends on the PHY and cable: the examples include 100 m Cat6a/10GBASE-T, hundreds of metres for 10GBASE-SR on appropriate multimode fibre, and 10 km for 10GBASE-LR.
- Pulse speed in the specified glass fibre is about the speed of light divided by its group index, roughly 0.68 of light speed. Copper velocity depends on construction; radio in air is nearly c.
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
