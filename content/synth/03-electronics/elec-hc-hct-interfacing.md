---
id: elec-hc-hct-interfacing
sourceLesson: elec-logic-levels
title: "Interfacing HC and HCT logic"
level: intermediate
minutes: 4
summary: "Compare actual HC and HCT thresholds before translating logic levels."
---

Use the threshold and noise-margin definitions from the preceding unit to choose an interface. The output limits in this example are illustrative driver guarantees: a high of at least 2.4 V and a low of at most 0.4 V. Check the real part’s load, supply, temperature, edge rates and receiving voltage limits.

## HC and HCT threshold examples

| Part (supply) | Reads high from | Reads low up to |
|---|---|---|
| SN74HC00 (4.5 V) | 3.15 V | 1.35 V |
| SN74HCT00 (4.5–5.5 V) | 2.0 V | 0.8 V |

Checked 16 October 2026: these examples use TI SN74HC00 datasheet SCLS181H (revision H, August 2021) and SN74HCT00 datasheet SCLS062F (revision F, October 2022). The SN74HC00 figures come from its datasheet (Recommended Operating Conditions with a 4.5 V supply). HC input thresholds scale with the supply voltage. The SN74HCT00 figures are "TTL-compatible" thresholds, designed to accept lower-voltage highs.

Suppose a 3.3 V microcontroller output guarantees a high of at least 2.4 V and a low of at most 0.4 V. These are illustrative output guarantees for this calculation, not a specification for an arbitrary microcontroller. Take the real ones from your chip's datasheet at your load current. Into each part:

```formula
HC:  NM_H = 2.4 V − 3.15 V = −0.75 V
HC:  NM_L = 1.35 V − 0.4 V = +0.95 V
HCT: NM_H = 2.4 V − 2.0 V = +0.4 V
HCT: NM_L = 0.8 V − 0.4 V = +0.4 V
where
HC: the SN74HC00 at a 4.5 V supply
HCT: the SN74HCT00 at a 4.5–5.5 V supply
NM_H: the high-state noise margin, the output's 2.4 V minimum high minus the input's minimum high, in volts (V)
NM_L: the low-state noise margin, the input's maximum low minus the output's 0.4 V maximum low, in volts
V: volts
In words: into the HC part the high margin is negative, so a high isn't guaranteed to be seen as high. Into the HCT part both margins are a positive 0.4 V, so these static input thresholds are met with 0.4 V of margin under the stated conditions.
```

The same check in Python:

```python
# Tuple: high and low margins, in volts.
def margins(voh, vol, vih, vil):
    hi = voh - vih   # high noise margin
    lo = vil - vol   # low noise margin
    return round(hi, 2), round(lo, 2)

# 3.3 V output into 74HC at 4.5 V
print(margins(2.4, 0.4, 3.15, 1.35))
# same output into 74HCT
print(margins(2.4, 0.4, 2.0, 0.8))
```

```
(-0.75, 0.95)
(0.4, 0.4)
```

The negative high margin means a 3.3 V output **isn't guaranteed** to be read as high by a 5 V HC input. It may work on your bench and fail on another day or another chip. The HCT part has positive margins in both states, which is why an HCT buffer powered from 5 V is a standard way to translate 3.3 V logic up to 5 V. TI's HCT application note (SCLA011) recommends HCT parts for the closely related problem of feeding TTL-level outputs into HC logic.

### The dangerous direction: 5 V into 3.3 V

Going down is the real hazard. A 5 V output driving a 3.3 V-only input exceeds that input's rating. Options, depending on speed and direction:

- A **level-shifter** chip designed for the job (the robust choice for fast or bidirectional signals).
- A **voltage divider** (two resistors) to scale 5 V down to about 3.3 V, for slow, one-way signals. Lesson 2's loading rules apply.
- An input the datasheet explicitly specifies as 5 V tolerant, under the stated conditions.

## Key takeaways

- HCT inputs can accept the example driver’s lower high voltage when every stated condition is satisfied.
- Going from a 5 V output to a 3.3 V-only input needs documented level conversion; the board supply does not establish I/O tolerance.

## Further reading

- [TI SN74HC00, SCLS181H](https://www.ti.com/lit/ds/symlink/sn74hc00.pdf)
- [TI SN74HCT00, manufacturer datasheet](https://www.ti.com/lit/ds/symlink/sn74hct00.pdf)
- [TI: interpreting standard-logic datasheets, SZZA036C](https://www.ti.com/lit/an/szza036c/szza036c.pdf)
