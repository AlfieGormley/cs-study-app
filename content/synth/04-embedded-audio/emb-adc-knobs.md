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

- **Resolution.** How many bits each reading has. More bits means more distinct codes. A 12-bit ADC gives 4,096 codes (0 to 4,095).
- **Reference voltage.** The voltage that corresponds to full scale. On both the Daisy Seed and Teensy 4.1 the analogue input range is 0–3.3 V.
- **Sample rate.** How often it converts. Audio ADCs (inside a codec) run at 48 kHz or more. For knobs, a few hundred to a thousand readings per second is plenty, because hands move slowly.

Each extra bit doubles the number of codes, because every existing pattern can now end in a 0 or a 1:

```formula
codes = 2^N
codes = 2^12 = 4096
where
codes: the number of distinct output values the ADC can produce (they run from 0 to codes − 1)
N: the ADC's resolution, in bits; here 12
2^N: 2 raised to the power N, that is, 2 multiplied by itself N times
In words: every extra bit doubles the number of codes, so 10 bits give 1,024, 12 bits give 4,096 and 16 bits give 65,536.
```

The input range is divided evenly between those codes. The size of one step, the smallest change the ADC can register, is called one **LSB** (least significant bit), because it is what a change in the lowest bit of the code is worth:

```formula
LSB = V_ref / 2^N
LSB = 3.3 V / 2^12
LSB = 3.3 V / 4096 ≈ 0.000806 V ≈ 0.81 mV
where
LSB: the voltage step between two neighbouring codes, in volts (V)
V_ref: the reference voltage, the input voltage that corresponds to full scale, in volts (V); here 3.3 V
N: the resolution, in bits; here 12
2^N: 2 raised to the power N, the number of codes
V: volt, the unit of voltage
mV: millivolt, one thousandth of a volt
≈: approximately equal to (the result is rounded)
In words: split the 3.3 V range into 4,096 equal steps and each step is about 0.8 mV; every extra bit halves the step.
```

The same sum for three common resolutions:

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

**Moving average.** Average the last few readings:

```formula
y = (x_1 + x_2 + … + x_M) / M
where
y: the smoothed output
x_1: the newest raw reading
x_2: the reading before that
x_M: the oldest reading still in the window
M: how many readings are averaged, for example 4 or 8
…: "and so on": every reading between x_2 and x_M is included in the sum
In words: add up the last M readings and divide by M. Random noise partly cancels out; a real change shows up only gradually.
```

Simple, and averaging M readings reduces random noise, but the output lags the input by roughly half the window and you need a buffer holding the last M readings. Strictly, the lag is half of one less than the window: 3.5 readings for an 8-reading window, which at 1,000 readings a second is 3.5 ms.

**One-pole low-pass (exponential smoothing).** Keep one state value and move it a fixed fraction of the way towards each new reading:

```formula
y_n = y_{n−1} + a × (x_n − y_{n−1})
where
y_n: the smoothed value after reading n
y_{n−1}: the smoothed value from the previous reading
x_n: the new raw reading
a: the smoothing coefficient, a number between 0 and 1 with no unit; small a (say 0.01–0.1) means heavy smoothing and slow response, a = 1 means no smoothing
n: the reading number
In words: each time a reading arrives, close the fraction a of the gap between the smoothed value and the reading. The smoothed value creeps towards the input and never overshoots.
```

In code this is one line, `y = y + a * (x - y)`. You can choose `a` from how quickly you want it to respond: a **time constant**, the time the output takes to cover about 63% of a sudden step:

```formula
a = 1 − e^(−1 / (τ × r))
a = 1 − e^(−1 / (0.010 s × 1000 /s))
a = 1 − e^(−0.1) ≈ 1 − 0.9048 = 0.0952
where
a: the smoothing coefficient per reading, between 0 and 1, no unit
e: Euler's number, about 2.71828, the base of natural exponential growth and decay
τ: tau, the time constant you want, in seconds (s); here 10 ms = 0.010 s
r: the update rate, how many readings per second the filter receives, in per second (/s); here 1,000
s: second, the unit of time
≈: approximately equal to (rounded)
In words: work out how many readings fit in one time constant (here 10), and a is the fraction that makes the filter cover 63% of a step in that many readings. A longer time constant gives a smaller a.
```

The same calculation, plus a check of how far the filter gets towards a step from 0 to 1:

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

Why 63%? Each reading leaves a fraction (1 − a) of the remaining gap, so after k readings the fraction of a step covered is:

```formula
covered = 1 − (1 − a)^k
covered = 1 − (1 − 0.0952)^10
covered = 1 − 0.368 ≈ 0.632
where
covered: the fraction of a sudden step the output has travelled, from 0 (none) to 1 (all of it)
a: the smoothing coefficient, here 0.0952
k: the number of readings since the step; here 10, one time constant at 1,000 readings per second
≈: approximately equal to
In words: after one time constant the filter has covered about 63% of any step, after two about 86%, after three about 95%. It never quite reaches 100%.
```

After one time constant (10 readings, which is 10 ms) the output has covered 63.2% of a step; after three, 95%. These figures hold whenever the time constant spans many readings; with very few readings per time constant the curve is a coarse staircase. This is the same filter as the one-pole low-pass in DSP, running at control rate. libDaisy's `AnalogControl` class applies exactly this kind of one-pole smoothing to each knob, with a default slew time of 0.002 s.

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

**Linear mapping** suits parameters we perceive linearly, such as pan position or a mix ratio:

```formula
v = lo + x × (hi − lo)
where
v: the parameter value sent to the synth, in the parameter's own unit
x: the knob position after scaling, from 0 (fully anticlockwise) to 1 (fully clockwise), no unit
lo: the parameter value at x = 0
hi: the parameter value at x = 1
In words: start at the bottom of the range and add the same fraction of the range as the knob's fraction of its travel. Equal knob movements give equal differences.
```

**Exponential mapping** suits frequency. Pitch perception is logarithmic: each octave doubles frequency. Map a 20 Hz–20 kHz cutoff linearly and almost the whole knob is spent above 5 kHz. Instead, multiply the bottom of the range by the whole ratio raised to the knob position:

```formula
f = f_lo × (f_hi / f_lo)^x
f = 20 Hz × (20000 Hz / 20 Hz)^0.5
f = 20 Hz × 1000^0.5 ≈ 20 Hz × 31.62
f ≈ 632 Hz
where
f: the cutoff frequency the knob sets, in hertz (Hz)
f_lo: the frequency at x = 0, in hertz (Hz); here 20 Hz
f_hi: the frequency at x = 1, in hertz (Hz); here 20 kHz = 20,000 Hz
x: the knob position, from 0 to 1, no unit; here 0.5, the middle
^x: raised to the power x; a power of 0.5 is the square root
Hz: hertz, cycles per second
≈: approximately equal to
In words: the middle of the knob lands at 632 Hz, which is the same ratio (about 31.6 times) above 20 Hz as it is below 20 kHz, so it sounds like the middle.
```

The Python below compares both maps at five knob positions:

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

With exponential mapping, equal knob movements give equal frequency *ratios*. 20 Hz to 20 kHz is a ratio of 1,000, which is just under 10 octaves:

```formula
octaves = log_2(f_hi / f_lo)
octaves = log_2(20000 Hz / 20 Hz)
octaves = log_2(1000) ≈ 9.97
step = (f_hi / f_lo)^Δx
step = 1000^0.25 ≈ 5.62
where
octaves: how many doublings of frequency fit in the range
log_2: the base-2 logarithm: log_2(y) is how many times you must double 1 to reach y; log_2(1024) = 10
f_hi: the top of the range, in hertz (Hz); here 20,000 Hz
f_lo: the bottom of the range, in hertz (Hz); here 20 Hz
step: the frequency ratio covered by a knob movement of Δx, anywhere on the knob
Δx: a change in knob position (0 to 1 scale); here a quarter turn of the range, 0.25
Hz: hertz, cycles per second
≈: approximately equal to
In words: the range spans almost 10 octaves, and every quarter of the knob multiplies the frequency by about 5.6, whether you start at 20 Hz or at 3.5 kHz.
```

The same idea applies to envelope times and, in decibels, to volume.

> [!tip] Map after smoothing
> Smooth the 0–1 control value, then map. If you smooth *after* an exponential map, the smoother works in hertz, which makes it lopsided in pitch: for a quarter-turn move (a ×5.6 frequency ratio), after one time constant a rise has covered about 79% of its musical distance but a fall only about 42%. Only the ratio matters, not where in the range you are, so upward sweeps feel snappy and downward ones sluggish everywhere, and the larger the move the worse the imbalance. Smoothing the 0–1 value (or log-frequency) gives 63% in both directions.

## Multiplexing many knobs

A synth with 16 knobs may have only 12 ADC pins (the Daisy Seed has 12; the Teensy 4.1 has 18). An **analogue multiplexer** (mux) such as the CD4051 is an 8-to-1 switch: three digital select lines choose which of eight inputs connects to one output. Each select line is one bit, so the number of inputs a mux can choose between doubles with each line:

```formula
channels = 2^s
channels = 2^3 = 8
where
channels: how many inputs the select lines can address
s: the number of digital select lines; here 3 on a CD4051
2^s: 2 raised to the power s, 2 multiplied by itself s times
In words: three select lines give eight combinations (000 to 111), one per input.
```

Two CD4051s read 16 knobs on two ADC pins with three shared select lines.

```
for ch in 0..7:
  set select pins to ch (3 bits)
  wait for the mux output to settle
  value[ch] = read_adc()
```

libDaisy supports this directly: `InitMux` takes an ADC pin, a channel count from 1 to 8 and up to three select pins. Things to watch:

- **Settling time.** After switching, the mux output and ADC input take time to settle to the new knob's voltage. Read too soon and you get a little of the previous knob ("crosstalk"). Allow time between switching and sampling, or discard the first reading.
- **Scan rate.** Each knob is read once per full scan, so the ADC behind each mux must convert once per channel per scan. At a 1 kHz scan and eight channels per mux, you need 8,000 conversions a second per ADC, which is easy for an MCU ADC.
- **Supply.** Power the mux from the same supply range as the signals, and keep pot signals within it.

Do the scanning outside the audio callback, or on a timer or DMA, so it never stretches the audio deadline.

## Key takeaways
- An N-bit ADC quantises its input range into 2 to the power N codes, and one step (1 LSB) is the reference voltage divided by that number: about 0.8 mV for 12 bits over 3.3 V. Usable resolution is limited by noise: Teensy 4.1 is practically about 10 bits.
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
