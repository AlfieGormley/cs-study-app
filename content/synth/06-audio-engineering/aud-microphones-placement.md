---
id: aud-microphones-placement
title: Control leakage and comb filtering
level: intermediate
minutes: 4
summary: Distance changes direct-to-room balance and leakage.
sourceLesson: aud-microphones
---

## Placement basics

- **Distance controls the direct-to-room balance.** Close placement gives more direct sound, less room, more proximity effect and more level variation as the performer moves. Further away captures more of the room.
- **Angle controls tone.** On a guitar cab, the centre of the cone is brighter; towards the edge it's darker. Small moves matter.
- Use **acoustic nulls**. Aim the null of a directional mic at what you *don't* want (a monitor, a neighbouring drum).
- Mind **sound reflections**. A music stand or desk near the mic adds a reflection a few milliseconds late, which comb-filters the sound.

### The 3:1 rule

When several mics are open at once, a source reaches its own mic and, more weakly and later, its neighbours. When the signals are mixed, the delayed copy comb-filters the direct one. The **3:1 rule** says the distance *between* mics should be at least **three times** the distance from each mic to its source.

Why it works: by the inverse square law, sound pressure falls in proportion to distance. A neighbouring mic three times further away picks up the source about **9.5 dB** quieter than its own mic does (assuming similar pickup and channel gains).

```formula reference
L_leak = 20 log_10(d_far / d_near)
where
L_leak: how far the leaked copy is below the direct sound, in decibels (dB)
d_far: the distance from the source to the neighbouring mic, in metres (m)
d_near: the distance from the source to its own mic, in metres (m)
log_10: the base-10 logarithm; 20 × log_10 because pressure is an amplitude
dB: decibel
m: metre
In words: The leaked copy is quieter than the direct sound by 20 times the logarithm of how many times further away the neighbouring mic is; three times further gives about 9.5 dB.
```

A copy that much quieter cannot cancel or double the direct sound. Mixed in, it can only nudge the sum: the comb filter's peaks are about +2.5 dB and its notches about −3.5 dB, instead of the +6 dB peaks and deep notches of two equal copies. The comb is still there, but shallow enough that it is rarely objectionable. The quieter the leak, the shallower the comb.

```diagram
  src A      src B
   |          |
  0.3 m      0.3 m
   |          |
  mic A ---- mic B
     >= 0.9 m apart
```

It's a rule of thumb that assumes omni-like pickup and similar levels. Directional mics aimed well, or very different source levels, change the numbers.

## Key takeaways
- Distance changes direct-to-room balance and leakage.
- The three-to-one spacing rule is a practical starting estimate.
- Leakage ripple also depends on source geometry, microphone response and channel gains.

## Further reading
- [Microphone technology — DPA](https://www.dpamicrophones.com/mic-university/technology/microphone-technology-the-essentials/)
- [U 87 Ai technical data — Neumann](https://www.neumann.com/en-en/products/microphones/u-87-ai/)
- [Phantom power — Schoeps](https://schoeps.de/en/knowledge/knowledge-base/technical-basics/phantom-power-p48p12.html)
- [Three-to-one rule — DPA](https://www.dpamicrophones.com/dict/3-1-rule/)
