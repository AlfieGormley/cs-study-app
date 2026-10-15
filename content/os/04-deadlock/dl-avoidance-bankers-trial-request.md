---
id: dl-avoidance-bankers-trial-request
title: Testing a resource request
level: intermediate
minutes: 2
sourceLesson: dl-avoidance-bankers
summary: Reject a request above the declared remaining need; wait if free units are insufficient.
---

## The request algorithm

When a process asks for more units, the system makes two comparisons and, if both pass, three trial updates:

```formula
Request ≤ Need[p]
Request ≤ Available
Available_new = Available − Request
Allocation_new[p] = Allocation[p] + Request
Need_new[p] = Need[p] − Request
where
p: the process making the request
Request: the vector of extra units p asks for now, one number per resource type
Need[p]: the units p may still request under its declared maximum
Available: the vector of units free right now
Allocation[p]: the units p holds now
Available_new, Allocation_new[p], Need_new[p]: the trial ("pretend") values if the request were granted
≤: less than or equal to, checked for every resource type
In words: a request must fit inside the process's remaining claim and inside what is free; if it does, move those units from the free pool to the process on paper, then test the result.
```

The request algorithm:

1. If any request component exceeds the corresponding remaining need: error. The process has exceeded its declared maximum.
2. If any request component exceeds the corresponding free count: the requesting process must wait; the resources simply aren't there.
3. Otherwise, **pretend to grant it** by making the three updates.
4. Run the safety algorithm on the pretend state. Safe: make it real. Unsafe: roll back and make `p` wait.

The worked example below runs exactly these steps with real numbers.

```python
def request(p, req, avail, alloc, need):
    if len(req) != len(avail):
        raise ValueError("request width")
    if any(x < 0 for x in req):
        raise ValueError("negative request")
    m = range(len(req))
    if any(req[r] > need[p][r] for r in m):
        raise ValueError("over max claim")
    if any(req[r] > avail[r] for r in m):
        return "wait"
    # pretend to grant, then test
    a = [avail[r] - req[r] for r in m]
    # Copy rows: trial grants must not
    # mutate.
    al = [row[:] for row in alloc]
    nd = [row[:] for row in need]
    for r in m:
        al[p][r] += req[r]
        nd[p][r] -= req[r]
    safe, _ = is_safe(a, al, nd)
    return "grant" if safe else "wait"
```

This request function returns a decision on copied state; it does not commit a grant. A real allocator must serialize the check and state update, validate process IDs and matrix dimensions, and manage waiting requests.

## Key takeaways
- Reject a request above the declared remaining need; wait if free units are insufficient.
- Trial grants update copied counts before running the safety test.
- A production allocator must serialize the decision and committed state change.

## Further reading
- [Dijkstra: the mathematics behind the Banker’s Algorithm](https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD623.html)
