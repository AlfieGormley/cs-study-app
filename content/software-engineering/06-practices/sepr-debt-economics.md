---
id: sepr-debt-economics
title: Find expensive debt and estimate payback
level: basic
minutes: 5
summary: Compare carrying costs and repayment effort, then investigate frequently changed complex code.
sourceLesson: sepr-technical-debt
---

Technical debt is useful as an economic metaphor when it guides a decision. The following figures are hypothetical engineering-effort estimates, not measured productivity rates.

## The interest is what matters
Not all ugly code is costly debt. Frequent changes expose design costs, but unchanged code can also incur incident response, security maintenance, runtime cost and knowledge risk. Compare those costs as well as change friction.

A worked example makes the trade-off concrete. Two quantities matter: the debt interest (the extra time you pay over a period because of the debt) and the **payback period** (how long the fix takes to earn back its own cost in saved interest):

```formula
I = a × c
T = F / I
where
I: the interest: extra days of work the debt costs per period (per quarter or per year)
a: the extra days each change to the area costs because of its poor structure
c: the number of changes to the area per period
T: the payback period, in the same periods as I: how long until the time saved equals the time spent on the fix
F: the one-off cost of the fix (the principal), in days
In words: interest is the extra cost per change times how often you change it, and a fix pays for itself once the interest it saves adds up to what the fix cost.
```

> [!example] Is it worth paying down?
> The checkout module's structure adds about 2 extra days to each feature that touches it, and the team ships 8 such features a quarter. A restructure is estimated at **20 days**.
>
> A legacy reporting module also adds 2 days per change, but changes once a year. The same 20-day fix would apply.

```formula
I_checkout = 2 d × 8 per qtr
I_checkout = 16 d per qtr
T_checkout = 20 d / (16 d per qtr)
T_checkout = 1.25 qtr
I_report = 2 d × 1 per yr
I_report = 2 d per yr
T_report = 20 d / (2 d per yr)
T_report = 10 yr
where
I_checkout: the interest the checkout module costs, in days per quarter
T_checkout: the payback period of fixing the checkout module, in quarters
I_report: the interest the reporting module costs, in days per year
T_report: the payback period of fixing the reporting module, in years
d: days of engineering work
qtr: a quarter: three months
yr: a year
In words: the busy checkout module costs 16 days a quarter, so a 20-day fix pays for itself in about a quarter and a bit; the rarely touched report module costs 2 days a year, so the same fix takes ten years to repay.
```

The checkout fix pays for itself in under two quarters and keeps paying after that. Ignoring other costs, the reporting fix takes ten years to repay through change savings alone; deferring it may make sense if security, operational and knowledge risks are also acceptable. The model assumes the interest stays constant and that the fix removes it completely; in practice both are estimates.

This is why "the code is ugly" is a weak argument and "this costs us 16 days a quarter" is a strong one.

### Finding hotspots

Adam Tornhill's **hotspot** analysis combines two signals you already have: how often a file changes (from version control) and how complex it is (lines of code or a complexity metric). Files that are both complex and frequently changed are candidates for expensive change friction; the two signals alone do not prove causation.

File change frequency from git:

```
# Count recorded path appearances.
git log --since="12 months ago" \
  --format=format: --name-only \
  | grep -v '^$' | sort | uniq -c \
  | sort -rn | head -20
```

This command is an illustrative history query, not fixed output. Run it in the repository you are investigating. It counts appearances of paths in the selected Git history and sorts larger counts first; merge history, renames and Git’s path-display conventions can affect interpretation. Cross-check the top entries with complexity, bug reports and the files developers complain about. You usually find that a small fraction of files accounts for most of the pain.

Other useful signals: lead time for changes in an area, how often a module appears in incident reports, and how long reviews take for PRs touching it.

## Key takeaways
- Compare change friction together with operational, security and knowledge risks.
- Payback estimates depend on how much cost the fix actually removes and how long savings continue.
- Hotspots combine complexity and file change frequency; confirm the signal against real delivery and incident evidence.

## Further reading
- [Technical Debt — Martin Fowler](https://martinfowler.com/bliki/TechnicalDebt.html)
- [Hotspot analysis — CodeScene](https://codescene.io/docs/guides/technical/hotspots.html)
- [Git log documentation](https://git-scm.com/docs/git-log)
