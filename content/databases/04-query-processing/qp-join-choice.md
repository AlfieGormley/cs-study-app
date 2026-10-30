---
id: qp-join-choice
title: Index probes and the join crossover
level: intermediate
minutes: 4
sourceLesson: qp-join-algorithms
summary: Why an index nested loop wins for a few outer rows and loses for many, and why the outer row estimate decides the join.
---

This lesson uses the textbook page-I/O model, which counts page transfers between disk and memory. It is a way of reasoning about algorithms, not PostgreSQL's planner cost units.

## Index nested loop

Instead of scanning the inner table S for each outer row, probe an index on S's join column. Each probe walks down a B-tree and then fetches the matching row from the table. In a cold-cache model, a 3-level B-tree plus one table page is about 4 random page reads per outer row:

```formula essential
C_INL = M + |R| × c_probe
where
C_INL: the cost of an index nested loop join, in page I/Os
M: the number of pages in the outer table R
R: the outer table
|R|: the number of rows in R that reach the join
c_probe: the page reads for one index lookup, about 4 for a 3-level B-tree plus one table page
In words: one index lookup per outer row, so the cost grows with the number of outer rows and hardly at all with the size of the indexed inner table.
```

That shape is the whole story of join choice:

- For 100 outer rows, the probes cost about 400 page reads, far less than scanning and hashing a large inner table.
- For 100,000 outer rows, they cost about 400,000 random reads, far more than reading both tables once for a hash join.
- A hash join's cost hardly changes with the outer row count, because it reads each table once whatever happens.

So there is a **crossover**: below some number of outer rows, index probes win; above it, scanning and hashing wins. PostgreSQL's planner draws the same picture with its own cost units, where a random page read (`random_page_cost`, default 4.0) costs four times a sequential one. Lowering `random_page_cost` makes each probe look cheaper and moves the crossover towards more outer rows.

The crossover is also why a wrong **outer row estimate** is dangerous. If the planner believes 10 rows will reach the join and 100,000 actually do, it picks the probe plan on the cheap side of the crossover and runs it far beyond.

## Why only three levels?

Each B-tree page holds hundreds of keys, so every level multiplies the number of reachable entries by hundreds:

```formula reference
h = ⌈log_f(n)⌉
where
h: an idealised number of page levels on a root-to-leaf path, assuming every page has fanout f; real occupancy and page metadata change the height
n: the number of entries in the index, greater than one
f: the assumed fanout, the number of child pointers per page, greater than one; a few hundred for small keys in 8 KiB pages
log_f: the logarithm to base f: how many times you must divide by f to get down to 1
⌈ ⌉: ceiling: round up to the next whole number
In words: with a few hundred entries per page, three levels already reach millions of entries, so a lookup stays a handful of page reads even in a big table. A fanout of 300 reaches 27 million entries in three levels.
```

The upper levels are read on almost every lookup, so they are usually already in memory, and a real probe often needs fewer than four disk reads.

## Key takeaways
- A cold index probe pays for B-tree traversal and heap access; cached tree levels can reduce physical reads.
- Index probes cost per outer row while a hash join's cost barely depends on it, so the outer row estimate decides which side of the crossover the planner thinks it is on.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)


