---
id: sep-comments-intent
title: Write comments that preserve reasons
level: advanced
minutes: 3
summary: Comments should explain reasons, constraints, warnings or references that code does not convey.
sourceLesson: sep-writing-for-others
---

Code that only its author can use is a liability. The moment anyone else touches it (a teammate, a library user, you in a year) everything not written down has to be rediscovered by reading, guessing or breaking things.

This lesson covers the layers through which code talks to other people, from the closest to the furthest away:

```
 inline comments   -> the next maintainer
 docstrings/types  -> callers of a function
 README/docs       -> users of a module
 commit messages   -> future debuggers
 public API        -> people you never meet
```

## Comments: explain why, not what

Code already says *what* it does. A comment that repeats it adds reading time and one more thing to keep in sync.

```python
# Bad: restates the code
i += 1  # increment i
```

Good comments carry information the code *can't*:

```python
# Stripe can deliver an event repeatedly.
# Dedupe by event id, not its timestamp.
if seen(event.id):
    return
```

```python
# Input is limited to 8 elements by the
# caller contract; keep this loop simple.
```

> [!note] Content gap
> The previous claim of a measured threefold speedup was removed because no benchmark or reproducible setup was available. No performance result is asserted here.

The webhook fragment only illustrates a comment. Production deduplication needs durable, atomic coordination with the effect. Stripe automatic retries last up to three days in live mode; manual CLI resends can occur up to 30 days later, so three days is not a universal deduplication-retention limit.

Useful kinds of comment:

- **Intent and reasons**: why this approach, why not the obvious one.
- **Warnings**: "not thread-safe", "called from a signal handler".
- **References**: a link to the spec, RFC, ticket or bug this works around.
- **TODOs with an owner or ticket**, so they can be found and finished.

### Comments rot

The compiler checks code; nothing checks comments. When code changes and the comment doesn't, the comment becomes a lie that's *more* convincing than no comment at all.

```python
# Retry up to 3 times
for _ in range(5):
    ...
```

So before writing a comment, see if a better name or a small function would make it unnecessary:

```python
# Before
# check if user can get free shipping
if u.orders > 10 and u.region in EU:

# After
if qualifies_for_free_shipping(u):
```

## Key takeaways
- Comments should explain reasons, constraints, warnings or references that code does not convey.
- A stale comment is conflicting documentation, so verify intent before changing either side.
- A small deduplication sketch does not establish atomic, durable webhook processing.

## Further reading
- [pyguide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [webhooks](https://docs.stripe.com/webhooks)
