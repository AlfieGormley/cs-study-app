---
id: emb-adc-knobs-change-hysteresis
sourceLesson: emb-adc-knobs
title: "Keep change detection quiet"
level: intermediate
minutes: 2
summary: "A dead band can reject bounded jitter that smoothing alone still passes."
---

## Hysteresis: stop the chatter

Smoothing shrinks jitter but does not remove it. To make bounded jitter around a held reading produce a still accepted value, add **hysteresis** (a dead band): only accept a new value when it differs from the held one by more than a threshold.

> [!analogy] Real-world analogy: A thermostat that does not chatter
> A heating thermostat set to switch on below 19 °C and off above 21 °C does not click on and off every few seconds when the room hovers around 20 °C.
>
> **How it maps:** The gap between switching points is the dead band. The held knob value changes only when a reading moves beyond the band, so small jitter around the held value produces no new event.
>
> **Where it stops:** A thermostat has two fixed switching points around a setpoint. The knob's band is centred on the last accepted value and moves with it. Make the band too wide and small deliberate turns are ignored.

```python
# Knob at rest; ADC codes jitter by +-2.
reads = [2048, 2050, 2047, 2049, 2046,
         2048, 2050, 2047, 2046, 2049]

def changes(xs):
    return sum(1 for a, b in zip(xs, xs[1:])
               if a != b)

# Hold the accepted code inside a dead band.
def hysteresis(xs, band):
    held = xs[0]
    out = []
    for x in xs:
        if abs(x - held) > band:
            held = x
        out.append(held)
    return out

# Startup windows contain only known
# readings.
def moving_avg(xs, n):
    out = []
    for i in range(len(xs)):
        w = xs[max(0, i - n + 1): i + 1]
        out.append(sum(w) // len(w))
    return out

# Count accepted changes for this exact
# trace.
print("raw changes:", changes(reads))
a = moving_avg(reads, 4)
print("avg4 changes:", changes(a),
      "range:", min(a), max(a))
h = hysteresis(reads, 3)
print("hyst3 changes:", changes(h), h[-1])
```

```output
raw changes: 9
avg4 changes: 6 range: 2047 2049
hyst3 changes: 0 2048
```

The raw value changed on every one of the nine steps. The 4-point average still changed six times, wandering between 2047 and 2049. Hysteresis with a ±3 band holds 2048 throughout. The cost: a deliberate movement must exceed the band before anything happens, so make the band just wider than the noise you measured.

A common pipeline is **smooth, then hysteresis for change detection**, then pass the smoothed value to the audio code, which applies its own per-sample smoothing (the safe-transfer units).

## Key takeaways
- A dead band can reject bounded jitter that smoothing alone still passes.
- Use hysteresis for change events and audio-rate smoothing for the sound parameter.

## Further reading
- [Getting started: ADCs — Electro-Smith](https://docs.daisy.audio/tutorials/_a4_Getting-Started-ADCs/)
- [Teensy 4.1 analog pins — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Coding schemes used with data converters (SBAA042) — Texas Instruments](https://www.ti.com/lit/an/sbaa042/sbaa042.pdf)
- [Analog-to-digital converter — Wikipedia](https://en.wikipedia.org/wiki/Analog-to-digital_converter)
- [Introduction to Digital Filters (one-pole filters) — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/)
