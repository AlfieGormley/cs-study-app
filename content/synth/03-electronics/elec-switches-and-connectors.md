---
id: elec-switches-and-connectors
sourceLesson: elec-components
title: "Switch contacts and connector pinouts"
level: intermediate
minutes: 2
summary: "Poles and throws describe routing; momentary describes spring return."
---

Poles and throws describe routing; momentary describes spring return.

## Switches and buttons
Switches are described by their poles and throws: **switch poles** are the independent circuits switched, and **switch throws** are the positions each pole can connect to.

- **SPST:** single pole, single throw. A simple on/off.
- **SPDT:** single pole, double throw. A common terminal switches between two others.
- **DPDT:** two SPDT switches moved together.

**Momentary switches** spring back when released; a normally open push button connects while pressed, whereas a normally closed one opens. **Latching switches** stay in the selected state. Toggle describes the actuator, and toggle switches can be latching or momentary. Tactile buttons often have four legs that are internally connected in pairs. Check which pairs with a continuity tester before wiring.

Mechanical contacts **bounce** (contact bounce): for a few milliseconds a press looks like several rapid presses. A microcontroller reading a button also needs a defined idle level from a pull-up or pull-down resistor. Debouncing and pull-ups are covered with the embedded topics.

## Connectors and pinouts
Connectors are where parts are most often wired wrong.

- **Pin headers** are commonly on a 2.54 mm (0.1 in) contact spacing. Pin 1 is marked by a square pad, a triangle or a dot.
- **Pinout diagrams can be drawn from either side.** "Looking into the socket" and "looking at the solder side" are mirror images. Check which view the diagram shows.
- **Audio jacks:** on a 3.5 mm or 6.35 mm TRS stereo jack, the tip carries left, the ring carries right and the sleeve is ground. On a mono TS jack, the tip carries the signal and the sleeve is ground.
- **Connector keying:** keyed connectors only fit one way. Unkeyed headers fit both ways, including the wrong one.
- **Product-specific connectors** (power inputs, MIDI DIN, board edge headers) have pinouts defined by the product or standard. Take them from that documentation, never from memory. DIN MIDI isn't a direct GPIO connection; it needs the interface circuit from the MIDI specification, covered in a later module.

> [!warning] Component polarity and pinout mistakes destroy parts
> Before power-up, check every polarised part (electrolytics, diodes, LEDs, chips) and every connector orientation against the schematic. It takes a minute and catches the most common fatal mistakes.

## Key takeaways

- Poles and throws describe routing; momentary describes spring return.
- Confirm both internal switch contacts and the view used for a connector pinout.

## Further reading

- [SparkFun: reading schematics](https://learn.sparkfun.com/tutorials/how-to-read-a-schematic/all)
- [SparkFun: breadboard connections](https://learn.sparkfun.com/tutorials/how-to-use-a-breadboard/all)
- [RaneNote 110: system interconnection](https://www.ranecommercial.com/legacy/note110.html)
