---
id: emb-adc-knobs-parameter-maps
sourceLesson: emb-adc-knobs
title: "Map knob travel to useful values"
level: intermediate
minutes: 4
summary: "Linear maps give equal differences; exponential maps give equal ratios."
---

## Mapping values to parameters

The ADC gives a number from 0 to 1 (after scaling). Musical parameters rarely want that range or a straight line.

**Linear mapping** suits parameters we perceive linearly, such as pan position or a mix ratio:

```formula
v = lo + x(hi − lo)
where
v: the parameter value sent to the synth, in the parameter's own unit
x: the knob position after scaling, from 0 (fully anticlockwise) to 1 (fully clockwise), no unit
lo: the parameter value at x = 0
hi: the parameter value at x = 1
In words: start at the bottom of the range and add the same fraction of the range as the knob's fraction of its travel. Equal knob movements give equal differences.
```

**Exponential mapping** suits frequency. Pitch perception is logarithmic: each octave doubles frequency. Map a 20 Hz–20 kHz cutoff linearly and almost the whole knob is spent above 5 kHz. Instead, multiply the bottom of the range by the whole ratio raised to the knob position:

```formula
f = f_lo (f_hi / f_lo)^x
f = 20 Hz × (20000 Hz / 20 Hz)^0.5
f = 20 Hz × 1000^0.5 ≈ 20 Hz × 31.62
f ≈ 632 Hz
where
f: the cutoff frequency the knob sets, in hertz (Hz)
f_lo: the frequency at x = 0, in hertz (Hz); here 20 Hz
f_hi: the frequency at x = 1, in hertz (Hz); here 20 kHz = 20,000 Hz
x: the knob position, from 0 to 1, no unit; here 0.5, the middle
^x: raised to the power x; a power of 0.5 is the square root
Hz: hertz, cycles per second
≈: approximately equal to
In words: the middle of the knob lands at 632 Hz, which is the same ratio (about 31.6 times) above 20 Hz as it is below 20 kHz, so it is the geometric midpoint; subjective cutoff response still depends on filter and signal.
```

The Python below compares both maps at five knob positions:

```python
# Both maps share their frequency endpoints.
lo, hi = 20.0, 20_000.0
for x in (0.0, 0.25, 0.5, 0.75, 1.0):
    lin = lo + x * (hi - lo)
    # Equal x steps now give equal ratios.
    exp = lo * (hi / lo) ** x
    print(f"x={x:.2f} lin={lin:8.0f} "
          f"exp={exp:7.0f}")
```

```output
x=0.00 lin=      20 exp=     20
x=0.25 lin=    5015 exp=    112
x=0.50 lin=   10010 exp=    632
x=0.75 lin=   15005 exp=   3557
x=1.00 lin=   20000 exp=  20000
```

With exponential mapping, equal knob movements give equal frequency *ratios*. 20 Hz to 20 kHz is a ratio of 1,000, which is just under 10 octaves:

```formula
octaves = log_2(f_hi / f_lo)
octaves = log_2(20000 Hz / 20 Hz)
octaves = log_2(1000) ≈ 9.97
step = (f_hi / f_lo)^Δx
step = 1000^0.25 ≈ 5.62
where
octaves: how many doublings of frequency fit in the range
log_2: the base-2 logarithm: log_2(y) is how many times you must double 1 to reach y; log_2(1024) = 10
f_hi: the top of the range, in hertz (Hz); here 20,000 Hz
f_lo: the bottom of the range, in hertz (Hz); here 20 Hz
step: the frequency ratio covered by a knob movement of Δx, anywhere on the knob
Δx: a change in knob position (0 to 1 scale); here a quarter turn of the range, 0.25
Hz: hertz, cycles per second
≈: approximately equal to
In words: the range spans almost 10 octaves, and every quarter of the knob multiplies the frequency by about 5.6, whether you start at 20 Hz or at 3.5 kHz.
```

The same idea applies to envelope times and, in decibels, to volume.

## Key takeaways
- Linear maps give equal differences; exponential maps give equal ratios.
- Choose a curve and valid range for the parameter rather than assuming all controls feel alike.

## Further reading
- [Getting started: ADCs — Electro-Smith](https://docs.daisy.audio/tutorials/_a4_Getting-Started-ADCs/)
- [Teensy 4.1 analog pins — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Coding schemes used with data converters (SBAA042) — Texas Instruments](https://www.ti.com/lit/an/sbaa042/sbaa042.pdf)
- [Analog-to-digital converter — Wikipedia](https://en.wikipedia.org/wiki/Analog-to-digital_converter)
- [Introduction to Digital Filters (one-pole filters) — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/)
