---
id: midi-hardware
title: MIDI hardware connections
level: intermediate
minutes: 16
summary: 5-pin DIN wiring and the 5 mA current loop, why MIDI inputs use an optocoupler, the 3.3 V-capable reference circuit from the MIDI electrical spec, TRS type A versus type B, and USB MIDI host and device roles.
---

This lesson is about the wires: how a MIDI byte physically gets from the Digitakt to your synth's microcontroller, and why you can't just connect a DIN socket to a GPIO pin. The project's electronics notes say exactly that: "DIN MIDI is not a direct connection to arbitrary GPIO pins." Here is why, and what to build instead.

> [!warning] Low-voltage work only
> Everything in this lesson runs from your development board's 3.3 V or 5 V supply. Never open or modify mains-powered equipment. Before connecting any circuit to a board, check the pin voltage limits in that board's documentation.

## The 5-pin DIN connection

MIDI uses a 5-pin DIN connector with its pins spread over 180°. The MIDI electrical specification (updated in 2014 as document CA-033) fixes the details:

- Devices have **female** sockets labelled MIDI IN, MIDI OUT and (optionally) MIDI THRU. Cables are male-to-male.
- Only **three pins** are used: **pin 4** (current source), **pin 5** (current sink, the data line) and **pin 2** (shield). Pins 1 and 3 are left unconnected.
- The cable is shielded twisted pair, at most **15 m (50 ft)**, with the shield connected to pin 2 at both ends.
- **Pin 2 is grounded at the transmitter only.** At a MIDI IN, pin 2 must have no DC path to the receiver's ground.

That last rule is the key to the whole design, and it comes from how the signal is carried.

## A current loop, not a voltage

Most logic signals are voltages measured against a shared ground. MIDI instead sends a **current of about 5 mA** around a loop through the cable: out of the transmitter on pin 4, through an LED inside the receiver, and back to the transmitter on pin 5.

```diagram
 SENDER                  RECEIVER
 VTX-RA-pin4 ---------> pin4
                         |
                      RB 220
                         |
                     LED anode
                     LED cathode
                         |
 TX--RC-pin5 <--------- pin5
 GND----pin2 --shield-- pin2 (no GND)
```

The current enters the receiver on pin 4 and leaves on pin 5, so the LED's anode faces pin 4. RB and the LED are in series, so it makes no electrical difference which leg RB sits on; follow the reference figure when you build it.

- **Logical 0 = current on.** When the UART's TX pin goes low, current flows from VTX through the loop into TX.
- **Logical 1 = current off.** TX high: no voltage across the loop, no current. The line idles at 1, so an idle UART means no current.

So the UART needs no inversion: start bits (0) light the receiver's LED, stop bits (1) turn it off. The spec also says one output drives exactly one input.

## Why the input needs an optocoupler

The receiver's end of the loop is the LED of an **optocoupler** (opto-isolator): an LED and a light-sensitive transistor sealed in one package. The only connection between the two sides is light.

This gives **galvanic isolation**:

- The receiver's circuit ground is never connected to the sender's ground through the MIDI cable.
- So a MIDI cable can't create a **ground loop**: a second ground path between two pieces of mains-powered equipment that already share earth through their power leads. Ground loops let current flow in signal grounds, which you hear as hum in audio.
- It also protects the receiver from the sender's voltage level and faults.

In a studio full of devices connected by audio cables as well as MIDI, this matters. The spec's own words: "To avoid ground loops, and subsequent data errors, the transmitter circuitry and receiver circuitry are internally separated by an opto-isolator."

Wiring the DIN pins straight to a GPIO would tie the grounds together, break this isolation, and expose your microcontroller to whatever the sender drives. With a 3.3 V board whose pins are not 5 V tolerant (PJRC states this for the Teensy 4.1, for example), a 5 V MIDI output could damage it.

## The reference MIDI IN circuit

Figure 2 of CA-033 gives the input circuit. The essential parts:

| Part | Role |
|---|---|
| RB = 220 Ω | Series resistor in the loop |
| Optocoupler | Isolation; e.g. PC900V, 6N138 |
| D1 (1N914) | Reverse protection for the LED |
| RD (pull-up) | Opto output to VRX |
| Pin 2 | No DC path to ground |

How it works:

1. Loop current flows through RB and the optocoupler's LED.
2. The LED switches on the phototransistor, pulling the output low against the pull-up RD.
3. That output goes to your UART's RX pin. Current on gives a low (0), current off gives a high (1): the same polarity the sender's UART produced.
4. D1, wired across the LED in the reverse direction, stops a reversed or faulty connection from putting a damaging reverse voltage on the LED.

Requirements from the spec: the receiver must need **less than 5 mA** to turn on, and rise and fall times should be under **2 µs** (one MIDI bit lasts 32 µs). The spec names the Sharp PC900V and HP 6N138 as acceptable and notes that other high-speed optocouplers may be. Its only recommended RD value is **280 Ω for the PC900V with VRX = 5 V**. Both named parts have open-collector outputs (the 6N138's output pin is the bare collector of its output transistor), which is why the pull-up RD is needed. The 6N138's datasheet characterises it at a 4.5 V supply, so for a 3.3 V receiver, pick an optocoupler whose datasheet supports a 3.3 V output supply and choose RD from that datasheet. Pull the output up to **your MCU's supply (3.3 V)**, never to 5 V on a pin that isn't 5 V tolerant.

Optional additions in CA-033: ferrite beads on the signal pins, and a **0.1 µF capacitor** from MIDI IN pin 2 (or the jack shield) to ground. At audio frequencies the capacitor is a high impedance (26.5 kΩ at 60 Hz), so it doesn't create a ground loop; at radio frequencies it is close to a short (0.16 Ω at 10 MHz), improving RF shielding.

## The reference MIDI OUT circuit, 3.3 V version

The original 1983 output used +5 V and two 220 Ω resistors. Most current microcontrollers run at 3.3 V, so the 2014 update adds a 3.3 V variant. In Figure 1, RA connects pin 4 to the supply VTX, and RC connects pin 5 to the UART TX (optionally through a buffer):

| VTX | RA (pin 4) | RC (pin 5) |
|---|---|---|
| +5 V ± 10% | 220 Ω 5% 0.25 W | 220 Ω 5% 0.25 W |
| +3.3 V ± 5% | 33 Ω 5% **0.5 W** | 10 Ω 5% 0.25 W |

Pin 2 is grounded at the transmitter. You can check the loop current with Ohm's law, treating the receiver as its 220 Ω RB plus an LED forward voltage drop:

```python
def loop_ma(vtx, ra, rc, vf, rb=220):
    # rb: receiver's series resistor
    r = ra + rc + rb
    return (vtx - vf) / r * 1000

# 5 V original circuit, 6N138 Vf 1.7 V
print(round(loop_ma(5.0, 220, 220, 1.7), 2))
# 3.3 V circuit, typical Vf 1.4 V
print(round(loop_ma(3.3, 33, 10, 1.4), 2))
# 3.3 V worst case from CA-033
print(round(loop_ma(3.135, 33*1.05,
                    10*1.05, 1.9,
                    220*1.05), 2))
# mistake: 3.3 V with 5 V resistors
print(round(loop_ma(3.3, 220, 220, 1.4), 2))
```

```
5.0
7.22
4.47
2.88
```

These match the spec's own figures: 5 mA for the original design, about 7.2 mA typical and 4.47 mA worst case for the 3.3 V design. The last line shows why you mustn't run the 5 V resistor values from 3.3 V: under 3 mA may not reliably switch every receiver.

Why is RA rated 0.5 W? If a cable fault shorts pin 4 to ground, RA sits directly across the supply. The spec's worst case is 3.465 V across 31.35 Ω: about **111 mA and 0.38 W**. The spec also assumes the buffer driving RC in 3.3 V designs is open-collector or open-drain, and warns not to exceed the driving buffer's short-circuit current rating.

> [!tip] Use the published circuit
> Copy CA-033's figures (or your board vendor's documented MIDI circuit) exactly, and note where each value came from. If you use a MIDI breakout or shield, check its schematic against CA-033 for the voltage your board runs at.

## MIDI THRU and daisy chains

A THRU socket re-transmits whatever arrives at IN. Each optocoupler slightly distorts the bit edges, and the errors accumulate along a chain. The spec says that for chains longer than three instruments, faster optocouplers help. Your Digitakt has a THRU port (it can also be set to send DIN sync instead).

## MIDI over TRS minijacks

Small devices often replace the DIN socket with a 3.5 mm TRS (tip-ring-sleeve) jack and an adapter cable. The MIDI Association standardised this in 2018 as **RP-054, which specifies Type A**. Before that, two incompatible wirings spread:

| TRS | Type A (standard) | Type B |
|---|---|---|
| Tip | Pin 5 (sink) | Pin 4 (source) |
| Ring | Pin 4 (source) | Pin 5 (sink) |
| Sleeve | Pin 2 (shield) | Pin 2 (shield) |

The MIDI Association's article (written before RP-054) lists Akai Pro, IK Multimedia, Korg, Line 6, littleBits and Make Noise as using Type A, and Arturia, 1010music and Novation as using Type B. Wiring varies by product, so check each device's manual rather than assuming by brand.

Pins 4 and 5 are swapped between the types, so a Type B adapter on a Type A device drives the loop backwards. The same article says that connecting with incompatible cables "should not damage devices designed in accordance with the MIDI spec": in the reference receiver, the reverse-protection diode D1 conducts instead of the LED, so the loop current stays limited by the resistors, but no data gets through. A device that departs from the reference circuit (for example, one without D1) has no such guarantee. A few devices also use a two-conductor TS jack, sometimes informally called "Type C".

If you put a TRS MIDI jack on your synth, use Type A, label it clearly, and never plug it into an audio jack.

## USB MIDI

USB MIDI carries the same MIDI messages over USB, defined by the USB-IF's **Device Class Definition for MIDI Devices** (release 1.0, 1999). Key facts from that document:

- MIDI is a subclass of the USB **Audio** class. A device that follows it is **class compliant**: operating systems that include a USB MIDI class driver can use it without a vendor driver.
- Data travels in fixed **32-bit USB-MIDI Event Packets**: a header byte with a 4-bit **cable number** (up to 16 virtual MIDI cables per endpoint) and a 4-bit **Code Index Number** (the message type), then three MIDI bytes, zero-padded.
- Each packet normally holds one complete message, status byte included, so running status isn't used. (The spec also has a single-byte mode, CIN 0xF, for passing an unparsed byte stream, but that is a special case.)

```
Note On, cable 0, ch 1, key 60, vel 100:
09 90 3C 64
^^ cable 0, CIN 9 (note on)
```

USB is also much faster than 31,250 bit/s, which helps with dense data. (USB MIDI 2.0, a later class specification, carries MIDI 2.0's packets natively and can fall back to USB MIDI 1.0.)

## Host and device: why two USB gadgets can't talk

USB is not peer-to-peer. Every USB connection has exactly one **host**, which schedules all transfers, and one or more **devices**, which only respond when the host polls them. Devices cannot talk to each other except via the host, and two hosts can't talk over USB directly. (USB On-The-Go and dual-role ports can switch roles, one end must provide a supported host role; the other can be an ordinary USB device.)

What this means for your setup:

- Both Digitakt models have a USB-B socket for connecting to a computer host, so the Digitakt acts as a USB **device**.
- Most development boards' main USB port is also a **device** port.
- Plug a USB-device synth into a USB-device Digitakt and **nothing happens**: there is no host. A matching cable shape doesn't mean the connection can work.

Ways to connect two USB devices:

1. **A computer as host.** Both plug into the computer, and software (Ableton, or a MIDI routing utility) forwards messages between them.
2. **A board with a USB host port.** PJRC's Teensy 4.1, for example, has a second USB port that operates in host mode, separate from its device port, supported by the USBHost_t36 library.
3. **A standalone USB MIDI host box** that hosts both devices and forwards between them.
4. **Use DIN MIDI instead.** Point to point, isolated, no host needed. For "Digitakt drives synth without a computer", DIN is the simplest, most robust option.

> [!note] USB connects grounds
> A USB cable connects the host's and device's grounds. DIN MIDI doesn't, because of the optocoupler. That is one reason USB connections between mains-powered studio gear can introduce hum, as lesson 6 discusses. (Elektron lists the original Digitakt's USB port as electrically isolated; check your own model's documentation.)

## Key takeaways
- DIN MIDI uses pins 4 (source), 5 (sink) and 2 (shield); cables are up to 15 m; pin 2 is grounded at the transmitter only.
- The signal is a roughly 5 mA current loop: current on is logical 0, idle is no current.
- The receiver's optocoupler isolates the two devices' grounds, preventing ground loops and protecting the input. Never wire DIN pins straight to GPIO.
- For a 3.3 V transmitter, CA-033 specifies RA = 33 Ω (0.5 W) and RC = 10 Ω; the 5 V design uses 220 Ω for both. On the receive side, pull the opto output up to your MCU's own supply.
- TRS Type A (RP-054) puts the sink on the tip and the source on the ring; Type B swaps them.
- USB always needs a host. The Digitakt and most dev boards are USB devices, so connecting them directly can't work; use DIN, a host port, a host box or a computer.

## Further reading
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5 Pin DIN Electrical Specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [How to make your own 3.5 mm TRS-to-MIDI DIN cables (Type A and B) — MIDI Association](https://midi.org/updated-how-to-make-your-own-3-5mm-mini-stereo-trs-to-midi-5-pin-din-cables)
- [USB Device Class Definition for MIDI Devices 1.0 — USB-IF](https://www.usb.org/sites/default/files/midi10.pdf)
- [USB On-The-Go (host and device roles) — Wikipedia](https://en.wikipedia.org/wiki/USB_On-The-Go)
- [Teensy 4.1 (device and host USB ports, 3.3 V pins) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Opto-isolator — Wikipedia](https://en.wikipedia.org/wiki/Opto-isolator)
