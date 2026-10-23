---
id: esc-adc-samples
title: Interpret an ADC sample carefully
level: basic
minutes: 5
summary: Distinguish an ideal quantised code from the accuracy of a physical voltage measurement.
---

An **analogue-to-digital converter** (ADC) turns an analogue input into a finite integer code. Software must know the selected channel, conversion configuration, result's bit layout and reference before interpreting that code. A valid numeric result does not itself prove the sensor wiring or measurement is correct.

## Resolution describes available codes

For an illustrative ideal unipolar converter, divide the reference span into equally wide bins. Assume the input lies from zero up to the reference, with the upper endpoint excluded, and use a floor-quantiser model. The real ADC transfer function may position transitions differently; use its datasheet for an actual design.

```formula
N = 2^b
ΔV = V_ref / N
N = 2^12 = 4096
ΔV = 3.3 V / 4096 ≈ 0.806 mV
where
N: the number of possible output codes; 4096 in this ideal example
b: the resolution in bits; 12 here
ΔV: the width of one ideal voltage bin, in volts (V) or millivolts (mV)
V_ref: the reference span, assumed to be exactly 3.3 volts for this calculation
V: volt, the unit of electrical potential difference
mV: millivolt, one thousandth of a volt
≈: approximately equal to; the displayed bin width is rounded
In words: twelve bits provide 4096 codes, so this assumed 3.3 volt span is divided into bins about 0.806 millivolts wide.
```

The codes run from 0 through 4095. Their count is 4096. These are different numbers: using the maximum code as the divisor is an endpoint-normalisation choice, not automatically the converter's physical code width.

> [!analogy] Real-world analogy: reading a ruler with finite marks
> A ruler gives you a finite spacing between marks. Adding more marks can make the reading more detailed, but it does not fix a ruler that was printed at the wrong scale.
>
> **How it maps:** The ADC's code spacing describes resolution. Reference error, converter error and the rest of the measurement circuit affect accuracy separately.
>
> **Where it stops:** An ADC also has noise, timing and an input circuit. More displayed digits do not remove these effects or prove that a sensor voltage has settled before sampling.

## Interpret a code under explicit assumptions

For our ideal bins, a lower-edge estimate is:

```formula
V_low = k V_ref / N
V_low = 2048 × 3.3 V / 4096
V_low = 1.65 V
where
V_low: the lower edge of the code's ideal voltage bin, in volts (V), not a guaranteed physical input value
k: the returned integer code; 2048 in this example
V_ref: the assumed reference span; 3.3 volts here
N: the number of ideal codes; 4096 here
V: volt, the unit of potential difference
In words: code 2048 starts the bin at 1.65 volts in this chosen ideal model; the input can be elsewhere inside the bin.
```

This complete C11 host program computes that estimate. The cast `(double)` chooses floating-point calculation; it is not an ADC operation or a recommendation about execution cost on a particular MCU.

```c
#include <stdint.h>
#include <stdio.h>

int main(void) {
    uint16_t code = 2048u;
    double v = (double)code * 3.3 / 4096.0;
    printf("%.3f\n", v); // prints 1.650
    return 0;
}
```

On hardware, check the input's permitted range, source impedance and acquisition requirements before connecting a known low-voltage signal. Do not assume a digital-tolerant pin has the same permitted analogue range. A reference may differ from its nominal value, and averaging cannot remove a fixed scale error. RP2040 is a concrete example whose advertised code width and measured effective resolution differ; this does not make its numbers universal for other devices.

## Key takeaways
- Code count, highest code and real measurement accuracy are different quantities.
- State the reference and converter model behind any voltage estimate.
- Use the actual analogue input and settling requirements before wiring or sampling.

## Further reading
- [Raspberry Pi SDK: ADC operation and effective resolution](https://raw.githubusercontent.com/raspberrypi/pico-sdk/2.2.0/src/rp2_common/hardware_adc/include/hardware/adc.h)
- [RP2040 datasheet: ADC transfer behaviour and electrical limits](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
