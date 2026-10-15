---
id: type-coercion-behaviour
title: Coercion and the strong/weak labels
level: basic
minutes: 3
sourceLesson: type-static-dynamic
summary: Strong and weak are informal labels; identify the exact conversion rules instead.
---

Static versus dynamic describes when checking happens. A different, informal discussion concerns which implicit conversions a language permits; it needs concrete operator examples rather than a single strength label.

## Strong and weak: how much coercion?

The second axis is about **implicit conversions** (coercions). When you combine mismatched types, does the language refuse, or does it convert one of them for you?

Unlike static/dynamic, "strong" and "weak" have no single formal definition. They describe a spectrum. JavaScript sits near the weak end:

```js
"5" + 2      // "52"  (number -> string)
"5" - 2      // 3     (string -> number)
"3" * "4"    // 12
[] + {}      // "[object Object]"
0 == ""      // true
1 + undefined // NaN
```

Under this informal coercion-based convention, Python sits near the strong end. `"5" + 2` raises `TypeError` rather than guessing. Python still has a few deliberate coercions: `1 + 2.5` widens the int to a float, and `1 + True` is `2` because `bool` is a subclass of `int`.



## Reading an operator before trusting it

In the first JavaScript expression, addition first converts operands to primitive values. Because one primitive is a string, the other becomes text and concatenation produces two characters. Subtraction instead requests numeric operands, so the text digit becomes a number before subtraction. The result therefore depends on the operator as well as on the values.

For equality, use the actual rule rather than the strong/weak label: JavaScript `==` can convert operands; `===` compares without that coercion. Strict equality still has its own rules, including that `NaN` is unequal to itself. Python’s refusal to concatenate a string and an integer does not imply it forbids every mixed numeric operation.

## Key takeaways
- Strong and weak are informal labels; identify the exact conversion rules instead.
- JavaScript addition and subtraction use different conversion rules; Python rejects string-plus-integer concatenation.

## Further reading
- [ECMAScript specification: Expressions](https://tc39.es/ecma262/multipage/ecmascript-language-expressions.html)
- [Python built-in numeric types](https://docs.python.org/3/library/stdtypes.html)
- [C11 draft standard](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
