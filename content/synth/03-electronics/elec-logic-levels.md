---
id: elec-logic-levels
title: Power, logic levels and datasheets
level: intermediate
minutes: 17
summary: 3.3 V versus 5 V, logic thresholds and noise margins, absolute maximum ratings versus recommended operating conditions, how to read a datasheet, protecting inputs, and why every chip needs a decoupling capacitor.
---

The fastest way to destroy a microcontroller board is to connect something at the wrong voltage. This lesson covers how to know, from the documents, what each pin will accept, and how to make two parts with different supplies talk safely.

> [!warning] Scope
> Everything here concerns low-voltage DC logic and audio circuits, typically 3.3 V and 5 V. Power your circuits from a certified USB supply or bench supply. Mains power-supply design is out of scope.

## Supply voltages: 3.3 V and 5 V

Two supply voltages dominate hobby digital electronics:

- **5 V:** USB's supply voltage, and the native supply of older logic families and many classic microcontrollers.
- **3.3 V:** the supply of most modern microcontrollers, including the ARM chips on audio-focused boards.

Many boards accept 5 V from USB and use an on-board **voltage regulator** to make 3.3 V for the chip. The board may expose both voltages on pins. **The fact that 5 V exists on the board says nothing about whether the chip's I/O pins tolerate 5 V.**

> [!example] A real board's limits
> PJRC's Teensy 4.1 page (checked 4 October 2026) states that its digital pins accept 0 to 3.3 V signals and "are not 5V tolerant", and that the analogue range is fixed at 0 to 3.3 V. Other boards differ: some microcontrollers have individual 5 V-tolerant pins. Read the exact board and revision's documentation and the microcontroller datasheet, and record the date you checked.

## Logic levels and thresholds

A digital input doesn't care about the exact voltage. It decides "high" or "low" using thresholds from its datasheet:

| Symbol | Meaning |
|---|---|
| V_IH(min) | Lowest voltage guaranteed read as high |
| V_IL(max) | Highest voltage guaranteed read as low |
| V_OH(min) | Lowest voltage a high output guarantees |
| V_OL(max) | Highest voltage a low output guarantees |

Between V_IL(max) and V_IH(min) is a forbidden zone where the input's behaviour isn't guaranteed.

An output can drive an input reliably only if the worst-case output always lands inside the region the input is guaranteed to accept, in both states:

```formula
V_{OH(min)} ≥ V_{IH(min)}
V_{OL(max)} ≤ V_{IL(max)}
where
V_{OH(min)}: the lowest voltage the driving output guarantees when it outputs a high, in volts (V)
V_{IH(min)}: the lowest voltage the receiving input is guaranteed to read as high, in volts
V_{OL(max)}: the highest voltage the driving output guarantees when it outputs a low, in volts
V_{IL(max)}: the highest voltage the receiving input is guaranteed to read as low, in volts
≥: is greater than or equal to
≤: is less than or equal to
In words: the first line says the weakest high the output can produce is still high enough for the input; the second says the worst low is still low enough. Both must be true.
```

The gaps between the two sides are the **noise margins**: how much noise (or ground offset) the link can tolerate before a bit is misread:

```formula
NM_H = V_{OH(min)} − V_{IH(min)}
NM_L = V_{IL(max)} − V_{OL(max)}
where
NM_H: the high-state noise margin, in volts (V)
NM_L: the low-state noise margin, in volts
V_{OH(min)}: the output's guaranteed minimum high voltage
V_{IH(min)}: the input's minimum voltage guaranteed to read as high
V_{IL(max)}: the input's maximum voltage guaranteed to read as low
V_{OL(max)}: the output's guaranteed maximum low voltage
In words: each margin is how far the worst-case output sits inside the input's acceptance region. A positive margin means the link is guaranteed; a negative one means it may fail.
```

### Real numbers from TI datasheets

| Part (supply) | Reads high from | Reads low up to |
|---|---|---|
| SN74HC00 (4.5 V) | 3.15 V | 1.35 V |
| SN74HCT00 (4.5–5.5 V) | 2.0 V | 0.8 V |

The SN74HC00 figures come from TI's datasheet (Recommended Operating Conditions with a 4.5 V supply). HC input thresholds scale with the supply voltage. The SN74HCT00 figures are "TTL-compatible" thresholds, designed to accept lower-voltage highs.

Suppose a 3.3 V microcontroller output guarantees a high of at least 2.4 V and a low of at most 0.4 V. These are illustrative figures (they match the JEDEC LVTTL limits for 3.3 V logic at a 2 mA load, and many 3.3 V microcontrollers do better at light loads). Take the real ones from your chip's datasheet at your load current. Into each part:

```formula
HC:  NM_H = 2.4 V − 3.15 V = −0.75 V
HC:  NM_L = 1.35 V − 0.4 V = +0.95 V
HCT: NM_H = 2.4 V − 2.0 V = +0.4 V
HCT: NM_L = 0.8 V − 0.4 V = +0.4 V
where
HC: the SN74HC00 at a 4.5 V supply
HCT: the SN74HCT00 at a 4.5–5.5 V supply
NM_H: the high-state noise margin, the output's 2.4 V minimum high minus the input's minimum high, in volts (V)
NM_L: the low-state noise margin, the input's maximum low minus the output's 0.4 V maximum low, in volts
V: volts
In words: into the HC part the high margin is negative, so a high isn't guaranteed to be seen as high. Into the HCT part both margins are a positive 0.4 V, so the link is guaranteed.
```

The same check in Python:

```python
def margins(voh, vol, vih, vil):
    hi = voh - vih   # high noise margin
    lo = vil - vol   # low noise margin
    return round(hi, 2), round(lo, 2)

# 3.3 V output into 74HC at 4.5 V
print(margins(2.4, 0.4, 3.15, 1.35))
# same output into 74HCT
print(margins(2.4, 0.4, 2.0, 0.8))
```

```
(-0.75, 0.95)
(0.4, 0.4)
```

The negative high margin means a 3.3 V output **isn't guaranteed** to be read as high by a 5 V HC input. It may work on your bench and fail on another day or another chip. The HCT part has positive margins in both states, which is why an HCT buffer powered from 5 V is a standard way to translate 3.3 V logic up to 5 V. TI's HCT application note (SCLA011) recommends HCT parts for the closely related problem of feeding TTL-level outputs into HC logic.

### The dangerous direction: 5 V into 3.3 V

Going down is the real hazard. A 5 V output driving a 3.3 V-only input exceeds that input's rating. Options, depending on speed and direction:

- A **level-shifter** chip designed for the job (the robust choice for fast or bidirectional signals).
- A **voltage divider** (two resistors) to scale 5 V down to about 3.3 V, for slow, one-way signals. Lesson 2's loading rules apply.
- An input the datasheet explicitly specifies as 5 V tolerant, under the stated conditions.

## Absolute maximum ratings versus recommended operating conditions

Every datasheet separates two very different tables.

**Absolute Maximum Ratings** are stress limits. The SN74HC00 datasheet's footnote is typical of TI's wording: "Stresses beyond those listed under Absolute Maximum Rating may cause permanent damage to the device. These are stress ratings only, which do not imply functional operation of the device at these or any other conditions beyond those indicated under Recommended Operating Condition. Exposure to absolute-maximum-rated conditions for extended periods may affect device reliability." For the SN74HC00 the table includes a supply maximum of 7 V and an input clamp current of ±20 mA.

**Recommended Operating Conditions** are where the part is guaranteed to work as specified: for the SN74HC00, a supply (V_CC) from 2 V to 6 V, with inputs between 0 V and the supply voltage.

```diagram
 0V                                    7V
 |--- recommended: 2–6 V ---|          |
 |------- stress limit: 7 V -----------|
    not a guaranteed operating range
```

Design inside recommended conditions with margin. Never treat an absolute maximum as a target. Living near it can shorten the part's life even if it doesn't fail at once.

## Reading a datasheet

Datasheets follow a predictable layout. In order of usefulness to a beginner:

1. **Features and description:** what the part is, supply range, key specs.
2. **Pin configuration:** pin numbers and names. Note which **view** (top view is standard for ICs) and the pin 1 marking.
3. **Absolute maximum ratings:** what will damage it.
4. **Recommended operating conditions:** where to design.
5. **Electrical characteristics:** guaranteed min/max values under stated **test conditions**, such as V_OH at a given load current.
6. **Typical characteristics (graphs):** how the part usually behaves. Not guaranteed.
7. **Application and layout information:** example circuits, decoupling and layout advice. Often the most practical section.

Rules of thumb:

- **Design to min/max, not "typ".** Typical values describe an average part on a good day.
- **Read the test conditions.** A guaranteed minimum high output at 20 µA isn't the same as at 4 mA. TI's SN74HC00 lists 4.4 V and 3.98 V respectively, with a 4.5 V supply at 25 °C.
- **Read the footnotes.** They hold the exceptions.
- **Get the datasheet for the exact part number**, including suffixes, from the manufacturer.

## Protecting inputs

Inputs that connect to the outside world (jacks, long wires, other equipment) see accidents: wrong voltages, static discharge, hot-plugging.

Most CMOS chips have internal **clamp diodes** from each input to the supply pin (V_CC) and to GND. When an input goes beyond a rail by a diode drop, the diode conducts and dumps the excess current into the rail.

```diagram
        VCC
         |
        ─┴─ clamp diode
  in ─[ R ]─┬──── chip input
        ─┬─ clamp diode
         |
        GND
```

A **series resistor** limits the current that flows into those clamps during a fault. TI's footnote reads: "The input and output voltage ratings may be exceeded if the input and output current ratings are observed." During a fault the clamp holds the pin about one diode drop above the rail, so the resistor takes the rest of the fault voltage:

```formula
I_clamp = (V_fault − V_CC − V_D) / R
I_clamp ≈ (5 V − 3.3 V − 0.5 V) / 10 kΩ
I_clamp ≈ 1.2 V / 10 kΩ ≈ 0.12 mA
where
I_clamp: the current pushed through the clamp diode into the supply rail, in milliamps (mA)
V_fault: the wrong voltage applied to the input, here 5 volts (V)
V_CC: the chip's supply rail, here 3.3 V
V_D: the clamp diode's forward drop, assumed about 0.5 V
R: the series resistor, here 10 kΩ
V: volts
kΩ: kilohms; 1 kΩ = 1000 ohms
mA: milliamperes; 1 mA = 0.001 amperes
≈: approximately equal to
In words: a 5 V mistake on a 3.3 V input pushes only about 0.12 mA through the clamp when a 10 kΩ resistor is in the way.
```

The 0.5 V clamp drop is an assumption: the real drop depends on the chip and the current, and like any silicon junction it is usually somewhat higher at milliamp currents. Assuming a low drop is the cautious choice, because it overestimates the current.

Be conservative:

- **Clamps are fault protection, not a level shifter.** Some manufacturers, such as PJRC for Teensy 4.1, say plainly not to drive pins above 3.3 V. Use proper level conversion for normal operation.
- **Microcontrollers specify their own injected-current limits.** Check the chip's datasheet rather than borrowing a 74HC figure.
- **Back-powering:** a signal driven into an unpowered chip can power it partly through the clamp diodes, causing strange behaviour or damage. Power boards up together, or make sure signals can't arrive before the supply.
- **External Schottky clamps** (with a lower forward drop than the internal diodes) are often added on exposed inputs, so they conduct before the chip's internal diodes do.

## Decoupling capacitors

Digital chips draw current in very short pulses each time their transistors switch. The supply wiring has resistance and inductance, so it can't deliver those pulses instantly. The local supply voltage dips and rings, and that noise spreads to everything sharing the supply, including audio.

A **decoupling capacitor** (bypass capacitor) next to the chip's supply pin acts as a local reservoir, supplying the pulses so the long supply path doesn't have to. TI's SN74HC00 datasheet says: "Each VCC terminal should have a good bypass capacitor to prevent power disturbance. A 0.1-μF capacitor is recommended for this device." It also suggests 0.1 µF and 1 µF in parallel, placed "as close to the power terminal as possible".

Practical rules:

- **100 nF ceramic at every supply pin,** with short connections to the pin and to ground. Distance adds inductance and defeats the purpose.
- **Bulk capacitance** (an electrolytic, say 10–100 µF) where power enters a board, for slower load changes. Values are typical, not prescriptive; follow the datasheets.
- **Follow the datasheet** where it gives specific values. Audio codecs and regulators often do.

Lesson 7 explains why this matters even more for audio.

## Key takeaways

- Know each pin's voltage limits from the board and chip documentation. 5 V on a board doesn't mean 5 V-tolerant pins.
- An output drives an input reliably only if its guaranteed high is at or above the input's minimum high, and its guaranteed low is at or below the input's maximum low. The gaps are the noise margins.
- 3.3 V into 5 V HC isn't guaranteed; an HCT buffer or level shifter fixes it. 5 V into 3.3 V-only pins can cause damage.
- Absolute maximums are damage limits. Design within recommended operating conditions.
- Design to guaranteed min/max under the stated test conditions, not to typical values.
- Series resistors and clamp diodes protect against faults. They aren't a substitute for proper level conversion.
- Put 100 nF of decoupling right at every chip's supply pin, plus bulk capacitance at the power entry.

## Further reading

- [SN74HC00 datasheet (Texas Instruments)](https://www.ti.com/lit/ds/symlink/sn74hc00.pdf)
- [SN74HCT00 datasheet (Texas Instruments)](https://www.ti.com/lit/ds/symlink/sn74hct00.pdf)
- [Understanding and interpreting standard-logic data sheets, SZZA036C (Texas Instruments)](https://www.ti.com/lit/an/szza036c/szza036c.pdf)
- [SN54/74HCT CMOS logic family applications and restrictions, SCLA011 (Texas Instruments)](https://www.ti.com/lit/pdf/scla011)
- [Teensy 4.1 pin voltage limits (PJRC)](https://www.pjrc.com/store/teensy41.html)
- [Logic levels (SparkFun)](https://learn.sparkfun.com/tutorials/logic-levels/all)
- [Decoupling capacitor (Wikipedia)](https://en.wikipedia.org/wiki/Decoupling_capacitor)
