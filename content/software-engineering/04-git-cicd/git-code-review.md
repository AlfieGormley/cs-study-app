---
id: git-code-review
title: Code review
level: intermediate
minutes: 12
summary: What review is really for, how big a change should be, what reviewers look for and in what order, writing useful comments, and the process settings that keep review fast.
---

Many teams review code before it reaches the main branch; others use pairing or selective post-merge review. Done well, review spreads knowledge, keeps the codebase coherent and catches real problems. Done badly, it is a queue where changes sit for days while people argue about brace placement.

This lesson covers what review actually achieves, how to be a good author and reviewer, and the process choices that decide whether review helps or hurts delivery.

## What review is for

Ask engineers why they review and most say "to find bugs". Research suggests the picture is broader:

- A 2013 Microsoft study by Bacchelli and Bird found that finding defects was the top *stated* motivation, but only a minority of review comments were actually about defects. Much of the value came from **knowledge transfer**, **team awareness** and **alternative solutions**.
- Google's 2018 case study of about 9 million reviewed changes ("Modern Code Review: A Case Study at Google") found **education** and maintaining **norms** (readability, consistency) to be central motivations alongside correctness.

So review is a bug filter, but also:

1. **Shared ownership**: review can help more people understand a change; approval alone does not guarantee understanding.
2. **Consistency**: the codebase stays readable to everyone, not just its author.
3. **Mentoring**, in both directions.
4. **A security and design checkpoint** before something is hard to undo.

Review does not replace tests. A targeted boundary test can catch an off-by-one that a reviewer misses; CI only detects what its checks actually exercise. Let machines check what machines can check, so reviewers spend attention on what only humans can judge.

## The standard: better, not perfect

Google's published engineering practices put it plainly: reviewers should favour approving a change once it **definitely improves the overall code health** of the system, even if it is not perfect. There is no perfect code, only better code.

That principle cuts both ways. A reviewer should not demand polish on every line. But a reviewer *should* block a change that makes the system worse: unclear design, missing tests, a new abstraction that does not pull its weight.

## Size is the biggest lever

Small changes get better reviews, faster. Large ones get skimmed.

Google's guidance suggests around **100 lines** is usually a reasonable size for a change and **1,000 lines** is usually too large, while noting that the number of files matters too: 200 lines in one file can be fine; spread over 50 files it usually is not.

Ways to keep changes small:

- **Separate refactoring from behaviour change.** A pure rename across 40 files is easy to approve on its own; mixed with logic changes it hides them.
- **Split by layer or step**: schema migration, then backend, then UI.
- **Stack changes**: open PR 2 on top of PR 1, so review of the first does not block writing the second.
- **Use feature flags** so a partial feature can merge safely (see the workflows lesson).

## What reviewers look for, in order

Google's list of what to look for is a useful checklist. Review from the top down: there is no point polishing names in code whose design is wrong.

| Area | Question |
|---|---|
| Design | Does this belong here? |
| Functionality | Does it do what's intended? |
| Complexity | Could it be simpler? |
| Tests | Correct, useful tests? |
| Naming, comments | Clear? Explain why? |
| Style, docs | Guide followed? Docs updated? |

Also read **every line** you are asked to review, look at the **context** (the whole file, not just the diff) and **say what is good**. Praise for a clean test is information too.

## A worked review

Here is a small change that looks fine at a glance:

```python
def find_orders(db, email, statuses=[]):
    statuses.append("open")
    sql = (
        "SELECT * FROM orders "
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
    wanted = list(statuses or []) + ["open"]
    marks = ", ".join("?" * len(wanted))
    sql = (
        "SELECT id, total, status "
        "FROM orders WHERE email = ? "
        f"AND status IN ({marks})"
    )
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

## Making review fast

Slow review quietly destroys trunk-based development: if a review takes two days, people batch work into bigger changes to "make the wait worth it", which makes reviews slower still.

Google's guideline is that **one business day is the maximum** time to respond to a review request, and that if you are not in the middle of a focused task you should review shortly after a request arrives. Responding does not have to mean finishing; an initial response can clarify expectations, but approval-dependent merges remain blocked until the required review is complete.

> [!tip] Ship, Show, Ask
> Rouan Wilsenach's model, published on martinfowler.com, classifies changes: **Ship** (merge directly, e.g. a typo fix), **Show** (open a PR, wait for automated checks, then merge without waiting for human feedback) and **Ask** (open a PR and wait for review). It suits teams with strong CI and high trust, and it is a reminder that not every change needs the same gate.

## Tooling and policy

- **Formatters and linters** (Black, Ruff, Prettier, gofmt) end style arguments. Run them in CI and pre-commit hooks so style never reaches a human.
- **Branch protection** on GitHub or GitLab can require N approvals and passing status checks before merging, and can dismiss stale approvals when new commits are pushed.
- **CODEOWNERS** maps paths to owners who can be requested for review; requiring owner approval is a separate protection setting. On GitHub the file lives in `.github/`, the repository root or `docs/`, and the **last matching pattern wins**:

```
# .github/CODEOWNERS
*              @acme/platform
/billing/      @acme/payments
*.tf           @acme/infra
```

With required code-owner review enabled, billing/api.py needs an eligible payments owner approval, and billing/main.tf an infra owner approval because *.tf matches last. Listing several owners on one line permits approval by any one of them; it does not require every listed team.

- **Pair or mob programming** is continuous review. Many teams accept pairing as satisfying the review requirement.

## Pitfalls

- **Rubber-stamping**: "LGTM" on a 2,000-line diff after two minutes. The fix is smaller changes, not stricter rules.
- **Bikeshedding**: long threads on trivia while the design question goes unasked. Automate style; review design first.
- **Gatekeeping**: one senior engineer must approve everything, and becomes the bottleneck. Spread ownership.
- **Approving what you did not understand.** If you cannot explain the change, ask. That is the review working.
- **Ignoring dependencies.** A one-line lockfile bump can pull in thousands of lines of third-party code. Review new dependencies deliberately.

## Key takeaways
- Review finds defects but its biggest benefits are shared knowledge, consistency and design feedback; let CI and linters handle what machines can.
- Approve changes that definitely improve code health, even if imperfect; block those that make things worse.
- Keep changes small (around 100 lines is reasonable, 1,000 usually too big) and separate refactors from behaviour changes.
- Review top-down: design, functionality, complexity, tests, then naming and style; label severity and explain why.
- Respond within a business day, and use branch protection and CODEOWNERS to route changes to the right people.

## Further reading
- [Google Engineering Practices: Code Review](https://google.github.io/eng-practices/review/)
- [The Standard of Code Review — Google](https://google.github.io/eng-practices/review/reviewer/standard.html)
- [Small CLs — Google](https://google.github.io/eng-practices/review/developer/small-cls.html)
- [Modern Code Review: A Case Study at Google](https://research.google/pubs/modern-code-review-a-case-study-at-google/)
- [Ship / Show / Ask — Rouan Wilsenach](https://martinfowler.com/articles/ship-show-ask.html)
- [About code owners — GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [Conventional Comments](https://conventionalcomments.org/)
