---
id: par-systolic-utilisation
title: Fill, drain and systolic utilisation
level: advanced
minutes: 3
sourceLesson: par-accelerators
summary: One isolated square product pays fill and drain costs.
---

How long does one product take, and how busy is the array during it? The bottom-right PE finishes last: its row and column delays are both as large as possible, and it must still work through every term. The array does one useful MAC operation per term per output element, spread over all its PEs:

```formula
t_last = (n − 1) + (n − 1) + (n − 1)
t_tot = t_last + 1 = 3n − 2
U = n^3 / (n^2 (3n − 2))
U = n / (3n − 2)
U = 2 / (3 × 2 − 2) = 2 / 4 = 0.5
U → 1/3   as n → ∞
where
t_last: the cycle on which the bottom-right PE does its last MAC operation: its row delay (n − 1), plus its column delay (n − 1), plus the last term index (n − 1)
t_tot: the number of cycles one n × n product takes, counting from cycle 0
n: the matrix size; the substitution line uses n = 2
U: the average utilisation: the fraction of PE-cycles that do a useful MAC operation
n^3: the number of MACs the product needs: n^2 output elements, each a sum of n products
n^2: the number of PEs in the array
→: approaches, gets ever closer to
∞: infinity: n grows without limit
In words: a single square product keeps the array only partly busy, because it takes time to fill and drain; for large arrays the average is about one third, not 100%.
```

For a two-by-two product the work takes four cycles: cycle zero activates only the top-left processing element, the next two cycles have three processing elements busy, and the final cycle only the bottom-right one. That is 8 busy PE-cycles out of 16, the 0.5 above. The utilisation **approaches one third**. A longer reduction dimension or an appropriately overlapped stream of tiles can amortise fill and drain costs.

Why this is efficient:

- In the illustrated full square output tile, each operand entering from the local buffer is reused once per output position along its row or column. Edge tiles and other dataflows differ.
- Local neighbour communication reduces repeated operand access. The simple PE does not decode an instruction for each MAC operation, but the full accelerator still needs buffers and control.
- The ideal schedule is regular. Real hardware also handles stalls, tiling, memory transfers and supported numerical modes.

The TPU used a *weight-stationary* variant: weights are preloaded into the PEs, activations flow across, and partial sums flow down.

## Key takeaways
- One isolated square product pays fill and drain costs.
- Tile overlap and a longer reduction dimension can change utilisation; reuse alone does not guarantee peak throughput.

## Further reading
- [Jouppi and colleagues: the first TPU](https://arxiv.org/abs/1704.04760)
- [Cloud TPU bfloat16 conversion](https://docs.cloud.google.com/tpu/docs/bfloat16)
- [AMD configurable logic blocks](https://docs.amd.com/r/en-US/ug474_7Series_CLB/CLB-Overview)
- [AMD high-level synthesis](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Introduction)
- [AMD MicroBlaze soft processor](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/microblaze.html)
