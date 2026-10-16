---
id: rel-th-counter-maintenance
title: Maintaining counters under writes
level: advanced
minutes: 2
sourceLesson: rel-th-denormalisation
summary: Maintaining counters under writes, with explicit examples and the conditions that make the reasoning valid.
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

## Key takeaways

- A database counter update avoids a lost increment but makes one parent row a contention point.
- Cover every mutation event and reconcile stored counts with their source.

## Further reading

- [PostgreSQL 18: refresh materialised views](https://www.postgresql.org/docs/18/sql-refreshmaterializedview.html)
- [PostgreSQL 18: generated columns](https://www.postgresql.org/docs/18/ddl-generated-columns.html)
- [AWS: transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- [PostgreSQL 18: row locks](https://www.postgresql.org/docs/18/explicit-locking.html)
- [PostgreSQL 18: CREATE TRIGGER](https://www.postgresql.org/docs/18/sql-createtrigger.html)
