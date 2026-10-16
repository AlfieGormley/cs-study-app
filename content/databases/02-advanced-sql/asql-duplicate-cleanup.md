---
id: asql-duplicate-cleanup
title: Removing duplicates and preventing their return
level: advanced
minutes: 3
summary: Keep a chosen survivor before deleting other rows with the same email.
sourceLesson: asql-interview-problems
---

signups has id as a primary key and email declared NOT NULL. ids 1, 3 and 6 use a@x.io; ids 2 and 5 use b@x.io; id 4 uses c@x.io.

## 4. Duplicates

"Find emails that appear more than once, then delete all but the earliest."

```sql
-- Keep the smallest id for each email.
SELECT email, COUNT(*)
FROM signups
GROUP BY email
HAVING COUNT(*) > 1;
```

With six signups where `a@x.io` appears three times and `b@x.io` twice, that returns those two emails. Assume email is NOT NULL and id is a non-NULL primary key. To delete, keep the lowest `id` per email (this means earliest only if ids encode insertion order):

```sql
-- Keep the smallest id for each email.
DELETE FROM signups
WHERE id NOT IN (
  SELECT MIN(id)
  FROM signups
  GROUP BY email);
-- ids 1, 2, 4 survive
```

`NOT IN` is safe here because `MIN(id)` of a primary key is never NULL. A Postgres-idiomatic version uses a self-join:

```sql
-- Keep the smallest id for each email.
DELETE FROM signups a
USING signups b
WHERE a.email = b.email
  AND a.id > b.id;
```

Every row with a lower-id twin is deleted. Then add a `UNIQUE` constraint so the duplicates can't come back, which is the answer interviewers actually want to hear. Without it, two concurrent sign-ups can still race past an application-level check.

## Key takeaways
- Keep a chosen survivor before deleting other rows with the same email.
- A UNIQUE constraint protects against future concurrent duplicates.

## Further reading
- [PostgreSQL 18: sql select](https://www.postgresql.org/docs/18/sql-select.html)
- [PostgreSQL 18: functions aggregate](https://www.postgresql.org/docs/18/functions-aggregate.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
