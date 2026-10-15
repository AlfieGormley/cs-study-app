---
id: comp-linear-scan-spills
title: "Linear scan, expiry and spilling"
level: advanced
minutes: 3
sourceLesson: comp-codegen-regalloc
summary: "Expire intervals before allocating their registers to new results."
---

## Linear scan

**Linear-scan register allocation** (Poletto and Sarkar, 1999), or linear scan for short, walks the live ranges in order of start, handing out free registers and taking them back when a range ends:

```python
def linear_scan(code, result, params, k):
    if k < 1:
        raise ValueError(
            "k must be positive")
    start, end = live_ranges(code, result,
                             params)
    free = [f"r{i}" for i in range(k)]
    active = []    # values in registers
    reg, spill = {}, []
    for v in sorted(start, key=start.get):
        if end[v] < 0:
            continue   # unused input
        # free registers whose value died
        for w in list(active):
            if end[w] <= start[v]:
                active.remove(w)
                free.append(reg[w])
        if free:
            reg[v] = free.pop(0)
            active.append(v)
            continue
        # no register: spill whichever
        # interval ends furthest ahead
        # Keep the interval that ends
        # sooner.
        far = max(active, key=end.get)
        if end[far] > end[v]:
            # Reassign the victim’s
            # register.
            reg[v] = reg.pop(far)
            active.remove(far)
            active.append(v)
            spill.append(far)
        else:
            spill.append(v)
    return reg, spill
```

`end[w] <= start[v]` lets a value that dies *at* an instruction give its register to the value that instruction defines, so `t3 = t1 * t1` can write the register `t1` was in. With `k = 2` and a simple emitter:

```
add r1, r0, r1      t1 = x + y
mul r1, r1, r1      t3 = t1 * t1
mul r0, r0, #8      t4 = x * 8
sub r1, r1, r0      t5 = t3 - t4
ret r1
```

Here `x` arrived in `r0` and `y` in `r1`. Two registers suffice, exactly MaxLive. For these interval ranges and interchangeable registers, start-order allocation finds a spill-free assignment when k is at least MaxLive. This is not a guarantee of minimum spill cost on real hardware. The guarantee applies to the stated interval model, not to arbitrary target constraints or minimum spill cost.

## Spilling

With `k = 1` there are not enough registers. This linear scan spills the interval whose end (last use) is furthest away, keeping it in a stack slot instead:

```
add r0, [sp+0], r0
mul r0, r0, r0
mul [sp+8], [sp+0], #8
sub r0, r0, [sp+8]
ret r0
```

`x` and `t4` now live in memory. This is pseudo-assembly that lets any operand be in memory; a real back end would reserve a scratch register and insert explicit loads and stores. This interval-end heuristic differs from farthest-next-use cache replacement and is not an optimal spill-cost algorithm. Spills inside a hot loop are a classic cause of slow code.

## Key takeaways
- Expire intervals before allocating their registers to new results.
- Spilling the latest-ending interval is a heuristic and requires real target load/store machinery.

## Further reading
- [LLVM code generator design](https://llvm.org/docs/CodeGenerator.html)
- [Linear scan register allocation — Poletto and Sarkar](https://web.cs.ucla.edu/~palsberg/course/cs132/linearscan.pdf)
- [Register allocation and coalescing research](https://www.cs.princeton.edu/~appel/modern/text/color1.html)
- [C11 committee draft: expressions and integer arithmetic](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [AArch64 procedure-call standard](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
