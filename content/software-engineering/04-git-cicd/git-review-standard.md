---
id: git-review-standard
title: Review goals, change size and priorities
level: intermediate
minutes: 4
sourceLesson: git-code-review
summary: Review supports knowledge transfer and coherent design as well as defect detection.
---

Many teams review code before it reaches the main branch; others use pairing or selective post-merge review. Done well, review spreads knowledge, keeps the codebase coherent and catches real problems. Done badly, it is a queue where changes sit for days while people argue about brace placement.

This lesson covers what review actually achieves, how to be a good author and reviewer, and the process choices that decide whether review helps or hurts delivery.

## What review is for

Ask engineers why they review and most say "to find bugs". Research suggests the picture is broader:

- A 2013 Microsoft study by Bacchelli and Bird found that finding defects was the top *stated* motivation, but only a minority of review comments were actually about defects. Much of the value came from **knowledge transfer**, **team awareness** and **alternative solutions**.
- Google's 2018 case study of about 9 million reviewed changes ("Modern Code Review: A Case Study at Google") found **education** and maintaining **norms** (readability, consistency) to be central motivations alongside correctness.

So review is a bug filter, but also:

1. **Collective ownership**: review can help more people understand a change; approval alone does not guarantee understanding.
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

## Key takeaways

- Review supports knowledge transfer and coherent design as well as defect detection.
- Approve definite improvements to code health without requiring personal perfection.
- Separate refactoring from behaviour changes and review design before details.

## Further reading

- [Google Engineering Practices: Code Review](https://google.github.io/eng-practices/review/)
- [The Standard of Code Review — Google](https://google.github.io/eng-practices/review/reviewer/standard.html)
- [Small CLs — Google](https://google.github.io/eng-practices/review/developer/small-cls.html)
- [Modern Code Review: A Case Study at Google](https://research.google/pubs/modern-code-review-a-case-study-at-google/)
