---
id: esc-adc-samples
title: Interpret an ADC sample carefully
level: basic
minutes: 4
summary: Distinguish an ideal quantised code from the accuracy of a physical voltage measurement.
---

An **analogue-to-digital converter** (ADC) turns an analogue input into a finite integer code. Software must know the selected channel, conversion configuration, result's bit layout and reference before interpreting that code. A valid numeric result does not itself prove the sensor wiring or measurement is correct.

## Resolution describes available codes

For an illustrative ideal unipolar converter, divide the reference span into equally wide bins. Assume the input lies from zero up to the reference, with the upper endpoint excluded, and use a floor-quantiser model. The real ADC transfer function may position transitions differently; use its datasheet for an actual design.

A 12-bit result has 4096 possible codes, numbered 0 through 4095. With an assumed reference span of exactly 3.3 volts, each ideal bin is about 0.806 millivolts wide. More bits make the bins finer for the same span; they do not guarantee a more accurate physical measurement.

The number of codes and the highest code are different. Dividing the reference span by the highest code makes an endpoint-normalised display scale; it is not automatically the converter's physical voltage interval.

> [!analogy] Real-world analogy: reading a ruler with finite marks
> A ruler gives you a finite spacing between marks. Adding more marks can make the reading more detailed, but it does not fix a ruler that was printed at the wrong scale.
>
> **How it maps:** The ADC's code spacing describes resolution. Reference error, converter error and the rest of the measurement circuit affect accuracy separately.
>
> **Where it stops:** An ADC also has noise, timing and an input circuit. More displayed digits do not remove these effects or prove that a sensor voltage has settled before sampling.

## Interpret a code under explicit assumptions

Under this model, code 2048 starts the bin halfway through the reference span, at 1.65 volts. The input could lie elsewhere inside that bin: the code identifies an interval, not a unique exact voltage. Reference error and converter error add further uncertainty on real hardware.

If the reference span increases while the code stays the same, its estimated voltage increases too. The same integer therefore need not mean the same voltage on two differently configured converters.

The relationships below are useful when implementing a conversion. They describe the stated ideal model, not an accuracy promise:

```formula reference
N = 2^b
ΔV = V_ref / N
V_low = k V_ref / N
where
N: the number of possible output codes, a unitless count
b: the resolution in bits
ΔV: the width of an ideal voltage bin, in volts
V_ref: the reference span, in volts
V_low: the lower edge of the returned code's ideal bin, in volts
k: the returned integer code, from zero through one less than the number of codes
In words: more code bits divide the same voltage span into finer bins. A code selects a bin along that span; changing the reference changes the voltage assigned to that same code.
```

On hardware, check the input's permitted range, source impedance and acquisition requirements before connecting a known low-voltage signal. Do not assume a digital-tolerant pin has the same permitted analogue range. A reference may differ from its nominal value, and averaging cannot remove a fixed scale error. RP2040 is a concrete example whose advertised code width and measured effective resolution differ; this does not make its numbers universal for other devices.

## Key takeaways
- Code count, highest code and real measurement accuracy are different quantities.
- State the reference and converter model behind any voltage estimate.
- Use the actual analogue input and settling requirements before wiring or sampling.

## Further reading
- [Raspberry Pi SDK: ADC operation and effective resolution](https://raw.githubusercontent.com/raspberrypi/pico-sdk/2.2.0/src/rp2_common/hardware_adc/include/hardware/adc.h)
- [RP2040 datasheet: ADC transfer behaviour and electrical limits](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
