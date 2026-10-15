---
id: sea-adr-records
sourceLesson: sea-adr-evolution
title: Recording architecture decisions
level: advanced
minutes: 4
summary: Write a small decision record that preserves context, accepted trade-offs and superseded history.
---

Two years into a project, a new engineer asks: "Why do we use an event bus between orders and billing? It makes everything harder." Nobody remembers. The person who decided has left. The team either keeps a design it doesn't understand, or rips it out and rediscovers the problem it solved.

These neighbouring units cover two complementary habits. **Architecture decision records** preserve the *why* behind structural choices. **Evolutionary architecture** treats structure as something you change continually and safely, rather than something you get right once.

## Architecture decision records

An **ADR** is a short document recording one architecturally significant decision: its context, the choice made and its consequences. Michael Nygard popularised the format in a 2011 blog post, and it's now widely used. Thoughtworks' Technology Radar placed lightweight ADRs in its *Adopt* ring.

Nygard's template has five parts:

```
# 7. Use events between orders and billing

Status: Accepted (2025-03-14)

## Context
Billing must react to placed orders.
A direct call made orders unavailable
whenever billing was slow, and billing
deploys froze the checkout team.

## Decision
Orders commits an outbox event with
its state. A relay sends to a durable
queue; a separate Billing worker
subscribes. No direct Orders call
to Billing is needed.

## Consequences
+ Checkout need not wait for Billing.
+ Separate deploys with stable contracts.
- Invoice delay depends on queue health.
- Event handlers need idempotency
  and monitoring for failures.
```

| Section | Answers |
|---|---|
| Title | What was decided (short noun phrase) |
| Status | Proposed, accepted, deprecated, superseded |
| Context | What forces were at play? |
| Decision | What we will do |
| Consequences | What becomes easier and harder |

The **consequences** section is especially useful for explaining accepted trade-offs. Writing down the downsides you accepted stops future readers assuming you didn't notice them.

### How teams use ADRs

- **Store them in the repository**, next to the code, as numbered Markdown files (`docs/adr/0007-events-orders-billing.md`). They are versioned, reviewed in pull requests and found by search.
- **Preserve the accepted decision as history.** If the choice changes, write a new ADR and mark the old one `Superseded by 0012`. Update status and add explicit corrections where needed, without silently rewriting what was decided. The log is a history, including the decisions you reversed.
- **Keep them short**: one or two pages. An ADR that takes a week to write won't get written.
- **Write one when a decision is significant**: costly to reverse, affecting structure, or likely to be questioned. Choosing Postgres, adopting hexagonal architecture or splitting a module qualifies; naming a variable doesn't.

Variants such as MADR (Markdown Architectural Decision Records) add a *considered options* section with pros and cons for each alternative, which helps reviewers see what was rejected and why.

> [!tip] ADRs as a review tool
> Write the ADR with status *Proposed* and open it as a pull request. Discussion can happen on the PR; define whether merging marks acceptance in your team's workflow. The decision and its debate are then preserved together.

## Key takeaways
- An ADR records one significant decision, its forces and its consequences.
- Keep accepted decision history while updating status and linking replacement records.
- A proposed ADR can support review before the decision is accepted.
- Explicit downsides explain why a future reader should not casually reverse the choice.

## Further reading
- [Documenting Architecture Decisions — Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [Architectural Decision Records](https://adr.github.io/)
- [MADR](https://adr.github.io/madr/)
- [Lightweight ADRs — Thoughtworks](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)
