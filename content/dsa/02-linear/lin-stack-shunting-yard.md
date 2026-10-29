---
id: lin-stack-shunting-yard
title: Precedence and associativity with shunting-yard
level: intermediate
minutes: 3
sourceLesson: lin-stacks
summary: Hold operators until their operands and precedence permit output.
---

Postfix evaluation needs no operator-precedence rule because each operator follows its operands. To convert ordinary infix text, keep a separate stack of pending operators while emitting the operand order. The conversion trace below concerns expression tokens, not Python source.

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

The result, `3 4 2 * +`, evaluates to 11, respecting precedence. Associativity matters too: `a - b - c` becomes `a b - c -` (left to right), while exponentiation is right-associative, so `2 ^ 3 ^ 2` becomes `2 3 2 ^ ^`. Grouping from the right gives a very different answer from grouping from the left:

```formula reference
2 ^ 3 ^ 2 = 2 ^ (3 ^ 2) = 2 ^ 9 = 512
(2 ^ 3) ^ 2 = 8 ^ 2 = 64
where
^: raised to the power of: 2 ^ 3 means 2 × 2 × 2 = 8
In words: grouping from the right first raises 3 to the power 2, giving 9, and then raises 2 to the power 9, giving 512. Grouping from the left would instead square 8 and give 64, so the associativity rule changes the answer.
```

Python's `**` follows the same convention: `2 ** 3 ** 2 == 512`.

### Equal precedence is the deciding test

Precedence alone cannot decide `a - b - c`, because both operators have the same precedence. Associativity breaks the tie. Subtraction groups from the left, so when the second `-` arrives it first pops the pending `-`: the first subtraction finishes before the second starts its right operand. With `10 - 4 - 2` that gives (10 − 4) − 2, which is 4; grouping from the right would wrongly give 8. A right-associative operator such as `^` does the opposite: an equal-precedence `^` already on the stack stays there, waiting for the right-hand exponent.

> [!analogy] Real-world analogy: A railway shunting yard
> The algorithm is named after a railway shunting yard because it works like one. Wagons arrive in one order, and some are pushed into a dead-end siding to wait while others go straight through to the departing train. A wagon parked last in the siding is the first to come back out.
>
> **How it maps:** Operands are wagons that go straight to the output train. Operators are parked in the siding, which is the operator stack, and leave it, newest first, when an incoming operator of lower precedence (or equal precedence and left-associative) or a closing bracket requires them to.
>
> **Where it stops:** A real siding has no rules about which wagon outranks another; precedence and associativity are what make the algorithm work. Brackets also have no railway counterpart: they act as markers inside the siding that stop operators being released too early.

The conversion handles each token once and each operator is pushed and popped at most once. This gives linear total stack work in the token count, assuming fixed-time token classification. The displayed rules describe binary operators; unary minus, functions and argument separators require additional grammar rules.

## Key takeaways
- Hold operators until their operands and precedence permit output.
- Equal precedence pops for left associativity but waits for right associativity.

## Further reading
- [Shunting yard algorithm — Wikipedia](https://en.wikipedia.org/wiki/Shunting_yard_algorithm)
- [Reverse Polish notation — Wikipedia](https://en.wikipedia.org/wiki/Reverse_Polish_notation)
