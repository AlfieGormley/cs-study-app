---
id: emb-gpio-buttons-pull-resistors
sourceLesson: emb-gpio-buttons
title: "Make button inputs definite"
level: basic
minutes: 3
summary: "A pull resistor defines the released state; an active-low button reads low when pressed."
---

## Floating inputs and pull resistors

An input pin has very high impedance. Connected to nothing, it *floats*: it picks up stray charge and reads random 0s and 1s. A button that only connects the pin to ground when pressed leaves it floating when released.

The fix is a **pull resistor** that sets a default level:

- **Pull-up** to 3.3 V: the pin reads 1 by default.
- **Pull-down** to ground: the pin reads 0 by default.

```diagram
 3.3V
  |
 [R] pull-up (e.g. 10k)
  |
  +------> GPIO input
  |
 [ ] button
  |
 GND
```

With a pull-up, pressing the button connects the pin straight to ground and it reads 0. Released, the resistor pulls it to 1. This is **active-low**: pressed means 0. It is the most common button wiring, and the one PJRC's Bounce library documentation describes ("pushbuttons connect between a pin and ground, and the pin mode is set to INPUT_PULLUP").

When pressed, current flows from 3.3 V through the pull-up and the closed button to ground. The resistor limits that current: a nominal 10 kΩ pull-up draws about 0.33 mA while held. This assumes the switch has negligible resistance and that the resistor is **ohmic**, so its current is proportional to the voltage across it (**Ohm's law**). Ordinary resistors behave this way closely within their ratings. On the same supply, a 1 kΩ pull-up would therefore draw about ten times as much, about 3.3 mA.

A larger pull-up wastes less current, but holds the input less strongly against leakage and interference. A smaller one holds it more firmly but draws more current when pressed. Choose within the pin and switch limits, rather than making the resistance arbitrarily large or small.

> [!analogy] Real-world analogy: A door closer
> A spring-loaded door closer keeps a door shut until someone pushes it open. A stiffer spring resists draughts better, but takes more effort to hold open.
>
> **How it maps:** The pull-up holds the input at its default level, like the closer holding the door shut. Pressing the button overrides it. A lower resistance holds the line more firmly against interference but passes more current while the button is held.
>
> **Where it stops:** A spring stores energy and pushes back with a force that changes as the door moves. A resistor stores nothing: it passes a steady current for as long as the button stays closed, and that current is wasted as heat.

### Internal or external?

Most MCUs have **internal** pull-up and pull-down resistors you switch on in firmware. Their values are typically tens of kilohms and loosely specified. Two examples: Teensy 4.x's `INPUT_PULLUP` selects the i.MX RT pad's 22 kΩ pull-up setting (from PJRC's core source), and ST specifies the STM32H7's weak pull-up at roughly 30–50 kΩ (40 kΩ typical). Treat these as nominal figures, not precise values, and check the datasheet for your exact part. Internal pulls save parts and wiring.

Use an **external** resistor (often 4.7–10 kΩ) when:

- the wire to the switch is long and picks up noise; a stronger (lower) pull-up resists it better;
- you need a known, documented value;
- the pin has something else attached. PJRC warns not to use `INPUT_PULLUP` on Teensy pin 13, which carries the on-board LED.

In firmware, "pressed" for an active-low button is `read() == 0`. Hide the inversion in one place so the rest of the code thinks in "pressed / released".

## Key takeaways
- A pull resistor defines the released state; an active-low button reads low when pressed.
- External pull-ups help when internal values, loading or interference are unsuitable.

## Further reading
- [A Guide to Debouncing, part 1 — Jack Ganssle](https://www.ganssle.com/debouncing.htm)
- [A Guide to Debouncing, part 2 — Jack Ganssle](https://www.ganssle.com/debouncing-pt2.htm)
- [Teensy 4.1 digital pins and limits — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Bounce library — PJRC](https://www.pjrc.com/teensy/td_libs_Bounce.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Pull-up resistor — Wikipedia](https://en.wikipedia.org/wiki/Pull-up_resistor)
- [Teensy 4 core: pinMode pad settings (digital.c) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/digital.c)
- [Ohm's law (ohmic and non-ohmic devices) — Wikipedia](https://en.wikipedia.org/wiki/Ohm%27s_law)
