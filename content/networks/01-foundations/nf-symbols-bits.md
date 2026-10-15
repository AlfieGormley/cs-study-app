---
id: nf-symbols-bits
sourceLesson: nf-physical-layer
title: Symbols, baud and bits
level: basic
minutes: 3
summary: Relate distinguishable symbol states to uncoded bit rate and explain the noise trade-off.
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
R_b = R_s k
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

## Key takeaways
- Baud counts symbols per second, while bit rate also depends on bits per symbol.
- Coding and other overhead reduce payload rate below an uncoded mapping’s raw rate.

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
