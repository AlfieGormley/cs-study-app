---
id: elec-pot-wiper-adc
sourceLesson: elec-dividers
title: "Wiring a potentiometer to an ADC"
level: basic
minutes: 2
summary: "Use the documented analogue supply and ADC voltage limits."
---

Use the documented analogue supply and ADC voltage limits.

## The potentiometer: a divider with a moving tap
A **potentiometer** (pot) is a resistive track with a wiper that slides along it. It has three terminals: the two ends of the track and the wiper.

```diagram
  pin 1 ──/\/\/\/\/\/\── pin 3
              ↑
           pin 2 (wiper)
```

Wire one end to the supply, the other to ground, and the wiper is a divider output. Turn the knob and you move the wiper position between the upper part of the track and the lower part. The total stays fixed:

```formula
R_top + R_bottom = R_pot
V_wiper = Vin R_bottom / R_pot
where
R_top: the track resistance between the supply end and the wiper, in ohms (Ω)
R_bottom: the track resistance between the wiper and the ground end, in ohms
R_pot: the pot's total (end-to-end) resistance, in ohms, e.g. 10 kΩ
V_wiper: the voltage on the wiper, measured to ground, in volts (V)
Vin: the voltage across the whole track, in volts
In words: the two parts of the track always add up to the pot's value, and the wiper voltage is the input scaled by the lower part's share.
```

For an unloaded linear 10 kΩ pot across 3.3 V, a quarter-track setting leaves 2.5 kΩ below the wiper and gives about 0.83 V. This assumes the ground end is the bottom and the track is ideal.

For a microcontroller knob:

```diagram
 3.3V ── pin 3
        pot track ── pin 2 ── ADC pin
 GND ── pin 1
```

Points to watch:

- **Use the board's documented analogue supply for the pot, matching the ADC range.** Do not load an unbuffered VREF pin unless the documentation explicitly allows it. If the pot is fed from a different voltage, the ADC's full range won't match the knob's full range. Feeding it from a higher voltage could also exceed the input's maximum (the logic and datasheet units).
- **Swapping pins 1 and 3** reverses the direction of the knob. It's harmless and easily fixed in software.
- **Never wire the wiper straight to a supply rail.** At one extreme the wiper sits at the end connected to ground, and you'd short the supply through a few ohms of track.
- **The pot's resistance** trades divider standing current against source impedance. Values around 10 kΩ are a common choice for microcontroller knobs, but confirm against the ADC's source-impedance limit.

## Worst-case source resistance

```formula
R_bottom = x R_pot
R_top = (1 − x)R_pot
R_out = R_pot x(1 − x)
R_out ≤ R_pot / 4
R_out = 100 kΩ / 4 = 25 kΩ
where
R_bottom: track resistance from wiper to ground, in ohms (Ω)
R_top: track resistance from supply to wiper, in ohms
R_pot: total ideal linear-track resistance, in ohms; 100 kΩ in the last line
x: fraction of the track below the wiper, between zero and one
R_out: unloaded wiper source resistance, in ohms; the last line is at mid-track
≤: less than or equal to
kΩ: kilohms, one thousand ohms
In words: The two track segments appear in parallel to a load. Their product is largest at mid-track, so a 100 kΩ pot can present 25 kΩ to the ADC. Do not assume that meets the ADC acquisition-time requirement.
```

## Key takeaways

- Use the documented analogue supply and ADC voltage limits.
- A pot’s wiper source resistance peaks in the middle of a linear track.

## Further reading

- [Bourns PDB181-GTR: circuit and taper charts](https://www.bourns.com/docs/product-datasheets/PDB181-GTR.pdf)
- [SparkFun: voltage dividers](https://learn.sparkfun.com/tutorials/voltage-dividers/all)
- [PJRC: Teensy 4.1 signal-voltage limits](https://www.pjrc.com/store/teensy41.html)
