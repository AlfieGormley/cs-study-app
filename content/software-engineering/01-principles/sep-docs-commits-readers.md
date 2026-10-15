---
id: sep-docs-commits-readers
title: Match documentation to its reader’s task
level: advanced
minutes: 3
summary: Separate learning, task steps, reference facts and explanation.
sourceLesson: sep-writing-for-others
---

Callers and maintainers need a reliable contract. State what they may rely on and preserve the reasons behind a decision.

## The four kinds of documentation

The [Diátaxis](https://diataxis.fr/) framework observes that docs fail when they mix purposes. There are four:

| Type | Reader wants to | Example |
|---|---|---|
| Tutorial | learn by doing | "Build your first app" |
| How-to | solve a problem | "Rotate API keys" |
| Reference | look up facts | Function signatures |
| Explanation | understand why | "How caching works" |

A tutorial that stops to explain design history loses beginners; a reference page padded with narrative is slow to scan. A good **README** is usually a mini-tutorial (what it is, install, a working example in under a minute) plus links to the rest.

A useful change boundary is one reason to change: a retry fix, a rename and a dependency update may deserve separate commits. That helps a future debugger isolate or revert the dependency change without discarding the fix. This is a review heuristic; an inseparable migration may need to travel together.

## Commit messages: notes for future debuggers

Months later, someone runs `git blame` on a strange line. The commit message is the only explanation they'll get. The widely used conventions:

- A subject line of about **50 characters**, in the imperative ("Fix rounding in VAT total").
- A blank line, then a body wrapped at about **72 characters** that explains **what and why**, not how. The diff already shows how.

The following fictional incident message demonstrates structure; its timings are illustrative, not benchmark evidence.

```
Cap retry backoff at 30s

Unbounded exponential backoff meant a
client offline for an hour waited 34
minutes after reconnecting. Cap delay at
30s; see INC-482.
```

## Key takeaways
- Separate learning, task steps, reference facts and explanation.
- Commit messages preserve the reason for a change for future debugging.
- Small logical commits make review, diagnosis and reversal more precise.

## Further reading
- [diataxis.fr](https://diataxis.fr/)
- [cbea.ms](https://cbea.ms/git-commit/)
