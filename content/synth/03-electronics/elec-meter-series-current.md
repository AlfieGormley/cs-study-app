---
id: elec-meter-series-current
sourceLesson: elec-measurement-soldering
title: "Measuring series current and burden voltage"
level: intermediate
minutes: 2
summary: "Power off before inserting the meter in series."
---

Power off before inserting the meter in series.

### Current: in series
To measure current, the current has to flow **through** the meter. Break the circuit and insert the meter into the gap:

```diagram
  +5V ──[ R1 ]──  ✂  ──[ LED ]── GND
              red    black
               └─ meter ─┘
```

1. Power off.
2. Move the red lead to the **mA** jack (or the A jack for larger currents) and select the current range.
3. Open the circuit at one point and connect the meter across the gap.
4. Power on and read.
5. **Power off and move the red lead back to VΩ** before your next measurement.

> [!warning] The classic fuse-blower
> In current mode the meter is almost a short circuit, by design. Put it *across* a supply (as you would for voltage) and you short the supply through the meter. The meter's fuse is there to blow in that case. Replace it only with the **exact type and rating** the manual specifies. Forgetting to move the red lead back to VΩ is the commonest way to do this.

Meters also have a **burden voltage**: the small voltage the meter drops while measuring current. It comes from the series resistance of the shunt and other current-path parts, including the fuse and connections. Model their combined resistance to estimate it with Ohm’s law:

```formula
V_burden = I × R_shunt
V_burden = 0.010 A × 10 Ω = 0.1 V
where
V_burden: the voltage lost across the meter, in volts (V)
I: the current being measured, here 10 mA = 0.010 amperes (A)
R_shunt: the combined series resistance of the meter’s current path on that range, in ohms (Ω); 10 Ω is illustrative, so check the specified burden voltage and lead effects
V: volts
A: amperes
Ω: ohms
In words: the meter steals a little voltage from the circuit, more at higher currents and on more sensitive ranges.
```

On sensitive low-voltage circuits that stolen voltage can slightly change what you're measuring. Compare that drop with the voltage left for the current-setting parts and with your allowed error. Even in a 5 V circuit, a 0.1 V drop can matter if an LED leaves little resistor headroom.

## Key takeaways

- Power off before inserting the meter in series.
- Restore the voltage jack after current measurements.

## Further reading

- [Fluke: current measurement](https://www.fluke.com/en-gb/learn/blog/digital-multimeters/how-to-measure-current)
- [SparkFun: using a multimeter](https://learn.sparkfun.com/tutorials/how-to-use-a-multimeter/all)
