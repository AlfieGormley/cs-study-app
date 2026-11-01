---
id: sea-module-monolith-dependencies
sourceLesson: sea-modularity
title: Modular monoliths and third-party packages
level: advanced
minutes: 5
summary: Adopt boundaries gradually in one deployable app and manage the packages it installs.
---

Module boundaries need not imply separate services. This unit applies public interfaces and automated checks to one existing application, then considers dependencies outside its codebase.

## Modular monoliths

A **modular monolith** is one deployable application split into modules with enforced boundaries, each with a public API and private internals. It aims for many of the code-level benefits people want from microservices (clear ownership, independent reasoning, a smaller blast radius for changes) without network calls, distributed transactions or separate deploys.

> [!analogy] Real-world analogy: a block of flats
> A block of flats is one building with one roof, one set of foundations and shared plumbing. Each flat has its own front door, and neighbours don't wander into each other's kitchens; they knock, or leave a note.
>
> **How it maps:** The building is the single deployable application, sharing one process and one database server. Each flat is a module, the front door is its public API, and the kitchen is its private internals. Moving a household to its own house later (extracting a service) is easier when it never relied on next door's kitchen.
>
> **Where it stops:** Walls physically stop you walking through. In code, nothing stops one module importing another's internals except a check run in CI, which is why the tooling below matters. And flats in a block can still share hidden things, like one database schema, that make moving out harder than it looks.

Shopify is one published example. Its core Rails monolith (over 2.8 million lines of Ruby by 2020) was reorganised into components, and the company built **Packwerk**, a static analysis tool that checks references between packages against each package's declared dependencies, fast enough to run on every pull request. Existing violations are recorded in a to-do file per package, so only *new* ones fail the build. Shopify has also written candidly that the work was gradual, and that an early push for consistent patterns, made without explaining the reasons well enough, added rules and friction without making the hard problems easier.

The usual path is:

1. Group code by business capability (orders, billing, catalogue).
2. Declare each module's public interface.
3. Record current violations as a baseline, so new ones fail CI.
4. Reduce the baseline over time.

A clean code boundary can help later extraction, though data ownership, transactions, failure modes and operations still need redesign.

## Third-party dependencies

Every package you install is code you don't control but must keep working. Some basics:

- **Direct vs transitive.** Installing one web framework can pull in dozens of transitive packages. You are exposed to all of them.
- **Ranges vs pins.** Libraries declare *ranges* (`requests>=2.28,<3`) so they can coexist with others. Applications should **lock** exact versions of everything, including transitive packages, with hashes (`uv lock`, `poetry.lock`, `pip-compile --generate-hashes`), to constrain resolved artifacts. Reproducibility also depends on the interpreter, platform, build tools, system libraries and installation options.
- **Upgrade continuously.** Tools such as Dependabot or Renovate can propose small, frequent upgrades, which may be easier to review and validate than accumulated changes.
- **Diamond conflicts.** If package A needs `lib<2` and package B needs `lib>=2`, pip can't install both into one environment. A normal pip-managed Python environment resolves one version of each distribution, unlike npm, which can nest different versions.
- **Supply-chain risk.** Typosquatting, compromised maintainer accounts and malicious updates are real. Locking with hashes, reviewing new dependencies and preferring well-maintained packages reduce exposure.

> [!warning] Wrap what you don't trust to stay still
> If a third-party API is spread across 200 files, an incompatible change can affect many call sites. Calling it through one adapter module implementing a core-owned port can limit the number of call sites, provided the changed semantics still fit the port. Don't wrap stable, ubiquitous libraries like the standard library; wrap volatile, swappable ones.

## Key takeaways
- A modular monolith separates code ownership and interfaces within one deployable application.
- Baseline old violations, reject new ones and reduce the baseline over time.
- Lock application dependency versions and artifacts while accounting for platform and build conditions.
- Conflicting Python package requirements need compatible versions, code changes or isolation.
- Adapters can reduce the call sites exposed to volatile third-party APIs.

## Further reading
- [Shopify: Under Deconstruction](https://shopify.engineering/shopify-monolith)
- [Packwerk — Shopify](https://github.com/Shopify/packwerk)
- [Dependency resolution — pip](https://pip.pypa.io/en/stable/topics/dependency-resolution/)
- [Secure installs — pip](https://pip.pypa.io/en/stable/topics/secure-installs/)
