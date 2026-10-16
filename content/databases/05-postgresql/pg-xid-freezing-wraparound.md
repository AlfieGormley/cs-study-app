---
id: pg-xid-freezing-wraparound
title: Why transaction IDs need freezing
level: intermediate
minutes: 4
sourceLesson: postgresql-in-practice
summary: Normal XID comparisons have an approximately two-billion-ID horizon.
---

PostgreSQL assigns a normal **transaction ID** (XID) when a transaction needs one, commonly when it first writes. A read-only transaction can also request an XID explicitly. Row-version headers use a 32-bit XID; newer SQL functions can expose a 64-bit full ID that includes an XID epoch. MVCC compares XIDs to decide whether a row version was written in the past (possibly visible) or the future (invisible). An XID counter has a fixed number of values and the comparison is circular, so only half of them can count as "the past":

```formula
N_xid = 2^32 = 4294967296 XIDs
H = N_xid / 2 = 2^31 XIDs
H = 2147483648 XIDs
where
N_xid: the total number of different values a 32-bit transaction ID can hold, about 4.3 billion
2^32: 32 copies of 2 multiplied together; each of the 32 bits doubles the number of possible values
H: the comparison horizon: for any XID, half the 32-bit XID representation’s possible values; the safe ordering window is approximately this large, with special reserved IDs and ordering-boundary exclusions
2^31: 31 copies of 2 multiplied together, half of 2^32
XIDs: transaction IDs, the unit counted here; normal transactions and subtransactions can consume them; allocation is not one XID for every SELECT
In words: any transaction ID can only look about 2.1 billion IDs into the past; anything further back would appear to be in the future.
```

If a row version kept its original XID while the counter moved more than about 2.1 billion transactions on, it would suddenly look as if it came from the future, and committed data would vanish from queries. This is **transaction ID wraparound**. VACUUM prevents it by **freezing** old row versions: marking their committed insertion as old enough to be visible to every current and future transaction, so that insertion XID no longer needs normal comparison. A later deletion or update still has its own visibility rules.

Postgres forces an anti-wraparound vacuum on any table whose oldest unfrozen XID is more than `autovacuum_freeze_max_age` XIDs old: 200 million by default, about one tenth of the 2.1 billion horizon, leaving a wide safety margin. These limits count allocated IDs rather than elapsed time or a simple number of top-level commits. It launches these even when autovacuum is disabled. If something such as a long-open transaction stops freezing from advancing, the server warns as the limit approaches and eventually refuses to assign new XIDs until vacuum catches up.

## Key takeaways

- Normal XID comparisons have an approximately two-billion-ID horizon.
- Freezing preserves old committed row visibility across wraparound.
- Anti-wraparound maintenance can run even when autovacuum is disabled.

## Further reading

- [PostgreSQL 18: routine vacuuming](https://www.postgresql.org/docs/18/routine-vacuuming.html)
- [PostgreSQL 18: datatype oid](https://www.postgresql.org/docs/18/datatype-oid.html)
- [PostgreSQL 18: functions info](https://www.postgresql.org/docs/18/functions-info.html)
