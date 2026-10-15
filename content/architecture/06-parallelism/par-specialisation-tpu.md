---
id: par-specialisation-tpu
title: Specialisation and the first TPU
level: advanced
minutes: 3
sourceLesson: par-accelerators
summary: Specialisation can reduce control and operand-movement overhead; benefits remain workload-dependent.
---

General-purpose execution spends energy on control and data movement as well as arithmetic. An accelerator can improve efficiency by specialising the computation, reusing operands and amortising instruction overhead. The benefit depends on workload, precision, utilisation, memory traffic and implementation; no universal energy ratio applies.

Power and thermal constraints helped motivate specialisation alongside architectural and process improvements. A **hardware accelerator** provides hardware suited to a class of operations, usually working with a host processor.

## Flexibility and specialisation

| Device | Relevant capability |
|---|---|
| CPU | General instruction execution and control |
| GPU | Many parallel threads and specialised execution units |
| FPGA | Configurable logic and routing for custom circuits |
| ASIC | Silicon designed for a particular application or domain |

This is not a universal efficiency ranking. An FPGA can implement a direct hardware pipeline without fetching one instruction per operation, but can also contain hard or soft processors. An ASIC may include programmable processors and configurable accelerators; “application-specific” does not mean every behaviour is permanently fixed.

## TPUs and the systolic array

By 2013 Google estimated that if people used voice search for a few minutes a day, running the neural networks on CPUs would need it to roughly double its data-centre capacity. So it built the **Tensor Processing Unit** (TPU), deployed in 2015 and described in a 2017 paper.

The first TPU was an inference chip built around one thing: a **256 × 256 matrix multiply unit** of 8-bit integer multiply-accumulate cells (MAC cells), 65,536 in all, at 700 MHz. Its peak rate is the number of MAC cells times the operations each does per cycle times the clock rate:

```formula
P_peak = N_MAC × 2 × f_clk
P_peak = 65,536 × 2 × 700 × 10^6 Hz
P_peak ≈ 91.8 × 10^12 ops/s ≈ 92 TOPS
where
P_peak: the peak arithmetic rate, in operations per second (ops/s)
N_MAC: the number of MAC cells: 256 × 256 = 65,536
2: each multiply-accumulate counts as two operations, a multiply and an add
f_clk: the clock frequency, in hertz (Hz); 700 MHz = 700 × 10^6 Hz
Hz: hertz, one cycle per second
ops: operations (here 8-bit integer multiplies and adds)
s: second
TOPS: tera-operations per second, 10^12 ops/s
≈: approximately equal to
In words: 65,536 cells each doing a multiply and an add 700 million times a second give about 92 trillion operations a second, if every cell is busy every cycle.
```

It also had 28 MiB of on-chip SRAM (a 24 MiB unified buffer for activations plus accumulators) and read weights from 8 GiB of DDR3 at about 34 GB/s. For the paper’s six production inference applications and compared Haswell CPU and NVIDIA K80 GPU systems, the authors reported average performance gains of roughly 15–30× and performance-per-watt gains of 30–80×. These are results of that study, not a guarantee for arbitrary networks or modern devices.

## Weight reuse can set another ceiling

The arithmetic peak is useful only if operands arrive quickly enough. In a deliberately simplified fully connected layer, assume each one-byte integer weight is transferred once per batch and performs one multiply-accumulate for each example. Ignore activations and every other kind of traffic. Each example therefore adds two operations of reuse per weight byte.

```formula
I_r = P / R
I_r = (92 × 10^12) / (34 × 10^9)
I_r ≈ 2706
N = I_r / 2 ≈ 1353
where
I_r: operations per transferred weight byte where the arithmetic and weight-bandwidth ceilings meet
P: arithmetic peak, 92 trillion operations per second in this rounded example
R: weight bandwidth, 34 billion bytes per second
N: batch size at the model intersection, in examples
2: a multiply and an add counted for each example’s use of one weight byte
≈: approximately equal to, with rounding
In words: weight reuse of about 1350 examples per transferred byte would be needed to reach this isolated arithmetic ceiling.
```

This is a model intersection, not a recommended batch size or an achievable production guarantee. Other traffic, available storage, latency limits and incomplete utilisation can lower the rate. The later roofline units generalise this comparison.

## Key takeaways
- Specialisation can reduce control and operand-movement overhead; benefits remain workload-dependent.
- TPU v1’s 92 TOPS is a full-utilisation arithmetic ceiling for its stated integer operations.

## Further reading
- [Jouppi and colleagues: the first TPU](https://arxiv.org/abs/1704.04760)
- [Cloud TPU bfloat16 conversion](https://docs.cloud.google.com/tpu/docs/bfloat16)
- [AMD configurable logic blocks](https://docs.amd.com/r/en-US/ug474_7Series_CLB/CLB-Overview)
- [AMD high-level synthesis](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Introduction)
- [AMD MicroBlaze soft processor](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/microblaze.html)
