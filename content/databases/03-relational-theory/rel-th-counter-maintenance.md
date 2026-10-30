---
id: rel-th-counter-maintenance
title: Maintaining counters under writes
level: advanced
minutes: 2
sourceLesson: rel-th-denormalisation
summary: Trigger-maintained counters: what they save, the hot-row contention they create and the events they must cover.
---

## Counters and write contention

`post.comment_count` saves a `COUNT(*)` over comments on every page view. If a post page is read 1,000 times a second and gets 5 comments a second, you trade 1,000 counts for 5 increments.

A trigger keeps it in step within the same transaction:

```sql
CREATE FUNCTION bump_count()
RETURNS trigger AS $$
BEGIN
  UPDATE post
     SET comment_count = comment_count + 1
   -- Increment the parent for this comment.
   WHERE id = NEW.post_id;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER comment_ins
AFTER INSERT ON comment
FOR EACH ROW EXECUTE FUNCTION bump_count();
```

The fixture assumes `post.id` is a primary key, `comment.post_id` is a non-null foreign key, and `post.comment_count` is non-null and initialised to zero. Each inserted comment adds one; rolling back its transaction also rolls back the increment. A production implementation must cover deletion, moving a comment between posts, bulk maintenance and any path that bypasses ordinary row triggers, such as `TRUNCATE`. This insert-only example intentionally demonstrates drift when another event is omitted. The hidden cost is **contention**. Every comment on a viral post updates the same row, and each `UPDATE` holds that row's lock until its transaction commits, so writers queue behind one another. Remedies: split the counter into several rows (say 16) and sum them on read (sharded counters), or buffer increments and apply them in batches.

> [!analogy] Real-world analogy: one tally clicker at a busy gate
> A stadium counts fans with a single hand-held clicker passed between stewards. Each steward must wait for the clicker before counting the next fan, so the queue grows at the busiest gate. Give each gate its own clicker and add the totals when someone asks.
>
> **How it maps:** The shared clicker is the single `comment_count` row, waiting for it is waiting for the row lock, and per-gate clickers summed on demand are sharded counter rows.
>
> **Where it stops:** A steward holds the clicker only for a moment. A database transaction holds the row lock until it commits, so a slow transaction elsewhere stretches every wait, and a rollback must also undo its click.

## Key takeaways

- A database counter update avoids a lost increment but makes one parent row a contention point.
- Cover every mutation event and reconcile stored counts with their source.

## Further reading

- [PostgreSQL 18: refresh materialised views](https://www.postgresql.org/docs/18/sql-refreshmaterializedview.html)
- [PostgreSQL 18: generated columns](https://www.postgresql.org/docs/18/ddl-generated-columns.html)
- [AWS: transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- [PostgreSQL 18: row locks](https://www.postgresql.org/docs/18/explicit-locking.html)
- [PostgreSQL 18: CREATE TRIGGER](https://www.postgresql.org/docs/18/sql-createtrigger.html)
