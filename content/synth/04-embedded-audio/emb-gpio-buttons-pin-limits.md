---
id: emb-gpio-buttons-pin-limits
sourceLesson: emb-gpio-buttons
title: "GPIO modes and voltage limits"
level: basic
minutes: 2
summary: "Configure each pin for its intended role before use."
---

A synth panel is mostly buttons, switches and LEDs. Each one connects to a **GPIO** (general-purpose input/output) pin. The ideas are simple, but two things trip up nearly every beginner: inputs that float, and buttons that bounce. Get those right and the "controls respond predictably" goal in the project brief becomes achievable.

All voltages in this lesson are low-voltage logic levels (3.3 V). No mains wiring is involved.

## Digital pins: inputs and outputs

A GPIO pin is configured in firmware as either:

- **Input.** The MCU reads the voltage on the pin as a logic 0 (near 0 V) or 1 (near the supply, here 3.3 V). In between is undefined.
- **Output.** The MCU drives low or high, able to source or sink limited current. Loaded output voltages differ from ideal 0 V and 3.3 V; check the datasheet guarantees.

```
pin_mode(BUTTON_PIN, INPUT_PULLUP)
pin_mode(LED_PIN, OUTPUT)
loop:
  pressed = (read(BUTTON_PIN) == 0)
  write(LED_PIN, pressed ? 1 : 0)
```

### Check the voltage limits first

Never assume a pin tolerates 5 V. The two candidate boards differ:

| Board | GPIO input limit |
|---|---|
| Teensy 4.1 | 0–3.3 V; not 5 V tolerant |
| Daisy Seed Rev 7 | Most pins 5 V tolerant |
| Daisy Seed Rev 7 | Pins 24, 25, 28, 29, 30: 3.3 V |

Sources: PJRC Teensy 4.1 page; Daisy Seed datasheet v1.2.0, Table 1. Both checked 2026-10-16. The Daisy pin numbers above are physical header positions, not libDaisy D-number labels. The table is a board-level digital-I/O summary, not permission to apply 5 V in ADC mode or with the board unpowered. ADC inputs remain limited to their documented analogue range. Design for 3.3 V logic unless a documented interface requires otherwise. Re-check the datasheet for your exact revision.

## Key takeaways
- Configure each pin for its intended role before use.
- Check pin-specific voltage limits, including board revision and operating mode.

## Further reading
- [A Guide to Debouncing, part 1 — Jack Ganssle](https://www.ganssle.com/debouncing.htm)
- [A Guide to Debouncing, part 2 — Jack Ganssle](https://www.ganssle.com/debouncing-pt2.htm)
- [Teensy 4.1 digital pins and limits — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Bounce library — PJRC](https://www.pjrc.com/teensy/td_libs_Bounce.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Pull-up resistor — Wikipedia](https://en.wikipedia.org/wiki/Pull-up_resistor)
- [Teensy 4 core: pinMode pad settings (digital.c) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/digital.c)
