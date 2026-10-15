---
id: git-review-flow-policy
title: Fast review, code owners and approval policy
level: intermediate
minutes: 3
sourceLesson: git-code-review
summary: Slow review encourages batching, which makes review slower.
---

Small changes and useful feedback still need a responsive process. This unit connects review turnaround with automated checks, ownership routing and approval controls.

## Making review fast

Slow review quietly destroys trunk-based development: if a review takes two days, people bundle work into bigger changes to "make the wait worth it", which makes reviews slower still.

Google's guideline is that **one business day is the maximum** time to respond to a review request, and that if you are not in the middle of a focused task you should review shortly after a request arrives. Responding does not have to mean finishing; an initial response can clarify expectations, but approval-dependent merges remain blocked until the required review is complete.

> [!tip] Ship, Show, Ask
> Rouan Wilsenach's model, published on martinfowler.com, classifies changes: **Ship** (merge directly, e.g. a typo fix), **Show** (open a PR, wait for automated checks, then merge without waiting for human feedback) and **Ask** (open a PR and wait for review). It suits teams with strong CI and high trust, and it is a reminder that not every change needs the same gate.

## Tooling and policy

- **Formatters and linters** (Black, Ruff, Prettier, gofmt) end style arguments. Run them in CI and pre-commit hooks so style never reaches a human.
Automate import ordering, known-vulnerable dependency checks, recognised bug patterns such as mutable defaults, and tests across supported interpreter versions. Scanners and linters depend on their configured rules and data; green results do not establish that a design fits the product.

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
- **Bikeshedding**: long review discussions on trivia while the design question goes unasked. Automate style; review design first.
- **Gatekeeping**: one senior engineer must approve everything, and becomes the bottleneck. Spread ownership.
- **Approving what you did not understand.** If you cannot explain the change, ask. That is the review working.
- **Ignoring dependencies.** A one-line lockfile bump can pull in thousands of lines of third-party code. Review new dependencies deliberately.

## Key takeaways

- Slow review encourages batching, which makes review slower.
- Use automated checks for mechanical work and route human review by relevant ownership.
- On GitHub the last matching CODEOWNERS pattern wins; required owner review and stale-approval dismissal are separate policies.
- Ship / Show / Ask varies the feedback gate with the change and team context.

## Further reading

- [Google Engineering Practices: Code Review](https://google.github.io/eng-practices/review/)
- [Ship / Show / Ask — Rouan Wilsenach](https://martinfowler.com/articles/ship-show-ask.html)
- [About code owners — GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
