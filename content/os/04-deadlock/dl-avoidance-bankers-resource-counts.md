---
id: dl-avoidance-bankers-resource-counts
title: Describing resource counts
level: intermediate
minutes: 3
sourceLesson: dl-avoidance-bankers
summary: Available counts free units; Allocation counts units held; Max bounds simultaneous holdings.
---

## What the algorithm needs

The algorithm counts resources in units: one lock, one tape drive, one buffer. Units of the same **resource type** are interchangeable, so a process asks for "two of type B", not for a particular one.

It writes these counts as lists with one number per resource type. With three types A, B and C, the list (7, 5, 3) means 7 of A, 5 of B and 3 of C. Such a list is a **vector**, and a table of vectors with one row per process is a **matrix**.

The algorithm stores a count for each process and resource type in four structures:

| Structure | Shape | Meaning |
|---|---|---|
| `Available` | One count per resource type | Free units of each type |
| `Max` | One row per process | Most each process may ever hold |
| `Allocation` | One row per process | Currently held |
| `Need` | One row per process | What each may still ask for |

`Need` is not declared by anyone; it is worked out from the other two, one entry at a time:

```formula
Need[i][j] = Max[i][j] − Allocation[i][j]
Need[P0][B] = 5 − 1 = 4
where
i: the process, numbered from zero to one less than the process count (P0, P1, …)
j: the resource type (A, B, C, … up to m types)
n: the number of processes
m: the number of resource types
Max[i][j]: the most units of type j that process i has declared it may ever hold at once
Allocation[i][j]: the units of type j that process i holds right now
Need[i][j]: the units of type j that process i may still ask for before it finishes
P0: process number 0
B: resource type B; in the example P0 has declared at most 5 units of B and holds 1
In words: what a process may still request is its declared maximum minus what it already has.
```

So a process that declared at most 5 units of B and already holds 1 may ask for 4 more. Doing this for every entry gives the whole `Need` matrix. The formula only makes sense if no process ever holds more than it declared, which the request algorithm below enforces.

The crucial requirement is `Max`: each process must **declare its maximum claim up front**. That is also the algorithm's biggest practical weakness.

## Key takeaways
- Available counts free units; Allocation counts units held; Max bounds simultaneous holdings.
- Need is the componentwise difference between Max and Allocation.
- Maximum claims and interchangeable resource units are essential assumptions.

## Further reading
- [Dijkstra: the mathematics behind the Banker’s Algorithm](https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD623.html)
