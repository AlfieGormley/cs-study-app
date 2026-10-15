---
id: nf-copper-wireless
sourceLesson: nf-physical-layer
title: Copper and wireless trade-offs
level: basic
minutes: 3
summary: Compare differential copper signalling with shared, fading radio channels.
---

## Copper

**Twisted pair** (Cat5e, Cat6, Cat6a) is the familiar Ethernet cable. Each pair carries a signal as a voltage *difference* between two wires. Twisting them means external interference hits both wires almost equally, and the receiver, looking only at the difference, rejects its common-mode component to the extent allowed by cable balance and receiver performance. Twisting also reduces **crosstalk** between neighbouring pairs.

- Common four-pair building-cabling Ethernet standards support **100 m** channels with the required cable category and installation quality. Other Ethernet PHYs and products have different reach limits. Signals attenuate and pick up noise with length, and higher frequencies attenuate faster.
- **1000BASE-T** sends PAM-5 on all four pairs at 125 Mbaud, in both directions at once, using echo cancellation to separate its own transmit signal from the incoming one.
- **10GBASE-T** can support 100 m on compliant Cat6a channels with suitable endpoints. Reach on other cable categories and power relative to optical alternatives require the specific cable and transceiver specifications; universal figures are omitted.
- **Coaxial cable** (a centre conductor in a shield) carried early Ethernet and still carries cable broadband (DOCSIS).

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
- Twisted pairs reject common-mode interference within practical balance limits.
- Radio rate and reliability depend on interference, fading, coordination and adaptation.

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
