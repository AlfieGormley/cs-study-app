---
id: rc-conditional-ui
title: Choose what to render
level: basic
minutes: 4
summary: Use JavaScript conditions to show alternatives and avoid rendering an accidental zero.
---

A screen often has alternatives: a ready message or a loading message, a result list or an empty state. **Conditional rendering** means describing different UI for different inputs. React uses normal JavaScript decisions rather than a separate template condition language.

## Choose an entire return value

Use an `if` statement before the JSX when a condition changes the whole result. Returning `null` tells React that this component contributes no visible content. It does not remove its parent's other children.

This component excerpt receives a boolean `visible` and a numeric `count`.

```jsx
function ResultSummary({ visible, count }) {
  if (!visible) {
    return null;
  }

  return (
    <p>
      {count > 0
        ? 'Results available'
        : 'No results'}
    </p>
  );
}
```

If `visible` is false, nothing appears from `ResultSummary`. If it is true with a count of zero, the paragraph says `No results`. A positive count produces `Results available`. `!visible` means the boolean opposite of `visible`.

The **ternary operator** has a condition before `?`, a value for the true case after it, and a value for the false case after `:`. It is an expression, so it can go inside JSX braces. An `if` statement itself cannot go there. Prefer an early return or a named variable if several nested ternaries make the JSX difficult to read.

## Show one optional element carefully

The JavaScript **logical AND** operator, `&&`, returns an operand value. When the left operand is falsy, it returns that left value; otherwise it evaluates and returns the right value. It does not always return a boolean.

React renders no text for boolean children, `null` or `undefined`. A number is different: React can display the number zero. This intentional pitfall is a valid component excerpt, but its UI is wrong for a badge that should disappear when the count is zero.

```jsx
function BadBadge({ count }) {
  // At zero, this renders the text 0.
  return <div>{count && <b>New</b>}</div>;
}
```

At zero, `count && ...` returns zero. React receives that number and displays it. Use a boolean condition on the left instead. This corrected component excerpt hides the badge entirely at zero.

```jsx
function Badge({ count }) {
  return (
    <div>
      {count > 0 && <b>New</b>}
    </div>
  );
}
```

Now the condition is false at zero, so React receives false and displays no child text. At a positive count, the condition is true and the `b` element appears. The condition makes the intended threshold explicit, including for negative numbers.

Conditional UI should handle meaningful empty cases, rather than leaving an unexplained blank area. If showing nothing would confuse someone waiting for results, use an explicit empty message instead of `null`. Choosing between these is a product decision; both are valid React values.

## Key takeaways
- Use `if` outside JSX or a ternary expression inside it.
- Returning `null` produces no visible content from that component.
- `&&` returns operand values, so numeric zero can become visible text.
- Compare a numeric count with a threshold before using `&&`.

## Further reading
- [Conditional rendering — React](https://react.dev/learn/conditional-rendering)
