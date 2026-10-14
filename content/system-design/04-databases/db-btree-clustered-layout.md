---
id: db-btree-clustered-layout
title: B-tree depth and clustered row layout
level: intermediate
minutes: 4
summary: Estimate shallow tree depth and explain how InnoDB primary-key layout affects secondary indexes and inserts.
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

- Each node is one **database page** (typically 4–16 KB) holding hundreds of keys, so the tree is very wide and shallow. With a B-tree fan-out of 500, four levels address 500⁴ ≈ 62 billion keys.
- Lookups walk root → leaf: O(log n), usually 3–4 page reads, and the top levels are almost always in memory. Here n is the number of keys in the index.
- Leaves are sorted and linked, so **range scans** (`BETWEEN`, `>`, `ORDER BY`) are efficient.
- Writes **update pages in place**. Inserting into a full page *splits* it into two. To survive crashes, every change is first written to the write-ahead log (see the storage internals lesson).

Why so shallow? Each level multiplies the number of keys the tree can reach by the **B-tree fan-out**, the number of child pointers per page. So the depth only grows with the logarithm of the number of keys:

```formula
n_max = f^h
h = ⌈log_f(n)⌉
where
n_max: the most keys a tree of this height can address
f: the B-tree fan-out, the number of children per page; typically a few hundred
h: the height, the number of levels from root to leaf, which is also the number of page reads per lookup
n: the number of keys in the index
log_f: the logarithm to base f: how many times you must multiply f by itself to reach n
⌈ ⌉: ceiling: round up to the next whole number, because a tree can't have part of a level
In words: every extra level multiplies the capacity by the B-tree fan-out, so a tree with hundreds of children per page needs only 3–4 levels even for billions of keys.
```

For this simplified estimate, assume full internal pages with 500 children and full leaves with 500 keys. Actual occupancy and leaf capacity can differ. For a B-tree fan-out of 500:

```formula
n_max = 500^4
n_max = 62,500,000,000
where
n_max: the most keys four levels can address, about 62 billion
In words: four levels of 500-way branching reach about 62 billion keys, so a lookup in a table of tens of billions of rows still reads only four pages.
```

That is the meaning of O(log n) here: doubling n adds almost nothing to the height. The estimate assumes full pages; real pages are rarely completely full, which lowers the effective B-tree fan-out a little but barely changes the height.

In InnoDB, the table *is* a B-tree clustered on the primary key, and secondary indexes store the primary key as their pointer. In Postgres, the table is an unordered heap and every index points to a physical tuple location.

That design choice has practical consequences in InnoDB:

- A non-covering secondary-index lookup generally needs two B-tree walks: find the primary key in the secondary index, then find the row in the clustered index.
- Every secondary index entry carries a copy of the primary key, so a wide key (a 36-character UUID string) bloats every index.
- Rows are stored in key order, so random keys (UUIDv4) insert all over the tree and cause page splits, while increasing keys (auto-increment, or time-ordered UUIDv7) append at the right-hand edge.
- Such a query is covered by the secondary index, but InnoDB may still visit the clustered record for MVCC visibility.

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
