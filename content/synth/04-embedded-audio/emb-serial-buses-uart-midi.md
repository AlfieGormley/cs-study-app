---
id: emb-serial-buses-uart-midi
sourceLesson: emb-serial-buses
title: "UART framing and DIN MIDI timing"
level: intermediate
minutes: 4
summary: "UART needs an agreed bit rate and framing; DIN MIDI uses ten bit times per byte."
---

Apart from audio itself, nearly everything a synth's MCU talks to uses one of three serial buses. MIDI arrives on a **UART**. Codecs and many small sensors are configured over **I2C**. Displays, flash memory and fast external ADCs use **SPI**. Each makes a different trade-off between wires, speed and complexity, and the right choice depends on the job.

## UART: asynchronous serial

A **UART** (universal asynchronous receiver-transmitter) sends bytes one bit at a time on a single wire per direction (TX and RX), with **no clock wire**. Both ends agree the bit rate (**baud rate**) in advance, and the receiver times each bit from the falling edge of a **start bit**.

A frame for the common **8-N-1** setting (8 data bits, no parity, 1 stop bit):

```
idle  start  D0 D1 D2 D3 D4 D5 D6 D7  stop
‾‾‾‾‾|____|  x  x  x  x  x  x  x  x |‾‾‾‾
       0     <- LSB first ->          1
```

- Idle line is high.
- Start bit is 0; stop bit is 1.
- Data bits go **LSB first** (the opposite of I2S's MSB-first audio words).
- 10 bit times per byte in total.

Because there is no clock, both ends' baud rates must match closely, typically within a few percent, or the receiver samples bits in the wrong place by the end of the frame.

> [!analogy] Real-world analogy: Playing to a count-in without a conductor
> Two musicians agree a tempo beforehand. One counts in, and both play the phrase from that moment by keeping time in their heads.
>
> **How it maps:** The agreed tempo is the baud rate and the count-in is the start bit's falling edge. The receiver times each later bit from that edge. A small tempo difference grows through the phrase, which is why errors from a mismatched baud rate appear in the last bits of a byte first.
>
> **Where it stops:** A UART restarts its timing at every byte's start bit and tolerates only a few percent of mismatch. Musicians can listen and adjust mid-phrase; a UART receiver cannot.

### MIDI is a UART

The MIDI Association's CA-033 electrical update (2014) specifies 31,250 baud with a rate tolerance of ±1%, one start bit, eight data bits and one stop bit. That is ten bit periods, or 320 microseconds per byte.

DIN MIDI therefore requires an 8-N-1 UART configured for 31,250 baud. The start and stop bits occupy wire time even though they are not payload. That makes a byte longer than just its eight data bits.

A three-byte note-on takes nearly a millisecond on the wire. A four-note chord is 12 bytes, so it takes about 3.8 ms to arrive in full (a little less if the sender uses MIDI's running-status shortcut, which omits repeated status bytes). That is a real, if small, timing smear, and it is part of the end-to-end latency budget in the real-time audio units.

> [!warning] DIN MIDI is not a bare UART pin
> The specification makes MIDI a 5 mA **current loop** with an **opto-isolator** at every MIDI IN, so this MIDI data connection does not require a shared galvanic signal ground (other cables may still connect equipment grounds). You need the specified circuit between the jack and the MCU's UART pins; the CA-033 update gives resistor values for both 5 V and 3.3 V transmitters. Never wire a DIN jack straight to GPIO.

Teensy 4.1 has eight hardware serial ports, and PJRC lists MIDI as a typical use. The Daisy Seed exposes several UARTs (USART1 on pins D13/D14, among others). USB MIDI is a different transport entirely: it uses the USB connection rather than a UART.

## Key takeaways
- UART needs an agreed bit rate and framing; DIN MIDI uses ten bit times per byte.
- DIN MIDI requires its specified isolated interface circuit, rather than direct GPIO.

## Further reading
- [MIDI 1.0 Electrical Specification Update (CA-033) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5-pin DIN electrical specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [A Basic Guide to I2C (SBAA565) — Texas Instruments](https://www.ti.com/lit/an/sbaa565/sbaa565.pdf)
- [Understanding the I2C Bus (SLVA704) — Texas Instruments](https://www.ti.com/lit/an/slva704/slva704.pdf)
- [Serial Peripheral Interface — Wikipedia](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface)
- [Universal asynchronous receiver-transmitter — Wikipedia](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter)
- [Teensy 4.1 communication ports — PJRC](https://www.pjrc.com/store/teensy41.html)
