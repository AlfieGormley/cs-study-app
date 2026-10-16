---
id: elec-meter-voltage-loading
sourceLesson: elec-measurement-soldering
title: "Voltage measurement, ranges and meter loading"
level: intermediate
minutes: 2
summary: "Voltage is measured across two points with the correct jack and range."
---

Measuring tells you whether the circuit is doing what you calculated. Soldering makes a circuit permanent. Both are hands-on skills with a few rules that, if you ignore them, destroy fuses, parts or your lungs.

> [!warning] Low-voltage work only
> Everything here assumes low-voltage DC circuits powered from USB, batteries or a bench supply. Don't use these techniques on mains-powered equipment. Mains measurement needs suitably rated (CAT-rated) instruments and training, and it's outside this project's scope.


A digital multimeter (DMM) has a rotary switch and usually three or four input jacks:

- **COM:** the common (black) lead. It stays here for everything.
- **VΩ** (shared with current only on some meters): red lead for voltage, resistance, continuity and diode test.
- **mA / µA:** red lead for small currents, protected by a fuse.
- **A or 10A:** red lead for large currents, fused only if the meter’s manual specifies it; some inexpensive meters leave that input unfused.

The jack layout differs between meters, so read the manual.


### Voltage: in parallel
Put the probes **across** the thing you're measuring, black on the reference (usually ground) and red on the point of interest. Nothing gets disconnected.

```diagram
  +5V ──[ R1 ]──┬──[ LED ]── GND
                │
             red probe
   (black probe on GND)
```

- Use **DC volts** (V⎓) for supply rails and logic. AC volts usually rejects the DC component, so it will not tell you a rail’s steady voltage. An average-responding meter is RMS-calibrated for a sine wave; other waveforms need a suitable true-RMS instrument within its frequency, crest-factor and range limits.
- A digital meter's voltage input is high-impedance, typically around 10 MΩ on DC volts, though some meters and ranges differ (check your meter's specification). It barely loads most circuits, but on a very high-resistance divider the meter itself pulls the reading down. Lesson 2's loading rule applies to meters too.
- A negative DC reading means the red probe is below the black probe in voltage. The probes may be reversed, or the measured voltage may genuinely have the opposite polarity.

### Choosing ranges
Autoranging meters choose for you. On a manual meter:

- **Start on a range above the largest value you expect,** then step down for resolution.
- An "OL" or "1" display means meter over-range. Go up a range.
- For current, start on the highest range if you're unsure, which on many meters means moving the red lead to the A jack.

## Key takeaways

- Voltage is measured across two points with the correct jack and range.
- The meter’s finite input impedance can load high-resistance circuits.

## Further reading

- [SparkFun: using a multimeter](https://learn.sparkfun.com/tutorials/how-to-use-a-multimeter/all)
- [SparkFun: voltage dividers](https://learn.sparkfun.com/tutorials/voltage-dividers/all)
