---
id: syn-envelopes-adsr-machine
title: An exponential ADSR state machine
level: intermediate
minutes: 5
summary: An exponential ADSR state machine.
sourceLesson: syn-envelopes
---

This standalone offline state-machine experiment uses positive attack, decay and release time constants, a sustain level between zero and one, and a fixed sample rate. Its “decay” stage asymptotically holds sustain instead of switching to a separate sustain state; gate-off from any stage starts release. A second gate-on attacks from the current level.

```python
import math

def coef(tau, fs):
    return 1.0 - math.exp(-1.0 / (tau * fs))

class ExpADSR:
    """a, d, r are time constants (s)."""
    def __init__(self, fs, a, d, s, r):
        self.ca = coef(a, fs)
        self.cd = coef(d, fs)
        self.cr = coef(r, fs)
        self.s = s
        self.stage, self.y = "idle", 0.0

    def _toward(self, c, target):
        # Move a fraction of the remaining
        # gap.
        self.y += c * (target - self.y)

    def gate(self, on):
        if on:
            self.stage = "attack"
        else:
            # Release starts from any
            # current level.
            self.stage = "release"

    def next(self):
        st = self.stage
        if st == "attack":
            # aim past 1.0 so we arrive
            self._toward(self.ca, 1.2)
            if self.y >= 1.0:
                self.y = 1.0
                self.stage = "decay"
        # Decay asymptotically holds
        # sustain.
        elif st == "decay":
            self._toward(self.cd, self.s)
        elif st == "release":
            self._toward(self.cr, 0.0)
            if self.y < 1e-5:      # -100 dB
                self.y = 0.0
                self.stage = "idle"
        return self.y

fs = 48000
env = ExpADSR(fs, a=0.005, d=0.1,
              s=0.6, r=0.2)
env.gate(True)
n = 0
while env.stage == "attack":
    env.next()
    n += 1
print("attack ms:", round(n / fs * 1000, 2))
for _ in range(fs):                # 1 s
    env.next()
print("level:", round(env.y, 4))
env.gate(False)
n = 0
while env.stage != "idle":
    env.next()
    n += 1
print("release ms:", round(n / fs * 1000))
```

```
attack ms: 8.98
level: 0.6
release ms: 2200
```

Notice the numbers. Both follow from one rule: the time an exponential segment takes depends only on how many times smaller the remaining distance must get.

```formula
t = τ ln(d_start / d_end)
t_a = 5 ms × ln(1.2 / 0.2) = 5 ms × ln(6)
t_a ≈ 5 ms × 1.79 ≈ 9 ms
t_r = 0.2 s × ln(0.6 / 0.00001)
t_r ≈ 0.2 s × 11.0 ≈ 2.2 s
where
t: the time the segment takes, in seconds (s) or milliseconds (ms)
τ: tau, the segment's time constant
ln: the natural logarithm (inverse of the exponential function)
d_start: the distance to the target when the segment starts
d_end: the distance to the target when the segment stops
t_a: the attack time: aiming at 1.2 from 0, the distance shrinks from 1.2 to 0.2 when the level reaches 1.0
t_r: the release time: aiming at 0 from 0.6, it stops at the 0.00001 (−100 dB) threshold
ms: milliseconds, thousandths of a second
s: seconds
≈: approximately equal to
In words: the time depends on the ratio of the start and end distances, not on their size, so a release that must fall a long way in decibels lasts many time constants.
```

So with a 5 ms time constant and a 1.2 target, the attack takes about 9 ms, and a 200 ms release time constant takes 2.2 s to fall from 0.6 to −100 dB. **"Release = 200 ms" is ambiguous** unless you say what it means: time constant, time to −60 dB, or time to silence. Pick a definition, document it, and convert the knob value to a coefficient accordingly.

## Key takeaways

- Overshoot the attack target so the peak is reached in finite time.
- Stop release at a documented small threshold and mark the voice idle.
- The demonstrated control times are time constants, not complete stage durations.

## Further reading

- [ADSR implementation — Nigel Redmon](https://www.earlevel.com/main/2013/06/03/envelope-generators-adsr-code/)
- [Time constant of one pole — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/Time_Constant_One_Pole.html)
