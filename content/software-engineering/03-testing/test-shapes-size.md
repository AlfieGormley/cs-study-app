---
id: test-shapes-size
sourceLesson: test-why-pyramid
title: Adapt suite shapes and separate size from scope
level: basic
minutes: 3
summary: Trophy and honeycomb shapes shift effort towards the boundaries that matter in their systems.
---

The test pyramid is a starting point, not a quota. Now consider where that shape fails, how other systems adjust it, and why a test’s resource use is separate from its scope.

### The ice-cream cone anti-pattern

Many teams end up with the pyramid upside down: a handful of unit tests, some integration tests, and hundreds of slow browser tests or manual QA scripts on top. This is the **ice-cream cone**.

```
   ____________________
  \   manual / E2E     /  hours, flaky
   \------------------/
    \  integration   /
     \--------------/
      \    unit    /      barely any
       \__________/
```

Symptoms: the suite takes an hour, fails randomly, and engineers re-run it until it goes green. Nobody trusts a red build, so real failures slip through.

### Other shapes

The pyramid is useful for systems with substantial internal business logic. Other shapes emphasise different risks:

- **Testing trophy** (Kent C. Dodds, for front ends): static analysis at the base and a big middle of integration tests that render components with their real children, to exercise interactions between parts of a UI.
- **Testing honeycomb** (Spotify, for microservices): mostly integration tests per service, since Spotify found a microservice's biggest complexity is not inside it but in how it talks to its database and other services.

The common principle is the same: pick the cheapest test that would catch the bug you are worried about.

## Test size versus test scope

Google separates two ideas that the word "unit" blurs.

- **Scope** is how much code is exercised (one function or the whole system).
- **Size** is what resources the test may use. Under the Google scheme described here, small tests run in a single process (in many languages, a single thread), without sleeping, I/O or other blocking calls; a hermetic, in-memory filesystem is the one stated exception. Medium tests may use multiple processes and localhost networking on one machine. Large tests may span machines.

The size constraints remove common sources of slowness and nondeterminism; they do not guarantee a particular execution duration or outcome. A narrow-scope test that secretly calls a real API is "unit" in name only.

## What makes a suite good

- **Fast.** If the suite takes 30 seconds, people run it constantly. If it takes 30 minutes, they push and hope.
- **Deterministic.** The same code gives the same result every run. Intermittent failures erode trust unless they are investigated; they can also expose real product defects.
- **Behaviour-focused.** Tests check what the code does through its public interface, not how it does it internally, so refactoring does not break them.
- **Clear when failing.** A failure message should tell you what was expected and what happened.
- **Part of the workflow.** Tests run on every change in CI, and a red build blocks merging.

## Key takeaways
- Trophy and honeycomb shapes shift effort towards the boundaries that matter in their systems.
- Google test size constrains resources; scope describes how much code is exercised.
- A trusted suite needs repeatable results, useful failures and a place in the change workflow.

## Further reading
- [Testing Overview — Software Engineering at Google, ch. 11](https://abseil.io/resources/swe-book/html/ch11.html)
- [The Testing Trophy — Kent C. Dodds](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications)
- [Testing of Microservices — Spotify Engineering](https://engineering.atspotify.com/2018/01/testing-of-microservices)
