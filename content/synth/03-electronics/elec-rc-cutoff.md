---
id: elec-rc-cutoff
sourceLesson: elec-components
title: "The RC low-pass cutoff"
level: intermediate
minutes: 1
summary: "An unloaded RC low-pass has its cutoff at one over two pi times RC."
---

An unloaded RC low-pass has its cutoff at one over two pi times RC.

## An RC low-pass filter

RC circuits show up across synth hardware. They smooth a noisy knob and slow a bouncing switch. A resistor followed by a capacitor to ground is also the simplest low-pass filter (an RC low-pass filter): it passes slow changes and shorts fast ones to ground. Its cut-off frequency is:

```formula
f_c = 1 / (2πRC)
f_c = 1 / (2π × 10,000 Ω × 100 nF)
f_c ≈ 159 Hz
where
f_c: the cut-off frequency, in hertz (Hz): where the output has fallen to about 71% of the input (−3 dB)
π: pi, about 3.14159
R: the resistance, here 10 kΩ = 10,000 ohms (Ω)
C: the capacitance, here 100 nF = 0.0000001 farads (F)
Hz: hertz, cycles per second
Ω: ohms, the unit of resistance
nF: nanofarads; one billionth of a farad
≈: approximately equal to (rounded)
In words: the same 10 kΩ and 100 nF that give a 1 ms time constant start cutting frequencies above about 159 Hz. Bigger R or C gives a lower cut-off.
```

This assumes whatever reads the capacitor draws almost no current. A load across the capacitor changes the cut-off, just as it loads a divider.

## Key takeaways

- An unloaded RC low-pass has its cutoff at one over two pi times RC.
- Loading and nonideal components change the simple model.

## Further reading

- [TI Precision Labs: passive RC response](https://www.ti.com.cn/content/dam/videos/external-videos/zh-cn/4/3816841626001/6119035031001.mp4/subassets/passive_components_and_circuits_2.pdf)

- [OpenStax: ideal RC circuits](https://openstax.org/books/university-physics-volume-2/pages/10-5-rc-circuits)
- [SparkFun: voltage dividers](https://learn.sparkfun.com/tutorials/voltage-dividers/all)
