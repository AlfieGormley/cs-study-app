---
id: aud-sound-systems
title: Sound systems and signal flow
level: advanced
minutes: 18
summary: The chain from source to listener, the mixing console's channel strip, sends, inserts, buses and subgroups, gain staging across a whole system, PA design with mains, subs, monitors and delay speakers, DI boxes, preventing acoustic feedback, and how studio and live systems differ.
---

Up to now we've looked at parts: microphones, drivers, boxes, crossovers, amplifiers. A **sound system** connects them so that a source (your synth, a voice, a drum) reaches listeners at the right level, with the right balance and without noise, distortion or feedback. Whether it's a desk in your bedroom or a festival PA, the principles are the same.

## The chain

```flow
Source: synth, mic or instrument
DI box or mic: to balanced mic/line level
Console: preamp gain, EQ, routing, mix
Processing: system EQ, delay, crossover
Power amplifiers (or powered speakers)
Loudspeakers
Room and listeners
```

Every stage has a **noise floor** below the signal and a **clipping point** above it. The job is to keep the signal comfortably between them at every stage.

## The mixing console

A console (mixer, desk) combines many inputs into a few outputs, with independent control over each. Digital consoles and DAWs (Ableton's mixer included) copy the analogue layout, so learning one teaches you the others.

### The channel strip

Signal flows from top to bottom of a typical channel:

1. **Input and preamp gain (trim).** Brings mic or line level up to the console's internal operating level. This is the most important control on the desk for noise and headroom. Phantom power and a pad switch usually live here.
2. **High-pass filter.** Removes rumble and handling noise below the useful range of the source. On most vocal and instrument channels it's switched in.
3. **Insert point.** A send and return that loops the channel's signal out to an external processor (a compressor, say) and back, in series.
4. **EQ.** Shelving and parametric bands for tone and to make room for other sources.
5. **Dynamics** (on many digital desks): gate and compressor.
6. **Aux sends.** Copies of the channel at an adjustable level to separate **aux buses**, used for monitor mixes and effects.
   - **Pre-fader** sends ignore the channel fader: right for **monitor mixes**, so the front-of-house engineer's fader moves don't change what the performer hears.
   - **Post-fader** sends follow the fader: right for **effects** like reverb, so the wet signal fades with the dry.
7. **Pan** places the signal in the stereo bus.
8. **Fader** sets the channel's level in the mix.
9. **Routing** assigns the channel to the main mix and/or **subgroups**.

### Buses and subgroups

A **bus** is any point where signals are summed. The main L/R mix is a bus; so are aux sends and subgroups.

- **Subgroups** sum related channels (all drums, all backing vocals) to one fader, so you can ride a whole section, or compress it together, with one control.
- **VCA or DCA groups** (on many consoles) are a variation: one fader remotely controls the faders of its member channels without summing audio.

## Gain staging across the system

Module 1 covered gain staging inside a digital synth. In a system, the same idea applies at every box:

1. **Set the preamp gain first**, with the performer at their loudest. Aim for healthy levels with headroom to spare: on a digital desk, nominal levels around −18 to −20 dBFS leave room for peaks (module 1); on an analogue desk, follow its meter calibration and overload-warning guidance, allowing headroom for unexpectedly loud peaks rather than deliberately clipping. The system's signal-to-noise ratio is largely fixed here: noise added at the mic preamp is amplified by everything after it.
2. **Keep faders near their unity (0 dB) mark** for normal levels, so there's travel in both directions.
3. **Set outboard gear to unity** where possible, passing the full signal without clipping.
4. **Set amplifier input sensitivity** as part of the system’s gain and protection plan. One approach maps the maximum clean system output to the required amplifier output; that output must also respect speaker and audience limits. Amp input controls are attenuators that set sensitivity, not "power" controls.

To work out how much preamp gain a mic needs, start from its sensitivity (its output voltage at a reference sound pressure of 1 pascal, which is 94 dB SPL), add however far the real source is above that reference, convert to dBu, and subtract from the level the console wants. Example: an SM58 (sensitivity −54.5 dBV/Pa) picks up a singer at 104 dB SPL, which is 10 dB above 1 Pa:

```formula
V_v = S + (L_p − 94)
V_v = −54.5 + (104 − 94) = −44.5 dBV
V_u = V_v + 20 × log_10(1 / 0.7746)
V_u ≈ −44.5 + 2.2 = −42.3 dBu
G = L_nom − V_u
G = 4 − (−42.3) = 46.3 dB
where
V_v: the mic's output level, in dBV (decibels relative to 1 volt)
S: the mic's sensitivity, in dBV per pascal (dBV/Pa): its output at 94 dB SPL; −54.5 dBV/Pa for an SM58, about 1.9 millivolts
L_p: the sound pressure level at the mic, in dB SPL; here 104 dB SPL
94: the sound pressure level of 1 pascal (Pa), in dB SPL: the reference at which sensitivity is measured
V_u: the same output level expressed in dBu (decibels relative to 0.7746 volts)
log_10: the base-10 logarithm: the power you raise 10 to in order to get the number
0.7746: the dBu reference voltage, 0.7746 volts (V); 20 × log_10(1 / 0.7746) ≈ 2.2 dB is the fixed gap between dBV and dBu
G: the preamp gain needed, in decibels (dB)
L_nom: the console's nominal operating level, here +4 dBu
dB: decibels, a logarithmic ratio; every 20 dB is a factor of 10 in voltage
dBV: decibels relative to 1 volt
dBu: decibels relative to 0.7746 volts
In words: the singer is 10 dB louder than the sensitivity reference, so the mic puts out 10 dB more than its rated sensitivity; the preamp must make up the gap between that and the console's +4 dBu working level.
```

About 46 dB of preamp gain. A condenser 24 dB more sensitive (lesson 3) would need only around 22 dB.

> [!warning] Two common mistakes
> - Low preamp gain "made up" with faders pushed to the top: the console's noise is amplified as much as the signal.
> - Preamp gain set with the singer warming up quietly: the first chorus clips the input, and no fader can undo clipping that happened upstream.

## DI boxes

A **DI (direct input) box** connects an instrument or line-level source to a console's balanced **mic input**:

- It accepts an instrument or line-level signal and provides a **low-impedance, balanced, mic-level** output. Passive guitar pickups often need a high input impedance; synth and keyboard line outputs are usually low impedance and may already be balanced. Choose the DI or direct line connection to suit both devices.
- That lets the signal travel down a long multicore to the desk with good noise rejection (module 5's balanced lines).
- Most DIs have a **ground lift** switch to break a ground loop between stage gear and the desk's ground (module 3), and many have a pad.

Two types:

- **Passive** DIs use a transformer. No power needed; robust; the transformer gives galvanic isolation.
- **Active** DIs use a buffer amplifier, powered by phantom power or a battery. They load high-impedance sources (like passive guitar pickups) very lightly.

For your synth on a stage, a DI is usually the right way into a PA, with the synth's output at line level into the DI's input (use its pad if needed).

## PA design

A typical live PA has several systems, each with its own job:

- **Mains (front of house).** Left/right or mono speakers covering the audience, flown or on stands. Larger venues use **line arrays**: vertical columns of boxes that control vertical coverage and lose level more slowly with distance over part of their range.
- **Subwoofers.** Below about 80–120 Hz. Usually on the ground. Several subs can be arranged (end-fire, cardioid, arc) to steer low frequencies away from the stage.
- **Monitors.** What performers hear: floor **wedges** aimed up at each performer, side fills, or **in-ear monitors (IEMs)**. Fed from **pre-fader aux** mixes.
- **Front fills.** Small speakers along the stage lip for the front rows, who are below the mains' coverage.
- **Delay speakers.** Further back in large venues, where the mains have lost too much level.

### Delay speakers, worked

At a chosen listener position, compare the path from the main speaker with the path from the delay speaker. Sound from the mains has further to travel, so without an electronic delay the delay speaker's copy would arrive first and pull the sound image towards it. The delay to dial in is the extra travel time, plus any difference in processing latency between the two paths:

```formula
D = d_main − d_delay
t_align = D / c + t_lat
t_align = 40 m / (343 m/s) + 0
t_align ≈ 0.117 s = 117 ms
where
D: the path difference, in metres (m): how much further the listener is from the main speaker than from the delay speaker
d_main: the distance from the main speaker to the chosen listener position, in metres (m)
d_delay: the distance from the delay speaker to the same listener position, in metres (m)
t_align: the electronic delay to apply to the delay speaker so the two arrivals line up, in seconds (s)
c: the speed of sound in air, about 343 metres per second (m/s)
t_lat: the difference in electronic processing latency between the two signal paths, in seconds (s); taken as 0 here
m: metres
m/s: metres per second
s: seconds
ms: milliseconds, thousandths of a second
In words: delay the delay speaker by the time sound takes to cover the extra distance from the mains, so both arrive together at the listener.
```

If the mains path is **40 m longer**, about 117 ms aligns arrivals in this simplified example. It only holds exactly at the chosen position; listeners nearer or further away see a different path difference. A designer may choose an additional offset to favour the mains as the first arrival, but no universal 10–20 ms setting guarantees fusion or stage localisation. Those depend on signal, relative level, geometry and reflections; measure and listen throughout the overlap region. Exact universal precedence offsets are absent because reliable evidence for such a guarantee was not established.

## Acoustic feedback

**Feedback** happens when the sound from a speaker re-enters a microphone, is amplified, comes out of the speaker louder, and so on. At any frequency where the **loop gain** (the total gain once round the loop: mic, console, amplifier, speaker, air and back) reaches 1, which is 0 dB, with a phase that reinforces itself, the system howls. Feedback develops at a frequency where both loop magnitude and reinforcing phase conditions are met: often a peak in a speaker's or mic's response, or a room resonance.

How to get more **gain before feedback**:

1. **Get the mic close to the source.** Halving the source-to-mic distance gives about 6 dB more source level at the mic (inverse square law), so 6 dB less gain is needed.
2. **Keep speakers away from mics**, and put mains in front of the mic line.
3. **Use directional mics and their nulls.** Put wedges in the null of the mic's pattern (lesson 3).
4. **Fewer open mics.** In the usual approximate potential-acoustic-gain model, doubling similarly coupled **open microphones (NOM)** costs about 3 dB; actual loop paths can differ. Mute what isn't in use.
5. **EQ.** "Ringing out" the system: raise gain until it starts to ring, identify the frequency, and cut it with a narrow EQ band. Automatic notch-based feedback suppressors do this live, but they typically add only a few dB of margin.
6. **In-ear monitors** remove the wedge-to-mic path altogether.

The 6 dB figure in step 1 comes from the inverse square law. For a small source in open air, the level change when you move from one distance to another is:

```formula
L_d = 20 × log_10(r_1 / r_2)
L_d = 20 × log_10(0.10 / 0.05)
L_d ≈ 20 × 0.301 ≈ 6.0 dB
where
L_d: how much louder the source is at the new distance, in decibels (dB)
log_10: the base-10 logarithm: the power you raise 10 to in order to get the number
r_1: the old source-to-mic distance, in metres (m); here 10 cm = 0.10 m
r_2: the new, closer distance, in metres (m); here 5 cm = 0.05 m
dB: decibels, a logarithmic ratio of levels
In words: every halving of the distance gives about 6 dB more level at the mic, so the channel needs 6 dB less gain for the same output.
```

Very close to a directional mic, the proximity effect also boosts the bass, and a voice is not a point source, so treat 6 dB per halving as a guide.

The 3 dB figure in step 4 comes from the potential acoustic gain (PAG) model, where open mics that each pick up the PA about equally add up as uncorrelated signals:

```formula
G_NOM = 10 × log_10(N_1 / N_2)
G_NOM = 10 × log_10(4 / 2)
G_NOM ≈ 10 × 0.301 ≈ 3.0 dB
where
G_NOM: the gain before feedback you get back by reducing the number of open microphones, in decibels (dB)
log_10: the base-10 logarithm
N_1: the number of open microphones (NOM) before muting
N_2: the number of open microphones after muting
dB: decibels
NOM: number of open microphones
In words: each halving of the number of open mics buys back about 3 dB of gain before feedback; each doubling costs about 3 dB.
```

It's 10 rather than 20 because the mics' pickups of the PA add as powers (they're not in step with each other), not as voltages. Real stages differ: mics nearer a wedge contribute more than the model assumes.

## Studio vs live

| | Studio | Live |
|---|---|---|
| Goal | Accurate monitoring | Coverage, level |
| Listeners | One position | Whole audience |
| Speakers | Near-field monitors | PA, subs, wedges |
| Feedback | Rarely an issue | Constant concern |
| Room | Treated (lesson 9) | Take what you get |

In a studio the monitors must tell the truth, so you can make decisions that translate to other systems. In a live system the goal is even, intelligible, sufficiently loud coverage for everyone, with controlled exposure and compliance with applicable venue limits. WHO’s 100 dB LAeq,15 min ceiling is one part of its safe-listening venue standard, not a guarantee that a whole event is safe at that level (lesson 2).

## Key takeaways
- Signal flows source → DI/mic → console → processing → amps → speakers → room; every stage has a noise floor and a clipping point.
- A channel strip runs gain → HPF → insert → EQ → dynamics → aux sends → pan → fader → routing; pre-fader sends for monitors, post-fader for effects.
- Gain stage at the preamp first; keep faders near unity; coordinate amplifier sensitivity with the required output and speaker protection limits.
- DI boxes convert high-impedance unbalanced sources to balanced mic level, often with a ground lift.
- A PA has mains, subs, monitors, fills and delays; delay speakers are aligned using path and processing-latency differences at the intended overlap positions.
- Feedback happens when loop gain reaches 0 dB in phase; fight it with distance, directivity, fewer open mics (−3 dB per doubling) and EQ.

## Further reading
- [Setting sound system level controls (RaneNote 135) — Rane](https://www.ranecommercial.com/legacy/note135.html)
- [Understanding acoustic feedback and suppressors (RaneNote 158) — Rane](https://www.ranecommercial.com/legacy/note158.html)
- [Mixing console — Wikipedia](https://en.wikipedia.org/wiki/Mixing_console)
- [Gain stage — Wikipedia](https://en.wikipedia.org/wiki/Gain_stage)
- [DI unit — Wikipedia](https://en.wikipedia.org/wiki/DI_unit)
- [Audio feedback — Wikipedia](https://en.wikipedia.org/wiki/Audio_feedback)
- [Gain before feedback — Wikipedia](https://en.wikipedia.org/wiki/Gain_before_feedback)
- [Sound reinforcement system — Wikipedia](https://en.wikipedia.org/wiki/Sound_reinforcement_system)
- [Precedence effect (delay speakers) — Wikipedia](https://en.wikipedia.org/wiki/Precedence_effect)
