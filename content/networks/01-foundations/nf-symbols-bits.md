---
id: nf-symbols-bits
sourceLesson: nf-physical-layer
title: Symbols, baud and bits
level: basic
minutes: 3
summary: Distinguish symbol rate from bit rate and explain why denser signalling needs reliable distinction.
---

The physical layer turns bits into signals that travel as voltages, light or radio waves. It chooses from distinguishable **symbols**, such as voltage levels or combinations of amplitude and phase.

## Symbols and bits measure different things

The **baud rate** counts symbols per second. The **bit rate** also depends on how much information each symbol distinguishes.

With two states, one symbol can distinguish 0 from 1. With four states it can distinguish 00, 01, 10 and 11: two bits per symbol. Each extra bit requires twice as many states for an uncoded fixed mapping.

| Scheme | States | Bits per symbol |
|---|---|---|
| Two voltage levels | 2 | 1 |
| PAM-4 | 4 | 2 |
| 16-QAM | 16 | 4 |
| 1024-QAM, used in Wi-Fi 6 | 1024 | 10 |

A 1 Gbaud PAM-4 mapping therefore represents 2 Gbit/s before overhead. Coding, framing and pilots (known reference symbols used by the receiver) reduce the useful payload rate.

```formula reference
k = log_2(M)
R_b = R_s k
where
k: number of bits carried by each symbol in the uncoded fixed mapping
M: number of distinguishable symbol states; assume a power of two for the fixed whole-bit mapping
log_2: base-two logarithm, the power to which two must be raised to obtain the argument
R_b: raw mapped bit rate in bits per second
R_s: symbol rate in symbols per second, also called baud
In words: more symbol states let each symbol carry more bits, and sending more symbols each second raises the raw bit rate; coding and other overhead reduce the useful payload rate.
```

## Why more levels have a cost

At a fixed signal range, putting states closer together makes them harder to distinguish in noise. More states can raise bits per symbol while also making the mapping less robust.

A receiver also needs suitable pulse shaping and timing: the waveform need not stay constant during a symbol interval. Choosing modulation means balancing rate against the channel conditions, coding and implementation limits.

## Key takeaways
- Baud counts symbols; bit rate also counts the bits represented by each symbol.
- Denser signal states increase raw rate but require reliable distinction in noise.

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
