---
id: db-storage-amplification-accounting
title: Account for storage amplification
level: advanced
minutes: 4
summary: Compare physical work with logical work and predict when whole-page rewrites amplify small changes.
sourceLesson: db-storage-internals
---

One logical write can create page writes, logs and compaction output. Compare engines by counting those physical costs under the same scope and workload assumptions.

## The three amplifications

Each amplification compares what the engine physically does with what the application asked for. **Write amplification** compares bytes written to storage with bytes the application wrote; **read amplification** compares disk reads with logical reads; **space amplification** compares space on disk with the size of the live data. Lower is better for all three.

```formula essential
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
In words: each amplification measures how much more work or space the engine uses than the bare data needs.
```

For example, if the application writes 1 GB a day and the engine writes 12 GB to disk, the write amplification is 12. Always say what you counted (WAL? compaction? the SSD's own internal copying?) because each choice gives a different number.

| | B-tree | LSM leveled | LSM tiered |
|---|---|---|---|
| Write amp | Medium–high | High | Low |
| Read amp | Low | Low–med | Higher |
| Space amp | Depends on page fill and retained versions | Depends on levels, versions and temporary output | Depends on retained files and temporary output |

A B-tree's write amplification comes from writing a whole 8–16 KB page (plus WAL, plus full-page images) for a small change. The key variable is how many changes a page collects before it's written back:

- Sequential inserts or a hot working set that fits in RAM: many changes per page write, so the amplification is modest.
- Random updates to a table far bigger than RAM: perhaps one 100-byte change per 16 KB page write, which is over 150 times the change, and InnoDB's doublewrite buffer writes each page twice, doubling that. This simplified estimate assumes no other change lands on the page before it is written, the worst case for coalescing, and leaves out the redo log and device-level copying, which add more.

So the same engine can have modest or severe write amplification depending on whether changes cluster on pages that stay in memory. More memory, or keys that keep hot rows together, lowers it.

Leveled LSM amplification comes instead from compaction overlap and repeated rewriting, so it depends on level sizes, overlap and update patterns. Neither family wins universally: compare measured read and write latency and amplification on your workload, remembering that an LSM read may check several levels and background compaction competes for I/O.

The **RUM conjecture** formalises the trade: you can optimise for two of Read, Update and Memory (space) overheads, at the expense of the third. Every engine picks a point; tuning moves it.

On SSDs, write amplification also matters because flash cells wear out after a limited number of program/erase cycles.

## Key takeaways
- Write, read and space amplification compare physical cost with application work or live data.
- A whole-page flush for one tiny change can amplify writes sharply; coalescing changes reduces that cost.
- State what is counted and use measured workload values rather than a universal engine winner.

## Further reading
- [stratos.seas.harvard.edu: designing access methods rum conjecture](https://stratos.seas.harvard.edu/publications/designing-access-methods-rum-conjecture)
- [dev.mysql.com: innodb doublewrite buffer](https://dev.mysql.com/doc/refman/8.4/en/innodb-doublewrite-buffer.html)
