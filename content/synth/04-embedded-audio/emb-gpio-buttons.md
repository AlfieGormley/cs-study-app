---
id: emb-gpio-buttons
title: GPIO and buttons
level: basic
minutes: 13
summary: Digital inputs and outputs, pull-up and pull-down resistors, active-low buttons, why switches bounce and four debouncing algorithms, and driving LEDs within a pin's current limits.
---

A synth panel is mostly buttons, switches and LEDs. Each one connects to a **GPIO** (general-purpose input/output) pin. The ideas are simple, but two things trip up nearly every beginner: inputs that float, and buttons that bounce. Get those right and the "controls respond predictably" goal in the project brief becomes achievable.

All voltages in this lesson are low-voltage logic levels (3.3 V). No mains wiring is involved.

## Digital pins: inputs and outputs

A GPIO pin is configured in firmware as either:

- **Input.** The MCU reads the voltage on the pin as a logic 0 (near 0 V) or 1 (near the supply, here 3.3 V). In between is undefined.
- **Output.** The MCU drives the pin to 0 V or 3.3 V, able to source or sink a limited current.

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

Sources: PJRC Teensy 4.1 page; Daisy Seed datasheet v1.2.0, Table 1. Both checked 2026-10-04. Even on a "tolerant" pin, design for 3.3 V logic unless you have a reason not to. Re-check the datasheet for your exact revision.

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

When pressed, current flows through the resistor: with 10 kΩ, I = 3.3 V / 10,000 Ω = 0.33 mA. That is why pull-ups are "weak" (high value): to waste little current while the button is held.

### Internal or external?

Most MCUs have **internal** pull-up and pull-down resistors you switch on in firmware. Their values are typically tens of kilohms and loosely specified. Two examples: Teensy 4.x's `INPUT_PULLUP` selects the i.MX RT pad's 22 kΩ pull-up setting (from PJRC's core source), and ST specifies the STM32H7's weak pull-up at roughly 30–50 kΩ (40 kΩ typical). Treat these as nominal figures, not precise values, and check the datasheet for your exact part. Internal pulls save parts and wiring.

Use an **external** resistor (often 4.7–10 kΩ) when:

- the wire to the switch is long and picks up noise; a stronger (lower) pull-up resists it better;
- you need a known, documented value;
- the pin has something else attached. PJRC warns not to use `INPUT_PULLUP` on Teensy pin 13, which carries the on-board LED.

In firmware, "pressed" for an active-low button is `read() == 0`. Hide the inversion in one place so the rest of the code thinks in "pressed / released".

## Switch bounce

When metal contacts close, they do not make one clean connection. They bounce apart and together for a short time, so the MCU sees a burst of transitions.

```
ideal:    ‾‾‾‾‾‾‾‾|________________
bouncing: ‾‾‾‾‾|_|‾|_||‾|__________
               <- bounce ->
```

How long? Jack Ganssle measured 18 different switches. Excluding two outliers, the other 16 averaged 1,557 µs of bounce, with a maximum of 6,200 µs. One outlier, a pushbutton, bounced for 157 ms when it opened (on release); the other once took 11.3 ms to close. His advice: most switches settle well under 10 ms, so use a debounce period of about 20 ms to be conservative. Separately, he found a 100 ms delay between press and response noticeable, while 50 ms seemed instantaneous, which gives you an upper bound on how much latency a debouncer can add.

If you count raw transitions, one press might register as five presses. For a synth, that means a menu skips items or a note retriggers.

> [!warning] Don't wire raw switches to interrupts
> Ganssle warns against connecting an undebounced switch to an interrupt input: very short glitches can fire an interrupt that ordinary polling would miss. Poll buttons on a regular tick (around 1 ms is common) instead.

## Four debouncing algorithms

All four below are called on a regular tick (say every 1 ms) with the raw reading, already inverted so 1 means pressed.

**1. Lockout (react, then ignore).** Accept the first change immediately, then ignore the pin for N ms. Fastest response, but a single noise spike counts as a press.

**2. Stable-for-N (time-based).** Only accept a new state after the input has disagreed with the current state for N consecutive ticks. Any bounce back resets the count. Robust and simple; adds N ms of latency. PJRC's Bounce library takes a milliseconds interval in this spirit.

**3. Shift register.** Shift each reading into a byte. A press edge is the pattern "one 0 followed by seven 1s" (`0x7F`); a release is `0x80`. libDaisy's `Switch` class works exactly this way, updating at most once per millisecond.

```
on tick:
  reg = ((reg << 1) | raw) & 0xFF
  if reg == 0x7F: on_press()
  if reg == 0x80: on_release()
```

**4. Integrator.** Keep a counter between 0 and TOP. Add one for each 1, subtract one for each 0 (clamped). Output becomes pressed only when the counter reaches TOP and released only when it reaches 0. Occasional opposite readings slow it down but do not reset it, which suits noisy inputs.

```
on tick:
  if raw == 1: acc = min(acc + 1, TOP)
  else:        acc = max(acc - 1, 0)
  if acc == TOP: state = PRESSED
  if acc == 0:   state = RELEASED
```

### Comparing them on one bouncy trace

This Python simulation feeds the same 35 ms trace (1 sample per ms, 1 = pressed) to each algorithm and prints the times of the debounced edges.

```python
raw = [0,0,1,0,1,1,0,1,1,1,1,1,1,1,1,
       1,1,1,1,1,0,1,0,0,1,0,0,0,0,0,
       0,0,0,0,0]

def edges(seq):
    return [t for t in range(1, len(seq))
            if seq[t] != seq[t - 1]]

def lockout(xs, hold):
    out, state, until = [], 0, 0
    for t, s in enumerate(xs):
        if t >= until and s != state:
            state, until = s, t + hold
        out.append(state)
    return out

def stable_for(xs, n):
    out, state, count = [], 0, 0
    for s in xs:
        if s != state:
            count += 1
        else:
            count = 0
        if count >= n:
            state, count = s, 0
        out.append(state)
    return out

def integrator(xs, top):
    out, acc, state = [], 0, 0
    for s in xs:
        acc = min(acc + 1, top) if s \
            else max(acc - 1, 0)
        if acc == top:
            state = 1
        elif acc == 0:
            state = 0
        out.append(state)
    return out

def shift_edges(xs):
    reg, found = 0, []
    for t, s in enumerate(xs):
        reg = ((reg << 1) | s) & 0xFF
        if reg == 0x7F:
            found.append(("press", t))
        if reg == 0x80:
            found.append(("release", t))
    return found

print("raw edges:", len(edges(raw)))
print("stable5:", edges(stable_for(raw, 5)))
print("integ4:", edges(integrator(raw, 4)))
print("shift:", shift_edges(raw))
print("lockout10:", edges(lockout(raw, 10)))
```

Output:

```
raw edges: 10
stable5: [11, 29]
integ4: [9, 27]
shift: [('press', 13), ('release', 31)]
lockout10: [2, 20]
```

Ten raw transitions become exactly one press and one release with every method. The difference is latency: lockout responds at 2 ms (on the very first bounce), the integrator at 9 ms, stable-for-5 at 11 ms, the shift register at 13 ms. Lockout is fastest because it trusts the first edge, which is also why a glitch can fool it.

The windows here (4–10 ms) are short so the trace fits on screen. On real hardware, start nearer Ganssle's 20 ms and adjust after testing your actual switches.

### Hardware debouncing

An RC filter (resistor plus capacitor) followed by a Schmitt-trigger input smooths bounce in hardware. Ganssle's second article walks through the maths. On an MCU with spare cycles, software debouncing is cheaper and adjustable, so it is the usual first choice.

## Driving LEDs

An LED needs a series resistor to limit current. The resistor drops the difference between the supply and the LED's forward voltage V_f:

R = (V_supply − V_f) / I

PJRC gives a recommended maximum of 4 mA per Teensy 4.1 output. With a red LED at V_f ≈ 2.0 V (check the LED's datasheet):

```python
v_supply, v_f = 3.3, 2.0
i_max = 0.004            # 4 mA
r_min = (v_supply - v_f) / i_max
print(f"R_min = {r_min:.0f} ohm")
for r in (330, 1000):
    i = (v_supply - v_f) / r * 1000
    print(f"{r} ohm -> {i:.1f} mA")
```

```
R_min = 325 ohm
330 ohm -> 3.9 mA
1000 ohm -> 1.3 mA
```

330 Ω sits just inside the limit only at the nominal voltages used here. Check worst-case supply, LED forward voltage and resistor tolerances; 1 kΩ leaves more margin, and modern LEDs are often bright enough at 1–2 mA. The Daisy Seed datasheet's LED example simply says the resistor value depends on the desired brightness and the LED part; for the current limit, consult ST's STM32H750 datasheet.

Pins also have a **total** current limit for the whole chip. A row of 16 LEDs at 4 mA is 64 mA, which may exceed it. For many LEDs, use a transistor, an LED driver chip or a shift register so the MCU only supplies logic signals. PWM (rapid switching) on an output dims LEDs without changing the resistor.

## Key takeaways
- Check each pin's voltage limit in the current datasheet; Teensy 4.x pins are not 5 V tolerant and Daisy has some 3.3 V-only pins.
- An unconnected input floats. Use a pull-up and an active-low button: pressed reads 0.
- Switches bounce for around a millisecond or two, sometimes far longer. Poll on a tick and debounce in software; don't send raw switches to interrupts.
- Lockout is fastest but trusts glitches; stable-for-N, shift-register and integrator methods trade a few milliseconds for robustness.
- LED resistor: R = (V_supply − V_f) / I. Respect per-pin and total-chip current limits.

## Further reading
- [A Guide to Debouncing, part 1 — Jack Ganssle](https://www.ganssle.com/debouncing.htm)
- [A Guide to Debouncing, part 2 — Jack Ganssle](https://www.ganssle.com/debouncing-pt2.htm)
- [Teensy 4.1 digital pins and limits — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Bounce library — PJRC](https://www.pjrc.com/teensy/td_libs_Bounce.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Pull-up resistor — Wikipedia](https://en.wikipedia.org/wiki/Pull-up_resistor)
- [Teensy 4 core: pinMode pad settings (digital.c) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/digital.c)
