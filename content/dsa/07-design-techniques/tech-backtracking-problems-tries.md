---
id: tech-backtracking-problems-tries
title: Many-word search and solver pitfalls
level: advanced
minutes: 2
sourceLesson: tech-backtracking-problems
summary: A trie shares prefix work across dictionary words.
---

The previous word-search unit used reversible marking for one word. A dictionary introduces shared prefixes: different target words may begin along exactly the same grid path. We can reuse that search while preserving the rule that a cell appears only once on the current path.

### Many words at once

To find which of thousands of words appear in the grid, don't run `exist` per word. Put all words in a **trie** and do one DFS from each cell that walks the grid and the trie together. You stop as soon as the current path isn't a prefix of any word, and you clear a found word’s terminal marker and optionally delete exhausted branches, preserving nodes still needed by longer words.

## Pitfalls

- **Expensive validity checks.** Scanning units costs their length; fixed 9 × 9 Sudoku has constant-size units. Incremental sets give expected constant-time membership, and bitmask cost depends on the represented width.
- **Incomplete undo.** Every structure updated in "choose" (grid, sets, masks, the empty list) must be restored in "unchoose".
- **Continuing after success.** If you need one solution, propagate a `True` back up and stop.
- **Symmetry.** N-Queens solutions come in groups of up to 8 under rotation and reflection (8-Queens has 12 fundamentally different solutions). Breaking symmetry, for example searching mirrored first-row branches only once, can reduce work. For odd n, handle the centre column separately; enumerating all solutions requires restoring omitted symmetric solutions.

## Key takeaways
- A trie shares prefix work across dictionary words.
- Undo, success propagation and symmetry handling must match whether one or all solutions are requested.

## Further reading
- [Backtracking — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/02-backtracking.pdf)
- [Knuth: Dancing Links](https://arxiv.org/pdf/cs/0011047)
