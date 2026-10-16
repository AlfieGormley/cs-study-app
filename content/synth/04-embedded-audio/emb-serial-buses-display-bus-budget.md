---
id: emb-serial-buses-display-bus-budget
sourceLesson: emb-serial-buses
title: "Budget display and peripheral traffic"
level: intermediate
minutes: 3
summary: "Bulk pixel transfers are long beside an audio callback deadline."
---

## Which bus for which job?

A worked comparison: a 128×64 monochrome OLED display holds one bit per pixel, so a full frame is 1,024 bytes. I2C spends 9 clocks per byte; SPI spends 8, because it has no ACK bit:

```formula
n = (W × H) / 8
n = (128 × 64) / 8 = 1024 bytes
t_I2C = (n × 9) / f_I2C
t_I2C = (1024 × 9) / 400000 Hz ≈ 23 ms
t_SPI = (n × 8) / f_SPI
t_SPI = (1024 × 8) / 8000000 Hz ≈ 1.02 ms
where
n: the number of bytes in one full frame
W: the display width, in pixels; here 128
H: the display height, in pixels; here 64
8: bits per byte (each pixel is one bit)
bytes: the unit of data size; one byte is 8 bits
t_I2C: the time to send the frame over I2C, in seconds (s)
f_I2C: the I2C clock frequency, in hertz (Hz); here 400 kHz
t_SPI: the time to send the frame over SPI, in seconds (s)
f_SPI: the SPI clock frequency, in hertz (Hz); here 8 MHz
Hz: hertz, cycles per second
s: second
ms: millisecond, one thousandth of a second
≈: approximately equal to
In words: a full redraw of this small display takes about 23 ms over 400 kHz I2C but only about 1 ms over 8 MHz SPI.
```

Python checks the arithmetic, including Standard-mode I2C:

```python
# One bit per pixel, eight bits per byte.
frame = 128 * 64 // 8
print("frame bytes:", frame)
for hz in (100_000, 400_000):
    # Include the ninth ACK/NACK clock.
    ms = frame * 9 / hz * 1000
    khz = hz // 1000
    print(f"I2C {khz} kHz: {ms:.1f} ms")
# SPI payload only; commands add more time.
spi = 8_000_000
ms = frame * 8 / spi * 1000
print(f"SPI 8 MHz: {ms:.2f} ms")
```

```output
frame bytes: 1024
I2C 100 kHz: 92.2 ms
I2C 400 kHz: 23.0 ms
SPI 8 MHz: 1.02 ms
```

(These ignore protocol overhead such as addresses and commands, so real I2C times are a little longer.) At 400 kHz I2C, a full redraw takes 23 ms; at 8 MHz SPI, about 1 ms. Both are usable for a status display, but SPI leaves far more headroom for animation, and a blocking 23 ms transfer must never run where it could delay audio.

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
