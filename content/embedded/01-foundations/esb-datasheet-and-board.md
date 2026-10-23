---
id: esb-datasheet-and-board
title: Read the chip, board and SDK documentation
level: basic
minutes: 3
summary: Use the chip datasheet, board wiring and SDK configuration together before controlling a pin.
---

An example says it blinks an LED, but your board stays dark. Before changing code at random, distinguish three sources of information.

The **datasheet** describes a component: its supported functions, electrical limits, registers and required operating conditions. A board manual and **schematic** describe how a particular circuit board connects those components. The **SDK**, or software development kit, supplies libraries, header files, examples and build support for a supported target.

None replaces the others. A chip may support a function on several pins, while the board uses one of those pins for another purpose. A library may also require a specific board selection so it chooses the correct implementation.

## Work from the device outward

For an onboard indicator, follow this sequence:

1. Identify the exact board model and revision, not just the processor family.
2. Read its manual or schematic to find how the indicator is connected.
3. Check which component controls that connection.
4. Use the official SDK example for that board and check its build configuration.
5. Observe the intended result before adding external circuitry.

The Raspberry Pi SDK's blink example illustrates why this matters. Its ordinary Pico LED path and Pico W wireless-chip LED path differ. The example selects the supported path using board configuration. Copying a pin number from a different board is not a substitute for that selection.

> [!analogy] Real-world analogy: an appliance manual and a room plan
> An appliance manual explains what the appliance can do. A room plan shows where it is installed and how it is connected. A control panel provides the supported way to operate it.
>
> **How it maps:** The component datasheet describes the device's capabilities, the board schematic describes actual connections and the SDK provides a software interface to those capabilities.
>
> **Where it stops:** A board's connections can constrain what is usable. Neither a convenient API nor a familiar connector overrides the component's electrical limits or the board's wiring.

## Keep the first experiment simple

Use a board's documented onboard indicator for the first hardware observation. If an example builds but does not work, check the selected board, the actual firmware image loaded and the documented indicator connection before concluding the MCU is broken.

Keep any later experiments to low-voltage development hardware. Before connecting an external signal, check the electrical limits for inputs, ground reference and power arrangement in the exact manuals. Do not connect unknown voltage sources or high-current loads directly to MCU pins. This course does not require external wiring to understand or test its first logic examples.

## Key takeaways
- A component's capabilities, a board's connections and an SDK's configuration answer different questions.
- Match an example to the exact board before assuming a particular pin controls its indicator.
- Electrical limits remain hardware requirements even when an API accepts a value.

## Further reading
- [SDK board selection and first examples — Raspberry Pi](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/microcontrollers/c_sdk/official_sdk.adoc)
- [Official blink implementation — Raspberry Pi](https://raw.githubusercontent.com/raspberrypi/pico-examples/master/blink/blink.c)
- [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
