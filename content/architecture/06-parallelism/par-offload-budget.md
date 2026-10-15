---
id: par-offload-budget
title: Accounting for transfer, batching and offload costs
level: advanced
minutes: 3
sourceLesson: par-accelerators
summary: Only saved computation pays for added copies, setup and queueing.
---

## When is offloading worth it?

1. **Amdahl.** Only the offloaded part speeds up. For fixed work with unchanged remaining time and no added overhead, a 50% accelerated fraction has a 2× speedup ceiling.
2. **Data movement.** Copying inputs to the device and results back can exceed the compute saved. Accelerators work best when data stays on the device across many operations.
3. **Batching versus latency.** Some accelerator workloads benefit from batching; others already expose enough parallelism within one request. A single request may wait for a batch to form, raising latency.
4. **Numerics.** Supported precision varies. Quantisation or mixed-precision execution requires validation against the application’s accuracy and special-value requirements.
5. **Software.** An accelerator is only as useful as its compiler and libraries. Compiler and library support, operation coverage and deployment tooling affect usable performance.
6. **Utilisation.** Peak TOPS remains an arithmetic ceiling, but does not predict bandwidth-limited layer performance. The TPU paper found several production networks were limited by memory bandwidth, not MACs, which the later roofline units make precise.

The first two points combine into one estimate. Normalise the original run time to 1, and add the transfer time to Amdahl's formula:

```formula
S = 1 / ((1 − f) + f / k + x)
S = 1 / (0.2 + 0.8 / 10 + 0.1)
S = 1 / 0.38 ≈ 2.6
where
S: the overall speedup of the whole job
f: the fraction of the original run time that is offloaded; here 0.8
k: how many times faster the accelerator runs that part; here 10
x: the time added by copying data to and from the device, as a fraction of the original run time; here 0.1
≈: approximately equal to
In words: offloading 80% of a job to a device that is 10 times faster, at a copying cost of 10% of the original time, makes the whole job only about 2.6 times faster.
```

Even with an infinitely fast accelerator this job could not beat 1 / (0.2 + 0.1) ≈ 3.3×, because the untouched work and the copies remain.

> [!note] Evidence limits
> Generic picojoule ratios, FPGA clock/build/financial-market latency ranges, ASIC dollar/lead-time estimates and a cross-generation accelerator catalogue is omitted because comparable primary evidence for those design-specific claims was not reliably established; they are not needed for the retained mechanism and arithmetic examples.

## Counting batch-formation delay

Suppose an empty batch needs 64 requests and arrivals are exactly one millisecond apart. The first arrival starts waiting; the sixty-fourth starts execution immediately. There are 63 arrival gaps, so the longest formation wait is 63 milliseconds. The last arrival has no formation wait. Service queueing, launch overhead and execution add separate delays.

A batching policy therefore needs a latency objective as well as a target batch size. A timeout may run a partly full batch earlier. Keeping weights or intermediates resident can reduce repeated movement without requiring the same waiting policy. Measure the actual arrival distribution and queue behaviour before applying a steady-state throughput result to individual request latency.

## Key takeaways
- Only saved computation pays for added copies, setup and queueing.
- Batching can improve reuse while increasing request waiting time.

## Further reading
- [Jouppi and colleagues: the first TPU](https://arxiv.org/abs/1704.04760)
- [Cloud TPU bfloat16 conversion](https://docs.cloud.google.com/tpu/docs/bfloat16)
- [AMD configurable logic blocks](https://docs.amd.com/r/en-US/ug474_7Series_CLB/CLB-Overview)
- [AMD high-level synthesis](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Introduction)
- [AMD MicroBlaze soft processor](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/microblaze.html)
