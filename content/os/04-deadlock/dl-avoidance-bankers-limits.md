---
id: dl-avoidance-bankers-limits
title: Claim edges and practical avoidance limits
level: intermediate
minutes: 3
sourceLesson: dl-avoidance-bankers
summary: Single-instance claim edges support a cycle-based avoidance test.
---

## Single-instance resources: the claim-edge graph

If every resource has one instance, there's a cheaper variant using the resource-allocation graph. Each process declares in advance which resources it may request; these appear as dashed **claim edges** `P - - > R`. A request turns a claim edge into a request edge, and it's granted only if converting it to an assignment edge `R → P` creates **no cycle** (counting claim edges). A graph traversal detects cycles in O(V + E), where V is the number of vertices (processes plus resources) and E the number of edges; a dense adjacency-matrix representation can take O(V²).

## Practical limitations

Using this safety test as a general resource manager requires strong assumptions:

- **Max claims are unknown.** A web server thread has no idea how many locks, buffers or file handles it will need.
- **The population changes.** Processes and threads come and go constantly; new claims must be registered and checked against the safety invariant. A changing population is additional bookkeeping, not a fundamental prohibition.
- **Resources change.** Devices fail and memory gets hot-plugged.
- **It's conservative.** Unsafe isn't deadlocked, so it refuses requests that would have been fine, wasting capacity.
- **It's expensive.** O(m·n²) on every request, where n is the number of processes and m the number of resource types, is a lot with thousands of threads.
- **It needs every holder to finish.** A process holding resources while waiting for user input breaks the "everyone eventually completes" assumption.

The *idea* lives on as **admission control**: reserve a worst-case budget before starting work, and refuse or queue requests that would overcommit.

- The Kubernetes scheduler places a pod only on a node whose unreserved capacity covers the pod's declared resource *requests*.
- Linux with `vm.overcommit_memory=2` refuses allocations that would push committed memory past a commit limit, rather than overcommitting and relying on the OOM killer later.
- Connection pools that cap each client at a fixed number of connections stop one client from holding them all.

None is the full Banker's algorithm. They illustrate admission or capacity checks, but Kubernetes requests are scheduling reservations rather than maximum usage claims, and a per-client connection cap alone does not prove pool deadlock freedom.

> [!note] Content gap
> No reproducible runtime benchmark or survey of production adoption accompanies this lesson. Complexity describes the shown algorithm, not a measured duration or proof that all admission-control systems implement it.

## Key takeaways
- Single-instance claim edges support a cycle-based avoidance test.
- Unknown claims, changing resources and check cost complicate general-purpose use.
- Admission controls share reservation ideas but are not all full Banker implementations.

## Further reading
- [Dijkstra: the mathematics behind the Banker’s Algorithm](https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD623.html)
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
