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

```formula
2 ^ 3 ^ 2 = 2 ^ (3 ^ 2) = 2 ^ 9 = 512
(2 ^ 3) ^ 2 = 8 ^ 2 = 64
where
^: raised to the power of: 2 ^ 3 means 2 × 2 × 2 = 8
In words: a right-associative operator works out the rightmost pair first, so 3 ^ 2 = 9 is computed before 2 is raised to it.
```

Python's `**` follows the same convention: `2 ** 3 ** 2 == 512`.

### Equal precedence is the deciding test

Consider three symbolic operand tokens separated by subtraction. The second subtraction must finish the first subtraction before starting its own right operand. By contrast, a right-associative exponent operator leaves an equal-precedence exponent pending until the right-hand exponent is available.

```formula
E_left = (a − b) − c
E_right = a − (b − c)
E_left = (10 − 4) − 2 = 4
E_right = 10 − (4 − 2) = 8
where
E_left: value of a left-associated subtraction expression
E_right: value of the alternative right-associated expression
a: the first operand, here ten
b: the second operand, here four
c: the third operand, here two
In words: changing association changes subtraction’s result, so the operator-stack rule must preserve the intended grouping.
```

The conversion handles each token once and each operator is pushed and popped at most once. This gives linear total stack work in the token count, assuming fixed-time token classification. The displayed rules describe binary operators; unary minus, functions and argument separators require additional grammar rules.

## Key takeaways
- Hold operators until their operands and precedence permit output.
- Equal precedence pops for left associativity but waits for right associativity.

## Further reading
- [Shunting yard algorithm — Wikipedia](https://en.wikipedia.org/wiki/Shunting_yard_algorithm)
- [Reverse Polish notation — Wikipedia](https://en.wikipedia.org/wiki/Reverse_Polish_notation)
