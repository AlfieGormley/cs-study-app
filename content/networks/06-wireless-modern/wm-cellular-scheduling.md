---
id: wm-cellular-scheduling
title: Radio scheduling, numerology and 5G options
level: intermediate
minutes: 5
summary: Twelve subcarriers set a resource block’s frequency width; spacing and time allocation are separate dimensions.
sourceLesson: wm-cellular
---

Wi-Fi stations mostly decide for themselves when to transmit. A cellular base station instead acts as a central scheduler, telling each phone which slices of frequency and time it may use. That design choice shapes how 4G and 5G handle many users, and why 5G can offer much shorter scheduling intervals.

## Scheduled radio access

LTE and NR divide the channel into a grid of frequency and time. In frequency, a **resource block** spans **12 subcarriers**: with LTE's 15 kHz subcarrier spacing that is 180 kHz. In time, conventional LTE schedules in 1 ms subframes. The base station's scheduler assigns resource blocks in each interval to particular phones, based on their demand, radio conditions and the operator's policy. Later features and specialised modes qualify a universal 1 ms rule, and LTE uplink commonly uses DFT-spread OFDM (SC-FDMA) rather than simply the downlink waveform.

For dynamically scheduled uplink data without an existing grant, a connected UE can request resources and receive an uplink grant. Existing/configured grants and random-access procedures mean a fresh request/grant is not required for every packet. Scheduling coordinates access but does not eliminate random-access collisions or inter-cell interference; fairness is a scheduler policy, not an automatic guarantee.

> [!analogy] Real-world analogy: Air traffic control versus an uncontrolled airfield
> At a small uncontrolled airfield, pilots listen to the radio, announce themselves and slot in when the circuit looks clear. At a busy airport, a controller assigns each aircraft a runway slot, and pilots must request clearance before moving.
>
> **How it maps:** The uncontrolled airfield is Wi-Fi's listen-and-wait contention. The controller is the base station's scheduler, a runway slot is a set of resource blocks in one time interval, and requesting clearance is the scheduling request and uplink grant.
>
> **Where it stops:** Even at a controlled airport the first call to the tower can clash with another aircraft's call, just as cellular random access can collide. Unlike separate airports, neighbouring cells commonly reuse the same frequencies, so one cell's transmissions can interfere with its neighbours'.

## 5G numerology: shorter slots

5G NR adds flexible **numerology**: the subcarrier spacing can be 15, 30, 60 or 120 kHz in common configurations (later releases add more). Each doubling of the spacing halves the OFDM symbol duration, and so halves the slot:

```formula reference
Δf = 15 kHz × 2^μ
T_slot = 1 ms / (2^μ)
where
Δf: delta-f, the subcarrier spacing, in kilohertz (kHz)
μ: mu, the numerology index, a whole number: 0, 1, 2 or 3 in these examples; 2^μ means 2 raised to the power μ, so 1, 2, 4 or 8
T_slot: the duration of one full slot with normal cyclic prefix (14 OFDM symbols), in milliseconds (ms)
kHz: kilohertz, one thousand hertz
ms: millisecond, one thousandth of a second
In words: doubling the subcarrier spacing makes each symbol, and so each slot, half as long.
```

| Spacing | Slot length | Typical use |
|---|---|---|
| 15 kHz | 1 ms | low band, wide coverage |
| 30 kHz | 0.5 ms | mid band (e.g. 3.5 GHz) |
| 60 kHz | 0.25 ms | some mid and high bands |
| 120 kHz | 0.125 ms | mmWave |

What changes when the spacing goes up:

- **More frequent scheduling opportunities.** Shorter slots let the scheduler react and grant resources more often. Mini-slot transmission need not occupy a full slot. This helps latency, but does not by itself guarantee lower latency for applications.
- **More tolerance of frequency error.** Wider spacing makes a given frequency offset or phase noise smaller relative to the gap between subcarriers, which matters at high frequencies.
- **Less tolerance of echoes.** The cyclic prefix shrinks with the symbol, so it can absorb less **delay spread** (the time between a signal and its reflections). Wide spacing therefore suits smaller cells, where reflections arrive close together. That is one reason low bands with wide coverage use narrow spacing.

## Spectrum: coverage versus capacity

NR specifications define release-specific frequency ranges, with different supported bandwidths and spacings:

- **FR1** includes low and mid bands. Lower frequencies often aid coverage, while wider available allocations can provide capacity; actual range depends on power, antennas and surroundings. A 3.5 GHz deployment is an illustrative mid-band case, not a universal regional allocation.
- **FR2** covers higher-frequency NR bands, commonly called mmWave in the industry, and has release-specific subdivisions. Wide channels and beamforming can support high capacity, but blockage and link budget matter. A fixed “few hundred metres” coverage rule is not reliable for every deployment.

> [!note] Why "5G" on your phone may be mostly 4G
> A common **NSA option 3** deployment uses LTE/EPC as the master/core with NR as secondary access. **SA option 2** connects NR to the 5G core. “NSA” has broader architectural usage, and a status icon alone does not prove which capabilities are active. Feature availability depends on release, configuration, device and operator support.

ITU IMT-2020 evaluation requirements include a 20 Gbit/s peak downlink data rate and 4 ms eMBB / 1 ms URLLC user-plane latency targets under their defined conditions. The latency measure is one-way radio user-plane latency, not an Internet ping RTT; the peak rate is not a per-user service guarantee. Scheduling, backhaul, core routing, server work and other parts of the path contribute to application latency.

### 5G-Advanced and what comes next

3GPP standards arrive in numbered releases. 5G-Advanced began with Release 18 (functionally frozen in 2024), and 3GPP calls Release 19 (completed in late 2025) the second 5G-Advanced release. In 2026 3GPP was working on Release 20, which carries further 5G-Advanced features alongside the first 6G studies; 3GPP plans normative 6G specifications for Release 21. These schedules change, so check 3GPP's releases page for the current status. Whether a phone or network supports a feature depends on what each operator and vendor actually deploys, not on the release number alone.

## Key takeaways
- A central scheduler allocates resource blocks in frequency and time; twelve subcarriers set a resource block's width.
- NR spacing and normal-prefix slot duration scale together; release and deployment determine supported features.

## Further reading
- [5G NR — Wikipedia](https://en.wikipedia.org/wiki/5G_NR)
- [3GPP: Releases and their status](https://www.3gpp.org/specifications-technologies/releases)
- [3GPP: Release 20, 5G-Advanced and 6G studies](https://www.3gpp.org/specifications-technologies/releases/release-20)
- [3GPP TS 38.211 Release 17: NR physical channels and modulation](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/17.06.00_60/ts_138211v170600p.pdf)
- [ITU-R M.2410: IMT-2020 evaluation requirements](https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-M.2410-2017-PDF-E.pdf)
