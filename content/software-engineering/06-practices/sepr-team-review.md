---
id: sepr-team-review
title: Review changes and build trust
level: advanced
minutes: 3
summary: Keep code review focused on code health and create conditions for shared learning.
sourceLesson: sepr-teams
---

Documentation spreads context before work starts; review spreads it as code changes. The same respect and willingness to ask questions matter in both.

## Code review
Code review catches defects, but its bigger benefits are spreading knowledge (raising the bus factor) and keeping the codebase consistent.

Google's published engineering practices give a useful standard: reviewers should favour approving a change once it **definitely improves the overall health of the code**, even if it is not perfect. Perfectionism in review slows everyone and drives people to accumulate changes into huge, unreviewable changes.

Practical habits:

- **Small changes.** Smaller coherent changes are easier to understand and review; line counts alone do not determine review quality. Split refactoring from behaviour change (see the refactoring lesson).
- **Fast responses.** Google's guide says one business day is the maximum time to respond to a review request. Slow reviews are a hidden tax on every engineer.
- **Comment on the code, not the person.** "This loop is O(n²); a set would make it O(n)" (where n is the number of items) rather than "why would you do this?".
- **Label severity.** Prefix optional suggestions with `Nit:` so the author knows what blocks approval.
- **Automate the trivial.** Formatters and linters in CI settle style, so humans spend review time on design and correctness.
- **Explain the why** in the PR description: context, approach, how it was tested, and what the reviewer should focus on.

## Team health in general
**Psychological safety** means the team believes it is safe to ask questions, acknowledge mistakes and take interpersonal risks. It helps people expose uncertainty during reviews and shared work.

- **Onboarding** is a test of your docs. Have every new joiner fix whatever confused them.
- **Pairing and mobbing** spread knowledge fast, especially on unfamiliar code.
- **Async by default** for things that do not need a meeting: written proposals, recorded decisions, threads rather than calls. Protect focus time.
- **Rotate ownership** of components and of on-call so expertise is not concentrated.

## Key takeaways
- Review small coherent changes promptly and distinguish blocking concerns from optional nits.
- Automate routine style so review can concentrate on design and correctness.
- Psychological safety, onboarding and shared work help people expose uncertainty and spread knowledge.

## Further reading
- [The Standard of Code Review — Google](https://google.github.io/eng-practices/review/reviewer/standard.html)
- [Speed of Code Reviews — Google](https://google.github.io/eng-practices/review/reviewer/speed.html)
- [Five dynamics of effective teams — Google](https://www.thinkwithgoogle.com/intl/en-emea/consumer-insights/consumer-trends/five-dynamics-effective-team/)
