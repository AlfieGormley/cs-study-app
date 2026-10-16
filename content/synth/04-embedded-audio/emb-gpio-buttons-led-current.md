---
id: emb-gpio-buttons-led-current
sourceLesson: emb-gpio-buttons
title: "Drive indicator LEDs within limits"
level: basic
minutes: 3
summary: "The LED series resistor takes the remaining voltage; use worst-case limits for real parts."
---

## Driving LEDs

An LED needs a series resistor to limit current. An LED has a curved current–voltage relationship: its **forward voltage** changes with current, temperature and the particular part. For a first nominal calculation use the datasheet voltage at the intended current, then check worst-case values. So the resistor takes up the rest of the supply voltage, and Ohm's law on the resistor alone gives the value you need:

```formula
R = (V_supply − V_f) / I
where
R: the series resistor, in ohms (Ω)
V_supply: the voltage the output pin drives when high, in volts (V); 3.3 V on Teensy and Daisy
V_f: the LED's forward voltage, in volts (V): roughly 1.8–2.2 V for red, up to about 3 V for blue or white; take it from the LED's datasheet
I: the current you want through the LED, in amperes (A); a few milliamperes (mA) for an indicator
Ω: ohm, the unit of resistance
V: volt, the unit of voltage
A: ampere, the unit of current
In words: subtract the LED's own voltage from the supply, then divide what is left by the current you want. A smaller resistor gives more current and a brighter LED.
```

PJRC gives a recommended maximum of 4 mA per Teensy 4.1 output. With a red LED at a forward voltage of about 2.0 V (check the LED's datasheet), the nominal resistance at that current is:

```formula
R_min = (V_supply − V_f) / I_max
R_min = (3.3 V − 2.0 V) / 0.004 A
R_min = 1.3 V / 0.004 A = 325 Ω
where
R_min: the nominal minimum series resistance for the assumed voltages and current, in ohms (Ω); real selection needs worst-case limits
V_supply: the output pin's high voltage, in volts (V); here 3.3 V
V_f: the red LED's forward voltage, in volts (V); here about 2.0 V
I_max: the largest current allowed, in amperes (A); here PJRC's 4 mA = 0.004 A
Ω: ohm, the unit of resistance
V: volt, the unit of voltage
A: ampere, the unit of current
In words: 1.3 V is left for the resistor, and 1.3 V at 4 mA needs 325 Ω, so select the next larger standard resistor value, 330 Ω.
```

The same sum in Python, also checking two standard resistor values:

```python
# Nominal fixture; not a worst-case design.
v_supply, v_f = 3.3, 2.0
i_max = 0.004            # 4 mA
r_min = (v_supply - v_f) / i_max
print(f"R_min = {r_min:.0f} ohm")
# Compare nominal current for each resistor.
for r in (330, 1000):
    i = (v_supply - v_f) / r * 1000
    print(f"{r} ohm -> {i:.1f} mA")
```

```output
R_min = 325 ohm
330 ohm -> 3.9 mA
1000 ohm -> 1.3 mA
```

330 Ω sits just inside the limit only at the nominal voltages used here. Check worst-case supply, LED forward voltage and resistor tolerances; 1 kΩ leaves more margin, but confirm brightness at that current from the selected LED datasheet or measurement. The Daisy Seed datasheet's LED example simply says the resistor value depends on the desired brightness and the LED part; for the current limit, consult ST's STM32H750 datasheet.

Pins also have a **total** current limit for the whole chip. A row of 16 LEDs at 4 mA is 64 mA, which may exceed it. For many LEDs, use a transistor or suitable LED driver. A shift register can save MCU pins, but its own output and package current limits still apply; it is not automatically a safe high-current driver. PWM (rapid switching) on an output dims LEDs without changing the resistor.

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
