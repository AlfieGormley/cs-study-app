---
id: snd-dither-converter-noise
title: Dither and converter noise floors
level: intermediate
minutes: 3
summary: Explain why reducing bit depth needs dither and why a converter’s word length exceeds its effective resolution.
sourceLesson: snd-sampling
---

## Dither and real converter noise

The same problem returns for **very quiet signals**, even at 16 bits. A sine whose amplitude is under half a step rounds to zero every time and vanishes completely. A fade-out turns gritty in its last few bits.

**Dither** addresses this by adding a tiny amount of random noise *before* quantising. Common triangular (TPDF) dither spans two quantisation steps peak-to-peak. With suitable dither and no overload, the output error’s mean and noise power no longer vary with the signal: you trade extra hiss for removal of systematic quantisation distortion, and quiet details survive statistically inside the noise. This does not mean every property of the total error is independent of the signal. Dither matters whenever you **reduce** bit depth, such as when exporting 16-bit files. Inside a 32-bit float synth it's rarely needed.

### Real converters

A "24-bit" converter outputs 24-bit words, but its analogue noise floor is far above the theoretical 146 dB. Examples from TI’s datasheets are 99 dB typical for the PCM1808 ADC and 112 dB typical for the PCM5102A DAC. These are A-weighted figures under the stated test conditions. The higher-performance PCM1792A specifies 127 dB with a 2 V RMS stereo test output and 132 dB in its mono test configuration. These are different configurations, not a guaranteed range for any board. Board circuitry and power supplies affect the result, so check the datasheet and measure. 24 bits gives a comfortable margin so that converter noise, not quantisation, sets the floor.

A noise-only estimate of effective resolution can be obtained by rearranging the full-scale-sine SQNR rule from the preceding unit. Formal ENOB measurements normally use SINAD, which includes distortion as well as noise; substituting an A-weighted dynamic-range figure gives only an estimate.

## Key takeaways

- Dither adds noise before quantisation to decorrelate error from quiet signals.
- Use dither when reducing bit depth; continuous float processing usually does not need it.
- A 24-bit converter’s analogue noise floor is higher than ideal 24-bit quantisation noise. Check and measure the hardware.

## Further reading

- [Dither — Wikipedia](https://en.wikipedia.org/wiki/Dither)
- [Taking The Mystery Out of the Infamous Formula "SNR = 6.02N + 1.76dB" — Analog Devices MT-001](https://www.analog.com/media/en/training-seminars/tutorials/MT-001.pdf)
- [PCM5102A audio DAC datasheet — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm5102a.pdf)
- [PCM1808 ADC datasheet — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm1808.pdf)
- [PCM1792A DAC datasheet — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm1792a.pdf)
- [SINAD, SNR and ENOB — Analog Devices MT-003](https://www.analog.com/media/en/training-seminars/tutorials/MT-003.pdf)
