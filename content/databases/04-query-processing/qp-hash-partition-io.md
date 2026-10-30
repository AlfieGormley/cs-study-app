---
id: qp-hash-partition-io
title: Hash partitioning and in-memory join I/O
level: intermediate
minutes: 3
sourceLesson: qp-join-algorithms
summary: How a Grace hash join partitions both tables so each piece fits in memory, what that costs in page I/O, and when one read of each table is enough.
---

This lesson uses the textbook page-I/O model, which counts page transfers between disk and memory. It is a way of reasoning about algorithms, not PostgreSQL's planner cost units.

It uses the same set-up as the nested-loop lesson: R occupies 1,000 pages, S occupies 500 pages and the join has 102 buffer pages. CPU work, partition slack and final output writes are excluded.

## Grace hash

When neither table fits in memory, split the problem into pieces that do:

1. **Partition.** Read both tables and hash each row's join key into one of 101 partitions (one fewer than the buffer pages, keeping one page for input), writing each partition to disk.
2. **Join.** Matching keys always hash to the same partition number, so partition 1 of R only needs partition 1 of S. Load one partition of the smaller table into an in-memory hash table and stream the matching partition of the other table past it, then move to the next pair.

Partitioning reads and writes every page (2 I/Os per page), and the join phase reads every partition once more (1 I/O per page). That is 3 I/Os per page of the two tables, 4,500 here.

The plan depends on each partition of the smaller table fitting in memory. S's 500 pages spread over 101 partitions gives about 5 pages each, which fits easily. If the hash spreads keys badly, some partitions are too big and must be partitioned again with a different hash function, adding another round of writes and reads. Repartitioning cannot help when one join-key value is itself too common to fit: every row with that key hashes to the same partition however often it is split, so that partition has to be joined another way (for example by a block nested loop over it) or allowed to exceed its memory budget. PostgreSQL's hash join stops adding batches in that situation and lets the oversized batch use more memory than planned. PostgreSQL's hybrid hash join, shown in the earlier hash join lesson as `Batches:` greater than 1, applies the same idea while keeping the first batch in memory.

## Hash, when S fits in memory

With a larger memory budget that holds all of S plus the hash table's overhead (unlike the 102-page set-up above), there is nothing to partition. Build the hash table from S and stream R past it: each table is read once, 1,000 + 500 = 1,500 page I/Os.

That is the lower bound for this unindexed model, because every page must be read at least once. It does not apply when an index lets a join skip most of a table.

> [!analogy] Real-world analogy: sorting post into pigeonholes
> A post room has too many letters and parcels to match on one table. Staff first drop every letter and every parcel into pigeonholes by the first letter of the surname. Then they empty one pigeonhole at a time onto the table and match its letters with its parcels.
>
> **How it maps:** the pigeonholes are partitions chosen by hashing the join key, and filling them is the partition phase that writes everything out once. Matching one pigeonhole at a time is the join phase, which only works because a surname always lands in the same pigeonhole on both sides.
>
> **Where it stops:** surnames are unevenly spread, so a busy pigeonhole such as "S" may not fit on the table; a database hash spreads keys more evenly, but skewed keys can still make a partition too big and force another round of partitioning. A single very common key is like one surname shared by half the post: no re-sorting of pigeonholes can split it.

## Key takeaways
- Grace hash reads and writes partitions, then reads them for joining; the simple model excludes skew and output writes, and rows sharing one very common key can never be split across partitions.
- The single-read in-memory case needs enough space for the build table and hash overhead.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)


