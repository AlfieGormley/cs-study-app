---
id: pipe-hazards-stall-counter
sourceLesson: pipe-hazards
title: Trace stalls with a dependency model
level: intermediate
minutes: 3
summary: Use a small readiness-slot simulation and recognise the hardware behaviour it intentionally omits.
---

The previous unit compared two schedules for eight instructions. This unit turns the same assumptions into a small executable model: in-order issue, one-cycle stages, and all operands needed by EX. With forwarding, the earlier naive schedule had two stalls and its reordered version had none; without forwarding, same-cycle WB then ID determines when a consumer may continue.

### Counting stalls in code

This function counts stall cycles for a straight-line program on the 5-stage pipeline. It records the earliest logical issue slot compatible with each dependency. With forwarding this is not the cycle when the register file itself contains the new value. Program entries are `(op, dst, srcs)` with integer register IDs 0–31, `dst=None` for no register result, and register 0 hard-wired to zero. All forwarded sources, including store data, are required by EX in this simplified model; it does not model a separate late store-data bypass, branches, cache misses or multicycle units:

```python
def stalls(prog, forwarding=True):
    rdy = {}     # reg -> ready slot
    cycle = 0    # logical issue slot
    total = 0
    for op, dst, srcs in prog:
        need = [rdy.get(r, 0)
                for r in srcs if r != 0]
        # Wait for operands and issue turn.
        start = max(need + [cycle])
        total += start - cycle
        cycle = start
        # Register zero never gains a value.
        if dst:
            if not forwarding:
                lat = 3      # wait for WB
            elif op == "lw":
                lat = 2      # load-use
            else:
                lat = 1      # EX -> EX
            # Track the newest version.
            rdy[dst] = cycle + lat
        cycle += 1
    # Return extra issue slots.
    return total
```

On the naive sequence above it returns 2 with forwarding and 8 without; on the scheduled one, 0 and 4. For this sequence and model, forwarding removes more stalls than scheduling alone; combining them removes all modelled stalls.

## Key takeaways
- Readiness slots represent when a dependent operation may start, not register-file update time.
- Loads and ordinary ALU results have different forwarding latencies.
- This model omits branches, cache misses, multicycle units and a late store-data bypass.

## Further reading
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)
- [RISC-V unprivileged ISA specification](https://riscv.github.io/riscv-isa-manual/snapshot/spec/)
