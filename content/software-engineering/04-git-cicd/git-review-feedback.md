---
id: git-review-feedback
title: Working through a review and giving feedback
level: intermediate
minutes: 4
sourceLesson: git-code-review
summary: Mutable defaults retain state across calls; interpolated SQL values allow injection.
---

Review design before details, and separate mechanical changes from behaviour changes. Now apply that priority to a concrete Python function and communicate the findings so the author can act.

## A worked review

Here is an example function that looks fine at a glance. It assumes a SQLite connection and an `orders` table; the next version keeps that interface while fixing the query construction.

```python
def find_orders(db, email, statuses=[]):
    # BUG: retain state across calls.
    statuses.append("open")
    sql = (
        "SELECT * FROM orders "
        # BUG: input becomes SQL syntax.
        f"WHERE email = '{email}' "
        f"AND status IN {tuple(statuses)}"
    )
    return db.execute(sql).fetchall()
```

Useful comments, in priority order:

1. **Security (blocking).** The query builds SQL with an f-string, so an email such as x' OR 1=1 -- can turn this SQLite query into an unconditional selection while commenting out the malformed trailing clause. Use parameters: `db.execute(sql, params)`.
2. **Bug (blocking).** `statuses=[]` is a mutable default. It is created once, so `"open"` is appended on every call and the list grows forever. Use `statuses=None`.
3. **Bug (blocking).** With an empty list plus "open", `tuple(statuses)` renders as `('open',)`. That trailing comma is invalid SQL. Parameterising fixes this too.
4. **Tests.** No test covers this function. A test calling it twice would have caught point 2.
5. **Nit:** `SELECT *` couples callers to every column; consider listing the ones you need.

A fixed version for Python sqlite3 (other drivers can use different placeholder syntax):

```python
def find_orders(db, email, statuses=None):
    # Keep the caller's list unchanged.
    wanted = list(statuses or []) + ["open"]
    # Interpolate placeholders, not values.
    marks = ", ".join("?" * len(wanted))
    sql = (
        "SELECT id, total, status "
        "FROM orders WHERE email = ? "
        f"AND status IN ({marks})"
    )
    # Bind every value through the driver.
    rows = db.execute(sql, [email, *wanted])
    return rows.fetchall()
```

Only the placeholders are interpolated; every value goes through the driver as a parameter.

## Writing good comments

- **Comment on the code, not the person.** "This loop re-reads the file each time" rather than "you wrote a slow loop".
- **Explain why.** "This needs a lock because two workers can call it at once" teaches; "add a lock" just instructs.
- **Label severity.** Google suggests prefixes like `Nit:` (minor, take or leave), `Optional:` or `Consider:`, and `FYI:` (for future reference). Some teams use the Conventional Comments format (`suggestion:`, `issue (blocking):`, `question:`).
- **Ask questions when unsure.** "What happens if `items` is empty here?" invites the author to check, and you may learn they already handled it.
- **Big disagreements go to a call.** After two rounds of back and forth in comments, talk. Then write the outcome in the PR for posterity.

## Being a good author

- **Write a description** that says what changed, why, and how it was tested. Link the ticket. Reviewers should not have to reverse-engineer intent from the diff.
- **Review your own diff first.** Debug prints, commented-out code and unrelated formatting changes are easy to spot in the PR view.
- **Make CI green before asking.** Do not spend a reviewer's attention on something the robot will reject.
- **Respond to every comment**, even if only "Done". If you disagree, explain why; reviewers can be wrong too.

## Key takeaways

- Mutable defaults retain state across calls; interpolated SQL values allow injection.
- Bind SQL values through the driver and build only placeholder syntax dynamically.
- Explain the reason and severity of comments, and supply intent and validation as the author.

## Further reading

- [Google Engineering Practices: Code Review](https://google.github.io/eng-practices/review/)
- [Conventional Comments](https://conventionalcomments.org/)
