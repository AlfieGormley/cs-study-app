---
id: elec-schematics-breadboards
title: Schematics and breadboarding
level: intermediate
minutes: 14
summary: Reading schematic symbols and nets, how a solderless breadboard is connected inside, translating a schematic into wiring, documenting it so you can rebuild it, and the checks to make before applying power.
---

A schematic says *what connects to what*. A breadboard is one physical way to make those connections. The skill is moving between the two without error, and checking your work before power goes on.

## Common symbols

Symbols vary between the US/ANSI style and the IEC style used in Europe. You'll meet both.

| Part | Symbol notes | Designator |
|---|---|---|
| Resistor | Zigzag (US) or rectangle (IEC) | R1, R2 |
| Capacitor | Two parallel plates | C1 |
| Polarised capacitor | One plate curved or marked + | C2 |
| Diode | Triangle against a bar (bar = cathode) | D1 |
| LED | Diode with outward arrows | D2, LED1 |
| Potentiometer | Resistor with an arrow (wiper) | RV1, VR1 |
| Switch / button | Broken line with a lever | SW1, S1 |
| IC | Box with numbered pins | U1, IC1 |
| Connector / jack | Varies; pins numbered | J1, P1 |
| Ground | Downward lines or a triangle | GND |
| Supply | Arrow, bar or label (+5V, 3V3) | VCC |

The **reference designator** (R1, C3, U2) links each symbol to the parts list and to the board's silkscreen. Use designators in your notes too: "R3 is wrong" is unambiguous.

## Reading a schematic

### Nets, not pictures

A schematic is a graph. Each **net** is a set of pins joined together electrically. Wire lengths and positions mean nothing; only connections do.

- **Junction dots** mark wires that connect. Two wires crossing *without* a dot don't connect. Many drawing conventions avoid four-way junctions entirely, so a cross is never ambiguous.
- **Net labels:** two wires with the same label (for example `ADC0` or `+3V3`) are connected even if no line joins them.
- **Power and ground symbols** are net labels too. Every ground symbol is the same net, as is every `+3V3`.
- **Hidden power pins:** some schematics omit an IC's supply pins from the drawing. Check the datasheet pinout so you don't forget to power the chip.

### Conventions that help

- Signals usually flow **left to right**: inputs on the left, outputs on the right.
- Higher voltages at the **top**, ground at the **bottom**.
- Values sit beside designators: `R1 10k`, `C4 100n`.

> [!example] Reading a pot input
> `+3V3 → RV1 pin 3`, `RV1 pin 1 → GND`, `RV1 pin 2 → net ADC0`, `C5 100n from ADC0 to GND`, and elsewhere `ADC0 → U1 pin 14`. That's three nets: +3V3, GND and ADC0. ADC0 has three members: the pot's wiper, C5 and U1 pin 14.

## How a breadboard is connected

A solderless breadboard has spring clips under the holes, joined in fixed groups:

```diagram
  + rail  ● ● ● ● ●   ● ● ● ● ●
  − rail  ● ● ● ● ●   ● ● ● ● ●

 row:  1   2   3   4   5   6
   a   ●   ●   ●   ●   ●   ●
   b   ●   ●   ●   ●   ●   ●
   c   ●   ●   ●   ●   ●   ●
   d   ●   ●   ●   ●   ●   ●
   e   ●   ●   ●   ●   ●   ●
      ===== centre channel =====
   f   ●   ●   ●   ●   ●   ●
   g   ●   ●   ●   ●   ●   ●
   h   ●   ●   ●   ●   ●   ●
   i   ●   ●   ●   ●   ●   ●
   j   ●   ●   ●   ●   ●   ●

  − rail  ● ● ● ● ●   ● ● ● ● ●
  + rail  ● ● ● ● ●   ● ● ● ● ●
```

- **Terminal strips:** in each numbered row, holes a–e are connected to each other, and f–j are connected to each other. The two halves are **not** connected across the centre channel.
- **Centre channel:** DIP chips straddle it, so each pin gets its own strip.
- **Power rails:** long strips along each edge, usually marked red (+) and blue or black (−).
- **Rails on opposite sides aren't connected.** Bridge them with jumpers if you want the same supply on both sides.
- **Some boards split the rails halfway along.** A gap in the red or blue line often marks this. Check with a continuity tester, because a split rail is a classic "half my circuit is dead" bug.

## From schematic to breadboard

A systematic method avoids most wiring errors:

1. **Number the nets.** Write every net from the schematic as a list: GND, +3V3, ADC0, LED_A, and so on.
2. **Give each net a home.** Power and ground go on the rails. Each other net gets one terminal strip (or several joined by a jumper).
3. **Place ICs across the channel first,** with pin 1 in a known row. Then place parts around them.
4. **Plug each component lead into the strip for its net.** A resistor between ADC0 and GND has one lead in the ADC0 row and one on the − rail.
5. **Avoid shorting a component to itself.** Both legs of a resistor in the same strip connect it to nothing.
6. **Colour code wires:** red for positive supply, black or blue for ground, other colours for signals. It's a convention, not a rule, but it makes checking much faster.
7. **Tick off each connection** on the schematic as you make it.

> [!tip] Breadboard limits
> Breadboards are for low-voltage, low-current, low-frequency prototyping. Spring contacts have some resistance and can loosen. Adjacent strips add a few picofarads of stray capacitance. Long jumpers pick up noise. Expect an audio prototype on a breadboard to be noisier than the finished build. That's normal, and it's no reason to chase every hum on the breadboard.

## Documenting wiring

Your future self, or the project's success criteria ("wiring, parts, limitations ... documented"), needs enough detail to rebuild the circuit:

- **A schematic** with designators and values. A hand drawing photographed is fine early on.
- **A connection table** for anything wired to a board's pins:

| Net | From | To |
|---|---|---|
| +3V3 | Board 3V3 pin | RV1 pin 3 |
| ADC0 | RV1 pin 2 | Board pin A0 |
| GND | Board GND | RV1 pin 1, rail − |

- **A photo** of the breadboard, taken from above in good light.
- **The exact parts:** manufacturer part numbers or at least values and types, and the board model and revision.
- **What you measured** (expected against actual) and the date.

Keep it with the code in version control, so a wiring change and the code that expects it stay together.

## Before you apply power

Do these checks every time, and they become fast:

1. **Visual check:** every polarised part (electrolytics, diodes, LEDs, ICs) the right way round. No stray wire ends or component legs touching.
2. **Supply to ground, power off:** use the meter's resistance or continuity mode across the supply rails. A dead short (a near-zero reading or a continuous beep) means stop and find it. A brief beep that stops can be capacitors charging from the meter.
3. **Check rail continuity:** each rail connects end to end (or you know where it's split).
4. **Check the supply's voltage before connecting it:** measure the supply's output on its own.
5. **Limit the current if you can:** a bench supply with an adjustable current limit, set just above the expected draw, turns a short into a reading instead of smoke.
6. **First power-up:** watch, sniff and touch-test carefully (hover a finger near parts rather than gripping them). Anything getting hot or smelling means disconnect at once.
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

- Schematics show nets. Junction dots and net labels define connections; geometry doesn't.
- Use reference designators everywhere: R1, C3, U1, J2.
- In a breadboard row, a–e connect and f–j connect, not across the channel. Rails may be split and opposite rails aren't joined.
- Translate by nets: one strip per net, power on the rails, ICs across the channel, tick off connections.
- Document with a schematic, a connection table, a photo, part numbers and measurements, kept in version control.
- Before power: check polarity, measure rail-to-rail resistance unpowered, verify the supply, limit current, then watch and measure.

## Further reading

- [How to read a schematic (SparkFun)](https://learn.sparkfun.com/tutorials/how-to-read-a-schematic/all)
- [Electronic symbol (Wikipedia)](https://en.wikipedia.org/wiki/Electronic_symbol)
- [Circuit diagram (Wikipedia)](https://en.wikipedia.org/wiki/Circuit_diagram)
- [How to use a breadboard (SparkFun)](https://learn.sparkfun.com/tutorials/how-to-use-a-breadboard/all)
- [Breadboard (Wikipedia)](https://en.wikipedia.org/wiki/Breadboard)
