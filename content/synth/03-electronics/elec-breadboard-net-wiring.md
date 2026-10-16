---
id: elec-breadboard-net-wiring
sourceLesson: elec-schematics-breadboards
title: "Breadboard connections and net-by-net wiring"
level: intermediate
minutes: 3
summary: "Verify the board’s internal strips and any split rails unpowered."
---

Verify the board’s internal strips and any split rails unpowered.

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
5. **Avoid shorting a component to itself.** Both legs of a resistor in the same strip bypass its resistance: both ends are on the same net.
6. **Colour code wires:** red for positive supply, black or blue for ground, other colours for signals. It's a convention, not a rule, but it makes checking much faster.
7. **Tick off each connection** on the schematic as you make it.

> [!tip] Breadboard limits
> Breadboards are for low-voltage, low-current, low-frequency prototyping. Spring contacts have some resistance and can loosen. Adjacent strips add stray capacitance whose value depends on the board and wiring. Long jumpers pick up noise. An audio prototype can be noisier than a well laid out finished board. Record the limitation and investigate unexplained hum rather than assuming every noise is unavoidable.

## Key takeaways

- Verify the board’s internal strips and any split rails unpowered.
- Place component ends on the intended different nets.

## Further reading

- [SparkFun: breadboard connections](https://learn.sparkfun.com/tutorials/how-to-use-a-breadboard/all)
- [SparkFun: reading schematics](https://learn.sparkfun.com/tutorials/how-to-read-a-schematic/all)
