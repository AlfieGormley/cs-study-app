---
id: syn-synthesis-overview-tables-models
title: Stored sound and physical models
level: basic
minutes: 3
summary: Stored sound and physical models.
sourceLesson: syn-synthesis-overview
---

### Wavetable

Store a set of single-cycle waveforms (a **wavetable**) and play one back with a phase accumulator, optionally sweeping or crossfading through the set to make the timbre evolve. The historical examples distinguish table lookup from later timbre-scanning systems. Hal Chamberlin’s September 1977 BYTE article describes accessing a stored cycle with a fractional table pointer. Julius O. Smith discusses Michael McNabb’s spectral-table interpolation in Dreamsong, while Wolfgang Palm’s PPG instruments made evolving stored-wave sounds a commercial approach in the late 1970s. Waldorf continued that lineage with the Microwave in 1989. These are examples of development, not a claim that any one person invented all table-lookup synthesis. Each table is cheap to play, but high notes alias unless you keep band-limited versions of each table (covered in the neighbouring synthesis units).

### Sample-based

Play back recordings of real sounds, re-pitched by reading them faster or slower, then shape them with envelopes and filters. Recordings can reproduce detailed source sounds, but storage and expressive coverage depend on the recordings, playback method and processing. Elektron’s Digitakt II is a manufacturer-described stereo sampler (product page checked 2026-10-16). The project names a Digitakt without confirming its model, so identify the actual instrument before applying model-specific connection or format advice.

### Physical modelling

Simulate the physics of a string, tube or membrane. The classic small example is **Karplus–Strong**: fill a short delay line with noise and feed it back through a gentle low-pass filter. The loop's length sets the pitch, and the filter makes high harmonics die first, like a plucked string. The total delay around the loop is roughly one period of the note.

A shorter loop repeats sooner and gives a higher pitch. The filter also delays the signal, so accurate tuning must include its delay; a fractional-delay adjustment can fill the gaps between whole-sample lengths.

So a 220 Hz string at 48 kHz needs a loop of about 218 samples, and a note an octave up (440 Hz) needs about 109. Julius O. Smith's *Physical Audio Signal Processing* covers this family in depth.

> [!tip] A reasonable first instrument
> Subtractive is the usual first build because each block (oscillator, filter, amplifier, envelope, LFO) can be built and tested on its own. The project brief suggests a monophonic digital subtractive synth as an option; this module teaches every block it would need without committing you to it.

## Key takeaways

- Wavetables store cycles; sample playback uses recordings.
- A Karplus–Strong loop needs roughly one period of delay, with filter delay included for accurate tuning.

## Further reading

- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
- [Karplus–Strong — Julius O. Smith](https://ccrma.stanford.edu/~jos/pasp/Karplus_Strong_Algorithm.html)
- [Digitakt II product description — Elektron](https://www.elektron.se/explore/digitakt)
- [Table lookup in BYTE, September 1977 — Hal Chamberlin](https://www.vintageapple.org/byte/pdf/197709_Byte_Magazine_Vol_02-09_Music_and_Computers.pdf)
- [Digital synthesis taxonomy — Julius O. Smith](https://ccrma.stanford.edu/~jos/kna/Taxonomy_Digital_Synthesis_Techniques.html)
- [PPG history — PPG](https://www.ppgsynth.com/1002/ppg)
- [Microwave history — Waldorf](https://waldorfmusic.com/about-us/)
