---
id: esc-gpio-input-output
title: GPIO direction, pulls and logical levels
level: basic
minutes: 4
summary: Configure a pin for the intended signal and interpret its level using the board circuit.
---

A **general-purpose input/output** pin, or GPIO, connects software to a digital signal. In input mode the peripheral samples the pin's level. In a typical output mode it drives a level. Many pins also have alternate peripheral functions, so naming a GPIO is only the first part of configuring it.

## Decide what each end is allowed to do

Before connecting anything, check the chip's allowed input range and the development board's actual wiring. Work only with known low-voltage development hardware. Do not connect a motor, relay coil, mains source, unknown voltage or high-current load directly to a GPIO. An onboard LED with its existing circuit is sufficient for this course.

An input is often high impedance: it should not strongly drive the wire it observes. If nothing determines the level, the input may float and produce unreliable readings. A **pull-up resistor** weakly connects it towards the permitted high reference; a **pull-down resistor** weakly connects it towards ground. Whether an internal pull is available, its strength and its suitability depend on the device and circuit.

For the following input model, the manual specifies a pull-up and a switch that connects the input to ground when pressed:

| Switch state | Sampled level | Logical pressed state |
|---|---|---|
| Released | High | False |
| Pressed | Low | True |

This is an **active-low** input: the active condition uses the low level. It is not a universal button convention. The phrase "write high" also does not universally mean "turn the onboard LED on"; some indicators are wired active-low or controlled through another device.

> [!analogy] Real-world analogy: a door sign with an agreed meaning
> A door sign can use either side to mean occupied, provided everyone follows the same convention. Looking at its colour without knowing the convention is ambiguous.
>
> **How it maps:** The sampled electrical level and the application's logical meaning are separate. The board circuit determines whether high or low means pressed or illuminated.
>
> **Where it stops:** A label cannot enforce voltage limits or prevent two outputs fighting one another. Electrical compatibility and correct direction must be established before software interprets the level.

## Keep hardware access at the boundary

This complete C11 host example tests the logical interpretation without wiring hardware:

```c
#include <stdbool.h>
#include <stdio.h>

bool pressed_from_level(bool high) {
    // The modelled switch is active-low.
    return !high;
}

int main(void) {
    printf("%u %u\n",
      (unsigned)pressed_from_level(true),
      (unsigned)pressed_from_level(false));
    return 0;
}
```

It prints `0 1`. The `!` operator negates a truth value. On a real target, a small driver obtains the electrical level through its SDK, then applies this interpretation. For example, the SDK for RP2040 documents separate operations for initialising GPIO, selecting direction, selecting pulls and reading or writing values. The correct sequence and pin assignment still depend on the exact board.

## Key takeaways
- Configure the signal function, direction and required pull before interpreting readings.
- Derive active-high or active-low meaning from the circuit, not a pin number.
- Test interpretation separately from the device driver and obey the actual electrical limits.

## Further reading
- [Raspberry Pi SDK: GPIO configuration and level access](https://raw.githubusercontent.com/raspberrypi/pico-sdk/2.2.0/src/rp2_common/hardware_gpio/include/hardware/gpio.h)
- [RP2040 datasheet: GPIO and electrical specifications](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
