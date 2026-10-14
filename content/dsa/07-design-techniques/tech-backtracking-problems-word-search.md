---
id: tech-backtracking-problems-word-search
title: Word search with reversible marking
level: advanced
minutes: 3
sourceLesson: tech-backtracking-problems
summary: Mark the current path without losing original letters, then restore on both success and failure.
---

## Word search

Given a rectangular grid of single-character strings, is a word spelled by a path of horizontally or vertically adjacent cells, using each cell no more than once? The empty word is accepted; a non-empty word on an empty board is rejected.

```python
def exist(board, word):
    if not word:
        return True
    if not board or not board[0]:
        return False
    R, C = len(board), len(board[0])
    if any(len(row) != C for row in board):
        raise ValueError("ragged board")
    if len(word) > R * C:
        return False
    # A unique object cannot match a word
    # letter.
    used = object()  # cannot equal a letter
    def dfs(r, c, k):
        if k == len(word):
            return True
        if not (0 <= r < R and 0 <= c < C):
            return False
        if board[r][c] != word[k]:
            return False
        ch, board[r][c] = board[r][c], used
        found = (dfs(r+1, c, k+1) or
                 dfs(r-1, c, k+1) or
                 dfs(r, c+1, k+1) or
                 dfs(r, c-1, k+1))
        # Restore on failure and on success
        # alike.
        board[r][c] = ch          # restore
        return found
    return any(dfs(r, c, 0)
               for r in range(R)
               for c in range(C))
```

- **Choose** = temporarily replace the cell with a unique object, which cannot equal a string character. This avoids a separate visited set; relative speed requires measurement.
- **Unchoose** = restore the letter. Forget this and a failed path permanently blocks cells that a later path needs.
- **Prune** = the letter mismatch check, which can reject a branch immediately; its effectiveness depends on the grid and word.

Complexity: count the paths the search can try. Every cell is a possible start; the first step has 4 directions and every later step at most 3 (you can't go back the way you came):

```formula
P ≤ 4RC 3^{L − 2}
P = O(RC 3^L)
P ≤ 12 × 4 × 3^8 = 314,928
where
P: the number of paths the search may explore, an upper bound
R: the number of rows in the grid
C: the number of columns in the grid
L: the length of the word, in letters (at least 2 for the first line)
3^{L − 2}: L − 2 copies of 3 multiplied together
O: Big-O, grows no faster than this up to a constant factor
≤: at most
In words: R × C starting cells, 4 choices for the first step and at most 3 for each later one; a 3 × 4 grid and a 10-letter word allow at most about 315,000 paths.
```

So the worst case is **O(R·C·3ᴸ)** for a word of length L. Mismatches and boundaries can reduce this upper bound, but no reduction is guaranteed for every input.

## Key takeaways
- Mark the current path without losing original letters, then restore on both success and failure.
- The branching bound is an upper bound; boundaries and mismatches can reduce actual work.

## Further reading
- [Backtracking — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/02-backtracking.pdf)
