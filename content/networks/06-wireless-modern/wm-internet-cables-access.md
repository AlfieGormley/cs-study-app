---
id: wm-internet-cables-access
title: Submarine resilience and shared access networks
level: advanced
minutes: 3
summary: Independent physical routes and surviving capacity matter more than merely counting logical links.
sourceLesson: wm-internet-structure
---

This unit focuses on submarine resilience and shared access networks. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Submarine cables

**Submarine fibre-optic cables** are central to intercontinental connectivity. Traffic shares and cable inventories depend on definitions and date; avoid treating a single unsourced percentage as a universal constant.

How they work:

- Cable systems use **fibre pairs** carrying multiple wavelengths (DWDM). Fibre count and capacity vary by design.
- Long-haul repeatered systems use optical amplifiers at design-specific intervals and shore-fed high-voltage DC power. Shorter unrepeatered systems also exist; spacing and voltage are not universal.
- Modern cables have design capacities in the hundreds of Tbit/s. Google's Dunant cable (US–France, 2021) was announced at 250 Tbit/s.
- Increasingly, cloud and content companies own or co-own cables rather than leasing capacity from telecoms consortia.

ICPC’s June 2025 guidance describes approximately **150–200 faults annually**, with 70–80% attributed to accidental damage, primarily fishing and vessel anchoring. This is a dated industry summary, not a prediction or an exhaustive cause breakdown; other natural and technical causes exist. A marine repair may require a ship to recover the cable and splice it, with timing dependent on fault location, ship availability, weather, permits and the repair method. Networks may reroute over surviving capacity, but regions served by only one or two cables (some island nations, parts of West and East Africa) can lose most connectivity when they are cut.

## The last mile

The **last mile** (or access network) connects homes and businesses to their ISP. It is one possible bottleneck; aggregation networks, interconnection, servers and local Wi-Fi can also limit service.

| Technology | Medium | Rate interpretation |
|---|---|---|
| ADSL / VDSL2 | copper pair | Profile, line quality, length and deployment determine rate |
| DOCSIS cable | shared coaxial cable | Version, spectrum allocation and service plan determine rate |
| GPON fibre | shared optical distribution | Common nominal line rates: 2.48832 Gbit/s down / 1.24416 up; not per-home goodput |
| XGS-PON fibre | shared optical distribution | 10 Gbit/s class (9.95328 Gbit/s nominal each way); shared and before protocol overhead |
| Fixed wireless, 4G/5G | radio | widely variable |

- **DSL** runs over the telephone pair. VDSL2 rates depend on copper length, line quality, profile and interference; shorter runs can support higher rates.
- **Cable** (DOCSIS) shares one coaxial cable network among a neighbourhood, so evening peaks can slow everyone; upload is traditionally much lower than download.
- **PON fibre** (FTTP) shares one fibre from the exchange among optical network terminals via passive splitters. Split ratios and scheduling vary; a marketed access rate is not necessarily a permanently reserved equal fraction.

> [!note] Contention
> Several layers can be oversubscribed: the PON split, the ISP's aggregation network, its transit and peering capacity. Capacity planning often uses busy-hour demand and service commitments rather than assuming every user saturates at once. This is a design choice, not a requirement that every link be oversubscribed. The same principle as data-centre oversubscription, applied to a country.

## Key takeaways
- Independent physical routes and surviving capacity matter more than merely counting logical links.
- PON line capacity is shared and precedes overhead; a service plan is not a permanently reserved share.

## Further reading
- [Submarine communications cable — Wikipedia](https://en.wikipedia.org/wiki/Submarine_communications_cable)
- [Submarine Cable Map — TeleGeography](https://www.submarinecablemap.com/)
- [Passive optical network — Wikipedia](https://en.wikipedia.org/wiki/Passive_optical_network)
- [ICPC: Cable protection and fault summary, June 2025](https://www.iscpc.org/publications/icpc-viewpoints/charting-submarine-cables-is-critical-for-maritime-safety-and-infrastructure-protection/)
- [Google: Dunant ready for service, February 2021](https://cloud.google.com/blog/products/infrastructure/googles-dunant-subsea-cable-is-now-ready-for-service)
- [ITU-T G.9807.1: XGS-PON](https://www.itu.int/rec/T-REC-G.9807.1)
- [ITU-T G.984.2: GPON physical layer](https://www.itu.int/rec/T-REC-G.984.2)
