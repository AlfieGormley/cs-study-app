---
id: asql-login-islands
title: Gaps and islands in login dates
level: advanced
minutes: 3
summary: Subtracting a row number gives one key for a consecutive-day run.
sourceLesson: asql-interview-problems
---

logins(user_id, day) stores ISO calendar dates. A login streak is a run of consecutive days. This example has one row per day and finds one user’s streaks; timezone boundaries must be settled before producing the day column.

## 5. Gaps and islands

"Find each user's streaks of consecutive login days." User 1 logged in on 1, 2, 3, 5, 6 and 9 March.

The trick: subtract a row number from the date. Within a run of consecutive days, both go up by one each row, so the difference is constant. A gap changes it.

```formula
g_i = d_i − rn_i
g_1 = 60 − 1 = 59
g_4 = 64 − 4 = 60
where
g_i: the island key of row i; rows with the same key form one island (run)
d_i: the date of row i, written here as its day number in 2026: 1 March is day 60 (January has 31 days, February 28), and 5 March is day 64
rn_i: row i's ROW_NUMBER() in date order, used as a number of days
i: the row's position, starting at 1
g_1, g_4: the keys for rows 1 and 4: day 59 is 28 February and day 60 is 1 March, matching the table below
In words: subtracting the row number cancels the steady one-day-per-row climb inside a run, so every day in a run gets the same key, and each gap moves the key forward.
```

| day | row position | island key |
|---|---|---|
| 03-01 | 1 | 02-28 |
| 03-02 | 2 | 02-28 |
| 03-03 | 3 | 02-28 |
| 03-05 | 4 | 03-01 |
| 03-06 | 5 | 03-01 |
| 03-09 | 6 | 03-03 |

Group by that difference:

```sql
-- Consecutive dates share an island key.
WITH g AS (
  SELECT day,
    date(day, '-' || ROW_NUMBER()
      OVER (ORDER BY day) || ' days')
      AS grp
  FROM logins
  WHERE user_id = 1
)
SELECT MIN(day) AS start,
       MAX(day) AS finish,
       COUNT(*) AS len
FROM g
GROUP BY grp;
```

| start | finish | len |
|---|---|---|
| 2026-03-01 | 2026-03-03 | 3 |
| 2026-03-05 | 2026-03-06 | 2 |
| 2026-03-09 | 2026-03-09 | 1 |

In Postgres, date minus integer is a date, so the group key is just `day - ROW_NUMBER() OVER (ORDER BY day)::int`. For several users, add `PARTITION BY user_id` and group by both user_id and grp.

The trick assumes **one row per day**. Two logins on the same day would break the arithmetic, so de-duplicate first (`SELECT DISTINCT user_id, day`). DENSE_RANK also fixes the island key with repeated days, but COUNT(*) would still count logins; use COUNT(DISTINCT day) for streak length.

An alternative that also handles "gaps of up to N days" is to compare each row with `LAG(day)`, flag a new island when the gap exceeds the limit, and take a running `SUM` of the flags as the island id.

## Key takeaways
- Subtracting a row number gives one key for a consecutive-day run.
- Deduplicate days before numbering or count distinct days after dense ranking.

## Further reading
- [PostgreSQL 18: sql select](https://www.postgresql.org/docs/18/sql-select.html)
- [PostgreSQL 18: functions aggregate](https://www.postgresql.org/docs/18/functions-aggregate.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
