---
id: elec-logic-noise-margins
sourceLesson: elec-logic-levels
title: "Logic thresholds and noise margins"
level: intermediate
minutes: 3
summary: "Compare worst-case output levels with guaranteed input thresholds."
---
Compare worst-case output levels with guaranteed input thresholds.

## Logic levels and thresholds
A digital input interprets voltage as high or low. Its datasheet gives guaranteed input regions; the actual switching point may vary between devices and conditions. All inputs must also stay within their permitted voltage range.

| Symbol | Meaning |
|---|---|
| V_IH(min) | Lowest voltage guaranteed read as high |
| V_IL(max) | Highest voltage guaranteed read as low |
| V_OH(min) | Lowest voltage a high output guarantees |
| V_OL(max) | Highest voltage a low output guarantees |

Between V_IL(max) and V_IH(min) is a forbidden zone where the input's behaviour isn't guaranteed.

An output can drive an input reliably only if the worst-case output always lands inside the region the input is guaranteed to accept, in both states.

The weakest guaranteed high from the driver must reach at least the receiver’s high threshold. The highest guaranteed low from the driver must stay at or below the receiver’s low threshold. Check both states under the actual supply, load and temperature conditions.

The gaps between the two sides are the **noise margins**: how much noise (or ground offset) the link can tolerate before a bit is misread:

```formula reference
NM_H = V_{OH(min)} − V_{IH(min)}
NM_L = V_{IL(max)} − V_{OL(max)}
where
NM_H: high-state static noise margin, in volts (V)
NM_L: low-state static noise margin, in volts
V_{OH(min)}: minimum guaranteed driver high voltage, in volts
V_{IH(min)}: receiver’s minimum guaranteed high-input voltage, in volts
V_{IL(max)}: receiver’s maximum guaranteed low-input voltage, in volts
V_{OL(max)}: maximum guaranteed driver low voltage, in volts
In words: Each margin is the distance inside a guaranteed input region. Positive margin allows some noise and ground offset; negative margin gives no guarantee. Timing and voltage stress must still be checked.
```

A driver guaranteed high at 2.4 V or above has room above a receiver’s 2.0 V high threshold. A 0.4 V maximum low also fits below a 0.8 V low threshold. Each leaves 0.4 V static margin; a disturbance larger than that can leave the guaranteed region without necessarily causing a particular chip to switch.

## Key takeaways

- Compare driver and receiver guarantees for both states.
- A positive static margin is a budget for specified noise and ground offset; electrical stress and timing still need separate checks.

## Further reading

- [TI SN74HC00, SCLS181H](https://www.ti.com/lit/ds/symlink/sn74hc00.pdf)
- [TI SN74HCT00, manufacturer datasheet](https://www.ti.com/lit/ds/symlink/sn74hct00.pdf)
- [TI: interpreting standard-logic datasheets, SZZA036C](https://www.ti.com/lit/an/szza036c/szza036c.pdf)
