---
id: par-accelerators
title: Accelerators: TPUs, FPGAs and ASICs
level: advanced
minutes: 14
summary: How specialised hardware can improve efficiency, how a TPU's systolic array multiplies matrices, what FPGAs are good for, and when offloading is worth it.
---

General-purpose execution spends energy on control and data movement as well as arithmetic. An accelerator can improve efficiency by specialising the computation, reusing operands and amortising instruction overhead. The benefit depends on workload, precision, utilisation, memory traffic and implementation; no universal energy ratio applies.

Power and thermal constraints helped motivate specialisation alongside architectural and process improvements. An **accelerator** provides hardware suited to a class of operations, usually working with a host processor.

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

The first TPU was an inference chip built around one thing: a **256 × 256 matrix multiply unit** of 8-bit integer multiply-accumulate (MAC) cells, 65,536 in all, at 700 MHz.

```
peak = 65536 MACs x 2 ops x 700e6
     ~ 92 x 10^12 ops/s  (92 TOPS)
```

It also had 28 MiB of on-chip SRAM (a 24 MiB unified buffer for activations plus accumulators) and read weights from 8 GiB of DDR3 at about 34 GB/s. For the paper’s six production inference applications and compared Haswell CPU and NVIDIA K80 GPU systems, the authors reported average performance gains of roughly 15–30× and performance-per-watt gains of 30–80×. These are results of that study, not a guarantee for arbitrary networks or modern devices.

### How a systolic array works

The key idea is to reuse data as it moves through a grid of processing elements (PEs), reducing repeated operand movement. An operand read from a local buffer can serve several operations; a large tiled problem may still require repeated DRAM reads. Each PE multiplies, adds, and passes values to its neighbours, like blood pulsed through the body (hence "systolic").

```
       b-col0  b-col1  b-col2
         v       v       v
a-row0> [PE]--> [PE]--> [PE]
         |       |       |
a-row1> [PE]--> [PE]--> [PE]
         |       |       |
a-row2> [PE]--> [PE]--> [PE]
```

In the *output-stationary* variant, PE(i, j) accumulates C[i][j]. Row i of A enters from the left, delayed by i cycles; column j of B enters from the top, delayed by j cycles. At cycle t, PE(i, j) sees A[i][k] and B[k][j] with k = t − i − j. The following ideal output-stationary model assumes one MAC per active PE per cycle and square matrices. It is an explanatory schedule, not an implementation of TPU v1’s exact datapath. Python integer inputs give exact integer results; floating-point inputs have Python’s rounding semantics:

```python
def systolic(A, B):
    n = len(A)
    if len(B) != n or any(
        len(row) != n
        for M in (A, B) for row in M
    ):
        raise ValueError("invalid shape")
    C = [[0] * n for _ in range(n)]
    pes = [(i, j) for i in range(n)
           for j in range(n)]
    for t in range(3 * n - 2):  # cycles
        for i, j in pes:
            k = t - i - j
            if 0 <= k < n:
                C[i][j] += A[i][k] * B[k][j]
    return C

print(systolic([[1, 2], [3, 4]],
               [[5, 6], [7, 8]]))
# [[19, 22], [43, 50]]
```

For n = 2 the work takes 3n − 2 = 4 cycles: cycle 0 activates only PE(0,0), cycles 1 and 2 have three PEs busy, and cycle 3 only PE(1,1). There are n³ useful MACs across n² PEs and 3n − 2 cycles, so average utilisation for this single square product is **n / (3n − 2)**, approaching **one third**, not 100%. A longer reduction dimension or an appropriately overlapped stream of tiles can amortise fill and drain costs.

Why this is efficient:

- In the illustrated full n × n output tile, each operand entering from the local buffer is reused n times along a row or column. Edge tiles and other dataflows differ.
- Local neighbour communication reduces repeated operand access. The simple PE does not decode an instruction for each MAC, but the full accelerator still needs buffers and control.
- The ideal schedule is regular. Real hardware also handles stalls, tiling, memory transfers and supported numerical modes.

The TPU used a *weight-stationary* variant: weights are preloaded into the PEs, activations flow across, and partial sums flow down.

### Later TPUs

Later TPU generations added floating-point support for training. **bfloat16** stores 1 sign bit, 8 exponent bits and 7 fraction bits, versus float32’s 23 stored fraction bits. Its normal exponent range is similar to float32’s, but precision, largest finite value and subnormal behaviour differ.

On Cloud TPU, XLA’s float32-to-bfloat16 conversion uses round-to-nearest, ties-to-even, overflows to infinity and flushes bfloat16 subnormals to zero. It is **not** simply mantissa truncation. The wider exponent field relative to IEEE binary16 can reduce the need for loss scaling, but overflow, underflow and numerical accuracy remain workload-dependent. Check the selected TPU generation and operation rather than assuming a single matrix-array configuration across all versions.

## FPGAs: rewirable hardware

A **field-programmable gate array** is a grid of configurable logic connected by a programmable routing fabric:

- **LUTs** (look-up tables): a k-input LUT can represent any Boolean function of its k inputs; available sizes depend on the device.
- **Flip-flops** for state and pipelining.
- **DSP blocks**: hard multiply-accumulate units.
- **Block RAM**: small on-chip memories spread across the chip.

You can describe a circuit in an HDL such as Verilog or VHDL, or use high-level synthesis for supported source programs. Tools synthesise, place and route the design and generate configuration data. Timing closure, verification and resource limits remain hardware-design tasks.

A custom pipeline can process several inputs concurrently at different stages. Its clock, initiation interval and end-to-end latency depend on the design, data width, memory access and backpressure. A one-item-per-cycle pipeline does not automatically accept a complete variable-length packet every cycle or guarantee fixed network latency.

FPGAs are useful for reconfigurable pipelines and prototyping logic before fabricating a chip. Their configurable routing has costs, but performance and economic comparisons require a particular design and deployment volume.

## ASICs: application-specific silicon

An **application-specific integrated circuit** is designed for an application or domain. Development includes design, verification and manufacturing preparation; costs and lead times vary substantially. A custom implementation can remove configurability overhead, but it is not universally the best performance-per-watt choice for every workload.

Fixed gates cannot be rewritten by loading an FPGA bitstream. However, firmware, programmable processors, configuration registers and supported algorithm parameters may let an ASIC adapt to changes within its design. An algorithm change does not automatically make every ASIC obsolete.

## When is offloading worth it?

1. **Amdahl.** Only the offloaded part speeds up. For fixed work with unchanged remaining time and no added overhead, a 50% accelerated fraction has a 2× speedup ceiling.
2. **Data movement.** Copying inputs to the device and results back can exceed the compute saved. Accelerators work best when data stays on the device across many operations.
3. **Batching versus latency.** Some accelerator workloads benefit from batching; others already expose enough parallelism within one request. A single request may wait for a batch to form, raising latency.
4. **Numerics.** Supported precision varies. Quantisation or mixed-precision execution requires validation against the application’s accuracy and special-value requirements.
5. **Software.** An accelerator is only as useful as its compiler and libraries. Compiler and library support, operation coverage and deployment tooling affect usable performance.
6. **Utilisation.** Peak TOPS remains an arithmetic ceiling, but does not predict bandwidth-limited layer performance. The TPU paper found several production networks were limited by memory bandwidth, not MACs, which the roofline model in the next lesson makes precise.

> [!note] Evidence limits
> Generic picojoule ratios, FPGA clock/build/financial-market latency ranges, ASIC dollar/lead-time estimates and a cross-generation accelerator catalogue is omitted because comparable primary evidence for those design-specific claims was not reliably established; they are not needed for the retained mechanism and arithmetic examples.

## Key takeaways
- Specialisation can reduce control overhead and data movement; savings must be evaluated for the workload and numerical contract.
- FPGA logic is field-configurable; ASICs target an application but may still contain programmable components.
- TPU v1 had 65,536 int8 MACs at 700 MHz, giving about 92 TOPS when counting a MAC as two operations.
- The illustrated single-product output-stationary array averages n / (3n − 2) utilisation; reuse alone does not guarantee peak throughput.
- Offloading pays when saved computation exceeds transfer, setup and any other added costs while preserving required results.

## Further reading
- [In-Datacenter Performance Analysis of a Tensor Processing Unit (Jouppi et al., 2017)](https://arxiv.org/abs/1704.04760)
- [An in-depth look at Google's first TPU — Google Cloud blog](https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu)
- [How to think about TPUs — JAX scaling book](https://jax-ml.github.io/scaling-book/tpus/)
- [Systolic array — Wikipedia](https://en.wikipedia.org/wiki/Systolic_array)
- [Field-programmable gate array — Wikipedia](https://en.wikipedia.org/wiki/Field-programmable_gate_array)

- [Cloud TPU bfloat16 conversion](https://docs.cloud.google.com/tpu/docs/bfloat16)

- [AMD MicroBlaze soft processor](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/microblaze.html)
