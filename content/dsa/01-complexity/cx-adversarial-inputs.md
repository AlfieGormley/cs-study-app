---
id: cx-adversarial-inputs
sourceLesson: cx-in-practice
title: Hostile inputs and worst-case bounds
level: advanced
minutes: 2
summary: Recognise when an attacker can force expensive algorithm paths.
---

Here n counts input items or characters, as stated in each example. Hostile input makes worst-case behaviour an engineering concern.

## Worst case and adversaries

Average-case performance is fine when inputs are benign. When an attacker controls the input, they will find your worst case.

- **Hash flooding.** Hash tables give O(1) average lookups, but if many keys collide, operations degrade to O(n) for a table of n keys, and inserting n colliding keys becomes Θ(n^2): about n × n / 2 comparisons. In 2011, researchers showed that many web frameworks could be knocked over by a single POST request whose parameter names all collided. Languages responded by randomising their hash functions per process. Python has randomised `str` hashing by default since 3.3 and uses SipHash since 3.4.
- **Regular expression backtracking.** Many regex engines use backtracking, which is exponential on some patterns and inputs. In July 2019 a single badly behaved regular expression exhausted CPU across Cloudflare's network and caused a global outage. RE2 and Rust's `regex` provide bounded search complexity for supported patterns. Rust documents O(mn) for individual searches (pattern size m, haystack size n), while repeated-match iterators can reach O(mn²). A fixed-pattern single search is linear in n.
- **Quicksort on sorted input.** A first- or last-element pivot can turn sorted distinct input into Θ(n²). Randomisation gives an expected bound; introsort's heapsort fallback provides the worst-case bound.

If an input could be hostile, choose algorithms with good **worst-case** bounds, or randomise.

## Key takeaways
- User-controlled input can expose an algorithm’s worst paths.
- Hash collisions, regex backtracking and bad pivots can amplify work.
- Choose a suitable worst-case guarantee or stated randomisation model for the workload.

## Further reading
- [Introsort — Wikipedia](https://en.wikipedia.org/wiki/Introsort)
