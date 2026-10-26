---
id: snd-alias-frequency-folding
title: Predict where aliases fold
level: intermediate
minutes: 4
summary: Wrap a component by the sample rate, reflect it below Nyquist and trace rising-frequency sweeps.
sourceLesson: snd-aliasing
---

## Following an alias frequency

Picture the frequency axis folded back and forth like a paper fan, with creases at every multiple of the Nyquist frequency (fs/2 in the drawing, where fs is the sample rate):

```diagram
 0      fs/2      fs      3fs/2
 |--------|--------|--------|
 0 ----> 24k
         24k <---- 48k
                  48k ----> 72k
```

Any frequency maps to the point directly below it on the first segment, from 0 up to the Nyquist frequency. As a procedure:

1. Divide the frequency by the sample rate and keep the remainder (this is "modulo"), giving a value from 0 up to the sample rate.
2. If the result is above the Nyquist frequency, subtract it from the sample rate.

This reference rule implements that procedure. It predicts the folded frequency; phase still affects the signed waveform and special fold-point samples.

```formula reference
r = f mod fs
f_a = min(r, fs − r)
where
f: the true frequency being sampled, in hertz (Hz); here 30 kHz
fs: the sample rate, in hertz (Hz); here 48 kHz
mod: "modulo": the remainder after removing as many whole multiples of fs as possible (50,000 mod 48,000 is 2,000)
r: the frequency after wrapping into the range 0 up to fs
min: the smaller of the two values
f_a: the alias, the frequency that actually appears after sampling, between 0 and fs/2, in hertz (Hz)
Hz: hertz, cycles per second
In words: wrap the frequency into one sample-rate's width, then, if it lands in the top half, reflect it down off the Nyquist frequency. 30 kHz sampled at 48 kHz appears at 18 kHz.
```

The formula holds for any frequency, sine by sine. A complex sound is a sum of sines, so apply it to each component separately.

```python
def alias(f, fs):
    f = f % fs          # wrap into [0, fs)
    # Reflect the upper half below Nyquist.
    return fs - f if f > fs / 2 else f

fs = 48_000
for f in (1_000, 23_000, 30_000, 47_000,
          50_000, 97_000):
    a = alias(f, fs)
    print(f"{f:>6} Hz -> {a:>6} Hz")
```

```text
  1000 Hz ->   1000 Hz
 23000 Hz ->  23000 Hz
 30000 Hz ->  18000 Hz
 47000 Hz ->   1000 Hz
 50000 Hz ->   2000 Hz
 97000 Hz ->   1000 Hz
```

The examples show that a very high input can appear near the bottom of the audio band. Removing whole sample-rate multiples first handles frequencies beyond the first fold.

Notice the behaviour as an input sweeps upwards: the alias rises to 24 kHz, then **falls** to 0 at 48 kHz, then rises again. A rising pitch whose alias falls is the unmistakable sound of aliasing.

## Key takeaways

- Take the frequency’s remainder after division by the sample rate.
- Reflect remainders above half the sample rate back into the lower half.
- Compute complex sounds component by component; aliases reverse direction at fold points.

## Further reading

- [Sampling Theorem — Julius O. Smith, Mathematics of the DFT (CCRMA)](https://ccrma.stanford.edu/~jos/mdft/Sampling_Theorem.html)
- [Aliasing — Wikipedia](https://en.wikipedia.org/wiki/Aliasing)
