---
id: qp-execution-models
title: Batches, compilation and workers
level: basic
minutes: 3
sourceLesson: qp-execution
summary: Vectorised, compiled and parallel execution as alternatives to one-row-at-a-time iterators, and what each one changes.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## Other execution models

The iterator model pays a function call per row per operator. That overhead is noticeable for analytical queries over billions of rows, so other designs exist:

- **Vectorised execution** (DuckDB, ClickHouse; Snowflake's 2016 design paper): operators process batches of values instead of one row per call; batch layout and size vary by engine, so loops are tight and CPU-cache friendly.
- **Compiled execution** (HyPer, Umbra, SingleStore): the plan is compiled to machine code that fuses operators into a single loop. Postgres has a limited form of this: it can **JIT-compile** expressions with LLVM for expensive queries.
- **Parallel query**: Postgres can split a scan across worker processes and gather their results through a `Gather` node. You'll see `Gather` and `Parallel Seq Scan` in real plans on big tables.

> [!analogy] Real-world analogy: carrying shopping in from the car
> You can carry one tin at a time from the car to the cupboard, or fill a box and carry thirty. The walking is the same each trip, so the box spreads that fixed cost over many tins. Asking a friend to help is a different improvement: two people walking at once.
>
> **How it maps:** each trip is a `next()` call with its fixed overhead. The box is a vectorised batch, which spreads that overhead over many values and keeps the CPU in a tight loop. The friend is a parallel worker process.
>
> **Where it stops:** batching does not reduce how much data must be read from storage, and a larger box is not always better: batches too big for the CPU caches lose some of the benefit.

Vectorisation batches CPU work; parallelism uses concurrent workers. They are separate choices: either model can run in one process or be combined with parallel work. Compilation is another axis and may fuse several operators. PostgreSQL expression JIT does not compile an entire query into one fused native loop.

The ideas in this module (plans as trees, join algorithms, cost estimation) apply to all of them.

## Key takeaways
- Vectorised execution amortises per-row calls; compilation can fuse work and reduce interpreter overhead.
- Workers add parallelism, which is separate from vectorisation and does not guarantee proportional speedup.

Snowflake's 2016 paper describes a columnar, vectorised engine with **push-based query execution**; it is a historical architecture example, rather than a promise about every current implementation detail.

## Further reading
- [The Snowflake Elastic Data Warehouse, section 3.2.3 (2016)](https://info.snowflake.net/rs/252-RFO-227/images/Snowflake_SIGMOD.pdf)
- [Neumann: compiling query plans for modern hardware (2011)](https://www.vldb.org/pvldb/vol4/p539-neumann.pdf)
- [Overview of PostgreSQL internals: the path of a query](https://www.postgresql.org/docs/18/query-path.html)
- [The PostgreSQL executor](https://www.postgresql.org/docs/18/executor.html)
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/18/using-explain.html)
- [Query plan — Wikipedia](https://en.wikipedia.org/wiki/Query_plan)
- [Parallel query — PostgreSQL docs](https://www.postgresql.org/docs/18/parallel-query.html)

