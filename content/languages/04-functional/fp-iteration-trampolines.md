---
id: fp-iteration-trampolines
title: Loops, explicit stacks and trampolines
level: intermediate
minutes: 3
sourceLesson: fp-recursion-tail-calls
summary: A loop or explicit work stack avoids deep Python recursion.
---

A loop or explicit work stack avoids deep Python recursion. This unit develops that mechanism using the earlier units as prerequisites.

## Working without TCO

When the language won't help, you have three options.

## 1. Write the loop

A tail-recursive function translates mechanically into a loop: the parameters become loop variables and the tail call becomes "update and go round again".

```python
# Slicing still copies the remaining list.
def length(xs):
    acc = 0
    while xs:
        xs, acc = xs[1:], acc + 1
    return acc
```

(Aside: `xs[1:]` copies the rest of the list on every step, so this is O(n²) overall, where n is the list's length. Real code would index or iterate. Python lists are arrays, not linked lists.)

```formula
(n − 1) + (n − 2) + ... + 1 + 0
  = n(n − 1) / 2
  = O(n^2)
where
n: the number of items in the list
...: "and so on" down to the last terms
O(n^2): Big-O notation: grows in proportion to n squared (n × n)
In words: the slices copy n − 1 items, then n − 2, and so on, which adds up to about half of n squared copies.
```

For a thousand-item list, the slices copy 499,500 item references altogether. Double the list and the copying roughly quadruples.

## 2. Use an explicit stack

For tree recursion that isn't tail-recursive, keep your own stack in a growable collection subject to available memory:

```python
# Pending tree nodes live in a list.
def tree_sum(root):
    total, stack = 0, [root]
    while stack:
        node = stack.pop()
        total += node.value
        stack.extend(node.children)
    return total
```

## 3. Trampolines

A **trampoline** turns each recursive call into a returned *thunk* (a zero-argument function), and a driver loop keeps calling thunks until it gets a real value. The driver keeps call depth bounded independently of the number of steps, though the exact number of frames depends on the implementation.

```javascript
// Returned functions describe the next
// step.
const trampoline = f => (...args) => {
  let r = f(...args);
  while (typeof r === "function") r = r();
  return r;
};

const count = trampoline(
  function go(n, acc = 0) {
    return n === 0
      ? acc
      : () => go(n - 1, acc + 1);
  });

count(1_000_000);   // 1000000, no overflow
```

It introduces closure/call overhead relative to a direct loop; measure the actual implementation. It's most useful for **mutual recursion** (`isEven` calls `isOdd` calls `isEven`), which a simple loop can't express as neatly.

## Key takeaways
- A loop or explicit work stack avoids deep Python recursion.
- A trampoline returns deferred calls to one iterative driver.

## Further reading
- [Python Types](https://docs.python.org/3/library/stdtypes.html)
- [Sicp](https://sicp.sourceacademy.org/chapters/1.2.2.html)
- [Scheme](https://standards.scheme.org/corrected-r7rs/r7rs-Z-H-5.html)
