---
id: mem-clock-replacement
sourceLesson: mem-page-replacement
title: Approximating recency with clock bits
level: intermediate
minutes: 3
summary: Commodity page-table bits do not expose a complete recency ordering.
---

## Why exact page LRU is expensive

Exact LRU needs enough information to order every page's latest use, whether maintained as a list or another structure. Commodity page tables do not expose a complete recency trace to the OS, and trapping every access is prohibitively expensive for ordinary workloads. Access bits and sampled/software observations support approximations.

So real systems **approximate** LRU using that bit.

## The clock algorithm

**Clock** (also called **second chance**) arranges frames in a circle with a hand pointing at one of them. In the drawing, A names the accessed flag: one means an access has been observed and zero means the flag is clear.

```
      +---+
   +--| 4 |--+      A bits
   |  +---+  |      4:1  7:0
 +---+     +---+    2:1  9:1
 | 9 |     | 7 |
 +---+     +---+
   |  +---+  |
   +--| 2 |--+
      +---+
       ^ hand
```

When a frame is needed:

1. Look at the page under the hand.
2. If its **A bit is 1**, clear it to 0 (a second chance) and advance.
3. If its **A bit is 0**, evict it and put the new page there.

A page used since the hand last passed survives one more lap. A page untouched for a whole lap goes. If every bit is 1 and no accesses intervene, the hand clears them and returns to its starting frame. This resembles FIFO for that scan; it does not make every subsequent clock decision identical to FIFO.

```python
def clock_victim(frames, abit, hand):
    # Nonempty equal lengths, valid hand.
    # No concurrent reference-bit updates.
    while True:
        if abit[hand]:
            # Clear the second chance.
            abit[hand] = 0
            hand = (hand + 1) % len(frames)
        else:
            # Return the victim slot.
            return hand
```

### Using the dirty bit too

Evicting a **dirty page** costs a write before the frame is reusable. The **enhanced clock** prefers, in order:

| (A, D) | Meaning | Preference |
|---|---|---|
| (0, 0) | Not used, clean | Best victim |
| (0, 1) | Not used, dirty | Needs writeback |
| (1, 0) | Used, clean | Probably needed |
| (1, 1) | Used, dirty | Worst victim |

## Key takeaways
- Commodity page-table bits do not expose a complete recency ordering.
- Clock clears accessed bits before selecting an unreferenced victim.
- Dirty status adds writeback cost to victim selection.

## Further reading
- [OSTEP: Beyond Physical Memory: Policies (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys-policy.pdf)
- [Page replacement algorithm — Wikipedia](https://en.wikipedia.org/wiki/Page_replacement_algorithm)
- [Bélády's anomaly — Wikipedia](https://en.wikipedia.org/wiki/B%C3%A9l%C3%A1dy%27s_anomaly)
- [Thrashing — Wikipedia](https://en.wikipedia.org/wiki/Thrashing_(computer_science))
- [The multi-generational LRU — LWN.net](https://lwn.net/Articles/851184/)
- [Multi-Gen LRU — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/multigen_lru.html)
- [Pressure stall information — Linux kernel docs](https://www.kernel.org/doc/html/latest/accounting/psi.html)
- [Page Frame Reclamation, from Understanding the Linux Virtual Memory Manager](https://www.kernel.org/doc/gorman/html/understand/understand013.html)
