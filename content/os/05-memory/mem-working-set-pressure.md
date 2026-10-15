---
id: mem-working-set-pressure
sourceLesson: mem-page-replacement
title: Working sets, thrashing and pressure stalls
level: intermediate
minutes: 4
summary: A working set counts distinct pages within a chosen recent window.
---

## Thrashing

Every process has a **working set**: the pages it is actively using over a recent window (Peter Denning's model, 1968). Denning’s original paper defines the window in the process’s own execution time. Here we explicitly use a discrete teaching model counted in memory references instead:

```formula
W(t, Δ) = {r_i  for t − Δ < i ≤ t}
where
W(t, Δ): the working set at time t: the set of distinct pages referenced in the last Δ references
t: the current time, counted in references (the t-th reference made so far)
Δ: delta, the window size: how many recent references count
r_i: the page referenced at time i
i: a reference time inside the window, from t − Δ + 1 to t
{ }: a set: each distinct page counts once, however often it is referenced
In words: look back over the last Δ references and list the different pages touched; the size of that set is roughly how many frames the process needs right now.
```

For example, with a four-reference window containing 4, 4, 3, 4, the working set is {3, 4}: two pages, so about two frames, even though four references were made. A window that is too short misses pages needed again soon; an overly long window includes pages from an earlier phase.

If the working sets of all running processes fit in RAM, faults are rare.

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

Illustrative command/output sample; actual values depend on the workload, system and observation interval:

```
$ cat /proc/pressure/memory
some avg10=12.31 avg60=8.05 ...
full avg10=4.10 avg60=2.77 ...
```

`some` means at least one task was stalled; `full` means all non-idle tasks were stalled at once. Tools like **systemd-oomd** and Meta's **oomd** can kill selected workloads according to configured pressure and cgroup policies before a kernel allocation failure; timing and enabled policies vary.

## Key takeaways
- A working set counts distinct pages within a chosen recent window.
- Excess resident demand can cause repeated eviction and refault rather than useful progress.
- PSI measures stalls; reducing demand or adding capacity addresses the illustrated shortage.

## Further reading
- [Denning: The Working Set Model for Program Behavior (1968)](https://denninginstitute.com/pjd/PUBS/WSModel_1968.pdf)
- [OSTEP: Beyond Physical Memory: Policies (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys-policy.pdf)
- [Page replacement algorithm — Wikipedia](https://en.wikipedia.org/wiki/Page_replacement_algorithm)
- [Bélády's anomaly — Wikipedia](https://en.wikipedia.org/wiki/B%C3%A9l%C3%A1dy%27s_anomaly)
- [Thrashing — Wikipedia](https://en.wikipedia.org/wiki/Thrashing_(computer_science))
- [The multi-generational LRU — LWN.net](https://lwn.net/Articles/851184/)
- [Multi-Gen LRU — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/multigen_lru.html)
- [Pressure stall information — Linux kernel docs](https://www.kernel.org/doc/html/latest/accounting/psi.html)
- [Page Frame Reclamation, from Understanding the Linux Virtual Memory Manager](https://www.kernel.org/doc/gorman/html/understand/understand013.html)
