---
id: elec-supply-versus-pin-limits
sourceLesson: elec-logic-levels
title: "Supply pins, signal limits and stress ratings"
level: intermediate
minutes: 2
summary: "A board’s power input does not specify its I/O voltage tolerance."
---

The fastest way to destroy a microcontroller board is to connect something at the wrong voltage. This lesson covers how to know, from the documents, what each pin will accept, and how to make two parts with different supplies talk safely.

> [!warning] Scope
> Everything here concerns low-voltage DC logic and audio circuits, typically 3.3 V and 5 V. Power your circuits from a certified USB supply or bench supply. Mains power-supply design is out of scope.

## Supply voltages: 3.3 V and 5 V
Two supply voltages dominate hobby digital electronics:

- **5 V:** a common board-input supply, including ordinary USB-powered examples in this module, and the native supply of older logic families and many classic microcontrollers.
- **3.3 V:** a common supply for modern microcontrollers, including the ARM chips on audio-focused boards.

Many boards accept 5 V from USB and use an on-board **voltage regulator** to make 3.3 V for the chip. The board may expose both voltages on pins. **The fact that 5 V exists on the board says nothing about whether the chip's I/O pins tolerate 5 V.**

> [!example] A real board's limits
> PJRC’s Teensy 4.1 product documentation (checked 16 October 2026; this page does not identify a separate PCB revision) states that its digital pins accept 0 to 3.3 V signals and "are not 5V tolerant", and that the analogue range is fixed at 0 to 3.3 V. Other boards differ: some microcontrollers have individual 5 V-tolerant pins. Read the exact board and revision's documentation and the microcontroller datasheet, and record the date you checked.

## Absolute maximum ratings versus recommended operating conditions
Every datasheet separates two very different tables.

**Absolute Maximum Ratings** describe stress limits, not guaranteed operation. Exceeding them can cause permanent damage; extended operation at those limits can reduce reliability. TI’s SN74HC00 datasheet SCLS181H (revision H, August 2021; checked 16 October 2026) includes a supply maximum of 7 V and an input clamp current of ±20 mA.

**Recommended Operating Conditions** are where the part is guaranteed to work as specified: for the SN74HC00, a supply (V_CC) from 2 V to 6 V, with inputs between 0 V and the supply voltage.

```diagram
 0V                                    7V
 |--- recommended: 2–6 V ---|          |
 |------- stress limit: 7 V -----------|
    not a guaranteed operating range
```

Design inside recommended conditions with margin. Never treat an absolute maximum as a target. Living near it can shorten the part's life even if it doesn't fail at once.

## Key takeaways

- A board’s power input does not specify its I/O voltage tolerance.
- Design inside recommended conditions, not at absolute maximum ratings.

## Further reading

- [TI SN74HC00, SCLS181H](https://www.ti.com/lit/ds/symlink/sn74hc00.pdf)
- [PJRC: Teensy 4.1 signal-voltage limits](https://www.pjrc.com/store/teensy41.html)
