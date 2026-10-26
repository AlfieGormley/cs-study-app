---
id: snd-line-level-voltage
title: From digital full scale to line voltage
level: intermediate
minutes: 3
summary: Convert dBu and dBV to RMS volts and match the synth output to its destination safely.
sourceLesson: snd-levels
---

## From dBFS to volts

The DAC turns 0 dBFS into some maximum output voltage. That voltage is set by the codec and the output circuit, so it's on the board's datasheet, not a universal number. What your audio interface expects is in its manual. Two common nominal **line levels** use different references:

| Level | Reference | RMS voltage |
|---|---|---|
| +4 dBu (pro) | 0 dBu = 0.7746 V | ≈ 1.228 V |
| −10 dBV (consumer) | 0 dBV = 1 V | ≈ 0.316 V |

Converting either unit to an RMS voltage is the decibel formula run backwards, with that unit's reference voltage:

```formula reference
V = V_ref × 10^(L / 20)
where
V: the RMS voltage, in volts (V)
V_ref: the reference voltage: 0.7746 V for dBu, 1 V for dBV
L: the level, in dBu or dBV; here +4 dBu and −10 dBV
10^x: 10 raised to the power x
dBu: decibels relative to 0.7746 V RMS
dBV: decibels relative to 1 V RMS
In words: +4 dBu is 4 dB above 0.7746 V, about 1.228 V RMS; −10 dBV is 10 dB below 1 V, about 0.316 V RMS.
```

These are *nominal* levels; real signals peak well above them, and equipment has headroom for that. Check both the synth's maximum output and the interface input's maximum level in their manuals, and set the synth's output level so that its loudest patch doesn't overload the input.

> [!warning] Keep to line-level connections
> Turn the monitor level down before testing a new connection and raise it gradually. Line, instrument, microphone, headphone and speaker connections are not interchangeable. Never connect a power amplifier's speaker output to a line input or to a development board. Work only with low-voltage, battery or USB-powered circuits and the board's documented audio outputs, and add any output protection the board's documentation recommends.

## Key takeaways

- dBu and dBV use different RMS voltage references; digital dBFS depends on the actual converter and circuit.
- Nominal line level leaves headroom for signal peaks. Check both devices’ maximum levels.
- Use documented line-level outputs and low-voltage circuits; speaker outputs must not feed line inputs.

## Further reading

- [Line level — Wikipedia](https://en.wikipedia.org/wiki/Line_level)
- [RMS voltage references and crest factor — RaneNote 169](https://www.ranecommercial.com/legacy/note169.html)
