---
id: tech-backtracking-applications
title: Backtracking outside puzzles
level: intermediate
minutes: 2
sourceLesson: tech-backtracking
summary: Regex backtracking can explore super-linear or exponential alternatives.
---

## Where backtracking shows up

- **Regular expression engines.** Backtracking engines such as Python’s `re` can explore exponentially many alternatives for `(a+)+$` on `"aaaa…ab"`. This can cause **regular-expression denial of service (ReDoS)**. Cloudflare’s 2 July 2019 outage involved a different pattern with super-linear backtracking; it is not evidence that this exact pattern was deployed. RE2 and Rust’s `regex` bound a single search by O(m × n), where m is the size of the regex and n the length of the input, hence linear in the input length for a fixed regex; repeated-search APIs can have different bounds.

> [!note] Measure rejection time separately
> The grouping count explains the growth risk. Seconds depend on the regex engine version, input and machine; measure those explicitly before quoting a runtime.
- **Dependency resolvers.** pip's resolver backtracks: it picks candidate versions and, after a conflict, undoes choices and tries alternative compatible versions; those need not always be older.
- **SAT and constraint solvers** (next lesson), Prolog's execution model, parsers with alternatives, and puzzle solvers.

## Pitfalls

- **Forgetting to unchoose**, or undoing in the wrong order, so later branches start from corrupted state.
- **Appending the shared path** instead of a copy.
- **Generating duplicates** because the loop restarts from 0 instead of `start`.
- **Not pruning early enough**: checking validity only at the leaves turns backtracking back into brute force.
- **Exploding output.** No pruning helps if the answer itself has n! entries.

## Key takeaways
- Regex backtracking can explore super-linear or exponential alternatives.
- Dependency resolution and constraint search undo incompatible choices; their guarantees depend on the actual algorithm.

## Further reading
- [Cloudflare’s 2019 outage](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/)
- [pip dependency resolution](https://pip.pypa.io/en/stable/topics/dependency-resolution/)
- [RE2 guarantees](https://github.com/google/re2)
