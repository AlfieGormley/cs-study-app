---
id: wm-cellular-scheduling
title: Radio scheduling, numerology and 5G options
level: intermediate
minutes: 5
summary: Twelve subcarriers set a resource block’s frequency width; spacing and time allocation are separate dimensions.
sourceLesson: wm-cellular
---

This unit focuses on radio scheduling, numerology and 5G options. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Scheduled radio access

LTE and NR use OFDM-based downlink resource allocation. A resource block spans **12 subcarriers**; the number of active subcarriers depends on the channel configuration. The width of one resource block follows directly:

```formula
W_RB = 12Δf
W_RB = 12 × 15 kHz = 180 kHz
where
W_RB: the width of one resource block, in kilohertz (kHz)
Δf: delta-f, the subcarrier spacing: the gap between neighbouring subcarrier centres, 15 kHz in LTE
kHz: kilohertz, one thousand hertz (cycles per second)
In words: a resource block is twelve subcarriers side by side, so its width is twelve times the spacing.
```

In the conventional LTE example, 15 kHz spacing gives 180 kHz per resource block and a 1 ms subframe scheduling interval. Later features and specialised modes qualify a universal 1 ms rule. LTE uplink commonly uses DFT-spread OFDM (SC-FDMA), rather than simply the same downlink waveform.

For dynamically scheduled uplink data without an existing grant, a connected UE can request resources and receive an uplink grant. Existing/configured grants and random-access procedures mean a fresh request/grant is not required for every packet. Scheduling coordinates access but does not eliminate random-access collisions or inter-cell interference; fairness is a scheduler policy, not an automatic guarantee.

5G NR adds flexible **numerology**. Common examples use 15, 30, 60 or 120 kHz spacing. This is not the complete set in later releases. Each step doubles the subcarrier spacing and halves the slot. For normal cyclic prefix (14 OFDM symbols per slot):

```formula
Δf = 15 kHz × 2^μ
T_slot = 1 ms / (2^μ)
μ = 1:  Δf = 30 kHz,  T_slot = 0.5 ms
μ = 3:  Δf = 120 kHz,  T_slot = 0.125 ms
where
Δf: delta-f, the subcarrier spacing, in kilohertz (kHz)
μ: mu, the numerology index, a whole number: 0, 1, 2 or 3 in these examples; 2^μ means 2 raised to the power μ, so 1, 2, 4 or 8
T_slot: the duration of one full slot, in milliseconds (ms)
kHz: kilohertz, one thousand hertz
ms: millisecond, one thousandth of a second
In words: doubling the subcarrier spacing makes each symbol, and so each slot, half as long.
```

Useful OFDM symbol duration is the reciprocal of subcarrier spacing: at 15 kilohertz it is about 66.7 microseconds before the cyclic prefix. Shorter slots permit more frequent scheduling opportunities; they do not guarantee lower end-to-end latency. Wider spacing reduces a given frequency error relative to the subcarrier separation, while cyclic-prefix length and channel conditions also constrain design. Mini-slot transmission need not occupy a full slot:

| Spacing | Slot length | Typical use |
|---|---|---|
| 15 kHz | 1 ms | low band, wide coverage |
| 30 kHz | 0.5 ms | mid band (e.g. 3.5 GHz) |
| 120 kHz | 0.125 ms | mmWave |

## Spectrum: coverage versus capacity

NR specifications define release-specific frequency ranges, with different supported bandwidths and spacings:

- **FR1** includes low and mid bands. Lower frequencies often aid coverage, while wider available allocations can provide capacity; actual range depends on power, antennas and surroundings. A 3.5 GHz deployment is an illustrative mid-band case, not a universal regional allocation.
- **FR2** covers higher-frequency NR bands, commonly called mmWave in the industry, and has release-specific subdivisions. Wide channels and beamforming can support high capacity, but blockage and link budget matter. A fixed “few hundred metres” coverage rule is not reliable for every deployment.

> [!note] Why "5G" on your phone may be mostly 4G
> A common **NSA option 3** deployment uses LTE/EPC as the master/core with NR as secondary access. **SA option 2** connects NR to the 5G core. “NSA” has broader architectural usage, and a status icon alone does not prove which capabilities are active. Feature availability depends on release, configuration, device and operator support.

ITU IMT-2020 evaluation requirements include a 20 Gbit/s peak downlink data rate and 4 ms eMBB / 1 ms URLLC user-plane latency targets under their defined conditions. The latency measure is one-way radio user-plane latency, not an Internet ping RTT; the peak rate is not a per-user service guarantee. Scheduling, backhaul, core routing, server work and other parts of the path contribute to application latency.

## Key takeaways
- Twelve subcarriers set a resource block’s frequency width; spacing and time allocation are separate dimensions.
- NR spacing and normal-prefix slot duration scale together; release and deployment determine supported features.

## Further reading
- [5G NR — Wikipedia](https://en.wikipedia.org/wiki/5G_NR)
- [3GPP TS 38.211 Release 17: NR physical channels and modulation](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/17.06.00_60/ts_138211v170600p.pdf)
- [ITU-R M.2410: IMT-2020 evaluation requirements](https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-M.2410-2017-PDF-E.pdf)
