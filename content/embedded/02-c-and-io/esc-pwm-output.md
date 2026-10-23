---
id: esc-pwm-output
title: PWM period and duty cycle
level: basic
minutes: 5
summary: Explain a digital pulse train and calculate its high fraction without calling it a true analogue voltage.
---

**Pulse-width modulation** (PWM) repeatedly switches an output between digital levels. Its period is the time for one complete cycle. Its duty cycle is the fraction of that cycle spent in the chosen active state. Frequency and duty cycle answer different questions: how often the waveform repeats and how much of each cycle it is active.

## A worked waveform

Assume an ideal active-high output repeating at 1,000 hertz, with a high time of 0.25 milliseconds in every cycle:

```formula
T = 1 / f
T = 1 / 1000 Hz = 1 ms
D = t_high / T
D = 0.25 ms / 1 ms = 0.25
where
T: the period, the time for a full cycle, in milliseconds (ms) here
f: the repetition frequency in hertz (Hz), cycles per second
D: the duty cycle as a unitless fraction; 0.25 means 25 percent
 t_high: the time spent high in one cycle, in milliseconds here
Hz: hertz, one cycle per second
ms: millisecond, one thousandth of a second
In words: a one-kilohertz signal repeats every millisecond; a quarter of that cycle high gives a 25 percent duty cycle.
```

The output is still a sequence of high and low levels. It does not become a constant quarter-scale analogue voltage merely because the duty cycle is 25 percent. A filter and load can respond to its average under suitable conditions, but their behaviour must be designed and measured. A dedicated digital-to-analogue converter is another way to obtain a controlled analogue output; it also has its own settling and load requirements.

> [!analogy] Real-world analogy: opening a tap for part of each cycle
> Imagine a tap opened for one quarter of every repeating interval and closed for the rest. Over many intervals it passes less water than a tap left open continuously.
>
> **How it maps:** The repeating interval represents the PWM period, and the open fraction represents duty cycle. Changing that fraction changes the average delivered activity without adding intermediate digital output levels.
>
> **Where it stops:** An electronic pin is not an unlimited power source, and a load does not necessarily average pulses harmlessly. Voltage, current, switching behaviour and the actual circuit remain design constraints.

## Count ticks before configuring a timer

This complete C11 host model uses a counter with 100 positions and marks its first 25 positions high:

```c
#include <stdbool.h>
#include <stdio.h>

int main(void) {
    unsigned high_count = 0u;
    for (unsigned t = 0u; t < 200u; ++t) {
        bool high = (t % 100u) < 25u;
        if (high)
            ++high_count;
    }
    printf("%u\n", high_count);
    return 0;
}
```

It prints `50`: two complete cycles, each with 25 high positions. This tests counting, not pin timing. A hardware PWM peripheral normally keeps counting without the CPU writing every edge. Real counter modes, clock dividers and compare rules determine the actual frequency and duty cycle. For example, RP2040's SDK documents a normal wrap counter whose maximum value is inclusive; a maximum of 99 means 100 positions. Other modes can count differently.

Use an onboard LED through its documented board interface for a first observation. For hardware PWM, first confirm that the board exposes a PWM-capable route to that indicator; an LED driven through another device may need a different interface. Confirm whether its circuit is active-high or active-low. Perceived brightness is not generally proportional to the duty percentage. Never attach a high-current load directly to a pin; this course does not design motor or relay drivers.

## Key takeaways
- Period and duty cycle describe different aspects of the pulse train.
- A PWM pin switches levels; it is not automatically a steady analogue output.
- Count the actual timer positions and check the board's output circuit before configuration.

## Further reading
- [Raspberry Pi SDK: PWM counter, wrap and compare behaviour](https://raw.githubusercontent.com/raspberrypi/pico-sdk/2.2.0/src/rp2_common/hardware_pwm/include/hardware/pwm.h)
- [RP2040 datasheet: PWM operation](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
- [Different onboard LED paths in the official blink example — Raspberry Pi](https://raw.githubusercontent.com/raspberrypi/pico-examples/master/blink/blink.c)
