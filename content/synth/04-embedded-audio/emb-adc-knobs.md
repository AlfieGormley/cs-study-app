---
id: emb-adc-knobs
title: ADCs and knobs
level: intermediate
minutes: 14
summary: How an ADC turns a knob's voltage into a number, why the reading jitters, how to smooth it with moving averages, one-pole filters and hysteresis, how to map it to musical parameters, and how to read many knobs through a multiplexer.
---

A knob on a synth is a potentiometer wired as a voltage divider. Turning it changes a voltage between 0 V and 3.3 V. An **ADC** (analogue-to-digital converter) measures that voltage and hands the firmware a number. Everything between "the user turned the knob" and "the filter cutoff moved" happens in this lesson, and almost all of it is about dealing with imperfection: noise, jitter and the mismatch between how knobs turn and how ears hear.

## How an ADC works

An ADC repeatedly samples a voltage and **quantises** it to an integer code. Three numbers describe it:

- **Resolution (N bits).** The number of distinct codes: 2^N. A 12-bit ADC gives 4,096 codes (0 to 4,095).
- **Reference voltage (V_ref).** The voltage that corresponds to full scale. On both the Daisy Seed and Teensy 4.1 the analogue input range is 0–3.3 V.
- **Sample rate.** How often it converts. Audio ADCs (inside a codec) run at 48 kHz or more. For knobs, a few hundred to a thousand readings per second is plenty, because hands move slowly.

The step size, or **LSB** (least significant bit), is V_ref / 2^N:

```python
vref = 3.3
for bits in (10, 12, 16):
    lsb = vref / 2**bits
    print(f"{bits}-bit: {2**bits} codes, "
          f"LSB {lsb*1e3:.4f} mV")
```

```
10-bit: 1024 codes, LSB 3.2227 mV
12-bit: 4096 codes, LSB 0.8057 mV
16-bit: 65536 codes, LSB 0.0504 mV
```

At 16 bits, one code is about 50 µV. Ordinary supply noise and wiring pick-up are far larger than that, so the bottom bits will be noise. Resolution is not the same as accuracy. PJRC says this plainly for Teensy 4.1: the default resolution is 10 bits, the hardware allows 12, "but in practice only up to 10 bits are normally usable due to noise". Electro-Smith describes the Daisy Seed's ADC as "up to 16-bits", returning a float from 0.0 to 1.0 via `GetFloat()`.

For a knob, 7 bits (128 steps, like a MIDI CC) is coarse; 10 usable bits (1,024 steps) is usually smooth enough, especially once you smooth and map the value.

## Reading a potentiometer

```diagram
 3.3V (analogue) --+
                   |
                 [pot]<-- wiper --> ADC
                   |
 GND --------------+
```

Both ends of the pot go to ground and the 3.3 V **analogue** supply; the wiper goes to an ADC-capable pin. Daisy's ADC guide wires pin 1 to GND, pin 3 to `3v3_A` and the middle leg to the ADC input. The Daisy Seed datasheet's example part is a 10 kΩ linear pot.

Two practical points:

- **Use the analogue supply as the top reference** when the board provides one. Then supply noise moves the pot's output and the ADC's reference together.
- **Pot value.** Most MCU ADCs charge a small internal sampling capacitor through your source. Very high-value pots can make readings inaccurate; low values waste current. 10 kΩ is a common middle ground (check the MCU datasheet's source-impedance guidance).

Pot **taper** matters too. A linear pot gives voltage proportional to rotation; an audio/log pot does not. B often means linear and A audio/log, but markings vary between manufacturers: confirm the taper in its datasheet. With an ADC in the loop, it is usually easier to use linear pots and apply the curve in software, where you can change it.

## Noise and jitter

Leave a knob still and read it repeatedly, and the code wanders by a few LSBs. Sources include supply ripple, digital switching noise coupling into the analogue path, and the ADC's own noise. If you feed the raw value straight into a parameter, two things go wrong:

1. **Zipper noise.** The parameter jumps in small steps that you can hear, especially on gain and filter cutoff.
2. **Chatter.** Anything that reacts to changes (sending MIDI CC, redrawing a display, recalling a preset) fires constantly while the knob is untouched.

## Smoothing: moving average and one-pole

**Moving average.** Average the last N readings. Simple, and with N readings it reduces random noise, but it adds a delay of roughly N/2 samples and needs a buffer.

**One-pole low-pass (exponential smoothing).** Keep one state value and move it a fraction `a` of the way towards each new reading:

```
y = y + a * (x - y)
```

Small `a` means heavy smoothing and slow response. You can choose `a` from a time constant τ and the update rate:

```python
import math
rate = 1000.0          # control reads/s
tau = 0.010            # 10 ms
a = 1 - math.exp(-1 / (tau * rate))
print(f"a = {a:.4f}")
y = 0.0
for n in range(1, 31):
    y += a * (1.0 - y)  # step to 1.0
    if n in (10, 20, 30):
        print(n, f"{y:.3f}")
```

```
a = 0.0952
10 0.632
20 0.865
30 0.950
```

After one time constant (10 readings = 10 ms) the output has covered 63.2% of a step; after three, 95%. This is the same filter as the one-pole low-pass in DSP, running at control rate. libDaisy's `AnalogControl` class applies exactly this kind of one-pole smoothing to each knob, with a default slew time of 0.002 s.

## Hysteresis: stop the chatter

Smoothing shrinks jitter but does not remove it. To make a still knob produce a *perfectly* still value, add **hysteresis** (a dead band): only accept a new value when it differs from the held one by more than a threshold.

```python
# Knob at rest; ADC codes jitter by +-2.
reads = [2048, 2050, 2047, 2049, 2046,
         2048, 2050, 2047, 2046, 2049]

def changes(xs):
    return sum(1 for a, b in zip(xs, xs[1:])
               if a != b)

def hysteresis(xs, band):
    held = xs[0]
    out = []
    for x in xs:
        if abs(x - held) > band:
            held = x
        out.append(held)
    return out

def moving_avg(xs, n):
    out = []
    for i in range(len(xs)):
        w = xs[max(0, i - n + 1): i + 1]
        out.append(sum(w) // len(w))
    return out

print("raw changes:", changes(reads))
a = moving_avg(reads, 4)
print("avg4 changes:", changes(a),
      "range:", min(a), max(a))
h = hysteresis(reads, 3)
print("hyst3 changes:", changes(h), h[-1])
```

```
raw changes: 9
avg4 changes: 6 range: 2047 2049
hyst3 changes: 0 2048
```

The raw value changed on every one of the nine steps. The 4-point average still changed six times, wandering between 2047 and 2049. Hysteresis with a ±3 band holds 2048 throughout. The cost: a deliberate movement must exceed the band before anything happens, so make the band just wider than the noise you measured.

A common pipeline is **smooth, then hysteresis for change detection**, then pass the smoothed value to the audio code, which applies its own per-sample smoothing (lesson 7).

## Mapping values to parameters

The ADC gives a number from 0 to 1 (after scaling). Musical parameters rarely want that range or a straight line.

**Linear mapping** suits parameters we perceive linearly, such as pan position or a mix ratio: `value = lo + x * (hi - lo)`.

**Exponential mapping** suits frequency. Pitch perception is logarithmic: each octave doubles frequency. Map a 20 Hz–20 kHz cutoff linearly and almost the whole knob is spent above 5 kHz.

```python
lo, hi = 20.0, 20_000.0
for x in (0.0, 0.25, 0.5, 0.75, 1.0):
    lin = lo + x * (hi - lo)
    exp = lo * (hi / lo) ** x
    print(f"x={x:.2f} lin={lin:8.0f} "
          f"exp={exp:7.0f}")
```

```
x=0.00 lin=      20 exp=     20
x=0.25 lin=    5015 exp=    112
x=0.50 lin=   10010 exp=    632
x=0.75 lin=   15005 exp=   3557
x=1.00 lin=   20000 exp=  20000
```

With exponential mapping, equal knob movements give equal frequency *ratios*. 20 Hz to 20 kHz is a ratio of 1,000 (just under 10 octaves), so each quarter of the knob covers the same ratio, 1000^0.25 ≈ 5.6×. The same idea applies to envelope times and, in decibels, to volume.

> [!tip] Map after smoothing
> Smooth the 0–1 control value, then map. If you smooth *after* an exponential map, the smoother works in hertz, which makes it lopsided in pitch: for a quarter-turn move (a ×5.6 frequency ratio), after one time constant a rise has covered about 79% of its musical distance but a fall only about 42%. Only the ratio matters, not where in the range you are, so upward sweeps feel snappy and downward ones sluggish everywhere, and the larger the move the worse the imbalance. Smoothing the 0–1 value (or log-frequency) gives 63% in both directions.

## Multiplexing many knobs

A synth with 16 knobs may have only 12 ADC pins (the Daisy Seed has 12; the Teensy 4.1 has 18). An **analogue multiplexer** such as the CD4051 is an 8-to-1 switch: three digital select lines choose which of eight inputs connects to one output. Two of them read 16 knobs on two ADC pins with three shared select lines.

```
for ch in 0..7:
  set select pins to ch (3 bits)
  wait for the mux output to settle
  value[ch] = read_adc()
```

libDaisy supports this directly: `InitMux` takes an ADC pin, a channel count from 1 to 8 and up to three select pins. Things to watch:

- **Settling time.** After switching, the mux output and ADC input take time to settle to the new knob's voltage. Read too soon and you get a little of the previous knob ("crosstalk"). Allow time between switching and sampling, or discard the first reading.
- **Scan rate.** Each knob is read once per full scan. At a 1 kHz scan and eight channels per mux, you need 8,000 conversions a second per ADC, which is easy for an MCU ADC.
- **Supply.** Power the mux from the same supply range as the signals, and keep pot signals within it.

Do the scanning outside the audio callback, or on a timer or DMA, so it never stretches the audio deadline.

## Key takeaways
- An ADC quantises 0–V_ref into 2^N codes; LSB = V_ref / 2^N. Usable resolution is limited by noise: Teensy 4.1 is practically about 10 bits.
- Wire pots between analogue ground and the analogue 3.3 V supply, wiper to an ADC pin; prefer linear pots and curve in software.
- Moving averages and one-pole filters reduce jitter; hysteresis removes chatter for change detection.
- Map frequency (and times and gain) exponentially: equal knob travel should give equal ratios.
- Analogue multiplexers like the CD4051 extend ADC inputs; allow settling time and scan outside the audio callback.

## Further reading
- [Getting started: ADCs — Electro-Smith](https://docs.daisy.audio/tutorials/_a4_Getting-Started-ADCs/)
- [Teensy 4.1 analog pins — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Coding schemes used with data converters (SBAA042) — Texas Instruments](https://www.ti.com/lit/an/sbaa042/sbaa042.pdf)
- [Analog-to-digital converter — Wikipedia](https://en.wikipedia.org/wiki/Analog-to-digital_converter)
- [Introduction to Digital Filters (one-pole filters) — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/)
