---
id: wm-internet-structure
title: How the Internet is built, from cables to satellites
level: advanced
minutes: 16
summary: Autonomous systems, transit and peering, Tier 1 networks and IXPs, the submarine cables that carry intercontinental traffic, last-mile technologies, and the latency physics of fibre, GEO and LEO satellites.
---

"The Internet" is not one network. It comprises independently administered networks exchanging traffic under their routing policies, connected by physical cables under streets and oceans, by switches in shared buildings, and increasingly by satellites.

To reason about latency, outages, costs and why your packets take the route they do, you need the physical and the commercial picture together: who connects to whom, why, over what, and how fast light can get there.

## Autonomous systems and BGP

The unit of the Internet is the **autonomous system** (AS): a network under one administration with its own routing policy, identified by an AS number. An organisation may operate one AS, several ASes, or use another organisation’s routing. Observed AS/prefix counts depend on date, collector and filtering; no undated count is used here.

ASes exchange reachability with **BGP** (Border Gateway Protocol). BGP announcements carry reachability attributes, including **AS_PATH** information. They can be incorrect or manipulated, and AS-path prepending means the attribute is not a simple record of physical routers. BGP chooses routes by **policy** first (business relationships, configured preferences) and only then by things like AS path length. It does not measure latency or bandwidth.

## Transit, peering and the tiers

Two kinds of business relationship connect ASes:

- **Transit**: a customer pays a provider to provide broad Internet reachability according to the service agreement. A full table or default route may be supplied; policy, filtering, partial-transit products and outages qualify “every destination”.
- **Peering**: two networks exchange traffic *between their own networks and customers only*, under agreed policy. **Settlement-free** peering has no traffic-exchange payment between the peers, while ports, circuits and colocation still cost money. Paid peering also exists; equal benefit is not guaranteed.

This creates a loose hierarchy:

```
   [Tier 1] ==peer== [Tier 1]
      |                  |
   transit            transit
      |                  |
   [Tier 2] ==peer== [Tier 2]
      |                  |
   [access ISP]     [content]
```

- **Tier 1** networks can reach every destination without paying anyone for transit: they peer with all other Tier 1s and have their own customers. This is a commercial/topological classification, not an IETF-certified membership list or proof of uninterrupted reachability.
- **Tier 2** networks peer widely but still buy some transit.
- **Tier 3** or stub networks buy transit and do little peering.

### Routing follows the money

A common economic routing model prefers customer routes over peer/provider routes and restricts export. Some operators further prefer peers over providers, but this is policy rather than a BGP requirement. In the simplified export model:

| Learned from | Exported to |
|---|---|
| Customer | everyone |
| Peer | customers only |
| Provider | customers only |

Under these model assumptions, networks do not offer transit between peers/providers. This produces **valley-free** paths: up through providers, at most one peering link across, then down through customers. Real agreements and traffic engineering can deviate from the model. Policy-selected paths need not minimise distance or latency.

> [!warning] Route leaks and hijacks
> BGP trusts announcements by default. In 2008 Pakistan Telecom announced a more specific prefix for YouTube, intended for local blocking; it leaked to its upstream and took YouTube offline for much of the world for hours. In 2019 a small network leaked routes it had learned from one provider to its other provider, Verizon, which accepted them, and significant traffic for Cloudflare and others was drawn through a tiny network. **RPKI route origin validation** checks prefix/origin authorisation against validated ROA information; it does not authenticate the whole AS path or detect every route leak. Local rejection policy, customer prefix filters, relationship-aware controls and monitoring provide complementary defences.

### The flattening of the Internet

Direct interconnection and distributed content delivery add paths outside the simple hierarchy. Content providers can peer with access networks and operate their own transport infrastructure; their footprints and arrangements vary. Netflix's Open Connect and Google Global Cache go further, placing caching servers **inside** ISPs' networks.

Content served inside an ISP or across direct peering need not cross a Tier 1. The fraction of any user’s traffic taking such paths requires measurement.

## Internet exchange points

Peering needs a physical meeting place. An **Internet exchange point** (IXP) is a shared layer 2 switching fabric, often spread across several colocation buildings in a city, where participating networks connect and establish agreed peerings. Sizes, port counts, physical sites and remote-access arrangements differ.

- A shared-fabric port can reach many willing peers, subject to membership and policy, instead of needing a separate physical link for each.
- **Route servers** distribute eligible participant routes according to policy; they normally do not forward the participants’ data traffic. Not every member joins the route server, and joining does not automatically peer with everyone. Redundant sessions are common.
- Large IXPs include DE-CIX Frankfurt, AMS-IX in Amsterdam and LINX in London; traffic peaks are time-sensitive operational measurements, not fixed properties of an IXP.

Networks may use a **private network interconnect** (PNI), such as a dedicated cross-connect or circuit, for capacity or policy reasons. It need not be one fibre in the same building, and there is no universal traffic threshold or majority-share claim here.

## Submarine cables

**Submarine fibre-optic cables** are central to intercontinental connectivity. Traffic shares and cable inventories depend on definitions and date; avoid treating a single unsourced percentage as a universal constant.

How they work:

- Cable systems use **fibre pairs** carrying multiple wavelengths (DWDM). Fibre count and capacity vary by design.
- Long-haul repeatered systems use optical amplifiers at design-specific intervals and shore-fed high-voltage DC power. Shorter unrepeatered systems also exist; spacing and voltage are not universal.
- Modern cables have design capacities in the hundreds of Tbit/s. Google's Dunant cable (US–France, 2021) was announced at 250 Tbit/s.
- Increasingly, cloud and content companies own or co-own cables rather than leasing capacity from telecoms consortia.

ICPC’s June 2025 guidance describes approximately **150–200 faults annually**, with 70–80% attributed to accidental damage, primarily fishing and vessel anchoring. This is a dated industry summary, not a prediction or an exhaustive cause breakdown; other natural and technical causes exist. A marine repair may require a ship to recover the cable and splice it, with timing dependent on fault location, ship availability, weather, permits and the repair method. Networks may reroute over surviving capacity, but regions served by only one or two cables (some island nations, parts of West and East Africa) can lose most connectivity when they are cut.

## The last mile

The **last mile** (or access network) connects homes and businesses to their ISP. It is one possible bottleneck; aggregation, interconnection, servers and local Wi-Fi can also limit service.

| Technology | Medium | Rate interpretation |
|---|---|---|
| ADSL / VDSL2 | copper pair | Profile, line quality, length and deployment determine rate |
| DOCSIS cable | shared coax segment | Version, spectrum allocation and service plan determine rate |
| GPON fibre | shared optical distribution | Common nominal line rates: 2.48832 Gbit/s down / 1.24416 up; not per-home goodput |
| XGS-PON fibre | shared optical distribution | 10 Gbit/s class (9.95328 Gbit/s nominal each way); shared and before protocol overhead |
| Fixed wireless, 4G/5G | radio | widely variable |

- **DSL** runs over the telephone pair. VDSL2 rates depend on copper length, line quality, profile and interference; shorter runs can support higher rates.
- **Cable** (DOCSIS) shares a coax segment among a neighbourhood, so evening peaks can slow everyone; upload is traditionally much lower than download.
- **PON fibre** (FTTP) shares one fibre from the exchange among optical network terminals via passive splitters. Split ratios and scheduling vary; a marketed access rate is not necessarily a permanently reserved equal fraction.

> [!note] Contention
> Several layers can be oversubscribed: the PON split, the ISP's aggregation network, its transit and peering capacity. Capacity planning often uses busy-hour demand and service commitments rather than assuming every user saturates at once. This is a design choice, not a requirement that every link be oversubscribed. The same principle as data-centre oversubscription, applied to a country.

## The physics of latency

Light in optical fibre travels at about c / 1.47, roughly 204,000 km/s, or about **5 µs per km**. A useful rule: **1 ms of round-trip time per 100 km** of fibre.

```python
C = 299_792            # km/s in vacuum
FIBRE = C / 1.47       # ~204,000 km/s

def rtt_ms(km, speed, legs=2):
    if km < 0 or speed <= 0 or legs < 1:
        raise ValueError("bad model input")
    return legs * km / speed * 1000

# Hypothetical 5570 km fibre each way
print(round(rtt_ms(5570, FIBRE), 1))  # 54.6
# GEO: user-sat-ground, and back
print(round(rtt_ms(35786, C, 4)))     # 477
# LEO at 550 km, satellite overhead
print(round(rtt_ms(550, C, 4), 1))    # 7.3
```

The 5,570 km fibre example is a hypothetical route-length calculation, not a measured transatlantic path. Real cable routes and return paths differ, and transmission, processing and queueing add delay. Shorter routes or nearer servers reduce propagation; reducing queueing can also reduce RTT without changing geography.

### GEO satellites

Geostationary satellites orbit at 35,786 km, above the equator, staying fixed in the sky so a dish can point at one permanently. A suitably spaced small GEO set can view much of the non-polar Earth in an ideal coverage model; elevation constraints, beams, capacity and redundancy determine an actual service.

The cost is latency: a request goes up and down, and so does the reply, four legs of nearly 36,000 km. The minimum is about 477 ms of round-trip time from physics alone, under the idealised minimum four-altitude-leg geometry. Slant range, processing and the terrestrial path increase actual RTT; no fixed deployment RTT is assumed. Fine for television broadcast and bulk downloads; painful for interactive use, gaming and many TCP connections.

### LEO constellations

**Low Earth orbit** satellites orbit much nearer Earth than GEO and move across the sky relative to a ground terminal. For a hypothetical 550 km overhead bent-pipe route, four altitude legs contribute about 7.3 ms of propagation. That is not an end-to-end service RTT or a claim about every current commercial orbit shell.

The trade-offs:

- Coverage and capacity determine constellation size; not every LEO service requires thousands of satellites.
- Terminals need suitable satellite tracking and handover, using electronically steered arrays or other supported antenna designs. Handover performance is deployment-specific.
- Traffic must reach a terrestrial gateway somewhere to connect with ground Internet services. Inter-satellite links can move that gateway farther from the user.
- **Laser inter-satellite links** travel approximately at vacuum light speed. A suitably short space route can beat a longer/slower fibre route in propagation, but orbital geometry, actual routing and processing determine the result.
- Shared capacity, obstructions, atmospheric conditions and available gateways affect performance.

| | GEO example | LEO example |
|---|---|---|
| Altitude | 35,786 km | Assumed 550 km |
| Four vertical legs at c | about 477 ms | about 7.3 ms |
| Apparent motion | approximately fixed for a ground observer | moves across the sky |
| Coverage design | non-polar geometry, beam and capacity constraints | constellation, tracking and handover constraints |

## Key takeaways
- BGP exchanges policy-controlled reachability; AS-path length is not geographic distance or an RTT measurement.
- Transit and peering differ in scope and agreement. Valley-free routing is a useful model with explicit assumptions, not a universal law.
- IXPs, private interconnects and embedded caches provide different ways to exchange/deliver traffic.
- Cable resilience requires physical diversity and sufficient surviving capacity; two logical links can share one failure risk.
- Access rates are shared/configuration-dependent, and nominal line rates differ from application goodput.
- Propagation models establish conditional lower bounds; operational latency also includes actual routing, queueing and processing.

> [!note] Evidence limits
> Current AS/prefix counts, IXP peaks, cable traffic shares, commercial satellite fleet sizes and universal measured RTTs are omitted because no consistent dated measurement was established for them. Satellite and fibre examples use explicit hypothetical distances; they do not predict a particular provider’s service or routing advantage. No cable, orbital-link or ISP performance experiment was run.

## Further reading
- [Autonomous system (Internet) — Wikipedia](https://en.wikipedia.org/wiki/Autonomous_system_(Internet))
- [Tier 1 network — Wikipedia](https://en.wikipedia.org/wiki/Tier_1_network)
- [Peering — Wikipedia](https://en.wikipedia.org/wiki/Peering)
- [Internet exchange point — Wikipedia](https://en.wikipedia.org/wiki/Internet_exchange_point)
- [Submarine communications cable — Wikipedia](https://en.wikipedia.org/wiki/Submarine_communications_cable)
- [Submarine Cable Map — TeleGeography](https://www.submarinecablemap.com/)
- [Passive optical network — Wikipedia](https://en.wikipedia.org/wiki/Passive_optical_network)
- [Starlink — Wikipedia](https://en.wikipedia.org/wiki/Starlink)
- [Netflix Open Connect](https://openconnect.netflix.com/en/)

- [ICPC: Cable protection and fault summary, June 2025](https://www.iscpc.org/publications/icpc-viewpoints/charting-submarine-cables-is-critical-for-maritime-safety-and-infrastructure-protection/)
- [Google: Dunant ready for service, February 2021](https://cloud.google.com/blog/products/infrastructure/googles-dunant-subsea-cable-is-now-ready-for-service)
- [ESA: Types of orbits](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)
- [ITU-T G.9807.1: XGS-PON](https://www.itu.int/rec/T-REC-G.9807.1)
- [DE-CIX: Peering and route-server participation](https://docs.de-cix.net/article/n3i1zu0abx-how-to-implement-peering-services)
- [ITU-T G.984.2: GPON physical layer](https://www.itu.int/rec/T-REC-G.984.2)
