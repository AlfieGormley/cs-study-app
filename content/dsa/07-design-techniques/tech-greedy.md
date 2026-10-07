---
id: tech-greedy
title: Greedy algorithms
level: intermediate
minutes: 14
summary: Make the locally best choice and never look back; how to prove that works with the greedy choice property and exchange arguments, applied to interval scheduling, meeting rooms and Huffman coding.
---

Backtracking tries every option and undoes bad ones. A **greedy algorithm** does the opposite: at each step it makes the choice that looks best *right now*, commits to it, and never reconsiders.

That makes greedy algorithms fast (often just a sort and a single pass) and simple to write. The catch is that "looks best right now" is frequently wrong. The hard part of greedy isn't the code; it's knowing whether the greedy choice is **safe**, and proving it.

## The two properties

A greedy algorithm produces an optimal answer when the problem has:

1. **The greedy choice property**: some optimal solution begins with the greedy choice. Making it never rules out the best answer.
2. **Optimal substructure**: after making the choice, what remains is a smaller instance of the same problem, and an optimal solution to it combines with the choice to give an optimal whole.

Optimal substructure is shared with dynamic programming. The greedy choice property is what lets greedy skip DP's "try every option and take the best": one option is provably enough.

## Interval scheduling

You have one meeting room and a list of requested meetings `(start, end)`. In both interval examples assume finite real endpoints with start < end, representing positive-duration half-open intervals [start, end). Accept as **many** meetings as possible with no overlaps. (In CLRS this is the **activity selection** problem.)

Several greedy rules sound plausible:

| Rule | Works? |
|---|---|
| Earliest start first | No |
| Shortest meeting first | No |
| Fewest conflicts first | No |
| **Earliest finish first** | **Yes** |

Counterexamples kill the wrong rules quickly:

```
Earliest start fails:
  [0-----------------10]
    [1-2] [3-4] [5-6]
  picks 1 meeting; best is 3

Shortest first fails:
  [1-----5]    [6-----10]
        [4--7]
  picks [4,7] alone; best is 2
```

The winning rule: **sort by end time, and take each meeting that starts at or after the last accepted one ends.**

```python
def max_meetings(intervals):
    chosen = []
    last_end = float("-inf")
    by_end = sorted(intervals,
                    key=lambda iv: iv[1])
    for s, e in by_end:
        if s >= last_end:   # compatible
            chosen.append((s, e))
            last_end = e
    return chosen
```

The sort dominates: **O(n log n)**. The `>=` treats a meeting ending at 10 and one starting at 10 as compatible; use `>` if touching intervals conflict in your problem.

> [!example] Trace
> Meetings sorted by end: (1,4), (3,5), (0,6), (5,7), (3,9), (5,9), (6,10), (8,11), (8,12), (2,14), (12,16).
> - Take (1,4). last_end = 4.
> - (3,5), (0,6) start before 4: skip. Take (5,7). last_end = 7.
> - (3,9), (5,9), (6,10) start before 7: skip. Take (8,11). last_end = 11.
> - (8,12), (2,14) start before 11: skip. Take (12,16).
>
> Result: 4 meetings.

### Why it's correct: the exchange argument

The standard proof technique for greedy is the **exchange argument**: take any optimal solution, and show you can swap in the greedy choice without making it worse.

1. Let g be the meeting with the earliest finish time overall.
2. Take any optimal schedule O, and let o be its first meeting.
3. Since g finishes earliest of all, g.end ≤ o.end.
4. Replace o with g. Every other meeting in O starts at or after o.end ≥ g.end, so none of them overlap g.
5. The new schedule is still valid and has the same size: it's also optimal, and it starts with g.

So the greedy first choice is safe (greedy choice property). After choosing g, the remaining problem is "schedule the meetings starting at or after g.end", the same problem on a smaller input (optimal substructure). Induction finishes the proof.

A related proof style is **greedy stays ahead**: show that after k steps, greedy's k-th meeting ends no later than the k-th meeting of any other valid schedule. Then greedy can never fall behind, so it fits at least as many.

## Interval partitioning: minimum rooms

Now every meeting *must* happen. What's the minimum number of rooms?

Greedy: process meetings by **start** time, and put each one in any room that has become free; open a new room only if none has. A min-heap of room end times finds the earliest-free room in O(log n).

```python
import heapq

def min_rooms(intervals):
    ends = []               # min-heap
    for s, e in sorted(intervals):
        if ends and ends[0] <= s:
            # reuse the earliest-free room
            heapq.heapreplace(ends, e)
        else:
            heapq.heappush(ends, e)
    return len(ends)
```

Why is it optimal? Greedy opens room k only when k − 1 rooms are all busy at time s, so k meetings overlap at that instant. No schedule can use fewer rooms than the maximum number of meetings overlapping at once. Greedy matches that lower bound. This is how calendar systems and some schedulers allocate resources: O(n log n).

## Huffman coding

Text is stored as bits. A fixed-length code gives every symbol the same length: 6 symbols need 3 bits each. If some symbols are much more common, a **variable-length** code can do better by giving them shorter codewords.

For immediate symbol-by-symbol decoding without separators, a **prefix code** is sufficient: no codeword is a prefix of another. Prefix codes correspond to binary trees with symbols at the leaves; the code for a symbol is its path (0 = left, 1 = right).

### The greedy algorithm

David Huffman's 1952 algorithm:

1. Make a leaf for each symbol, weighted by its frequency.
2. Repeatedly remove the **two lowest-weight** trees and merge them under a new node whose weight is their sum.
3. Stop when one tree remains.

```python
import heapq, itertools

def huffman(freq):
    if not freq:
        return {}
    if any(not isinstance(sym, str)
           or type(f) is not int or f <= 0
           for sym, f in freq.items()):
        raise ValueError("frequencies")
    tie = itertools.count()  # tie-breaker
    heap = [(f, next(tie), sym)
            for sym, f in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        f1, _, a = heapq.heappop(heap)
        f2, _, b = heapq.heappop(heap)
        node = (f1 + f2, next(tie), (a, b))
        heapq.heappush(heap, node)
    codes = {}
    pending = [(heap[0][2], "")]
    while pending:
        node, code = pending.pop()
        if isinstance(node, tuple):
            pending.append(
                (node[1], code + "1"))
            pending.append(
                (node[0], code + "0"))
        else:
            codes[node] = code or "0"
    return codes
```

The function accepts string symbols with positive integer frequencies and returns an empty mapping for an empty alphabet. For one symbol it uses the non-empty code "0"; a format with a known message length could instead use an empty codeword. Tree construction uses O(k log k) heap operations for k symbols; materialising all code strings adds their total length, which can be Θ(k²). Integer arithmetic and string costs are additional to unit-cost heap analysis.

The tie counter matters: without it, two entries with equal frequency make `heapq` compare the third elements, and comparing a string with a tuple raises `TypeError`.

> [!example] Six symbols per 100 characters
> Frequencies: a 45, b 13, c 12, d 16, e 9, f 5.
> 1. Merge f 5 + e 9 = 14.
> 2. Merge c 12 + b 13 = 25.
> 3. Merge 14 + d 16 = 30.
> 4. Merge 25 + 30 = 55.
> 5. Merge a 45 + 55 = 100.
>
> Code lengths: a 1, b 3, c 3, d 3, e 4, f 4. Total = 45·1 + 13·3 + 12·3 + 16·3 + 9·4 + 5·4 = **224 bits**, versus 300 with a fixed 3-bit code: about 25.3% fewer payload bits, excluding codebook and framing overhead.

```
            (100)
           0/   \1
          a45   (55)
              0/    \1
            (25)    (30)
            / \     /  \
          c12 b13 (14) d16
                  / \
                f5   e9
```

### Why it's optimal

Exchange argument again: in some optimal tree, the two least frequent symbols are **siblings at the deepest level**. If not, swap them with whatever is deepest; moving a rarer symbol deeper and a more common one shallower can't increase the total cost. So merging the two rarest first is safe, and the merged node behaves like a single symbol in a smaller problem.

Huffman minimises expected length among binary prefix codes for the supplied individual-symbol frequencies. Arithmetic coding and ANS encode sequences so the average cost per symbol need not be an integer; physical output bits remain whole. Zstandard uses FSE, an ANS variant, for sequence symbols and can use Huffman coding for literals.

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
- Greedy commits to the locally best choice and never undoes it; it's usually a sort plus one pass.
- It is correct only with the greedy choice property and optimal substructure, and needs a proof.
- Exchange argument: swap the greedy choice into any optimal solution and show nothing gets worse.
- Interval scheduling: sort by end time. Minimum rooms: sort by start, min-heap of end times.
- Huffman repeatedly merges the two rarest trees, giving an optimal prefix code; it underpins DEFLATE, JPEG and HPACK.

## Further reading
- [Greedy algorithm — Wikipedia](https://en.wikipedia.org/wiki/Greedy_algorithm)
- [Jeff Erickson, Algorithms, chapter 4: Greedy Algorithms (PDF)](https://jeffe.cs.illinois.edu/teaching/algorithms/book/04-greedy.pdf)
- [Interval scheduling — Wikipedia](https://en.wikipedia.org/wiki/Interval_scheduling)
- [Activity selection problem — Wikipedia](https://en.wikipedia.org/wiki/Activity_selection_problem)
- [Huffman coding — Wikipedia](https://en.wikipedia.org/wiki/Huffman_coding)
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [Matroid — Wikipedia](https://en.wikipedia.org/wiki/Matroid)
