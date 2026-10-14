---
id: db-storage-amplification-accounting
title: Account for storage amplification
level: advanced
minutes: 4
summary: Measure physical work against logical work and compute a small-change page rewrite under explicit assumptions.
sourceLesson: db-storage-internals
---

One logical write can create page writes, logs and compaction output. Compare engines by counting those physical costs under the same scope and workload assumptions.

## The three amplifications

**Write amplification**: bytes written to disk ÷ bytes the application wrote. **Read amplification**: disk reads per logical read. **Space amplification**: bytes on disk ÷ size of live data.

```formula
WA = B_disk / B_app
RA = R_disk / R_logical
SA = S_disk / S_live
where
WA: write amplification, a ratio with no unit; 1 would mean every byte is written exactly once
B_disk: the bytes the engine physically writes to storage (pages, WAL, compaction output), in bytes
B_app: the bytes of data the application asked to write, in bytes
RA: read amplification, a ratio with no unit
R_disk: the number of disk reads the engine performs
R_logical: the number of reads the application asked for, e.g. point lookups
SA: space amplification, a ratio with no unit
S_disk: the space the database uses on disk, in bytes
S_live: the size of the data that is still current (not overwritten or deleted), in bytes
In words: each amplification measures how much more work or space the engine uses than the bare data needs; lower is better.
```

For example, if the application writes 1 GB a day and the engine writes 12 GB to disk, the write amplification is 12. Always say what you counted (WAL? compaction? the SSD's own internal copying?) because each choice gives a different number.

| | B-tree | LSM leveled | LSM tiered |
|---|---|---|---|
| Write amp | Medium–high | High | Low |
| Read amp | Low | Low–med | Higher |
| Space amp | Depends on page fill and retained versions | Depends on levels, versions and temporary output | Depends on retained files and temporary output |

A B-tree's write amplification comes from writing a whole 8–16 KB page (plus WAL, plus full-page images) for a small change. The key variable is how many changes a page collects before it's written back:

- Sequential inserts or a hot working set that fits in RAM: many changes per page write, so the amplification is modest.
- Random updates to a table far bigger than RAM: perhaps one 100-byte change per 16 KB page write, which is over 150×, and InnoDB's doublewrite buffer doubles it.

```formula
WA = 16,384 B / 100 B ≈ 164
WA_dw = 2 × 164 ≈ 328
where
WA: write amplification of the page write alone
WA_dw: write amplification once InnoDB's doublewrite buffer writes each page twice
B: bytes; an InnoDB page is 16 KiB = 16,384 bytes
≈: approximately equal to
In words: rewriting a whole 16 KiB page to save a 100-byte change writes about 164 times more than the change itself, and doublewrite doubles that.
```

This is a worst case: it ignores the WAL and assumes no other change lands on the page before it is written.

Leveled LSM amplification comes from compaction overlap and repeated rewriting. No universal 10–30× range or winner is supplied because a matched workload benchmark is absent. Compare measured read/write latency and amplification: an LSM read may check several levels, and background compaction competes for I/O.

The **RUM conjecture** formalises the trade: you can optimise for two of Read, Update and Memory (space) overheads, at the expense of the third. Every engine picks a point; tuning moves it.

On SSDs, write amplification also matters because flash cells wear out after a limited number of program/erase cycles.

## Key takeaways
- Write, read and space amplification compare physical cost with application work or live data.
- A whole-page flush for one tiny change can amplify writes sharply; coalescing changes reduces that cost.
- State what is counted and use measured workload values rather than a universal engine winner.

## Further reading
- [stratos.seas.harvard.edu: designing access methods rum conjecture](https://stratos.seas.harvard.edu/publications/designing-access-methods-rum-conjecture)
- [dev.mysql.com: innodb doublewrite buffer](https://dev.mysql.com/doc/refman/8.4/en/innodb-doublewrite-buffer.html)
