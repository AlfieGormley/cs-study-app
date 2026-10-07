---
id: lin-stacks
title: Stacks
level: intermediate
minutes: 13
summary: The last-in, first-out stack, how to implement it on an array or a linked list, the call stack that runs your programs, and the classic stack algorithms — balanced brackets, expression evaluation and the monotonic stack.
---

A **stack** is a collection where you can only touch the top. You add to the top (**push**) and remove from the top (**pop**), so the last thing in is the first thing out: **LIFO**.

Think of a pile of plates. You can't pull one from the middle without disturbing the rest; you take the one on top.

That restriction sounds limiting, but it is exactly the shape of a huge number of problems: anything nested, anything you need to undo in reverse order, and anything where the most recent item is the one that matters.

## The operations

| Operation | What it does | Cost |
|---|---|---|
| `push(x)` | Put x on top | O(1) |
| `pop()` | Remove and return the top | O(1) |
| `peek()` | Return the top without removing | O(1) |
| `is_empty()` | Any items left? | O(1) |

Popping or peeking an empty stack is an error (an **underflow**). Pushing onto a full fixed-size stack is an **overflow**.

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

Push and pop are amortised O(1) in CPython (growth or shrinking can resize the pointer array), and the elements are contiguous, so this is fast in practice.

Putting the top at the *front* (`insert(0, x)` and `pop(0)`) would make every operation O(n). Always grow stacks at the cheap end.

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
        self.head = self.head.next
        return x
```

Each operation uses O(1) pointer updates and there is never a resize, assuming constant-time node allocation and reclamation in the data-structure model. The cost is a heap allocation per push and worse cache behaviour.

A linked stack is also the basis of the classic **lock-free stack** (the Treiber stack): push and pop retry compare-and-swap on the head until successful. Lock-free progress is not bounded per-thread latency, and safe memory reclamation/ABA handling requires care.

### In the standard libraries

- **Python:** use `list`. (`collections.deque` also works; `queue.LifoQueue` adds thread-safe blocking, which you only need between threads.)
- **Java:** use `ArrayDeque` via the `Deque` interface (`push`, `pop`, `peek`). The old `java.util.Stack` extends `Vector`, so it inherits synchronized methods and it exposes index-based methods that break the stack abstraction. Oracle's docs recommend `Deque` instead.
- **C++:** `std::stack` is an adaptor over another container, `std::deque` by default (you can choose `std::vector`).

## The call stack

Your programs run on a stack. Each time a function is called, the runtime pushes a **stack frame** holding its arguments, local variables and the **return address** (where to continue when it finishes). When it returns, the frame is popped.

```python
def a(): return b() + 1
def b(): return c() * 2
def c(): return 5
a()
```

```
call a     call b     call c     c returns 5
+-----+    +-----+    +-----+    +-----+
|     |    |     |    |  c  |    |     |
|     |    |  b  |    |  b  |    |  b  |
|  a  |    |  a  |    |  a  |    |  a  |
+-----+    +-----+    +-----+    +-----+
```

This is why recursion uses O(depth) memory, and why unbounded recursion fails:

- Native thread stacks have implementation- and configuration-dependent limits. Excessive native recursion can exhaust them, often causing a fault; Java can raise StackOverflowError. Compiler optimizations and runtime-managed frames can change this simple model.
- CPython guards itself with a recursion limit, **1,000** frames by default, raising `RecursionError`.

Any recursive algorithm can be rewritten with an **explicit stack** on the heap, which can grow to gigabytes. Depth-first search on a large graph is the usual example (see the graphs module).

## Balanced brackets

Is `{[()()]}` balanced? Is `([)]`? Nesting means the most recently opened bracket must be the first one closed: a stack.

```python
def balanced(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack:
                return False
            if stack.pop() != pairs[ch]:
                return False
    return not stack
```

Three ways to fail:

1. A closer that doesn't match the top: `([)]` fails at `)`, because the top is `[`.
2. A closer with an empty stack: `())`.
3. Openers left over at the end: `((`.

O(n) time, O(n) space in the worst case. Compilers, linters, JSON and XML parsers and your editor's bracket matching all use this idea.

> [!tip] One bracket type?
> If there's only `(` and `)`, you don't need the stack itself, just a counter: +1 for `(`, −1 for `)`, fail if it goes negative, and require 0 at the end.

## Evaluating expressions

### Postfix (Reverse Polish notation)

In **postfix** notation, operators come after their operands: `3 4 +` means 3 + 4. There are no brackets and no precedence rules, and evaluation is a single stack pass:

- Number: push it.
- Operator: pop two values, apply, push the result.

```python
def eval_rpn(tokens):
    stack = []
    for t in tokens:
        if t in {"+", "-", "*", "/"}:
            b = stack.pop()  # right
            a = stack.pop()  # left
            if t == "+":
                stack.append(a + b)
            elif t == "-":
                stack.append(a - b)
            elif t == "*":
                stack.append(a * b)
            else:
                stack.append(a / b)
        else:
            stack.append(float(t))
    if len(stack) != 1:
        raise ValueError("malformed RPN")
    return stack.pop()
```

This teaching evaluator expects numeric tokens and binary operators. Missing operands raise IndexError; invalid numeric tokens raise ValueError. It uses floating-point arithmetic.

Note the pop order: the **first** pop is the **right** operand. Getting it backwards breaks `-` and `/`.

```
5 1 2 + 4 * + 3 -

token  stack
5      [5]
1      [5, 1]
2      [5, 1, 2]
+      [5, 3]
4      [5, 3, 4]
*      [5, 12]
+      [17]
3      [17, 3]
-      [14]
```

HP calculators, the PostScript language, the JVM's bytecode and CPython's bytecode interpreter are all stack machines that work this way.

### Infix to postfix: the shunting-yard algorithm

Humans write **infix** (`3 + 4 * 2`). Edsger Dijkstra's **shunting-yard algorithm** converts it to postfix using a stack of pending operators:

- Operand: send straight to the output.
- `(`: push.
- `)`: pop operators to the output until the matching `(`; discard both brackets.
- Operator `o`: while the top of the stack is an operator with **higher** precedence, or **equal** precedence and `o` is left-associative, pop it to the output. Then push `o`.
- At the end, pop everything left.

```
3 + 4 * 2

token  output      ops
3      3
+      3           +
4      3 4         +
*      3 4         + *   (* beats +)
2      3 4 2       + *
end    3 4 2 * +
```

The result, `3 4 2 * +`, evaluates to 11, respecting precedence. Associativity matters too: `a - b - c` becomes `a b - c -` (left to right), while exponentiation is right-associative, so `2 ^ 3 ^ 2` becomes `2 3 2 ^ ^`, which is 2⁹ = 512.

## The monotonic stack

A **monotonic stack** keeps its contents in sorted order (all increasing or all decreasing) by popping anything that would break the order before each push. It solves "for each element, find the nearest element to the left or right that is bigger (or smaller)" in O(n).

**Next greater element:** for each value, find the first larger value to its right.

```python
def next_greater(nums):
    res = [-1] * len(nums)
    stack = []  # indices; values decrease
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            res[stack.pop()] = x
        stack.append(i)
    return res

next_greater([2, 1, 2, 4, 3])
# [4, 2, 4, -1, -1]
```

The stack holds indices still **waiting** for a bigger value. When `x` arrives, every waiting element smaller than `x` has found its answer and is popped.

There's a `while` inside a `for`, but it's still **O(n)**: each index is pushed once and popped at most once, so the total number of pops over the whole run is at most n. This is an amortised argument, like dynamic array growth.

The same pattern answers "how many days until a warmer temperature", stock span problems and the largest rectangle in a histogram.

## Other uses

- **Undo** in editors: push each action; undo pops it. Redo is a second stack.
- **Browser back button:** a stack of visited pages.
- **Backtracking** (maze solving, Sudoku): push choices, pop to retreat.
- **Parsers:** compilers use a stack to track nested constructs.

## Key takeaways
- A stack is LIFO with constant-time pointer operations or amortised constant-time dynamic-array push/pop; keep the top at the end of an array or the head of a linked list.
- In Java, use `ArrayDeque`, not the legacy synchronised `Stack`.
- Function calls run on the call stack; deep recursion overflows it (CPython's default limit is 1,000), so convert to an explicit stack.
- Balanced brackets and postfix evaluation are single-pass stack algorithms; shunting-yard converts infix to postfix using precedence and associativity.
- A monotonic stack finds next-greater/next-smaller elements in O(n), because each item is pushed and popped at most once.

## Further reading
- [Stack (abstract data type) — Wikipedia](https://en.wikipedia.org/wiki/Stack_(abstract_data_type))
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)
- [Shunting yard algorithm — Wikipedia](https://en.wikipedia.org/wiki/Shunting_yard_algorithm)
- [Reverse Polish notation — Wikipedia](https://en.wikipedia.org/wiki/Reverse_Polish_notation)
- [Deque — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Deque.html)
- [Using lists as stacks — Python tutorial](https://docs.python.org/3/tutorial/datastructures.html)
