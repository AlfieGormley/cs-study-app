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

When pressed, current flows through the resistor. The pin end of the resistor is now at 0 V and the other end at 3.3 V, so the whole supply voltage sits across it. Ohm's law gives the current:

```formula
I = V / R
I = 3.3 V / 10000 Ω
I = 0.00033 A = 0.33 mA
where
I: the current flowing through the pull-up resistor while the button is held, in amperes (A)
V: the voltage across the resistor, in volts (V); here the full 3.3 V supply, because the pressed button holds the pin at 0 V
R: the pull-up resistance, in ohms (Ω); here 10 kΩ = 10,000 Ω
A: ampere, the unit of current
mA: milliampere, one thousandth of an ampere
Ω: ohm, the unit of resistance
In words: a 10 kΩ pull-up wastes only a third of a milliampere while the button is held; a bigger resistor wastes even less.
```

That is why pull-ups are "weak" (high value): to waste little current while the button is held. The formula assumes the button itself has almost no resistance; a worn or dirty contact adds a little, which only lowers the current.

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
