---
id: elec-hc-hct-interfacing
sourceLesson: elec-logic-levels
title: "Interfacing HC and HCT logic"
level: intermediate
minutes: 3
summary: "Compare actual HC and HCT thresholds before translating logic levels."
---

Use the threshold and noise-margin definitions from the preceding unit to choose an interface. The output limits in this example are illustrative driver guarantees: a high of at least 2.4 V and a low of at most 0.4 V. Check the real part’s load, supply, temperature, edge rates and receiving voltage limits.

## HC and HCT threshold examples

| Part (supply) | Reads high from | Reads low up to |
|---|---|---|
| SN74HC00 (4.5 V) | 3.15 V | 1.35 V |
| SN74HCT00 (4.5–5.5 V) | 2.0 V | 0.8 V |

Checked 29 October 2026: these examples use TI SN74HC00 datasheet SCLS181H (revision H, August 2021) and SN74HCT00 datasheet SCLS062F (revision F, October 2022). The SN74HC00 figures come from its datasheet (Recommended Operating Conditions with a 4.5 V supply). HC input thresholds scale with the supply voltage. The SN74HCT00 figures are "TTL-compatible" thresholds, designed to accept lower-voltage highs.

Suppose a 3.3 V microcontroller output guarantees a high of at least 2.4 V and a low of at most 0.4 V. These are illustrative output guarantees for this calculation, not a specification for an arbitrary microcontroller. Take the real ones from your chip's datasheet at your load current, then compare them with each receiver.

The illustrative 2.4 V guaranteed high falls below the HC input’s 3.15 V requirement, so that state is not guaranteed. The 0.4 V low satisfies its 1.35 V low limit. HCT accepts both: its 2.0 V high threshold and 0.8 V low limit each leave 0.4 V static margin for this driver.

The negative high margin means a 3.3 V output **isn't guaranteed** to be read as high by a 5 V HC input. It may work on your bench and fail on another day or another chip. The HCT part has positive margins in both states, which is why an HCT buffer powered from 5 V is a standard way to translate 3.3 V logic up to 5 V. TI's HCT application note (SCLA011) recommends HCT parts for the closely related problem of feeding TTL-level outputs into HC logic.

### The dangerous direction: 5 V into 3.3 V

Going down is the real hazard. A 5 V output driving a 3.3 V-only input exceeds that input's rating. Options, depending on speed and direction:

- A **level-shifter** chip designed for the job (the robust choice for fast or bidirectional signals).
- A **voltage divider** (two resistors) to scale 5 V down to about 3.3 V, for slow, one-way signals. The divider-loading rules from the earlier divider lessons apply.
- An input the datasheet explicitly specifies as 5 V tolerant, under the stated conditions.

## Key takeaways

- HCT inputs can accept the example driver’s lower high voltage when every stated condition is satisfied.
- Going from a 5 V output to a 3.3 V-only input needs documented level conversion; the board supply does not establish I/O tolerance.

## Further reading

- [TI SN74HC00, SCLS181H](https://www.ti.com/lit/ds/symlink/sn74hc00.pdf)
- [TI SN74HCT00, manufacturer datasheet](https://www.ti.com/lit/ds/symlink/sn74hct00.pdf)
- [TI: interpreting standard-logic datasheets, SZZA036C](https://www.ti.com/lit/an/szza036c/szza036c.pdf)
