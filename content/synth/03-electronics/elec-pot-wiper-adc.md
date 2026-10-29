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

Wire one end to the supply, the other to ground, and the wiper is a divider output. The wiper divides the fixed end-to-end track into an upper and a lower resistance; turning the knob changes their split, not their total. Moving towards the supply end increases the lower share and raises the unloaded output; moving towards ground lowers it.

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

The source resistance seen by an ADC is the two track segments in parallel, assuming a stiff supply. It is lowest near the ends and largest where the two segments have equal resistance: at mid-rotation for an ideal linear pot. The maximum is one quarter of the total track resistance: 25 kΩ for a 100 kΩ pot, or 2.5 kΩ for a 10 kΩ pot.

A high source resistance can prevent the ADC’s sampling capacitor settling in time. Use a lower-value pot, a documented longer ADC acquisition time or a suitable buffer/filter arrangement as the ADC manufacturer recommends. A capacitor alone is not a universal fix.

## Key takeaways

- Use the documented analogue supply and ADC voltage limits.
- A pot’s wiper source resistance peaks in the middle of a linear track.

## Further reading

- [Bourns PDB181-GTR: circuit and taper charts](https://www.bourns.com/docs/product-datasheets/PDB181-GTR.pdf)
- [SparkFun: voltage dividers](https://learn.sparkfun.com/tutorials/voltage-dividers/all)
- [PJRC: Teensy 4.1 signal-voltage limits](https://www.pjrc.com/store/teensy41.html)
- [Microchip: ADC acquisition time](https://developerhelp.microchip.com/xwiki/bin/view/products/data-converters/adc-specs/acquisition-time/)
