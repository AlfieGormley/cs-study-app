---
id: par-configurable-silicon
title: FPGA fabrics, hardware pipelines and ASICs
level: advanced
minutes: 3
sourceLesson: par-accelerators
summary: FPGA configuration defines logic and routing; hardware design still needs timing and resource checks.
---

## FPGAs: rewirable hardware

A **field-programmable gate array** is a grid of configurable logic connected by a programmable routing fabric:

- **LUTs** (look-up tables): a small memory holding one output bit for every combination of its inputs. A 4-input LUT stores 16 bits, so it can represent any Boolean function of those four inputs; available input counts depend on the device (4 to 6 is common).
- **Flip-flops** for state and pipelining.
- **DSP blocks**: hard multiply-accumulate units.
- **Block RAM**: small on-chip memories spread across the chip.

You can describe a circuit in an HDL such as Verilog or VHDL, or use high-level synthesis for supported source programs. Tools synthesise, place and route the design and generate configuration data. Timing closure, verification and limits on chip resources remain hardware-design tasks.

A custom hardware pipeline can process several inputs concurrently at different stages. Its clock, initiation interval and end-to-end latency depend on the design, data width, memory access and backpressure. A one-item-per-cycle pipeline does not automatically accept a complete variable-length packet every cycle or guarantee fixed network latency.

FPGAs are useful for reconfigurable hardware pipelines and prototyping logic before fabricating a chip. Their configurable routing has costs, but performance and economic comparisons require a particular design and deployment volume.

## ASICs: application-specific silicon

An **application-specific integrated circuit** is designed for an application or domain. Development includes design, verification and manufacturing preparation; costs and lead times vary substantially. A custom implementation can remove configurability overhead, but it is not universally the best performance-per-watt choice for every workload.

Fixed gates cannot be rewritten by loading an FPGA bitstream. However, firmware, programmable processors, configuration registers and supported algorithm parameters may let an ASIC adapt to changes within its design. An algorithm change does not automatically make every ASIC obsolete.

## Throughput is not latency

Consider a hypothetical packet pipeline clocked at 300 megahertz that accepts one complete packet every cycle. Assume enough link bandwidth, no stalls and a design that actually supports that packet size. Its steady-state rate is 300 million packets per second, regardless of how many stages a packet takes to traverse. A deeper pipeline can retain that rate while increasing the time one packet spends inside.

For comparison, assume eight CPU cores at three gigahertz each require 200 cycles per packet and scale perfectly. Their combined rate follows:

```formula
R = N f / C
R = (8 × 3 × 10^9 Hz) / 200
R = 120 × 10^6 packets/s
where
R: total steady-state packet rate, in packets per second
N: number of CPU cores, eight here
f: sustained per-core clock, in hertz (Hz)
C: cycles required per packet per core, 200 here
Hz: cycles per second
packets: the counted complete input packets
s: second
In words: divide the combined cycles available each second by the assumed cycles required per packet.
```

This example compares stated designs, not all CPUs with all FPGAs. Variable packet sizes, memory stalls, backpressure and external links can change either rate.

## Key takeaways
- FPGA configuration defines logic and routing; hardware design still needs timing and resource checks.
- An ASIC can contain programmable components even though its fabricated gates are fixed.

## Further reading
- [Jouppi and colleagues: the first TPU](https://arxiv.org/abs/1704.04760)
- [Cloud TPU bfloat16 conversion](https://docs.cloud.google.com/tpu/docs/bfloat16)
- [AMD configurable logic blocks](https://docs.amd.com/r/en-US/ug474_7Series_CLB/CLB-Overview)
- [AMD high-level synthesis](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Introduction)
- [AMD MicroBlaze soft processor](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/microblaze.html)
