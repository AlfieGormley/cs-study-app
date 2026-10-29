---
id: elec-rc-cutoff
sourceLesson: elec-components
title: "The RC low-pass cutoff"
level: intermediate
minutes: 2
summary: "More RC smoothing means a slower response."
---

An RC low-pass filter smooths changes. A resistor feeds a node with a capacitor to ground, and the output is taken across the capacitor. Slow variations appear largely at the output; rapid variations are reduced because changing the capacitor voltage quickly requires more current.

## Smoothing trades noise for response speed
A knob with unwanted voltage fluctuation can become steadier after RC filtering, but it also takes longer to respond to deliberate movement. Increasing either resistance or capacitance makes the filter slower and lowers its cutoff. Filtering a switch can help with bounce, but the receiver’s threshold and allowed input transition time still matter.

The cutoff is a reference point on a gradual response, not a brick wall. For the ideal unloaded first-order circuit, a sinusoid at cutoff has about 71% of its input amplitude, or −3 dB. Frequencies above it are progressively reduced.

```formula reference
f_c = 1 / (2πRC)
where
f_c: cutoff frequency, in hertz (Hz)
π: pi, approximately 3.14159
R: resistance, in ohms (Ω)
C: capacitance, in farads (F)
In words: Increasing the resistance or capacitance lowers the cutoff, giving more smoothing but a slower response. This formula assumes the ideal output is effectively unloaded.
```

For example, 10 kΩ with 100 nF gives about 159 Hz cutoff. This is a model result, not a measured filter specification. Source resistance, output loading and real component tolerances change the response. A load across the capacitor can change both the low-frequency gain and the cutoff.

## Key takeaways

- More smoothing also slows deliberate changes.
- Cutoff marks gradual attenuation, not an abrupt stop.
- Check loading, input transition and ADC acquisition requirements before relying on the ideal RC model.

## Further reading

- [TI Precision Labs: passive RC response](https://www.ti.com.cn/content/dam/videos/external-videos/zh-cn/4/3816841626001/6119035031001.mp4/subassets/passive_components_and_circuits_2.pdf)
- [OpenStax: ideal RC circuits](https://openstax.org/books/university-physics-volume-2/pages/10-5-rc-circuits)
- [SparkFun: voltage dividers](https://learn.sparkfun.com/tutorials/voltage-dividers/all)
