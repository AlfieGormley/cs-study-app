---
id: elec-reproducible-wiring-notes
sourceLesson: elec-schematics-breadboards
title: "Documenting a reproducible prototype"
level: intermediate
minutes: 1
summary: "Keep the schematic, pin table, parts, photos and measurements together."
---

Keep the schematic, pin table, parts, photos and measurements together.

## Documenting wiring
Your future self, or the project's success criteria ("wiring, parts, limitations ... documented"), needs enough detail to rebuild the circuit:

- **A schematic** with designators and values. A hand drawing photographed is fine early on.
- **A connection table** for anything wired to a board's pins:

| Net | From | To |
|---|---|---|
| +3V3 | Board 3V3 pin | RV1 pin 3 |
| ADC0 | `RV1 pin 2` | Documented ADC input |
| GND | Board GND | RV1 pin 1, rail − |

- **A photo** of the breadboard, taken from above in good light.
- **The exact parts:** manufacturer part numbers or at least values and types, and the board model and revision.
- **What you measured** (expected against actual) and the date.

Keep it with the code in version control, so a wiring change and the code that expects it stay together.

## Key takeaways

- Keep the schematic, pin table, parts, photos and measurements together.
- Name the exact board revision and documentation checked.

## Further reading

- [SparkFun: reading schematics](https://learn.sparkfun.com/tutorials/how-to-read-a-schematic/all)
- [SparkFun: breadboard connections](https://learn.sparkfun.com/tutorials/how-to-use-a-breadboard/all)
