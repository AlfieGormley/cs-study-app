---
id: db-btree-clustered-layout
title: B-tree depth and clustered row layout
level: intermediate
minutes: 4
summary: Explain why B-trees stay shallow and how InnoDB primary-key layout affects secondary indexes and inserts.
sourceLesson: db-indexing
---

A B-tree reaches a key through a small number of wide pages. Its row-pointer design also explains why the same primary-key choice can affect the size and locality of every secondary index.

## B-trees

The **B-tree** (strictly, the B+tree) is the default index in Postgres, MySQL InnoDB, SQL Server, Oracle and SQLite.

```
            [ 40 | 80 ]          root
          /      |      \
   [10|25]   [50|65]   [90|99]   internal
   / | \      / | \      / | \
  leaves: sorted keys + row pointers,
  linked left to right for range scans
```

- Each node is one **database page** (typically 4–16 KB) holding hundreds of keys, so the tree is very wide and shallow.
- Lookups walk root → leaf: O(log n), usually 3–4 page reads, and the top levels are almost always in memory. Here n is the number of keys in the index.
- Leaves are sorted and linked, so **range scans** (`BETWEEN`, `>`, `ORDER BY`) are efficient.
- Writes **update pages in place**. Inserting into a full page *splits* it into two. To survive crashes, every change is first written to the write-ahead log (see the storage internals lesson).

Why so shallow? Each level multiplies the number of keys the tree can reach by the **B-tree fan-out**, the number of child pointers per page. So the depth grows only with the logarithm of the number of keys:

```formula reference
h ≈ log_f(n)
where
h: the height, the number of levels from root to leaf, which is also the number of index pages read per lookup (round up to a whole level)
f: the B-tree fan-out, the number of children per page; typically a few hundred
n: the number of keys in the index
log_f: the logarithm to base f: the power you must raise f to in order to reach n
≈: approximately equal to; real pages are not completely full
In words: every extra level multiplies the capacity by the fan-out, so a tree with hundreds of children per page needs only 3–4 levels even for billions of keys.
```

With a fan-out of 500 and full pages, four levels reach about 62 billion keys. That is the practical meaning of O(log n) here: growing the table tenfold adds at most about one level, and real pages that are only partly full lower the effective fan-out a little without changing the picture.

In InnoDB, the table *is* a B-tree clustered on the primary key, and secondary indexes store the primary key as their pointer. In Postgres, the table is an unordered heap and every index points to a physical tuple location.

That design choice has practical consequences in InnoDB:

- A non-covering secondary-index lookup generally needs two B-tree walks: find the primary key in the secondary index, then find the row in the clustered index.
- Every secondary index entry carries a copy of the primary key, so a wide key (a 36-character UUID string) bloats every index.
- Rows are stored in key order, so random keys (UUIDv4) insert all over the tree and cause page splits, while increasing keys (auto-increment, or time-ordered UUIDv7) append at the right-hand edge.

## When a secondary index covers the result

An InnoDB secondary index on email also carries the primary-key id. Queries returning just email or id, or counting matching entries, have all required columns there; returning name needs the clustered row too. Being covered does not remove every possible MVCC visibility visit to the clustered index. Covering PostgreSQL queries is explained in the unit on composite and covering indexes.

## Key takeaways
- Wide B-tree fan-out makes B-trees shallow; sorted leaves also support ranges.
- InnoDB clusters rows by primary key and copies that key into secondary indexes.
- Wide random primary keys increase secondary-index size and scatter inserts.

## Further reading
- [www.postgresql.org: indexes](https://www.postgresql.org/docs/current/indexes.html)
- [MySQL: Clustered and secondary indexes](https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html)
- [www.rfc-editor.org: rfc9562](https://www.rfc-editor.org/rfc/rfc9562)
