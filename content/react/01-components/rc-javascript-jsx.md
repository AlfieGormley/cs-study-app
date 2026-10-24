---
id: rc-javascript-jsx
title: JavaScript values inside JSX
level: basic
minutes: 4
summary: Connect JavaScript expressions, destructuring, callbacks and module imports to readable JSX.
---

JSX does not replace JavaScript. Use JavaScript to calculate a value, then insert that value where the UI needs it. An **expression** is code that produces a value, such as a variable name, a function call or an arithmetic operation. A statement such as `if` controls execution and cannot go directly inside JSX braces.

## Read values with braces

Quotes pass literal text. Braces evaluate a JavaScript expression. `title="name"` passes the text `name`; `title={name}` passes the value held by the variable. In JSX children, `{name}` displays that value. A plain object is not itself a valid text child: choose one of its properties instead.

**Destructuring** extracts named properties into local variables. In a function parameter, `{ name }` reads the `name` property from its argument. The value of that property is not another object merely because braces appear around the parameter.

An **arrow function** is a compact function expression. `name => name.toUpperCase()` takes one input and returns the expression after the arrow. A function passed into another operation is a **callback**. Array `map` calls its callback for each item and collects the returned values into a new array.

This component excerpt receives `person`, an object with a `name` string. No imports are needed inside this excerpt in a project using the modern JSX transform.

```jsx
function Greeting({ person }) {
  const { name } = person;
  const names = ['Ada', 'Grace'];
  // Transform each name, then join text.
  const shout = names.map(
    name => name.toUpperCase()
  ).join(', ');

  return (
    <section title={name}>
      <h2>Hello, {name}</h2>
      <p>{shout}</p>
    </section>
  );
}
```

Given a person named Sam, the heading reads `Hello, Sam`; the paragraph reads `ADA, GRACE`. `map` has not changed the original strings in `names`. Here it produces strings which the array join method combines into one string; a later lesson maps data directly to JSX elements.

If an arrow callback has a block body with braces, write an explicit `return` to return a value. Parentheses around JSX group an expression; braces after the arrow begin a block. Mixing these up can make a list silently contain `undefined` instead of the intended elements.

## Move components between files

An **export** makes a value available outside its file. An **import** obtains it from another module. A JavaScript module is a file executed under JavaScript's module rules; imports and exports let it share values. A default export is imported without braces and can be given a local name. A named export is imported with braces and its exported name, unless explicitly renamed.

The following two labelled files form one example. `./Badge.jsx` is the relative path to the neighbouring file. Named-import braces select an export; they are not object destructuring, despite the similar appearance.

```jsx
// Badge.jsx
export default function Badge() {
  return <span>Beginner</span>;
}
export const courseTitle = 'React';

// App.jsx
import Badge, {
  courseTitle
} from './Badge.jsx';

export default function App() {
  return (
    <h1>{courseTitle} <Badge /></h1>
  );
}
```

These are ordinary JavaScript module rules, not a special React data flow. The earlier `Greeting` function can similarly be exported and imported. Imports run at the file level; they do not belong inside a component body.

## Key takeaways
- Quotes give literal strings; JSX braces evaluate expressions.
- Destructuring reads object properties into local names.
- An arrow expression returns implicitly; a block body needs `return`.
- Default imports and named imports use different syntax.

## Further reading
- [JavaScript in JSX with curly braces — React](https://react.dev/learn/javascript-in-jsx-with-curly-braces)
- [Importing and exporting components — React](https://react.dev/learn/importing-and-exporting-components)
- [Arrow functions — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions)
- [Destructuring — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring)
