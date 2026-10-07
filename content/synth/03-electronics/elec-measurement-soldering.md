---
id: elec-measurement-soldering
title: Measurement and soldering
level: intermediate
minutes: 16
summary: Using a multimeter correctly (parallel voltage, series current, unpowered resistance and continuity, ranges and fuses), what an oscilloscope adds, and safe, reliable soldering, including how to inspect a joint.
---

Measuring tells you whether the circuit is doing what you calculated. Soldering makes a circuit permanent. Both are hands-on skills with a few rules that, if you ignore them, destroy fuses, parts or your lungs.

> [!warning] Low-voltage work only
> Everything here assumes low-voltage DC circuits powered from USB, batteries or a bench supply. Don't use these techniques on mains-powered equipment. Mains measurement needs suitably rated (CAT-rated) instruments and training, and it's outside this project's scope.

## The multimeter

A digital multimeter (DMM) has a rotary switch and usually three or four input jacks:

- **COM:** the common (black) lead. It stays here for everything.
- **VΩ** (often shared with mA): red lead for voltage, resistance, continuity and diode test.
- **mA / µA:** red lead for small currents, protected by a fuse.
- **A or 10A:** red lead for large currents, usually separately fused.

The jack layout differs between meters, so read the manual.

### Voltage: in parallel

Put the probes **across** the thing you're measuring, black on the reference (usually ground) and red on the point of interest. Nothing gets disconnected.

```diagram
  +5V ──[ R1 ]──┬──[ LED ]── GND
                │
             red probe
   (black probe on GND)
```

- Use **DC volts** (V⎓) for supply rails and logic. AC volts reads an RMS value of the AC part; on most meters it ignores the DC level, so it won't tell you a rail's voltage.
- A digital meter's voltage input is high-impedance, typically around 10 MΩ on DC volts, though some meters and ranges differ (check your meter's specification). It barely loads most circuits, but on a very high-resistance divider the meter itself pulls the reading down. Lesson 2's loading rule applies to meters too.
- A negative reading just means the probes are swapped.

### Current: in series

To measure current, the current has to flow **through** the meter. Break the circuit and insert the meter into the gap:

```diagram
  +5V ──[ R1 ]──  ✂  ──[ LED ]── GND
              red    black
               └─ meter ─┘
```

1. Power off.
2. Move the red lead to the **mA** jack (or the A jack for larger currents) and select the current range.
3. Open the circuit at one point and connect the meter across the gap.
4. Power on and read.
5. **Power off and move the red lead back to VΩ** before your next measurement.

> [!warning] The classic fuse-blower
> In current mode the meter is almost a short circuit, by design. Put it *across* a supply (as you would for voltage) and you short the supply through the meter. The meter's fuse is there to blow in that case. Replace it only with the **exact type and rating** the manual specifies. Forgetting to move the red lead back to VΩ is the commonest way to do this.

Meters also have a **burden voltage**: the small voltage the meter drops while measuring current. On sensitive low-voltage circuits it can slightly change what you're measuring.

### Resistance and continuity: only unpowered

Resistance mode works by passing a small test current from the meter's own battery and measuring the resulting voltage. So:

- **The circuit must be unpowered.** External voltages corrupt the reading and can damage the meter.
- **Measure parts out of circuit, or lift one leg.** In circuit, other paths in parallel lower the reading. Lesson 2's parallel rule explains why.
- **Continuity mode** beeps below a low resistance threshold. Use it to check wires, solder joints, breadboard rails and switch contacts, and to find shorts.
- **Diode test mode** shows a diode's forward voltage (about 0.5–0.7 V for silicon) one way and open circuit the other. It often lights an LED faintly too, which is handy for identifying LED polarity.
- Discharge large capacitors before measuring around them.

### Choosing ranges

Autoranging meters choose for you. On a manual meter:

- **Start on a range above the largest value you expect,** then step down for resolution.
- An "OL" or "1" display means over-range. Go up a range.
- For current, start on the highest range if you're unsure, which on many meters means moving the red lead to the A jack.

## The oscilloscope: seeing voltage over time

A multimeter gives one number: a steady DC value or an RMS summary. An **oscilloscope** draws voltage against time, so you can see what's actually happening:

- the shape of an audio waveform, and whether it clips;
- noise and ripple riding on a supply rail;
- logic or PWM signals and their timing;
- switch bounce lasting a few milliseconds.

Core controls:

- **Vertical (V/div):** volts per grid square.
- **Horizontal (time/div):** seconds per grid square.
- **Trigger:** the condition (a level and a rising or falling edge) that starts each sweep at the same point, so a repeating waveform stands still on screen.
- **Probe ×1/×10:** ×10 probes load the circuit less and extend bandwidth. Set the scope to match the probe.

> [!warning] Probe ground clips
> On a typical mains-powered bench scope, the probe's ground clip is connected to protective earth through the scope. Only ever clip it to your circuit's ground. Clipping it to another point in a circuit that's also earth-referenced creates a short through the probe. A circuit is earth-referenced if anything connected to it ties its ground to earth: a desktop PC's USB port usually does, and so do some laptop adapters with three-pin plugs, while two-pin laptop adapters usually leave the output floating. Don't rely on knowing which. To measure across a component, use two probes (both grounds on circuit ground) and the scope's A − B maths, or a differential probe. Never defeat a scope's safety earth to "float" it. Instrument manuals strongly warn against it.

The project doesn't require owning a scope at first. A multimeter covers the foundation exercises. Consider a scope when you need to debug noise, audio clipping or timing that a meter can't show.

## Soldering

### Safety

- **Fume:** the HSE states that rosin (colophony)-based solder flux fume is "a common cause of occupational asthma". Work in a well-ventilated space and use suitable local fume extraction that captures fume at the source. A desk fan merely moving fume around the room is not equivalent to extraction. Consider rosin-free or reduced-rosin fluxes.
- **Lead:** if you use leaded solder, wash your hands afterwards and don't eat or drink while soldering.
- **Eyes:** wear safety glasses. Flux can spit and clipped leads fly.
- **Burns:** always put the iron back in its stand. Never catch a falling iron. Keep the cable clear.
- **Unpowered:** never solder a circuit while it's powered.

### Leaded or lead-free

| | Leaded (63/37 Sn-Pb) | Lead-free (e.g. Sn-Ag-Cu) |
|---|---|---|
| Melting point | 183 °C (eutectic) | ~217 °C and up |
| Ease | Flows easily, forgiving | Needs more heat, less forgiving |
| Joint look | Shiny | Duller, slightly grainy |
| Health/regulation | Contains lead | Required in most electronics sold in the UK and EU (RoHS) |

Either is fine for hobby work with the precautions above. Many beginners find 63/37 easier. A eutectic alloy melts and solidifies at a single temperature, so it has no pasty phase where movement spoils the joint.

### Temperature

Use a **temperature-controlled** iron. SparkFun's through-hole soldering guide suggests a "good medium heat (325-375 degrees C)" as a starting point. Lead-free usually needs the upper end. If the solder smokes heavily or flux burns off instantly, turn the heat down. If the joint won't flow within a few seconds, a bigger tip often helps more than more heat.

### Technique for a through-hole joint

1. **Clean and tin the tip:** wipe on a damp sponge or brass wool, then melt a little solder on the tip. This helps heat transfer.
2. **Heat both the pad and the lead together** with the side of the tip touching both.
3. **Feed solder into the joint,** not onto the iron. It should flow around the lead and across the pad. Flux in the solder's core cleans oxide so the solder can wet the metal.
4. **Remove the solder, then the iron.** A small joint takes a few seconds in total.
5. **Don't move the joint** until it solidifies.
6. Trim the lead above the joint.

### Inspecting a joint

```diagram
  good:   /‾\      concave cone, wets
         /   \     both pad and lead
  ──────/     \──────

  cold:  ( ● )     ball sitting on pad,
  ──────(     )──  dull, not wetted
```

- **Good:** a smooth, concave "volcano" fillet that wets both the pad and the lead. Shiny with leaded solder, somewhat duller with lead-free.
- **Cold joint:** dull, grainy or lumpy, often balled up. Either the pad or the lead wasn't hot enough. Reheat with a little fresh flux.
- **Bridge:** solder joining adjacent pads. Remove it with desoldering braid or by dragging a clean tip.
- **Insufficient:** the hole isn't filled or the pad isn't covered.
- **Overheated:** burnt flux, discoloured board, or a **lifted pad** (the copper peeling off). Use less time and the right tip.

Finally, test each joint with **continuity mode** and look for bridges under a magnifier.

## Common mistakes

- Measuring voltage with the red lead still in the current jack (blown fuse, or a short).
- Measuring resistance on a powered circuit.
- Forgetting the meter's own loading on high-impedance nodes.
- Clipping a scope's ground lead to a non-ground point.
- Heating only the lead or only the pad, giving a cold joint.
- Carrying solder to the joint on the iron tip, where the flux burns off before it reaches the joint.
- Soldering polarised parts in backwards. Check before you solder; desoldering is harder.
- Soldering without ventilation.

## Key takeaways

- Voltage: in parallel. Current: in series, with the red lead in the fused current jack, and move it back afterwards.
- Resistance, continuity and diode test only on unpowered circuits, ideally out of circuit.
- Start on a high range and step down. Replace fuses only with the specified type.
- A scope shows voltage against time. Its ground clip is usually earthed, so clip it only to circuit ground.
- Solder with a temperature-controlled iron (about 325–375 °C to start), ventilation, eye protection, and hand-washing for leaded solder.
- Heat pad and lead together, feed solder to the joint, and look for a concave, wetted fillet.

## Further reading

- [How to use a multimeter (SparkFun)](https://learn.sparkfun.com/tutorials/how-to-use-a-multimeter/all)
- [Multimeter: input impedance and burden voltage (Wikipedia)](https://en.wikipedia.org/wiki/Multimeter)
- [How to measure current (Fluke)](https://www.fluke.com/en-gb/learn/blog/digital-multimeters/how-to-measure-current)
- [Oscilloscope (Wikipedia)](https://en.wikipedia.org/wiki/Oscilloscope)
- [Adafruit guide to excellent soldering](https://learn.adafruit.com/adafruit-guide-excellent-soldering)
- [How to solder: through-hole soldering (SparkFun)](https://learn.sparkfun.com/tutorials/how-to-solder-through-hole-soldering/all)
- [Controlling health risks from rosin-based solder flux fume, INDG249 (HSE)](https://www.hse.gov.uk/pubns/indg249.pdf)
- [Solder: alloys and melting points (Wikipedia)](https://en.wikipedia.org/wiki/Solder)
