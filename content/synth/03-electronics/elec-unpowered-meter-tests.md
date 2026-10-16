---
id: elec-unpowered-meter-tests
sourceLesson: elec-measurement-soldering
title: "Unpowered resistance and continuity checks"
level: intermediate
minutes: 1
summary: "Remove all power and discharge capacitors before resistance tests."
---

Remove all power and discharge capacitors before resistance tests.

### Resistance and continuity: only unpowered
Resistance mode works by passing a small test current from the meter's own battery and measuring the resulting voltage. So:

- **The circuit must be unpowered.** External voltages corrupt the reading and can damage the meter.
- **Measure parts out of circuit, or lift one leg.** In circuit, other paths in parallel lower the reading. Lesson 2's parallel rule explains why.
- **Continuity mode** beeps below a low resistance threshold. Use it to check wires, solder joints, breadboard rails and switch contacts, and to find shorts.
- **Diode test mode** shows a diode's forward voltage (about 0.5–0.7 V for silicon) one way and open circuit the other. It often lights an LED faintly too, which is handy for identifying LED orientation.
- Discharge large capacitors before measuring around them.

## Key takeaways

- Remove all power and discharge capacitors before resistance tests.
- Parallel circuit paths can invalidate an in-circuit component measurement.

## Further reading

- [Fluke: resistance measurement](https://www.fluke.com/en-us/learn/blog/digital-multimeters/how-to-measure-resistance)
- [SparkFun: using a multimeter](https://learn.sparkfun.com/tutorials/how-to-use-a-multimeter/all)
