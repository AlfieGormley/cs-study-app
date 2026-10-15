---
id: par-tpu-numerics
title: bfloat16 precision and conversion
level: advanced
minutes: 3
sourceLesson: par-accelerators
summary: bfloat16 trades fraction precision for a wide exponent field.
---

### Later TPUs

Later TPU generations added floating-point support for training. **bfloat16** stores 1 sign bit, 8 exponent bits and 7 fraction bits, versus float32’s 23 stored fraction bits. Its normal exponent range is similar to float32’s, but precision, largest finite value and subnormal behaviour differ.

On Cloud TPU, XLA’s float32-to-bfloat16 conversion uses round-to-nearest, ties-to-even, overflows to infinity and flushes bfloat16 subnormals to zero. It is **not** simply mantissa truncation. The wider exponent field relative to IEEE binary16 can reduce the need for loss scaling, but overflow, underflow and numerical accuracy remain workload-dependent. Check the selected TPU generation and operation rather than assuming a single matrix-array configuration across all versions.

## Range is different from precision

The exponent field mainly controls the range of magnitudes a format can express. The fraction field controls the spacing between nearby normal values. Sharing an exponent width therefore does not make two formats interchangeable: a value can fit comfortably within bfloat16's range while losing distinctions that float32 preserves.

For a concrete example, near one, adjacent bfloat16 values are separated by one part in 128. The number 1.003 lies closer to 1 than to the next representable value, so round-to-nearest converts it to exactly 1. A float32 value at that scale has much finer spacing. This is a rounding example, not a claim about a model's final prediction accuracy.

Accumulation precision is a separate choice. A matrix operation may multiply bfloat16 inputs but accumulate products into float32. That can preserve more of the running sum than a low-precision accumulator, while the information discarded when converting each input is already gone. Check both operand and accumulator formats.

Before changing precision, validate representative inputs and difficult cases: very small magnitudes, large sums, cancellation and special values. Compare application-level error and end-to-end performance with the original. A wide exponent range can make some training workflows easier without proving that loss scaling is never useful or that every operation has identical numerical behaviour.

## Key takeaways
- bfloat16 trades fraction precision for a wide exponent field.
- Conversion rounding, overflow and subnormal rules belong to the selected platform contract.

## Further reading
- [Jouppi and colleagues: the first TPU](https://arxiv.org/abs/1704.04760)
- [Cloud TPU bfloat16 conversion](https://docs.cloud.google.com/tpu/docs/bfloat16)
- [AMD configurable logic blocks](https://docs.amd.com/r/en-US/ug474_7Series_CLB/CLB-Overview)
- [AMD high-level synthesis](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Introduction)
- [AMD MicroBlaze soft processor](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/microblaze.html)
