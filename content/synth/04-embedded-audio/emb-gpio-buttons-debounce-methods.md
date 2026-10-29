---
id: emb-gpio-buttons-debounce-methods
sourceLesson: emb-gpio-buttons
title: "Choose a debounce algorithm"
level: basic
minutes: 3
summary: "Contact bounce is a burst of transitions, not several intentional presses."
---

## Switch bounce

When metal contacts close, they do not make one clean connection. They bounce apart and together for a short time, so the MCU sees a burst of transitions.

```
ideal:    ‾‾‾‾‾‾‾‾|________________
bouncing: ‾‾‾‾‾|_|‾|_||‾|__________
               <- bounce ->
```

How long? Jack Ganssle measured 18 different switches. Excluding two outliers, the other 16 averaged 1,557 µs of bounce, with a maximum of 6,200 µs. One outlier, a pushbutton, bounced for 157 ms when it opened (on release); the other once took 11.3 ms to close. His advice: most switches settle well under 10 ms, so use a debounce period of about 20 ms to be conservative. Separately, he found a 100 ms delay between press and response noticeable, while 50 ms seemed instantaneous, which illustrates a responsiveness trade-off, rather than a universal perceptual bound or a guarantee for other users and tasks.

If you count raw transitions, one press might register as five presses. For a synth, that means a menu skips items or a note retriggers.

> [!analogy] Real-world analogy: A dropped ball settling
> Drop a ball and it bounces a few times before coming to rest. If you want to know where it landed, you wait until it has stayed still for a moment rather than reporting the first touch.
>
> **How it maps:** The ball's bounces are the contact bounce. Waiting for an unbroken still period is the stable-for-N approach; the integrator is similar but tolerates the odd small hop, because it counts net evidence rather than restarting. Reporting the first touch and then ignoring the ball for a while is lockout: quick, but fooled if the first touch was something else.
>
> **Where it stops:** A ball's bounces shrink in a regular way. Switch bounce is irregular, can differ between press and release, and electrical interference can produce spikes that have nothing to do with the contacts moving.

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

**4. Integrator debouncer.** Keep a counter between 0 and TOP. Add one for each 1, subtract one for each 0 (clamped). Output becomes pressed only when the counter reaches TOP and released only when it reaches 0. Occasional opposite readings slow it down but do not reset it, which suits noisy inputs.

```
on tick:
  if raw == 1: acc = min(acc + 1, TOP)
  else:        acc = max(acc - 1, 0)
  if acc == TOP: state = PRESSED
  if acc == 0:   state = RELEASED
```

## Key takeaways
- Contact bounce is a burst of transitions, not several intentional presses.
- Lockout trusts the first glitch; persistence and integrator debouncer methods trade debounce delay for rejection.

## Further reading
- [A Guide to Debouncing, part 1 — Jack Ganssle](https://www.ganssle.com/debouncing.htm)
- [A Guide to Debouncing, part 2 — Jack Ganssle](https://www.ganssle.com/debouncing-pt2.htm)
- [Teensy 4.1 digital pins and limits — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Bounce library — PJRC](https://www.pjrc.com/teensy/td_libs_Bounce.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Pull-up resistor — Wikipedia](https://en.wikipedia.org/wiki/Pull-up_resistor)
- [Teensy 4 core: pinMode pad settings (digital.c) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/digital.c)
- [Switch implementation — libDaisy](https://github.com/electro-smith/libDaisy/blob/master/src/hid/switch.cpp)
