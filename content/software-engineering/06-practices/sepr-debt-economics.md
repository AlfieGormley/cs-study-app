---
id: sepr-debt-economics
title: Find expensive debt and estimate payback
level: basic
minutes: 5
summary: Compare how often debt is paid against what fixing it costs, know what that estimate leaves out, and find frequently changed complex code.
sourceLesson: sepr-technical-debt
---

Technical debt is useful as an economic metaphor when it guides a decision: which debt is worth paying down first? The figures below are invented estimates to show the reasoning, not measured productivity rates.

## The interest is what matters
Not all ugly code is costly debt. The change-related cost of debt (its interest) depends on two things: how much extra effort each change costs, and how often the area changes. A fix (paying the principal) is worth it when the interest it saves adds up to more than the fix costs, soon enough to matter.

```formula reference
I = a c
T = F / I
where
I: the interest: extra days of work the debt costs per period (per quarter or per year)
a: the extra days each change to the area costs because of its poor structure
c: the number of changes to the area per period
T: the payback period, in the same periods as I: how long until the time saved equals the time spent on the fix
F: the one-off cost of the fix (the principal), in days
In words: the interest is the extra cost of each change multiplied by how often the area changes, and a fix pays for itself once the interest it saves adds up to what the fix cost.
```

> [!example] Same pain per change, very different interest
> The checkout module's structure adds about 2 extra days to each feature that touches it, and the team ships 8 such features a quarter: roughly 16 days of interest a quarter. A 20-day restructure would pay for itself in about a quarter and keep paying after that.
>
> A legacy reporting module also adds 2 days per change, but changes once a year. The same 20-day fix would take about ten years to repay through change savings alone.

Per-change pain is identical; frequency makes the difference. That is why "the code is ugly" is a weak argument and "this costs us about 16 days a quarter" is a strong one.

## What the estimate does and does not tell you
The calculation is useful for ranking candidates, not for promising savings. Fowler is blunt that none of these costs can be measured objectively: you estimate the extra effort, the change rate and the fix, and such estimates are not very accurate.

- It assumes the area keeps changing at the same rate. If checkout is about to be replaced, its interest stops anyway.
- It assumes the fix removes the extra effort completely. A partial fix saves less and pays back more slowly.
- It counts only change friction. Code that rarely changes can still carry security, incident, runtime or knowledge risk (only one person understands it), and those costs need a separate judgement before you decide to leave it alone.

Because the numbers are rough, Fowler's preferred route is to pay the principal off gradually: clean up a little each time you work in an area. That automatically spends the most effort where changes are most frequent, which is exactly where the interest is highest.

## Finding hotspots

Adam Tornhill's **hotspot** analysis combines two signals you already have: how often a file changes (from version control) and how complex it is (lines of code or a complexity metric). Files that are both complex and frequently changed are candidates for expensive change friction; the two signals alone do not prove causation.

File change frequency from git:

```
# Count recorded path appearances.
git log --since="12 months ago" \
  --format=format: --name-only \
  | grep -v '^$' | sort | uniq -c \
  | sort -rn | head -20
```

Run it in the repository you are investigating. It lists the files that appear most often in the last year's commits, most-changed first. Renames split one file's history across two names, so treat the list as a lead. Cross-check the top entries with complexity, bug reports and the files developers complain about. Often a small fraction of files accounts for most of the pain.

Other useful signals: lead time for changes in an area, how often a module appears in incident reports, and how long reviews take for PRs touching it.

## Key takeaways
- Compare change friction together with operational, security and knowledge risks.
- Payback estimates rank candidates; they rest on rough guesses about change rate and how much cost the fix removes.
- Hotspots combine complexity and file change frequency; confirm the signal against real delivery and incident evidence.

## Further reading
- [Technical Debt — Martin Fowler](https://martinfowler.com/bliki/TechnicalDebt.html)
- [Hotspot analysis — CodeScene](https://codescene.io/docs/guides/technical/hotspots.html)
- [Git log documentation](https://git-scm.com/docs/git-log)
