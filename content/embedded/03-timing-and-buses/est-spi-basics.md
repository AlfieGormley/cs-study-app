---
id: est-spi-basics
title: Match SPI clocks and chip selection
level: basic
minutes: 4
summary: Use a peripheral datasheet to set SPI sampling edges, selection and exchange boundaries.
---

A common four-signal **SPI**, or serial peripheral interface, connects a controller and a peripheral with a clock, data in each direction and **chip select**. The controller supplies clock pulses. The two data directions can shift bits during the same clocks, although a particular command may use only one direction's useful result.

Signal names vary. A controller's data output is often called COPI or MOSI; its data input is CIPO or MISO. Follow the actual device labels and directions, not just familiar wire colours. Work only with low-voltage development hardware. Check electrical compatibility and the board's pin-function configuration before connecting devices.

## Agree which edge means sample

**Clock polarity** (CPOL) chooses the idle clock level. **Clock phase** (CPHA) chooses which clock edge samples a bit relative to that idle level. In the commonly named mode 0, the clock idles low and the receiver samples on the leading, rising edge; subsequent data changes happen on trailing, falling edges. The first transmitted bit must already be valid before the first sampling edge.

Do not memorise “always read on rising edges”: a different required mode can use different edges. Configure the mode, bit order, number of bits per transfer and maximum clock rate specified by the peripheral. Also respect chip select setup and hold times; lowering the clock rate does not fix the wrong sampling mode.

> [!analogy] Real-world analogy: a leader setting the beat
> Two people pass items in time with a leader's beat. They must agree which part of the beat means present an item and which means take it.
>
> **How it maps:** The controller's clock sets the transfer rhythm, and the configured sampling edge determines when a bit must be valid. Chip select identifies the intended exchange.
>
> **Where it stops:** Real devices specify exact timing, bit order and chip select behaviour. Matching a beat does not establish a shared command language or prove that the receiver accepted a command.

## Trace a command without inventing a device

Assume a fictional peripheral uses an active-low chip select and requires a command byte followed by one dummy byte, all within one selection. It returns status while the dummy byte is clocked. This is that fictional device's rule, not a universal SPI frame format.

1. Drive its chip select active using the required timing.
2. Transfer the command byte and discard the simultaneously received placeholder.
3. Transfer the dummy byte while collecting the returned status.
4. Wait for the transfer to finish, then deassert chip select at the allowed time.

A transmit function returning can mean data entered a buffer rather than that the last clock finished; use the documented driver semantics. The Pico SDK's blocking transfer operations are one concrete example to inspect, rather than assuming every API means the same thing.

SPI itself does not provide I2C-style addressing and per-byte ACK. Check the returned device status or other documented evidence. For multiple peripherals sharing a data-return wire, each unselected device must release it as its datasheet requires; chip-select wiring alone does not prove the bus is electrically shareable.

## Key takeaways
- Match polarity, phase, bits per transfer, bit order and rate to the device's specification.
- Chip select timing and command framing belong to the peripheral's protocol.
- Clocking bits does not itself prove successful application-level communication.

## Further reading
- [Pico SDK SPI format and transfer semantics](https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/src/rp2_common/hardware_spi/include/hardware/spi.h)
- [RP2040 datasheet: SPI peripheral timing](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
