---
id: wm-internet-satellite-paths
title: GEO, LEO and satellite path geometry
level: advanced
minutes: 5
summary: A four-leg vertical bent-pipe model isolates altitude propagation from a complete service path.
sourceLesson: wm-internet-structure
---

This unit focuses on GEO, LEO and satellite path geometry. It builds on the earlier units in this module; the examples below state their additional assumptions.

## A leg-by-leg propagation model

The same formula, with the number of legs made explicit, covers satellites, where the signal goes up and down in vacuum at approximately vacuum light speed:

```formula
RTT = (md) / v
RTT_fibre = (2 × 5,570 km) / 204,000 km/s
RTT_fibre ≈ 0.0546 s = 54.6 ms
RTT_GEO = (4 × 35,786 km) / 299,792 km/s
RTT_GEO ≈ 0.477 s = 477 ms
RTT_LEO = (4 × 550 km) / 299,792 km/s
RTT_LEO ≈ 0.0073 s = 7.3 ms
where
RTT: the propagation round-trip time, in seconds (s) or milliseconds (ms)
m: the number of one-way legs the signal travels: 2 for a direct path (there and back), 4 for a satellite bent pipe (up, down, up, down)
d: the length of each leg, in kilometres (km)
v: the propagation speed: about 204,000 km/s in fibre, 299,792 km/s in vacuum
RTT_fibre: a hypothetical 5,570 km fibre route; its propagation RTT is in seconds or milliseconds
RTT_GEO: a geostationary satellite overhead, 35,786 km up
RTT_LEO: a low-Earth-orbit satellite overhead, 550 km up
km/s: kilometres per second
s: second
ms: millisecond
≈: approximately equal to
In words: the supplied four-leg GEO model contributes about 477 milliseconds of propagation, while the supplied overhead 550-kilometre LEO model contributes about 7.3 milliseconds; neither is a full service RTT.
```

The same model in Python:

```python
C = 299_792            # km/s in vacuum
FIBRE = C / 1.47       # ~204,000 km/s

def rtt_ms(km, speed, legs=2):
    if km < 0 or speed <= 0 or legs < 1:
        raise ValueError("bad model input")
    return legs * km / speed * 1000

# Hypothetical 5570 km fibre each way
print(round(rtt_ms(5570, FIBRE), 1))  # 54.6
# GEO: four ideal altitude legs, in ms.
print(round(rtt_ms(35786, C, 4)))     # 477
# LEO: four 550 km legs; no processing.
print(round(rtt_ms(550, C, 4), 1))    # 7.3
```


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
