---
id: lin-stack-storage-choices
title: Stack operations and storage choices
level: intermediate
minutes: 4
sourceLesson: lin-stacks
summary: LIFO uses the newest item first.
---

A **stack** is a collection where you can only touch the top. You add to the top (**push**) and remove from the top (**pop**), so the last thing in is the first thing out: **LIFO**.

> [!analogy] Real-world analogy: A pile of plates
> In a pile of clean plates you put new plates on top and take plates from the top. The plate you washed last is the first one you use.
>
> **How it maps:** Putting a plate on is `push`, taking the top plate is `pop`, glancing at it is `peek`, and the plate at the bottom is the oldest item, which leaves last: LIFO.
>
> **Where it stops:** You could physically slide a plate out of the middle; a stack's interface forbids it. A dynamic-array stack also has a capacity that grows by copying, which a pile of plates never needs.

That restriction sounds limiting, but it is exactly the shape of a huge number of problems: anything nested, anything you need to undo in reverse order, and anything where the most recent item is the one that matters.

## The operations

| Operation | What it does | Cost |
|---|---|---|
| `push(x)` | Put x on top | O(1) amortised on a dynamic array |
| `pop()` | Remove and return the top | O(1) amortised on a dynamic array |
| `peek()` | Return the top without removing | O(1) |
| `is_empty()` | Any items left? | O(1) |

Popping or peeking an empty stack is an error (a **stack underflow**). Pushing onto a full fixed-size stack is a **stack overflow**.

```
push 1, push 2, push 3, pop

 |   |     |   |     | 3 |     |   |
 |   |     | 2 |     | 2 |     | 2 |
 | 1 |     | 1 |     | 1 |     | 1 |
 +---+     +---+     +---+     +---+
                          pop -> 3
```

## Implementations

### On a dynamic array

Keep the top at the **end** of the array, so push and pop never shift anything. In Python, a list already is a stack:

```python
stack = []
stack.append(1)    # push
stack.append(2)
top = stack[-1]    # peek -> 2
stack.pop()        # pop  -> 2
if not stack:      # empty check
    ...
```

Push and pop are amortised O(1) in CPython (growth or shrinking can resize the pointer array), and the list’s reference slots are contiguous, so this is fast in practice.

Putting the top at the *front* (`insert(0, x)` and `pop(0)`) would make every operation O(n) on a stack of n items, because every other item shifts. Always grow stacks at the cheap end.

### On a linked list

Push and pop at the **head**:

```python
class LinkedStack:
    def __init__(self):
        self.head = None

    def push(self, x):
        self.head = Node(x, self.head)

    def pop(self):
        if self.head is None:
            raise IndexError("empty")
        x = self.head.val
        # Expose the next item as the new
        # top.
        self.head = self.head.next
        return x
```

Each operation uses O(1) pointer updates and there is never a resize, assuming constant-time node allocation and reclamation in the data-structure model. The cost is a heap allocation per push and worse cache behaviour.

A linked stack is also the basis of the classic **lock-free stack** (the Treiber stack): push and pop retry compare-and-swap on the head until successful. Lock-free progress is not bounded per-thread latency, and safe memory reclamation/ABA handling requires care.

### In the standard libraries

- **Python:** use `list`. (`collections.deque` also works; `queue.LifoQueue` adds thread-safe blocking, which you only need between threads.)
- **Java:** use `ArrayDeque` via the `Deque` interface (`push`, `pop`, `peek`). The old `java.util.Stack` extends `Vector`, so it inherits synchronized methods and it exposes index-based methods that break the stack abstraction. Oracle's docs recommend `Deque` instead.
- **C++:** `std::stack` is an adaptor over another container, `std::deque` by default (you can choose `std::vector`).

## Key takeaways
- LIFO uses the newest item first.
- Place the top at an array end or linked-list head to avoid shifting.

## Further reading
- [Stack (abstract data type) — Wikipedia](https://en.wikipedia.org/wiki/Stack_(abstract_data_type))
- [Deque — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Deque.html)
- [Using lists as stacks — Python tutorial](https://docs.python.org/3/tutorial/datastructures.html)
