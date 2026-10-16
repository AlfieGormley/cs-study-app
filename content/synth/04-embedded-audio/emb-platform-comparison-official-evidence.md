---
id: emb-platform-comparison-official-evidence
sourceLesson: emb-platform-comparison
title: "Record revision-specific hardware facts"
level: advanced
minutes: 3
summary: "Use dated manufacturer evidence for the exact board and audio expansion."
---

## Step 3: gather evidence from official sources only

Below is what the official sources state, checked 2026-10-16. Source-code defaults describe the fetched version, not a permanent platform contract.

### A: Daisy Seed (Rev 7)

Sources: Electro-Smith Daisy Seed page and datasheet v1.2.0 (18 March 2026); libDaisy documentation.

- Arm Cortex-M7 at 480 MHz; 64 MB SDRAM; 8 MB flash (external QSPI; internal flash is 128 KB).
- 96 kHz / 24-bit stereo audio in and out (PCM3060 codec on Rev 7); line-level output, 0 dBFS at 1 V RMS, 100 Ω output impedance.
- 31 GPIO, 12 × 16-bit ADC inputs, 2 × 12-bit DAC outputs; SPI, UART, I2S, I2C.
- Micro USB port, plus USB pins for OTG host and device.
- Power: VIN 5–17 V. Most GPIO 5 V tolerant; five listed pins are 3.3 V only.
- Flashing: DFU via BOOT + RESET, or a web programmer; debugging with an ST-Link V3 Mini (recommended in the getting-started guide).
- Software: libDaisy and DaisySP in C++; the datasheet also lists Arduino and Max/MSP Gen~. Default audio block 48 samples at 48 kHz.

### B: Teensy 4.1 + audio adaptor Rev D2

Sources: PJRC Teensy 4.1 page; PJRC audio adaptor page; Teensy Audio Library source.

- Arm Cortex-M7 at 600 MHz; 1,024 KB RAM (512 KB tightly coupled memory); 7,936 KB flash; pads for extra PSRAM or QSPI flash devices.
- 55 I/O pins (42 breadboard-accessible); 18 analogue inputs (10-bit default, "only up to 10 bits are normally usable due to noise"); 8 serial, 3 SPI, 3 I2C, 2 I2S/TDM ports.
- Pins are 3.3 V and not 5 V tolerant; recommended maximum output current 4 mA.
- USB device port (with class-compliant USB MIDI and USB audio options) and a separate USB host port.
- Audio adaptor: SGTL5000 codec, 16-bit 44.1 kHz; headphone and line out; line in or mic in; controlled over I2C.
- Audio Library default: 128-sample blocks at 44.1 kHz, 16-bit integer processing.
- Flashing: Teensy Loader via the Arduino IDE with the Teensy boards add-on (Teensyduino), PlatformIO or Makefiles; recovery via the Program button. PJRC does not document a probe-based debugging header.
- Revision notes: PJRC's page lists component changes for boards made after 2022 (for example, the bootloader chip U2 became a GD32E230F8 from June 2022), so record when your board was made.
- PJRC's pages note that SparkFun now manufactures Teensy products.

### C: Raspberry Pi 5 + DAC+

Sources: Raspberry Pi 5 product brief; Raspberry Pi audio boards documentation.

- Quad-core Arm Cortex-A76 at 2.4 GHz; 1–16 GB RAM options; 4 USB ports; 40-pin GPIO header; 5 V / 5 A USB-C power.
- No analogue audio output: the product brief lists none, and Raspberry Pi's model list shows a 3.5 mm audio/AV jack for earlier models but not for Pi 5. A HAT or USB interface is needed.
- DAC+: TI PCM5122, 24-bit 192 kHz, line out 0–2 V RMS on phono sockets, headphone amplifier; output only (the Codec Zero adds inputs).
- HATs are auto-detected from an on-board EEPROM, or configured with a device-tree overlay; audio runs through Linux.
- GPIO pins are 3.3 V digital I/O (Raspberry Pi's GPIO documentation describes them only as high/low inputs and outputs, with no ADC), so knobs need an external ADC chip.
- Production stated until at least January 2036 (product brief).

## Key takeaways
- Use dated manufacturer evidence for the exact board and audio expansion.
- Capabilities on a specification do not establish workload, noise or compatibility.

## Further reading
- [Daisy Seed hardware page — Electro-Smith](https://docs.daisy.audio/hardware/Seed/)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Teensy 4.1 — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Audio adaptor boards for Teensy — PJRC](https://www.pjrc.com/store/teensy3_audio.html)
- [Teensy Audio Library — PJRC](https://www.pjrc.com/teensy/td_libs_Audio.html)
- [Raspberry Pi 5 product brief — Raspberry Pi](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf)
- [Raspberry Pi audio boards overview — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/audio/introduction.adoc)
- [Raspberry Pi audio boards configuration — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/audio/configuration.adoc)
- [GPIO on Raspberry Pi — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/gpio-on-raspberry-pi.adoc)
- [Raspberry Pi models and their ports (Pi 5 lists no 3.5 mm jack) — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/introduction.adoc)
