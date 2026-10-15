---
id: pipe-out-of-order-rename-register-versions
sourceLesson: pipe-out-of-order
title: Rename register versions
level: advanced
minutes: 3
summary: Trace physical mappings and remove WAR/WAW without removing true dependences.
---

The preceding unit separated in-order front-end work, ready-instruction execution and in-order retirement. Register renaming supports that design by giving simultaneously live register versions distinct storage. RAW means read-after-write data flow; WAR and WAW are name dependences from reusing an architectural register.

## Register renaming

Out-of-order execution exposes the **name dependences** from the earlier hazard units:

```
i1: mul x1, x2, x3
i2: add x4, x1, x5   # RAW on x1 (real)
i3: add x1, x6, x7   # WAW i1, WAR i2
i4: add x8, x1, x2   # RAW on i3's x1
```

i3 and i4 have nothing to do with i1 and i2; they just reuse the name x1. But if i3 ran before i1 finished, it could have its x1 overwritten by the slow `mul` (WAW), or i2 could read i3's x1 instead of i1's (WAR).

**Register renaming** assigns distinct storage to simultaneously live register versions. A physical-register implementation maintains more result storage than the architectural register set. Exact counts depend on the core and ISA extensions; they are omitted without a specified implementation. A **register alias table** (RAT) maps each architectural register to the physical register holding its newest value.

This teaching renamer handles a finite straight-line sequence of ordinary register-producing operations. It has no retirement, branches, zero-register semantics or free-list reclamation; names beginning with x are generic, not a complete RISC-V implementation.

```python
def rename(prog, n_arch=32, n_phys=128):
    if not 0 < n_arch <= n_phys:
        raise ValueError("bad counts")
    rat = {f"x{i}": f"p{i}"
           for i in range(n_arch)}
    free = [f"p{i}"
            for i in range(n_arch, n_phys)]
    for op, dst, srcs in prog:
        # Read sources before replacing dst.
        s = [rat[r] for r in srcs]
        if dst not in rat:
            raise ValueError("bad dst")
        if not free:
            raise ValueError("no registers")
        # Give this result its own storage.
        rat[dst] = free.pop(0)
        print(f"{rat[dst]} = {op}"
              f"({', '.join(s)})")

rename([
    ("mul", "x1", ["x2", "x3"]),
    ("add", "x4", ["x1", "x5"]),
    ("add", "x1", ["x6", "x7"]),
    ("add", "x8", ["x1", "x2"]),
])
```

Output lists each new destination followed by its already-renamed sources:

```
p32 = mul(p2, p3)
p33 = add(p32, p5)
p34 = add(p6, p7)
p35 = add(p34, p2)
```

The two x1s are now p32 and p34. Only true register dependences remain in this arithmetic trace (p32 → p33, p34 → p35), so i3 and i4 can execute while the `mul` is still running. Sources are renamed *before* the destination, so `add x1, x1, x2` correctly reads the old x1.

In a simple design without shared physical mappings or other retained references, the free list is refilled at retirement: when an instruction that overwrites x1 commits, the physical register that held the *previous* x1 can no longer be needed and is freed.

## Key takeaways
- Read source mappings before allocating a fresh destination version.
- Renaming removes register-name WAR and WAW, leaving the real data-flow edges.
- Retirement may free the previous physical register only once all required references are finished.

## Further reading
- [BOOM implementation: rename stage](https://docs.boom-core.org/en/latest/sections/rename-stage.html)
