---
id: syn-oscillators-integer-phase
title: Integer phase and table indexing
level: basic
minutes: 4
summary: Integer phase and table indexing.
sourceLesson: syn-oscillators
---

The preserved C fragment below is a DDS implementation example, not a C lesson. Assume valid positive sample rate, a non-negative frequency below Nyquist, finite arithmetic, an unsigned 32-bit phase, and between one and 31 table-index bits. The shift chooses the sample *after* the phase advance; that is a consistent one-step phase offset if used throughout.

## Integer phase accumulators

Hardware and many embedded libraries use an unsigned 32-bit integer for phase, where the full range 0 to 2³² − 1 represents one cycle. Storing an unsigned addition back into that 32-bit type wraps it automatically. The increment is still rounded to a finite frequency grid. The high phase bits choose the table entry; the remaining bits track progress between entries:

```formula reference
N_inc = round((f 2^{32}) / f_s)
P_next = (P + N_inc) mod 2^{32}
i = floor(P_next / 2^{(32 − b)})
where
N_inc: the phase increment, as a whole number of counts per sample
P: the phase, a whole number from 0 to 2^{32} − 1 (4,294,967,295) standing for 0 up to just under one cycle
P_next: the phase on the next sample
f: the frequency wanted, in hertz (Hz)
f_s: the sample rate, in Hz
2^{32}: 4,294,967,296, the number of different values a 32-bit unsigned integer can hold
round: rounds to the nearest whole number
mod: modulo, the remainder after dividing; "mod 2^{32}" is the wrap, which a 32-bit unsigned integer does by itself when it overflows
i: the index into a wavetable (a lookup table of one cycle) that has 2^{b} entries
b: the number of index bits; a 2,048-entry table has b = 11
floor: rounds down to a whole number; dividing by 2^{(32 − b)} and rounding down keeps only the top b bits of P_next
In words: scale the frequency from cycles into counts; adding that each sample lets the register overflow to wrap, and the top bits of the phase choose the table entry.
```

For 1000 Hz at 48 kHz the rounded increment is 89,478,485 counts per sample. In C, using the shift operator `>>` to keep the top bits:

```c
uint32_t inc = (uint32_t)llround(
    f * 4294967296.0 / fs);
phase += inc;        /* wraps at 2^32 */
uint32_t index = phase >> (32 - BITS);
```

The frequency resolution is the frequency that one count of increment represents. At 48 kHz, changing the increment by one count changes the frequency by about 0.000011 Hz. That fine frequency grid is separate from the table resolution: using more phase bits does not create more stored waveform samples.

This is the **numerically controlled oscillator** at the heart of direct digital synthesis (DDS) chips, and the PJRC Teensy Audio Library's waveform object uses a `uint32_t` phase accumulator in the same way (source checked 2026-10-04).

## Key takeaways

- Unsigned integer phase wraps modulo its range.
- The high phase bits select a wavetable entry; frequency quantisation is set by one increment count.

## Further reading

- [Waveform implementation — PJRC](https://raw.githubusercontent.com/PaulStoffregen/Audio/3039be2773e86daf1f381a1e8bdc1e6a55ed11f1/synth_waveform.cpp)
- [C11 committee draft — WG14](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
