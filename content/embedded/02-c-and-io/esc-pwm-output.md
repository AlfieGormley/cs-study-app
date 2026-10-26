---
id: esc-pwm-output
title: PWM period and duty cycle
level: basic
minutes: 4
summary: Explain how pulse repetition and active time change an output without producing a steady analogue voltage.
---

**Pulse-width modulation** (PWM) repeatedly switches an output between digital levels. Its period is the time for one complete cycle. Its duty cycle is the fraction of that cycle spent in the chosen active state. Frequency and duty cycle answer different questions: how often the waveform repeats and how much of each cycle it is active.

## Change the active fraction or the repetition rate

An active-high waveform that is high for one quarter of every cycle has a 25 percent duty cycle. Increasing that duty cycle makes the output spend more of each cycle high. It need not change how often the cycles repeat.

Increasing frequency while keeping duty cycle unchanged makes each full cycle shorter, including both its high and low parts. The active fraction stays the same. For example, a signal repeating at 1,000 hertz has a one-millisecond period; if it is high for a quarter of that period, its high time is 0.25 milliseconds.

When configuring timing, these relationships are useful reference:

```formula reference
T = 1 / f
D = t_high / T
where
T: the period, or duration of a complete cycle, in seconds
f: the repetition frequency in hertz, meaning cycles per second
D: the unitless duty fraction for the stated active-high signal
 t_high: the time spent high within one cycle, in seconds
In words: a faster repetition rate makes each cycle shorter. For an active-high signal, duty cycle is the share of that cycle spent high.
```

The output is still a sequence of high and low levels. It does not become a constant quarter-scale analogue voltage merely because the duty cycle is 25 percent. A filter and load can respond to its average under suitable conditions, but their behaviour must be designed and measured. A dedicated digital-to-analogue converter is another way to obtain a controlled analogue output; it also has its own settling and load requirements.

> [!analogy] Real-world analogy: opening a tap for part of each cycle
> Imagine a tap opened for one quarter of every repeating interval and closed for the rest. Over many intervals it passes less water than a tap left open continuously.
>
> **How it maps:** The repeating interval represents the PWM period, and the open fraction represents duty cycle. Changing that fraction changes the average delivered activity without adding intermediate digital output levels.
>
> **Where it stops:** An electronic pin is not an unlimited power source, and a load does not necessarily average pulses harmlessly. Voltage, current, switching behaviour and the actual circuit remain design constraints.

## Check the timer's counting rules

A hardware PWM peripheral normally keeps counting without the CPU writing every edge. Its counter mode, clock divider and compare rule determine the waveform. A compare value is checked against the counter to choose when the output changes state.

For a simple active-high model, the counter visits positions 0 through 99 and the output is high at positions below 25. That means 100 positions per cycle, with the first 25 high. Increasing the compare value while keeping the counter clock and range fixed lengthens the high part without changing the cycle length. This is a reasoning model, not code to run fast enough to create accurate pin timing.

RP2040's SDK documents a normal wrap counter whose maximum is inclusive: a maximum of 99 means 100 positions. Its normal counting mode can implement this model, but other modes and output inversion change how settings map to pulses. Check the actual mode before interpreting a configuration.

Use an onboard LED through its documented board interface for a first observation. For hardware PWM, first confirm that the board exposes a PWM-capable route to that indicator; an LED driven through another device may need a different interface. Confirm whether its circuit is active-high or active-low. Perceived brightness is not generally proportional to the duty percentage. Never attach a high-current load directly to a pin; this course does not design motor or relay drivers.

## Key takeaways
- Period and duty cycle describe different aspects of the pulse train.
- A PWM pin switches levels; it is not automatically a steady analogue output.
- Count the actual timer positions and check the board's output circuit before configuration.

## Further reading
- [Raspberry Pi SDK: PWM counter, wrap and compare behaviour](https://raw.githubusercontent.com/raspberrypi/pico-sdk/2.2.0/src/rp2_common/hardware_pwm/include/hardware/pwm.h)
- [RP2040 datasheet: PWM operation](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
- [Different onboard LED paths in the official blink example — Raspberry Pi](https://raw.githubusercontent.com/raspberrypi/pico-examples/master/blink/blink.c)
