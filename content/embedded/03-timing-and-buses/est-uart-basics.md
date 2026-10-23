---
id: est-uart-basics
title: Read a UART frame and budget its bytes
level: basic
minutes: 4
summary: Separate UART framing, payload rate and the receive buffer that software must drain.
---

A **UART**, or universal asynchronous receiver/transmitter, converts bytes into a serial bit stream and reconstructs received bytes. A common full-duplex connection uses a transmit signal in each direction, plus the electrical reference required by the interface. Asynchronous means there is no separate shared bit-clock wire; each end uses its configured timing.

Both ends must agree on baud rate, data bits, parity and stop bits. Pin functions and electrical levels are separate requirements. Work only with low-voltage development hardware. Use a board-approved adapter and the device manuals: a UART framing setting does not establish a safe voltage, and an RS-232 electrical interface is not directly interchangeable with a microcontroller's logic-level pins.

## Count framing as well as payload

Assume an ordinary binary UART link with **8N1** framing: one start bit, eight data bits, no parity and one stop bit. That is ten transmitted bit periods for one payload byte, before any gaps between frames.

```formula
T = N × b / R
T = (96 × 10 / 9600) s
T = 0.1 s = 100 ms
where
T: ideal wire time for the data, in seconds (s) or milliseconds (ms)
N: number of payload bytes, here 96
b: transmitted bits per byte under the assumed framing, here 10 for 8N1
R: line rate in bits per second, here 9600; for this binary UART signalling it matches 9600 baud
s: second
ms: millisecond, one thousandth of a second
In words: 96 payload bytes need 960 line bits, taking 100 milliseconds at 9600 bits per second, before any additional gaps.
```

A UART's FIFO and any software receive buffer provide temporary storage. They do not increase the sustained drain rate. If input keeps arriving faster than software consumes it, a finite buffer eventually overflows. An overrun can lose data; check the hardware and driver error reporting.

> [!analogy] Real-world analogy: letters arriving in a tray
> A tray can hold letters while someone is busy, but it eventually fills if letters arrive faster than they are opened.
>
> **How it maps:** UART receive buffers hold a bounded amount of incoming data until firmware reads it. A larger buffer buys time during a pause, not unlimited sustained capacity.
>
> **Where it stops:** Real UARTs have framing and error flags, and their buffers retain bytes rather than whole application messages. A tray does not define when one command ends.

## Give the byte stream a meaning

For a first text command protocol, agree a terminator such as a newline and a maximum command length. Accumulate bytes until the terminator, reject an overlong command, and decide how to resynchronise. For binary messages, use a specified length and framing scheme. Receiving one byte is not the same as receiving a complete valid command.

Trace `O`, `N`, newline: the parser stores the first two bytes and handles the command only when the terminator arrives. A receive call may return before, at or after those three bytes have arrived; preserve the parser's partial state across calls. Keep interrupt receive work short and perform command interpretation outside the ISR where possible.

## Key takeaways
- UART timing and framing must agree at both ends; electrical compatibility is separate.
- Include start, data, parity and stop bits when estimating wire time.
- Buffers are finite, and application messages need their own framing rules.

## Further reading
- [TI: RS-232 electrical interface and logic-level conversion](https://www.ti.com/lit/an/slla607/slla607.pdf)
- [Pico SDK UART framing and receive interfaces](https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/src/rp2_common/hardware_uart/include/hardware/uart.h)
- [RP2040 datasheet: UART peripheral](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
