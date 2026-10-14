---
id: tech-greedy-optimality
title: Huffman optimality and greedy limits
level: intermediate
minutes: 3
sourceLesson: tech-greedy
summary: Huffman is optimal among binary prefix codes for the supplied symbol frequencies.
---

For example, earliest-finish accepts (0, 2) and (3, 4), two meetings. If each is worth 2 while a conflicting (1, 5) is worth 9, the two-meeting answer is worth only 4. Maximising value requires considering the single valuable meeting instead. This is why the objective belongs in the correctness proof.

The previous unit constructed a Huffman prefix tree from positive symbol frequencies. We now justify its greedy merge and identify the specific objective it optimises, then contrast that with greedy rules for other problems.

### Why it's optimal

Exchange argument again: in some optimal tree, the two least frequent symbols are **siblings at the deepest level**. If not, swap them with whatever is deepest; moving a rarer symbol deeper and a more common one shallower can't increase the total cost. So merging the two rarest first is safe, and the merged node behaves like a single symbol in a smaller problem.

Huffman minimises expected length among prefix codes made of 0s and 1s for the supplied individual-symbol frequencies. Arithmetic coding and ANS encode sequences so the average cost per symbol need not be an integer; physical output bits remain whole. Zstandard uses FSE, an ANS variant, for sequence symbols and can use Huffman coding for literals.

### Where Huffman is used

DEFLATE, used by gzip and PNG and supported by ZIP, combines LZ77-style matches with Huffman coding in compressed blocks (stored blocks also exist). Baseline JPEG uses Huffman entropy coding; other JPEG modes can use arithmetic coding. MP3 uses Huffman coding for quantised spectral data. HTTP/2’s HPACK can encode string literals with a specified static Huffman code.

## Other greedy algorithms you'll meet

- **Dijkstra's shortest paths**: always finalise the closest unvisited vertex (guaranteed under non-negative edge weights; some negative-edge instances also happen to work).
- **Prim's and Kruskal's** minimum spanning trees: Prim chooses the cheapest edge across its current tree’s cut; Kruskal chooses the cheapest remaining edge that joins different components.
- **Fractional knapsack**: take items by value per kilogram (next lesson).

Problems where greedy is always optimal often have **matroid** structure, a formal condition guaranteeing that "add the best element that keeps things valid" works. Spanning forests in a graph are the classic example.

## Pitfalls

- **Trusting intuition.** Three of the four interval rules above sound reasonable and are wrong. Always try to break your rule with a small counterexample, then prove it.
- **The wrong sort key.** Sorting meetings by start instead of end silently gives wrong answers on some inputs.
- **Boundary conditions.** Decide whether touching intervals overlap (`>` versus `>=`).
- **Changing the objective.** Add weights to interval scheduling (maximise total value, not count) and earliest-finish greedy fails; that version has an efficient DP solution; earliest-finish greedy alone is insufficient.

## Key takeaways
- Huffman is optimal among binary prefix codes for the supplied symbol frequencies.
- Changing an objective, such as adding meeting values, can invalidate a safe counting rule.

## Further reading
- [Greedy algorithms and Huffman codes — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/04-greedy.pdf)
- [Python heapq](https://docs.python.org/3/library/heapq.html)
