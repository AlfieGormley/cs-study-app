---
id: midi-hardware-output-loop-current
title: Check the 3.3 V output current
level: intermediate
minutes: 4
sourceLesson: midi-hardware
summary: Use the resistor values for the specified transmitter voltage and account for receiver and driver drops.
---

## The reference MIDI OUT circuit, 3.3 V version

The original 1983 output used +5 V and two 220 Ω resistors. Most current microcontrollers run at 3.3 V, so the 2014 update adds a 3.3 V variant. In Figure 1, RA connects pin 4 to the supply VTX, and RC connects pin 5 to the UART TX (optionally through a buffer):

| VTX | RA (pin 4) | RC (pin 5) |
|---|---|---|
| +5 V ± 10% | 220 Ω 5% 0.25 W | 220 Ω 5% 0.25 W |
| +3.3 V ± 5% | 33 Ω 5% **0.5 W** | 10 Ω 5% 0.25 W |

Pin 2 is grounded at the transmitter. You can check the loop current with Ohm's law, treating the receiver as its 220 Ω RB plus an LED forward voltage drop. All three resistors are in series around the loop, so their resistances add, and the voltage left to push current through them is the supply minus what the LED drops:

```formula
I = (V_TX − V_F) / (R_A + R_C + R_B)
I = (3.3 V − 1.4 V) / (263 Ω)
I = 1.9 V / (263 Ω)
I ≈ 0.00722 A = 7.22 mA
where
I: the loop current, in amperes (A); about 5 mA is the design target
V_TX: the transmitter's supply voltage (VTX), in volts (V); 3.3 V here
V_F: the forward voltage dropped across the optocoupler's LED while it conducts, in volts; typically about 1.4 V to 1.9 V
R_A: the transmitter's resistor from the supply to pin 4, in ohms (Ω); 33 Ω here
R_C: the transmitter's resistor from the UART TX pin to pin 5, in ohms; 10 Ω here
R_B: the receiver's series resistor, 220 Ω
V: volt, the unit of voltage
Ω: ohm, the unit of resistance
A: ampere, the unit of current
mA: milliampere, a thousandth of an ampere
≈: approximately equal to (rounded)
In words: the voltage left after the LED's drop, divided by all the resistance in the loop, gives about 7 mA with the 3.3 V resistor values.
```

This ignores the small voltage left across the UART's TX output when it pulls low and the cable's own resistance, which is why the spec quotes ranges rather than one exact figure. The same calculation for all four cases in the spec:

```python
def loop_ma(vtx, ra, rc, vf, rb=220):
    # rb: receiver's series resistor
    # Simplified series loop, no
    # driver drop.
    r = ra + rc + rb
    # Ohm law gives amps; scale to
    # milliamps.
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

```output
5.0
7.22
4.47
2.88
```

These match the spec's own figures: 5 mA for the original design, about 7.2 mA typical and 4.47 mA worst case for the 3.3 V design. The last line shows why you mustn't run the 5 V resistor values from 3.3 V: under 3 mA may not reliably switch every receiver.

## Key takeaways
- Use the resistor values for the specified transmitter voltage and account for receiver and driver drops.

## Further reading
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5 Pin DIN Electrical Specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [How to make your own 3.5 mm TRS-to-MIDI DIN cables (Type A and B) — MIDI Association](https://midi.org/updated-how-to-make-your-own-3-5mm-mini-stereo-trs-to-midi-5-pin-din-cables)
- [USB Device Class Definition for MIDI Devices 1.0 — USB-IF](https://www.usb.org/sites/default/files/midi10.pdf)
- [USB On-The-Go (host and device roles) — Wikipedia](https://en.wikipedia.org/wiki/USB_On-The-Go)
- [Teensy 4.1 (device and host USB ports, 3.3 V pins) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Opto-isolator — Wikipedia](https://en.wikipedia.org/wiki/Opto-isolator)
