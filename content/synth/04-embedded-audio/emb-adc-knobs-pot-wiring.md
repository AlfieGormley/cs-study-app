---
id: emb-adc-knobs-pot-wiring
sourceLesson: emb-adc-knobs
title: "Wire a knob and recognise jitter"
level: intermediate
minutes: 2
summary: "Use the documented analogue supply and ADC-capable pin for a potentiometer."
---

## Reading a potentiometer

```diagram
 3.3V (analogue) --+
                   |
                 [pot]<-- wiper --> ADC
                   |
 GND --------------+
```

Both ends of the pot go to ground and the 3.3 V **analogue** supply; the wiper goes to an ADC-capable pin. Daisy's ADC guide wires pin 1 to GND, pin 3 to `3v3_A` and the middle leg to the ADC input. The Daisy Seed datasheet's example part is a 10 kΩ linear pot.

Two practical points:

- **Use the analogue supply as the top reference** when the board provides one. When the pot and ADC reference track the same supply, this ratiometric arrangement can reject common supply changes; it does not cancel unrelated noise or reference differences.
- **Pot value.** Most MCU ADCs charge a small internal sampling capacitor through your source. Very high-value pots can make readings inaccurate; low values waste current. 10 kΩ is a common middle ground (check the MCU datasheet's source-impedance guidance).

Pot **taper** matters too. A linear pot gives voltage proportional to rotation; an audio/log pot does not. B often means linear and A audio/log, but markings vary between manufacturers: confirm the taper in its datasheet. With an ADC in the loop, it is usually easier to use linear pots and apply the curve in software, where you can change it.
## Noise and jitter

Leave a knob still and read it repeatedly, and the code wanders by a few LSBs. Sources include supply ripple, digital switching noise coupling into the analogue path, and the ADC's own noise. If you feed the raw value straight into a parameter, two things go wrong:

1. **Zipper noise.** The parameter jumps in small steps that you can hear, especially on gain and filter cutoff.
2. **Chatter.** Anything that reacts to changes (sending MIDI CC, redrawing a display, recalling a preset) fires constantly while the knob is untouched.

## Key takeaways
- Use the documented analogue supply and ADC-capable pin for a potentiometer.
- Source impedance, taper, supply coupling and noise affect the useful readings.

## Further reading
- [Getting started: ADCs — Electro-Smith](https://docs.daisy.audio/tutorials/_a4_Getting-Started-ADCs/)
- [Teensy 4.1 analog pins — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Coding schemes used with data converters (SBAA042) — Texas Instruments](https://www.ti.com/lit/an/sbaa042/sbaa042.pdf)
- [Analog-to-digital converter — Wikipedia](https://en.wikipedia.org/wiki/Analog-to-digital_converter)
- [Introduction to Digital Filters (one-pole filters) — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/)
