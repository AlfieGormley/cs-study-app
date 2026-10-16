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
A digital input doesn't care about the exact voltage. It decides "high" or "low" using thresholds from its datasheet:

| Symbol | Meaning |
|---|---|
| V_IH(min) | Lowest voltage guaranteed read as high |
| V_IL(max) | Highest voltage guaranteed read as low |
| V_OH(min) | Lowest voltage a high output guarantees |
| V_OL(max) | Highest voltage a low output guarantees |

Between V_IL(max) and V_IH(min) is a forbidden zone where the input's behaviour isn't guaranteed.

An output can drive an input reliably only if the worst-case output always lands inside the region the input is guaranteed to accept, in both states:

```formula
V_{OH(min)} ≥ V_{IH(min)}
V_{OL(max)} ≤ V_{IL(max)}
where
V_{OH(min)}: the lowest voltage the driving output guarantees when it outputs a high, in volts (V)
V_{IH(min)}: the lowest voltage the receiving input is guaranteed to read as high, in volts
V_{OL(max)}: the highest voltage the driving output guarantees when it outputs a low, in volts
V_{IL(max)}: the highest voltage the receiving input is guaranteed to read as low, in volts
≥: is greater than or equal to
≤: is less than or equal to
In words: the first line says the weakest high the output can produce is still high enough for the input; the second says the worst low is still low enough. Both must be true.
```

The gaps between the two sides are the **noise margins**: how much noise (or ground offset) the link can tolerate before a bit is misread:

```formula
NM_H = V_{OH(min)} − V_{IH(min)}
NM_L = V_{IL(max)} − V_{OL(max)}
where
NM_H: the high-state noise margin, in volts (V)
NM_L: the low-state noise margin, in volts
V_{OH(min)}: the output's guaranteed minimum high voltage
V_{IH(min)}: the input's minimum voltage guaranteed to read as high
V_{IL(max)}: the input's maximum voltage guaranteed to read as low
V_{OL(max)}: the output's guaranteed maximum low voltage
In words: each margin is how far the worst-case output sits inside the input's acceptance region. A positive static margin leaves that amount for noise and ground offset under the stated load, supply and temperature conditions. Timing, edge rate and voltage stress still need separate checks; a negative margin gives no guarantee of correct interpretation.
```

## Key takeaways

- Compare driver and receiver guarantees for both states.
- A positive static margin is a budget for specified noise and ground offset; electrical stress and timing still need separate checks.

## Further reading

- [TI SN74HC00, SCLS181H](https://www.ti.com/lit/ds/symlink/sn74hc00.pdf)
- [TI SN74HCT00, manufacturer datasheet](https://www.ti.com/lit/ds/symlink/sn74hct00.pdf)
- [TI: interpreting standard-logic datasheets, SZZA036C](https://www.ti.com/lit/an/szza036c/szza036c.pdf)
