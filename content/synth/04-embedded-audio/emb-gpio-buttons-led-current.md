---
id: emb-gpio-buttons-led-current
sourceLesson: emb-gpio-buttons
title: "Drive indicator LEDs within limits"
level: basic
minutes: 3
summary: "The LED series resistor takes the remaining voltage; use worst-case limits for real parts."
---

## Give the LED a controlled current

An indicator LED needs a **series resistor** or a suitable current-limiting driver. The LED's **forward voltage** is the voltage across it while conducting; it changes with current, temperature and the particular part. The resistor takes the remaining voltage and limits the current.

An LED is **not ohmic**. Its current rises very steeply over a narrow range of voltage, so a small change in voltage can mean a large change in current. There is no single fixed switch-on voltage: the forward voltage at a given current shifts with temperature and from part to part. That is why you cannot set an LED's current by choosing its voltage directly. The resistor is close to ohmic: its current is proportional to the voltage across it, so it turns the leftover voltage into a predictable current.

Forward voltage also depends on colour and on the particular part. For example, Kingbright's 5 mm WP7113ID red LED lists 1.9 V typical and 2.3 V maximum at 10 mA, while its WP7113QBC/D blue LED lists 3.3 V typical and 4.0 V maximum at 20 mA (datasheets checked 2026-10-29). A blue or white LED on a 3.3 V pin leaves little or no voltage for the resistor, so it may be dim, inconsistent between parts or not light at all. Use the selected part's datasheet values at your intended current.

For the same supply and LED, a smaller resistor normally means more current and brightness; a larger resistor reduces current. Do not connect an LED directly to a GPIO and rely on the pin's resistance to protect it.

### Choose margin, not just a nominal answer

PJRC recommends no more than 4 mA from a Teensy 4.1 output. With an assumed 3.3 V output and a red LED dropping 2.0 V, a 330 Ω resistor gives about 3.9 mA. That is close to the limit **only for those nominal values**. A higher supply voltage, lower LED forward voltage or lower actual resistance can increase current.

A nominal 1 kΩ resistor gives about 1.3 mA in the same example and leaves more margin; confirm that your selected LED is bright enough there. Read its datasheet at the intended current and temperature. Also check the output pin's loaded high-voltage guarantee and resistor tolerance.

This reference relationship helps select a starting resistance; it is not a complete worst-case design:

```formula reference
R = (V_supply − V_f) / I
where
R: series resistance, in ohms (Ω)
V_supply: output pin voltage under the intended load, in volts (V)
V_f: LED forward voltage at the intended current and conditions, in volts (V)
I: intended LED current, in amperes (A)
Ω: ohm, the unit of resistance
V: volt, the unit of voltage
A: ampere, the unit of current
In words: the resistor must absorb the voltage left after the LED's drop, while limiting current to the chosen value. Check worst-case voltages and component tolerances before using the result.
```

### Many LEDs share a package limit

A row of 16 LEDs at 4 mA draws 64 mA when all are on. Every pin can be within its individual limit while the group exceeds a chip or port limit. Check both in the MCU datasheet; Daisy users must consult the STM32H750 limits rather than borrowing the Teensy recommendation.

For many LEDs, use suitable transistors or an LED driver. A shift register saves pins but its own output and package current limits still apply. PWM dims an LED by switching it rapidly; the resistor must still limit the current during each on interval. Switching many outputs can couple supply and ground disturbances into audio.

## Key takeaways
- The LED series resistor takes the remaining voltage; use worst-case limits for real parts.
- Check both per-pin and package current, and use suitable drivers for many LEDs.

## Further reading
- [A Guide to Debouncing, part 1 — Jack Ganssle](https://www.ganssle.com/debouncing.htm)
- [A Guide to Debouncing, part 2 — Jack Ganssle](https://www.ganssle.com/debouncing-pt2.htm)
- [Teensy 4.1 digital pins and limits — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Bounce library — PJRC](https://www.pjrc.com/teensy/td_libs_Bounce.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Pull-up resistor — Wikipedia](https://en.wikipedia.org/wiki/Pull-up_resistor)
- [Teensy 4 core: pinMode pad settings (digital.c) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/digital.c)
- [LED characteristics at specified test conditions — Kingbright](https://www.kingbrightusa.com/images/catalog/SPEC/WP7113ID.pdf)
- [Blue LED characteristics (WP7113QBC/D) — Kingbright](https://www.kingbrightusa.com/images/catalog/SPEC/WP7113QBC-D.pdf)
- [Ohm's law (ohmic and non-ohmic devices) — Wikipedia](https://en.wikipedia.org/wiki/Ohm%27s_law)
