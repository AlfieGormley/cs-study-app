---
id: elec-first-power-checks
sourceLesson: elec-schematics-breadboards
title: "Checking a prototype before first power"
level: intermediate
minutes: 2
summary: "Check component polarity, rail resistance and supply voltage before power."
---

Check component polarity, rail resistance and supply voltage before power.

## Before you apply power
Do these checks every time, and they become fast:

1. **Visual check:** every polarised part (electrolytics, diodes, LEDs, ICs) the right way round. No stray wire ends or component legs touching.
2. **Supply to ground, power off:** use the meter's resistance or continuity mode across the supply rails. A steady near-zero reading or unexplained continuous beep means stop and investigate. Continuity thresholds vary: a beep alone does not prove a dead short. A brief beep that stops can be capacitors charging from the meter. Remove all power sources and discharge stored energy before this test.
3. **Check rail continuity:** each rail connects end to end (or you know where it's split).
4. **Check the supply's voltage before connecting it:** measure the supply's output on its own.
5. **Limit the current if you can:** a bench supply with an adjustable current limit, set just above the expected draw, can reduce sustained fault current. It cannot guarantee protection: supply output capacitance, current-limit reaction delay, device limits and wiring still matter.
6. **First power-up:** observe the supply current and watch for abnormal heat or smell; use a suitable thermometer if needed. Do not touch exposed energised conductors or hot components. Anything getting hot or smelling means disconnect at once.
7. **Measure the rails powered:** confirm the supply voltage at the chip's pins, not just at the supply.

```flow
Visual check of polarity and stray leads
Unpowered resistance check across rails
Verify supply voltage on its own
Set current limit if available
Power up and watch for heat or smell
Measure rail voltages at the chips
```

## Key takeaways

- Check component polarity, rail resistance and supply voltage before power.
- A current limit reduces available fault current but cannot guarantee protection.

## Further reading

- [Keysight E3633A/E3634A: load and output-capacitance limits](https://www.keysight.com/us/en/assets/9018-01164/user-manuals/9018-01164.pdf)
- [Tektronix: bench-supply CV/CC operation](https://www.tek.com/en/blog/bench-power-supply-basics)
- [SparkFun: breadboard connections](https://learn.sparkfun.com/tutorials/how-to-use-a-breadboard/all)
- [Fluke: resistance measurement](https://www.fluke.com/en-us/learn/blog/digital-multimeters/how-to-measure-resistance)
- [SparkFun: using a multimeter](https://learn.sparkfun.com/tutorials/how-to-use-a-multimeter/all)
