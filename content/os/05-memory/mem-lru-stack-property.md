---
id: mem-lru-stack-property
sourceLesson: mem-page-replacement
title: LRU, cyclic scans and Belady’s anomaly
level: intermediate
minutes: 4
summary: LRU tracks recent use but performs poorly on loops just larger than memory.
---

## LRU

**Least recently used**: evict the page whose last use is furthest in the *past*. It bets that the recent past predicts the near future, which is what locality says.

| Ref | Frames (old to new) | Fault? |
|---|---|---|
| 1, 2, 3 | 1 2 3 | F F F |
| 1 | 2 3 1 | hit |
| 4 | 3 1 4 | F (evict 2) |
| 1 | 3 4 1 | hit |
| 2 | 4 1 2 | F (evict 3) |
| 5 | 1 2 5 | F (evict 4) |

**6 faults**, between FIFO and OPT. LRU kept page 1 because it was used recently.

A simulator for any of these takes a few lines:

```python
from collections import OrderedDict

def lru_faults(refs, frames):
    if frames < 1:
        raise ValueError("positive frames")
    mem = OrderedDict()
    faults = 0
    for p in refs:
        if p in mem:
            # Most recent goes last.
            mem.move_to_end(p)
            continue
        faults += 1
        if len(mem) == frames:
            # Evict the oldest entry.
            mem.popitem(last=False)
        mem[p] = True
    return faults

s = [1, 2, 3, 1, 4, 1, 2, 5]
print(lru_faults(s, 3))  # 6
```

### LRU's blind spot

LRU fails badly on a **loop slightly larger than memory**. Cycle through pages 1 to 4 with 3 frames, and LRU always evicts exactly the page needed next: every reference faults. Large sequential scans (a backup, a `grep` over a huge log) have the same shape, and flush genuinely hot pages out of memory as they pass. Real systems need **scan resistance**, which Linux gets from its two-list design below.

## Belady's anomaly

Surely more frames always means fewer faults? Not for FIFO. Take this string:

```
1 2 3 4 1 2 5 1 2 3 4 5
```

| Policy | 3 frames | 4 frames |
|---|---|---|
| FIFO | 9 | **10** |
| LRU | 10 | 8 |
| OPT | 7 | 6 |

With FIFO, adding a frame made things **worse**. This is **Belady's anomaly**.

LRU and OPT cannot suffer it because they are **stack algorithms**. Run the same reference string twice, once with one frame fewer, and compare what is in memory after each reference:

```formula
M(n, t) ⊆ M(n + 1, t)   for all t
where
M(n, t): the set of pages in memory just after reference number t, when the policy runs with n frames
n: the number of frames
t: the position in the reference string: 1 for the first reference, 2 for the second, and so on
⊆: "is a subset of": every page in the left-hand set is also in the right-hand set
In words: at every step, whatever the policy holds with n frames it would also be holding with one more frame.
```

A hit with fewer frames therefore remains a hit with one extra frame, and adding frames cannot add faults. LRU keeps the most recently used pages, which are nested as capacity increases. For OPT’s resident-set inclusion statement, use consistent choices when future-use ties admit multiple optimal victims; arbitrary independent tie choices need not produce identical nested sets. FIFO lacks this property because its eviction order depends on arrival time, which changes as the frame count changes.

## Key takeaways
- LRU tracks recent use but performs poorly on loops just larger than memory.
- FIFO can fault more with extra frames; suitable stack policies avoid that anomaly.

## Further reading
- [OSTEP: Beyond Physical Memory: Policies (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys-policy.pdf)
- [Page replacement algorithm — Wikipedia](https://en.wikipedia.org/wiki/Page_replacement_algorithm)
- [Bélády's anomaly — Wikipedia](https://en.wikipedia.org/wiki/B%C3%A9l%C3%A1dy%27s_anomaly)
- [Thrashing — Wikipedia](https://en.wikipedia.org/wiki/Thrashing_(computer_science))
- [The multi-generational LRU — LWN.net](https://lwn.net/Articles/851184/)
- [Multi-Gen LRU — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/multigen_lru.html)
- [Pressure stall information — Linux kernel docs](https://www.kernel.org/doc/html/latest/accounting/psi.html)
- [Page Frame Reclamation, from Understanding the Linux Virtual Memory Manager](https://www.kernel.org/doc/gorman/html/understand/understand013.html)
