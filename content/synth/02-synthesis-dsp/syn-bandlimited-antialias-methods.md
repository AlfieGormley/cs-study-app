---
id: syn-bandlimited-antialias-methods
title: Oversampling, BLIT and BLEP methods
level: intermediate
minutes: 3
summary: Oversampling, BLIT and BLEP methods.
sourceLesson: syn-bandlimited
---

### 3. Oversampling

Run the naive oscillator at a multiple of the sample rate (say 4× or 8×), low-pass filter, then discard samples (decimate). The higher sample rate moves the folding boundary upwards. The low-pass filter removes content above the final Nyquist before decimation, but aliases that already folded into the wanted band survive; oversampling a discontinuous naive waveform does not guarantee zero aliasing. Simple to reason about, costly in CPU, and the decimation filter must be good.

### 4. BLIT: band-limited impulse train

Stilson and Smith (CCRMA, 1996) generate a band-limited train of impulses using a closed-form formula, then **integrate** it to get a saw (or integrate a bipolar impulse train for a square). It's elegant and accurate, though the integrators need care to avoid DC drift.

### 5. BLEP and PolyBLEP: correct the jumps

Insight: a saw is smooth everywhere *except* at its jump. Aliasing comes from the jumps. So generate the naive wave, then **add a correction** around each discontinuity that approximates a suitably low-pass-smoothed step. Ideal band-limited steps have infinite support; practical finite corrections leave some residual aliasing.

- **minBLEP** (Eli Brandt, 2001) precomputes a band-limited step, makes it minimum-phase, and stores the difference from an ideal step in a table. At each jump, the oscillator adds the table, aligned to the jump's exact fractional position.
- **PolyBLEP** (Välimäki and Huovilainen, 2007) replaces the table with a tiny polynomial that only touches two samples: the one just before the jump and the one just after it. It is cheap and needs no correction lookup table, at the cost of weaker suppression than a long table.

```diagram
naive saw          PolyBLEP saw
    /|  /|             /\  /\
   / | / |            /  \/  \
  /  |/  |           /        \
 jump: 1 sample      jump spread over
 (aliases)           ~2 samples
```

## Key takeaways

- Oversampling requires filtering before decimation.
- BLIT integrates a band-limited impulse train; BLEP methods correct discontinuities.
- Finite tables and short polynomial corrections reduce rather than guarantee zero aliasing.

## Further reading

- [Alias-free classic waveforms — Stilson and Smith](https://ccrma.stanford.edu/~stilti/papers/blit.pdf)
- [Hard sync without aliasing — Eli Brandt](https://www.cs.cmu.edu/~eli/papers/icmc01-hardsync.pdf)
- [Antialiasing oscillators — Välimäki and Huovilainen](https://research.aalto.fi/en/publications/antialiasing-oscillators-in-subtractive-synthesis/)
