---
id: emb-serial-buses-display-bus-budget
sourceLesson: emb-serial-buses
title: "Budget display and peripheral traffic"
level: intermediate
minutes: 3
summary: "Bulk pixel transfers are long beside an audio callback deadline."
---

## Which bus for which job?

A 128×64 monochrome display holds 1,024 payload bytes. A full redraw takes about 23 ms of payload/acknowledgement clocking over 400 kHz I2C, compared with about 1.02 ms of payload clocking over 8 MHz SPI. At 100 kHz I2C, it is about 92 ms. Addresses, commands, setup and stretching add time, so measure the actual driver.

Those times are long beside a 1 ms audio-block deadline. Faster SPI gives more display headroom, but even its nominal payload time does not fit inside that deadline. A blocking call waits for completion even when hardware generates the clocks.

Keep display updates in foreground work or use a suitable asynchronous/DMA driver. Check interrupt masking, memory-bus competition and completion-handler cost: moving the transfer out of the callback is necessary but does not itself prove audio timing.

| Job in a synth | Usual bus | Why |
|---|---|---|
| DIN MIDI in/out | UART | The MIDI spec is a UART |
| Codec configuration | I2C | Few writes, two wires |
| Codec audio data | I2S/SAI | Continuous, clocked |
| OLED/TFT display | SPI (or I2C) | Bulk pixel data |
| SD card, flash | SPI or SDIO | Bulk data |
| GPIO/LED expander | I2C or SPI | Pin count vs speed |
| External ADC | SPI | Fast, many reads |

Practical rules:

- **I2C** when you need few wires and modest data, and can afford a bus that one misbehaving device can lock up.
- **SPI** when speed matters and you have pins for a CS per device.
- **UART** when the protocol demands it (MIDI) or for a debug console.
- Do bus transfers from the main loop or with DMA, never by blocking inside the audio callback.

## Key takeaways
- Bulk pixel transfers are long beside an audio callback deadline.
- Keep blocking display transfers in the foreground and measure their real cost.

## Further reading
- [MIDI 1.0 Electrical Specification Update (CA-033) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5-pin DIN electrical specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [A Basic Guide to I2C (SBAA565) — Texas Instruments](https://www.ti.com/lit/an/sbaa565/sbaa565.pdf)
- [Understanding the I2C Bus (SLVA704) — Texas Instruments](https://www.ti.com/lit/an/slva704/slva704.pdf)
- [Serial Peripheral Interface — Wikipedia](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface)
- [Universal asynchronous receiver-transmitter — Wikipedia](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter)
- [Teensy 4.1 communication ports — PJRC](https://www.pjrc.com/store/teensy41.html)
