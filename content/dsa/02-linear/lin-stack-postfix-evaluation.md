---
id: lin-stack-postfix-evaluation
title: Evaluate postfix expressions with a stack
level: intermediate
minutes: 3
sourceLesson: lin-stacks
summary: Push operands and replace the last two with each operator result.
---

A stack removes its newest value first. In postfix notation that value is the right operand of a binary operator, and the next value is the left operand. This is a teaching evaluator for numeric tokens, not a complete expression parser.

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
            # Operand tokens wait for their
            # operator.
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

### Trace the operand contract

For the tokens `10 4 -`, push ten, then four. The first pop is four, the right operand; the second is ten, the left operand. Subtracting in that order returns six. For `8 2 /`, the same rule returns four. Reversing the order would return negative six and one quarter respectively.

The example deliberately leaves several malformed-input errors visible. An operator with too few operands raises IndexError. A nonnumeric operand token raises ValueError during float conversion. Two leftover values raise the final malformed-expression error. Division by zero raises ZeroDivisionError. A production parser would catch and present these errors with token positions.

Each token is processed once, so evaluation is linear in the token count when token conversion and arithmetic costs are treated as fixed. The stack can hold a linear number of operands. Very large numeric tokens, precision requirements and arbitrary-precision arithmetic need their own cost and representation model.

## Key takeaways
- Push operands and replace the last two with each operator result.
- The first popped value is the right operand.

## Further reading
- [Reverse Polish notation — Wikipedia](https://en.wikipedia.org/wiki/Reverse_Polish_notation)
