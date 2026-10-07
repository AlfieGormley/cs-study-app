from pathlib import Path
p=Path('content/networks/06-wireless-modern/wm-internet-structure.md');s=p.read_text()
def r(a,b):
 global s
 assert a in s,a[:70]
 s=s.replace(a,b)
r('Your ISP, a cloud provider, a university and a large bank are each an AS. More than 70,000 ASes appear in the global routing table, which carries around a million IPv4 prefixes.','An organisation may operate one AS, several ASes, or use another organisation’s routing. Observed AS/prefix counts depend on date, collector and filtering; no undated count is used here.')
r('Each AS announces the prefixes it can deliver, and each announcement carries the **AS path** it has travelled.','BGP announcements carry reachability attributes, including **AS_PATH** information. They can be incorrect or manipulated, and AS-path prepending means the attribute is not a simple record of physical routers.')
r('carry its traffic to and from *the whole Internet*. The provider announces the customer\'s routes to everyone and gives the customer a full table (or a default route).','provide broad Internet reachability according to the service agreement. A full table or default route may be supplied; policy, filtering, partial-transit products and outages qualify “every destination”.')
r('typically **settlement-free** (no money changes hands) because both benefit roughly equally.','under agreed policy. **Settlement-free** peering has no traffic-exchange payment between the peers, while ports, circuits and colocation still cost money. Paid peering also exists; equal benefit is not guaranteed.')
r('Examples include Lumen, NTT, Arelion and Tata Communications. The membership list is debated, and rarely matters in practice.','This is a commercial/topological classification, not an IETF-certified membership list or proof of uninterrupted reachability.')
r('Networks prefer routes in order of revenue: **customer routes** (they get paid) over **peer routes** (free) over **provider routes** (they pay). And they **export** selectively:','A common economic routing model prefers customer routes over peer/provider routes and restricts export. Some operators further prefer peers over providers, but this is policy rather than a BGP requirement. In the simplified export model:')
r('No network carries traffic between two of its peers or two providers for free. The result is **valley-free** paths:','Under these model assumptions, networks do not offer transit between peers/providers. This produces **valley-free** paths:')
r('It also means BGP\'s chosen path is often not the shortest or fastest one.','Real agreements and traffic engineering can deviate from the model. Policy-selected paths need not minimise distance or latency.')
r('**RPKI** route origin validation and filtering customer announcements are the defences.','**RPKI route origin validation** checks prefix/origin authorisation against validated ROA information; it does not authenticate the whole AS path or detect every route leak. Local rejection policy, customer prefix filters, relationship-aware controls and monitoring provide complementary defences.')
r('The tidy hierarchy has largely given way to a flatter mesh. Large content networks such as Google, Meta, Netflix, Amazon, Microsoft and Cloudflare run their own global backbones and peer directly with access ISPs in hundreds of locations.','Direct interconnection and distributed content delivery add paths outside the simple hierarchy. Content providers can peer with access networks and operate their own transport infrastructure; their footprints and arrangements vary.')
r('As a result, much of the traffic a typical home user receives never crosses a Tier 1 network: it comes from a cache in their ISP or across a single peering link from the content provider.','Content served inside an ISP or across direct peering need not cross a Tier 1. The fraction of any user’s traffic taking such paths requires measurement.')
r('where hundreds of networks connect one port each and peer with each other over it.','where participating networks connect and establish agreed peerings. Sizes, port counts, physical sites and remote-access arrangements differ.')
r('**Route servers** let a network peer with many others through a single BGP session.','**Route servers** distribute eligible participant routes according to policy; they normally do not forward the participants’ data traffic. Not every member joins the route server, and joining does not automatically peer with everyone. Redundant sessions are common.')
r('DE-CIX Frankfurt\'s peak traffic is above 10 Tbit/s.','traffic peaks are time-sensitive operational measurements, not fixed properties of an IXP.')
r('When two networks exchange a lot of traffic, they move it to a **private network interconnect** (PNI): a dedicated fibre between their routers in the same colocation facility (often run by Equinix, Digital Realty and similar). PNIs carry most traffic between the largest networks; IXPs provide breadth.','Networks may use a **private network interconnect** (PNI), such as a dedicated cross-connect or circuit, for capacity or policy reasons. It need not be one fibre in the same building, and there is no universal traffic threshold or majority-share claim here.')
r('Between continents, almost everything travels through **submarine fibre-optic cables**; the figure often quoted is about 99% of intercontinental traffic. There are several hundred cable systems, totalling well over a million kilometres.','**Submarine fibre-optic cables** are central to intercontinental connectivity. Traffic shares and cable inventories depend on definitions and date; avoid treating a single unsourced percentage as a universal constant.')
r('Each cable holds a small number of **fibre pairs** (often 8 to 24 in modern systems), each carrying many wavelengths of light (DWDM).','Cable systems use **fibre pairs** carrying multiple wavelengths (DWDM). Fibre count and capacity vary by design.')
r('**Repeaters** every 50–100 km or so amplify the light optically. They are powered by direct current fed along the cable from the shore at thousands of volts.','Long-haul repeatered systems use optical amplifiers at design-specific intervals and shore-fed high-voltage DC power. Shorter unrepeatered systems also exist; spacing and voltage are not universal.')
r('**Faults** happen often: roughly 150–200 a year worldwide, mostly from fishing gear and ship anchors in shallow water, plus earthquakes and undersea landslides.','ICPC’s June 2025 guidance describes approximately **150–200 faults annually**, with 70–80% attributed to accidental damage, primarily fishing and vessel anchoring. This is a dated industry summary, not a prediction or an exhaustive cause breakdown; other natural and technical causes exist.')
r('which can take days to weeks.','with timing dependent on fault location, ship availability, weather, permits and the repair method.')
r('Networks survive because traffic reroutes over other cables,','Networks may reroute over surviving capacity,')
r('It is usually where bandwidth is lowest and contention is highest.','It is one possible bottleneck; aggregation, interconnection, servers and local Wi-Fi can also limit service.')
r('| Technology | Medium | Typical speeds |','| Technology | Medium | Rate interpretation |')
r('| ADSL / VDSL2 | phone copper | 10–80 Mbit/s, falls with distance |','| ADSL / VDSL2 | copper pair | Profile, line quality, length and deployment determine rate |')
r('| DOCSIS cable | coax, shared | 100 Mbit/s to 1 Gbit/s+ down |','| DOCSIS cable | shared coax segment | Version, spectrum allocation and service plan determine rate |')
r('| GPON fibre | fibre, shared | 2.5 down / 1.25 up, split |','| GPON fibre | shared optical distribution | Common nominal line rates: 2.48832 Gbit/s down / 1.24416 up; not per-home goodput |')
r('| XGS-PON fibre | fibre, shared | 10 Gbit/s symmetric, split |','| XGS-PON fibre | shared optical distribution | Nominal 10 Gbit/s symmetric line rate; shared and before protocol overhead |')
r('among typically 32 or 64 homes via passive optical splitters. Each home\'s plan is a slice of the shared rate.','among optical network terminals via passive splitters. Split ratios and scheduling vary; a marketed access rate is not necessarily a permanently reserved equal fraction.')
r('Every layer is oversubscribed:','Several layers can be oversubscribed:')
r('ISPs size them for typical busy-hour demand, not for every customer at full speed at once.','Capacity planning often uses busy-hour demand and service commitments rather than assuming every user saturates at once. This is a design choice, not a requirement that every link be oversubscribed.')
r('def rtt_ms(km, speed, legs=2):\n    return','def rtt_ms(km, speed, legs=2):\n    if km < 0 or speed <= 0 or legs < 1:\n        raise ValueError("invalid model input")\n    return')
r('# London-New York fibre, great circle','# Hypothetical 5570 km fibre each way')
r('Real London–New York RTTs are around 70 ms, because cables do not follow great circles and routers, terrestrial backhaul and queues add more. No protocol optimisation can beat the speed of light; the only fix for distance is to move the server closer (CDNs, edge regions, caches inside ISPs).','The 5,570 km fibre example is a hypothetical route-length calculation, not a measured transatlantic path. Real cable routes and return paths differ, and transmission, processing and queueing add delay. Shorter routes or nearer servers reduce propagation; reducing queueing can also reduce RTT without changing geography.')
r('Three satellites can cover most of the planet.','A suitably spaced small GEO set can view much of the non-polar Earth in an ideal coverage model; elevation constraints, beams, capacity and redundancy determine an actual service.')
r('and real-world figures are typically around 600 ms or more.','under the idealised minimum four-altitude-leg geometry. Slant range, processing and the terrestrial path increase actual RTT; no fixed deployment RTT is assumed.')
a=s.index('**Low Earth orbit** constellations');b=s.index('## Further reading',a)
s=s[:a]+'''**Low Earth orbit** satellites orbit much nearer Earth than GEO and move across the sky relative to a ground terminal. For a hypothetical 550 km overhead bent-pipe route, four altitude legs contribute about 7.3 ms of propagation. That is not an end-to-end service RTT or a claim about every current commercial orbit shell.

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

''' +s[b:]
s+='\n- [ICPC: Cable protection and fault summary, June 2025](https://www.iscpc.org/publications/icpc-viewpoints/charting-submarine-cables-is-critical-for-maritime-safety-and-infrastructure-protection/)\n- [Google: Dunant ready for service, February 2021](https://cloud.google.com/blog/products/infrastructure/googles-dunant-subsea-cable-is-now-ready-for-service)\n- [ESA: Types of orbits](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)\n- [ITU-T G.9807.1: XGS-PON](https://www.itu.int/rec/T-REC-G.9807.1)\n- [DE-CIX: Peering and route-server participation](https://docs.de-cix.net/article/n3i1zu0abx-how-to-implement-peering-services)\n'
p.write_text(s)
