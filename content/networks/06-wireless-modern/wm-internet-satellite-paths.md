---
id: wm-internet-satellite-paths
title: GEO, LEO and satellite path geometry
level: advanced
minutes: 4
summary: A four-leg vertical bent-pipe model isolates altitude propagation from a complete service path.
sourceLesson: wm-internet-structure
---

Satellite Internet trades cables for altitude. How high the satellite orbits decides the minimum latency, which is why geostationary links feel sluggish for interactive use while low-Earth-orbit constellations can compete with terrestrial paths.

## A leg-by-leg propagation model

A satellite link in its simplest "bent pipe" form relays signals: your request goes up to the satellite and down to a ground station, and the reply goes up and down again. That is four legs through space, at almost the vacuum speed of light, so the minimum propagation RTT depends mainly on how high the satellite is.

```formula reference
RTT = (md) / v
where
RTT: the propagation round-trip time, in seconds (s)
m: the number of one-way legs the signal travels: 2 for a direct path (there and back), 4 for a satellite bent pipe (up, down, up, down)
d: the length of each leg, in kilometres (km)
v: the propagation speed: about 204,000 km/s in fibre, about 299,792 km/s in vacuum
In words: the round trip is the number of legs times the length of each, divided by the signal speed; a satellite path has twice as many legs as a direct cable, so altitude counts four times.
```

Taking each leg as the satellite's altitude, directly overhead:

| Path | Legs | Propagation RTT |
|---|---|---|
| GEO, 35,786 km up | 4 | about 477 ms |
| LEO, 550 km up | 4 | about 7.3 ms |
| 5,570 km of fibre | 2 | about 55 ms |

These are idealised minimums for propagation alone, not service RTTs.

## GEO satellites

Geostationary satellites orbit at 35,786 km, above the equator, staying fixed in the sky so a dish can point at one permanently. A suitably spaced small GEO set can view much of the non-polar Earth in an ideal coverage model; elevation constraints, beams, capacity and redundancy determine an actual service.

The cost is latency: a request goes up and down, and so does the reply, four legs of nearly 36,000 km. The minimum is about 477 ms of round-trip time from physics alone, under the idealised minimum four-altitude-leg geometry. Slant range, processing and the terrestrial path increase actual RTT; no fixed deployment RTT is assumed. Fine for television broadcast and bulk downloads; painful for interactive use, gaming and many TCP connections.

## LEO constellations

**Low Earth orbit** satellites orbit much nearer Earth than GEO and move across the sky relative to a ground terminal. For a hypothetical 550 km overhead bent-pipe route, four altitude legs contribute about 7.3 ms of propagation. That is not an end-to-end service RTT or a claim about every current commercial orbit shell.

The trade-offs:

- Coverage and capacity determine constellation size; not every LEO service requires thousands of satellites.
- Terminals need suitable satellite tracking and handover, using electronically steered arrays or other supported antenna designs. Handover performance is deployment-specific.
- Traffic must reach a terrestrial gateway somewhere to connect with ground Internet services. Inter-satellite links can move that ground station farther from the user.
- **Laser inter-satellite links** travel approximately at vacuum light speed. A suitably short space route can beat a longer/slower fibre route in propagation, but orbital geometry, actual routing and processing determine the result.
- Shared capacity, obstructions, atmospheric conditions and available ground gateways affect performance.

| | GEO example | LEO example |
|---|---|---|
| Altitude | 35,786 km | Assumed 550 km |
| Four vertical legs at light speed | about 477 ms | about 7.3 ms |
| Apparent motion | approximately fixed for a ground observer | moves across the sky |
| Coverage design | non-polar geometry, beam and capacity constraints | constellation, tracking and handover constraints |

> [!note] Evidence limits
> Current AS/prefix counts, IXP peaks, cable traffic shares, commercial satellite fleet sizes and universal measured RTTs are omitted because no consistent dated measurement was established for them. Satellite and fibre examples use explicit hypothetical distances; they do not predict a particular provider’s service or routing advantage. No cable, orbital-link or ISP performance experiment was run.

## Key takeaways
- A four-leg vertical bent-pipe model isolates altitude propagation from a complete service path.
- Slant range, routing, tracking, gateways and shared capacity shape an operational satellite service.

## Further reading
- [Starlink — Wikipedia](https://en.wikipedia.org/wiki/Starlink)
- [ESA: Types of orbits](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)
