---
id: mem-page-replacement
title: Page replacement and thrashing
level: intermediate
minutes: 15
summary: When RAM is full, which page goes? FIFO, the optimal algorithm, LRU and the clock approximation traced by hand, Belady's anomaly, how Linux actually reclaims memory, and why too little memory makes a machine thrash.
---

Demand paging and swap (previous lesson) let processes use more memory than the machine has. The price is a decision the kernel must make constantly: when a page fault needs a free frame and none is left, **which page do we evict?**

Choose well and the evicted page is not needed for a long time. Choose badly and you evict something that is needed a microsecond later, potentially paying a storage-backed refault to bring it back.

This is the same problem as cache eviction, with two differences that shape the answers:

- **A miss is enormous.** A storage-backed fault can be much slower than a resident memory access, so it is worth spending CPU on a good choice.
- **The hardware gives almost no help.** The CPU does not tell the OS about every access; it just sets the **accessed (A)** bit in a PTE. Practical policies can combine access-bit sampling with refault history, software-observed accesses and other signals.

## The setup

We measure policies on a **reference string**: the sequence of pages a program touches. With a fixed number of frames, count the **page faults**. Fewer is better. With initially empty frames and no prefetching, the first touch of each page faults (a *compulsory* miss); the policies differ on the rest.

Throughout, we use this string and **3 frames**:

```
1 2 3 1 4 1 2 5
```

## FIFO

Evict the page that has been in memory longest. It is trivial to implement as a queue.

| Ref | Frames | Fault? |
|---|---|---|
| 1 | 1 | F |
| 2 | 1 2 | F |
| 3 | 1 2 3 | F |
| 1 | 1 2 3 | hit |
| 4 | 2 3 4 | F (evict 1) |
| 1 | 3 4 1 | F (evict 2) |
| 2 | 4 1 2 | F (evict 3) |
| 5 | 1 2 5 | F (evict 4) |

**7 faults.** FIFO's flaw is visible at reference 4: it evicted page 1, the most popular page, simply because it arrived first. Age of arrival says nothing about usefulness.

## OPT: the optimal policy

**Belady's optimal algorithm (OPT or MIN)**: evict the page whose next use is *furthest in the future*. It provably gives the fewest faults possible.

| Ref | Frames | Fault? |
|---|---|---|
| 1, 2, 3 | 1 2 3 | F F F |
| 1 | 1 2 3 | hit |
| 4 | 1 2 4 | F (3 never used again) |
| 1 | 1 2 4 | hit |
| 2 | 1 2 4 | hit |
| 5 | 2 4 5 | F (any page) |

**5 faults.** OPT needs to know the future, so no real OS can run it. Its use is as a **yardstick**: simulate a trace offline and see how close a real policy gets.

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
            mem.move_to_end(p)
            continue
        faults += 1
        if len(mem) == frames:
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

LRU and OPT cannot suffer it because they are **stack algorithms**: the set of pages held with *n* frames is always a subset of the set held with *n + 1* frames. Anything that hits with *n* frames also hits with more. FIFO lacks this property because its eviction order depends on arrival time, which changes as the frame count changes.

## Why exact page LRU is expensive

Exact LRU needs enough information to order every page's latest use, whether maintained as a list or another structure. Commodity page tables do not expose a complete recency trace to the OS, and trapping every access is prohibitively expensive for ordinary workloads. Access bits and sampled/software observations support approximations.

So real systems **approximate** LRU using that bit.

## The clock algorithm

**Clock** (also called **second chance**) arranges frames in a circle with a hand pointing at one of them.

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
            abit[hand] = 0
            hand = (hand + 1) % len(frames)
        else:
            return hand
```

### Using the dirty bit too

Evicting a **dirty** page costs a write before the frame is reusable. The **enhanced clock** prefers, in order:

| (A, D) | Meaning | Preference |
|---|---|---|
| (0, 0) | Not used, clean | Best victim |
| (0, 1) | Not used, dirty | Needs writeback |
| (1, 0) | Used, clean | Probably needed |
| (1, 1) | Used, dirty | Worst victim |

## How Linux does it

Linux does not run a textbook clock. Its classic design keeps, per memory node and per cgroup, separate LRU lists for **anonymous** and **file** pages, each split into **active** and **inactive**:

```
new page
   |
   v
inactive --- used again ---> active
   |     <------ demote ------
   v
 evict
```

- In the classic design, file-page admission to inactive lists and promotion based on observed reuse help resist one-pass scans. Refault handling and access paths add exceptions; active pages are not immune to pressure or scans.
- Reclaim scans the tail of the inactive lists, checking A bits (through the reverse map from page to PTEs). Referenced pages get another chance; unreferenced ones are evicted.
- When the active list is too large, pages are demoted from it.
- **Refault detection**: when an evicted file page is faulted back in, the kernel works out how long it was gone (from a shadow entry left in the page cache). Refault distance and related history can influence activation. This is a workload-size/eviction-history signal, not simply elapsed wall-clock time.

Since Linux 6.1 there is also the **multi-generational LRU (MGLRU)**, from Google. It sorts pages into several generations by age rather than two lists and scans page tables more efficiently. Its documentation describes aging, eviction and refault feedback for workload-dependent reclaim decisions. Distros choose whether to enable it (`/sys/kernel/mm/lru_gen/enabled`).

### When reclaim runs

Each memory zone has three **watermarks**: min, low and high.

- Free memory drops below **low**: the background thread **kswapd** wakes and reclaims until free memory reaches **high**.
- An allocation that cannot be satisfied may enter **direct reclaim** if its allocation flags allow it. Watermarks are part of that decision; memory-cgroup limits, fragmentation, allocation order and reclaim restrictions also matter. Not every allocation below min performs reclaim. This is a common source of mysterious latency spikes.

`vm.min_free_kbytes` and `vm.watermark_scale_factor` tune these levels.

## Thrashing

Every process has a **working set**: the pages it is actively using over a recent window (Peter Denning's model, 1968). If the working sets of all running processes fit in RAM, faults are rare.

When sustained demand outruns available resident capacity, repeated faults can evict pages needed again soon, which causes another fault, which evicts another needed page. The system spends its time moving pages, not running programs. That is **thrashing**.

```
throughput
  ^     ____
  |    /    \
  |   /      \
  |  /        \___ thrashing
  | /
  +-------------------> processes
           ^ working sets exceed RAM
```

Possible symptoms include high refault/reclaim rates, swap or file I/O, pressure stalls and poor responsiveness. Thrashing does not require swap, a saturated disk, a particular iowait value or a fixed login delay.

Adding CPU does not solve the illustrated capacity shortage; adding memory-demanding jobs can worsen it. The cures reduce demand on memory:

- **Run fewer things.** Classic OS texts suspend or swap out whole processes. Today that means scheduling fewer jobs per machine, or letting an OOM killer act.
- **Page-fault frequency control**: give a process more frames if its fault rate is high, take frames away if it is low.
- **Add RAM**, or shrink the working set (smaller caches, better locality).

### Measuring pressure

Free memory alone is misleading, since Linux keeps RAM full of cache. **Pressure stall information (PSI)** reports the share of time tasks were stalled waiting for memory:

```
$ cat /proc/pressure/memory
some avg10=12.31 avg60=8.05 ...
full avg10=4.10 avg60=2.77 ...
```

`some` means at least one task was stalled; `full` means all non-idle tasks were stalled at once. Tools like **systemd-oomd** and Meta's **oomd** can kill selected workloads according to configured pressure and cgroup policies before a kernel allocation failure; timing and enabled policies vary.

## Key takeaways
- Page replacement chooses a victim frame on a fault; because misses are so expensive, good choices matter more than for CPU caches.
- OPT evicts the page used furthest in the future; it is unrealisable but is the benchmark.
- FIFO is simple but evicts hot pages and suffers Belady's anomaly; LRU and OPT are stack algorithms and cannot.
- Exact page recency tracking is generally too costly on commodity systems; clock approximates it with access bits, and dirty state informs writeback cost.
- Linux uses active and inactive lists per page type for scan resistance, refault detection to spot thrashing, and MGLRU on newer kernels; kswapd reclaims in the background, direct reclaim stalls allocators.
- Excess resident demand can cause repeated eviction/refault and poor throughput. PSI measures memory stalls, which can have causes beyond thrashing.

## Further reading
- [OSTEP: Beyond Physical Memory: Policies (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys-policy.pdf)
- [Page replacement algorithm — Wikipedia](https://en.wikipedia.org/wiki/Page_replacement_algorithm)
- [Bélády's anomaly — Wikipedia](https://en.wikipedia.org/wiki/B%C3%A9l%C3%A1dy%27s_anomaly)
- [Thrashing — Wikipedia](https://en.wikipedia.org/wiki/Thrashing_(computer_science))
- [The multi-generational LRU — LWN.net](https://lwn.net/Articles/851184/)
- [Multi-Gen LRU — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/multigen_lru.html)
- [Pressure stall information — Linux kernel docs](https://www.kernel.org/doc/html/latest/accounting/psi.html)
- [Page Frame Reclamation, from Understanding the Linux Virtual Memory Manager](https://www.kernel.org/doc/gorman/html/understand/understand013.html)
