---
id: sea-adr-evolution
title: Architecture decision records and evolutionary architecture
level: advanced
minutes: 14
summary: Writing ADRs that capture why a decision was made, telling reversible decisions from irreversible ones, guarding architecture with fitness functions, and changing structure safely with strangler fig and branch by abstraction.
---

Two years into a project, a new engineer asks: "Why do we use an event bus between orders and billing? It makes everything harder." Nobody remembers. The person who decided has left. The team either keeps a design it doesn't understand, or rips it out and rediscovers the problem it solved.

This lesson covers two complementary habits. **Architecture decision records** preserve the *why* behind structural choices. **Evolutionary architecture** treats structure as something you change continually and safely, rather than something you get right once.

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
- **Never edit an accepted ADR's decision.** If it changes, write a new ADR and mark the old one `Superseded by 0012`. The log is a history, including the decisions you reversed.
- **Keep them short**: one or two pages. An ADR that takes a week to write won't get written.
- **Write one when a decision is significant**: costly to reverse, affecting structure, or likely to be questioned. Choosing Postgres, adopting hexagonal architecture or splitting a module qualifies; naming a variable doesn't.

Variants such as MADR (Markdown Architectural Decision Records) add a *considered options* section with pros and cons for each alternative, which helps reviewers see what was rejected and why.

> [!tip] ADRs as a review tool
> Write the ADR with status *Proposed* and open it as a pull request. Discussion can happen on the PR; define whether merging marks acceptance in your team's workflow. The decision and its debate are then preserved together.

## Reversible and irreversible decisions

Not every decision deserves the same care. Jeff Bezos's 2015 shareholder letter split them into **Type 1** (one-way doors, consequential and hard to reverse) and **Type 2** (two-way doors, which you can walk back through).

| Decision | Door |
|---|---|
| Name of an internal helper | Two-way |
| Choice of logging library behind an adapter | Two-way |
| Public library API at 1.0 | One-way-ish |
| Primary database for 10 years of data | One-way-ish |
| Splitting into separately deployed services | One-way-ish |

Two consequences for architecture:

1. **Spend ADR and review effort on one-way doors.** Make two-way decisions quickly.
2. **Turn one-way doors into two-way ones** where you can. Putting the database behind a repository port, or a vendor SDK behind an adapter, can reduce call-site changes, but migration cost also depends on data and semantic compatibility. Much of good architecture is buying reversibility.

The related idea of the **last responsible moment** says to delay irreversible decisions until you have the most information, but no later, since not deciding is also a decision.

## Evolutionary architecture

Neal Ford, Rebecca Parsons and Patrick Kua's *Building Evolutionary Architectures* defines an evolutionary architecture as one that supports **guided, incremental change** across multiple dimensions. The key word is *guided*: change is constant, but some properties must be protected while it happens.

### Fitness functions

A **fitness function** is an objective, preferably automated, check of an architectural characteristic. Rather than hoping the layering survives, you test for it.

Examples:

| Characteristic | Fitness function |
|---|---|
| Layering | import-linter contract in CI |
| No cycles | Acyclic import check |
| Latency | p99 < 200 ms in load test |
| Dependency hygiene | No package > 1 major behind |
| Bundle size | Fail if > 250 KB gzipped |

A fitness function can be an ordinary test:

```python
import ast
import pathlib

def imports(path):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level == 0:
                yield node.module or ""
        elif isinstance(node, ast.Import):
            for a in node.names:
                yield a.name

def test_domain_has_no_framework():
    banned = ("flask", "sqlalchemy")
    root = pathlib.Path("shop/domain")
    files = list(root.rglob("*.py"))
    assert files, "no domain files found"
    for f in files:
        for mod in imports(f):
            top = mod.split(".")[0]
            bad = top in banned
            assert not bad, f"{f}: {mod}"
```

This small example checks direct absolute import statements, requires at least one source file, and matches the top-level package exactly. It does not resolve relative or dynamic imports and can include imports guarded by TYPE_CHECKING. A dedicated tool like import-linter also follows indirect chains, which is why it's usually the better choice. The point is that architecture rules become executable and fail the build like any other bug.

### Making change incremental

A long all-at-once rewrite can delay feedback and lose undocumented behavior. Joel Spolsky's essay Things You Should Never Do argues against this approach using Netscape as a cautionary example.

> [!note] Evidence gap
> A universal rewrite failure rate and a precise single-cause Netscape chronology are omitted; an opinion essay is not sufficient evidence for those claims. The alternative is a set of techniques for changing structure in small, safe steps.

**Strangler fig.** Named by Martin Fowler after vines that grow around a host tree until they replace it. Put a routing layer in front of the old code; move one capability at a time to the new implementation; route to it; delete the old part. The aim is to keep the system serving throughout, but each cutover still needs compatible data, operational checks and a recovery plan.

```
 step 1           step 2          step 3
 +-------+        +-------+       +-------+
 | facade|        | facade|       | facade|
 +---+---+        +-+---+-+       +---+---+
     |              |   |             |
   [old]         [old] [new]        [new]
```

**Branch by abstraction.** For replacing a component used throughout the code (an ORM, a payment provider) without a long-lived feature branch:

1. Introduce an abstraction (a port) over the existing component.
2. Move all callers onto the abstraction.
3. Build the new implementation behind the same abstraction.
4. Switch over, often with a feature toggle, a slice of traffic at a time.
5. Delete the old implementation, and the toggle.

Every step is a small commit on the main branch, so you avoid a months-long merge.

**Parallel run.** For risky logic like pricing, run old and new implementations side by side, return the old result, and log differences. GitHub's open-source `Scientist` library (Ruby, with ports in other languages) does exactly this. Switch only when relevant differences are understood. Shadow execution must isolate side effects and cap additional load; Scientist evaluates both behaviors but does not inherently run them concurrently.

### Other evolutionary ideas

- **Monolith first.** In his 2015 essay, Fowler reported that almost all successful microservice stories he had heard began with monoliths, while many from-scratch stories involved trouble. This is practitioner experience, not a representative success-rate study; because boundaries are hard to get right before you understand the domain. A well-modularised monolith keeps the option open.
- **Sacrificial architecture.** Sometimes the right design for today is one you expect to throw away when you reach 10× scale. Fowler's example is eBay, which moved from Perl to C++ to Java as it grew, as recounted in his essay. Knowing it's temporary changes how much you invest.
- **Conway's law.** "Organizations which design systems are constrained to produce designs which are copies of the communication structures of these organizations." Shared ownership can affect boundaries, but Conway's observation does not deterministically predict that any shared module will blur. The *inverse Conway manoeuvre* shapes teams to match the architecture you want.

## Pitfalls

1. **ADRs written after the fact for show.** If they don't influence decisions, they become stale paperwork. Write them at decision time.
2. **ADR as a design document.** ADRs record a *decision*. Long technical designs belong elsewhere and can be linked.
3. **Fitness functions nobody runs.** A check outside CI is a suggestion.
4. **Evolution as an excuse for no design.** "We'll refactor later" works only if the code is testable and modular enough to refactor, and if later actually comes.
5. **Toggles that never die.** Independent binary flags can create up to 2^n configurations; dependencies and mutually exclusive flags can reduce reachable combinations. Put a removal date on them.

## Key takeaways
- An ADR records one significant decision's context, decision and consequences; keep it short and preserve accepted decision history, while updating status and adding explicit corrections or superseding records.
- Write down the downsides you accepted; that is what future readers need most.
- Spend care on one-way-door decisions, and use ports and adapters to make more decisions reversible.
- Fitness functions turn architectural rules into automated checks that fail the build.
- Change structure incrementally with strangler fig, branch by abstraction and parallel runs instead of big-bang rewrites.
- Conway's law links team structure and architecture; design both together.

## Further reading
- [Documenting Architecture Decisions — Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [Architectural Decision Records — adr.github.io](https://adr.github.io/)
- [Lightweight Architecture Decision Records — Thoughtworks Technology Radar](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)
- [Strangler Fig Application — Martin Fowler](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Branch By Abstraction — Martin Fowler](https://martinfowler.com/bliki/BranchByAbstraction.html)
- [Monolith First — Martin Fowler](https://martinfowler.com/bliki/MonolithFirst.html)
- [Sacrificial Architecture — Martin Fowler](https://martinfowler.com/bliki/SacrificialArchitecture.html)
- [Conway's law — Wikipedia](https://en.wikipedia.org/wiki/Conway%27s_law)
