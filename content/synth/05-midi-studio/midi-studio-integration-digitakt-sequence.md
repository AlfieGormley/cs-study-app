---
id: midi-studio-integration-digitakt-sequence
title: Prove the Digitakt MIDI track path
level: advanced
minutes: 3
sourceLesson: midi-studio-integration
summary: Check port function, output route, track channel and note length before treating silence or a held note as a firmware fault.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Step 2: sequence the synth from a Digitakt MIDI track

Both manuals give the same procedure (section "Controlling a synthesizer using the MIDI tracks"):

1. Connect Digitakt **MIDI OUT** to the synth's **MIDI IN** with a standard MIDI cable.
2. In SETTINGS > MIDI CONFIG > PORT CONFIG, set **OUT PORT FUNC to MIDI** (not DIN 24/48 sync).
3. In the same menu, set **OUTPUT TO** to **MIDI** (or MIDI+USB).
4. Select a MIDI track. On the original Digitakt these are tracks 9–16. On the Digitakt II, first assign the **MIDI machine** to a track (FUNC + SRC opens the machine menu).
5. Press SRC and set **CHAN** to the channel your synth listens on (OFF or 1–16).
6. Set the synth to receive on that channel.

Then program notes as on any track. Things your synth will see:

- **Note on/off** with the trig's note, VEL and LEN. LEN decides when the note off is sent; the original Digitakt manual lists an **INF** (infinite note length) setting, so a note can be held indefinitely by design. Check LEN before blaming your firmware for a stuck note.
- **Chords**: a MIDI trig can send up to four notes (NOT2–NOT4). A mono synth will apply its note priority to them, so keep chords off unless you want that effect.
- **Pitch bend, aftertouch, mod wheel, breath** (PB, AT, MW, BC on the SRC page) and **assignable CCs**, whose values and CC numbers are set on the Digitakt FLTR page and Digitakt AMP page (the layout differs between the two models; see your manual). They're OFF by default; enable each one, then pick its CC number to match the CC map implemented by your synth, introduced in **Choose and decode control changes**. Parameter locks and LFOs can then automate your synth's parameters.
- **Bank and program change** (BANK, SBNK, PROG) if your synth supports presets.
- **Clock and transport**, if CLOCK SEND / TRANSPORT SEND are enabled in MIDI CONFIG > SYNC. Your parser must tolerate the `F8` stream.

> [!tip] Prove the MIDI path in isolation first
> Before wiring the synth, send the Digitakt's MIDI to the computer (USB MIDI) or through a USB MIDI interface into a MIDI monitor, and check the bytes match what you expect: channel nibble, note numbers, velocity-0 or 8n note offs, CC numbers. Then connect the synth.

## Key takeaways
- Check port function, output route, track channel and note length before treating silence or a held note as a firmware fault.

## Further reading
- [Digitakt II user manual (OS 1.17) — Elektron](https://www.elektron.se/wp-content/uploads/2026/10/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf)
- [Digitakt user manual (OS 1.53) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
- [Digitakt II support and downloads — Elektron](https://www.elektron.se/support-downloads/digitakt-ii)
- [Live 12 manual: Routing and I/O (monitoring, external instruments) — Ableton](https://www.ableton.com/en/live-manual/12/routing-and-i-o/)
- [Live 12 manual: External Instrument device — Ableton](https://www.ableton.com/en/live-manual/12/live-instrument-reference/)
- [Live 12 manual: Synchronizing with Link, Tempo Follower and MIDI — Ableton](https://www.ableton.com/en/live-manual/12/synchronizing-with-link-tempo-follower-and-midi/)
- [Ground loop (electricity) — Wikipedia](https://en.wikipedia.org/wiki/Ground_loop_(electricity))
