---
id: rc-jsx-rules
title: Write valid JSX
level: basic
minutes: 3
summary: Use fragments, closed tags, className and style objects without confusing JSX with HTML.
---

JSX describes elements using familiar tag shapes, but a JavaScript tool must be able to read it as an expression. A few consistent rules prevent most beginner syntax errors. React and JSX are separate ideas: React is the UI library; JSX is an optional way of writing its element descriptions.

## Group and close the markup

A component returning several neighbouring elements must group them into one returned value. A wrapper such as `section` works when that element belongs in the page structure. A **fragment**, written `<>...</>`, groups neighbouring elements without adding a wrapper element to the browser's DOM.

The DOM, or Document Object Model, is the browser's live tree of DOM nodes. A fragment changes the JSX grouping without creating a new node in that tree. It is useful when a wrapper would be meaningless, but it does not supply layout or styling of its own.

Every JSX tag must close. Write `<br />` rather than `<br>` and `<li>Read</li>` rather than leaving the closing tag out. Paired tags must nest properly: close the inner element before the outer one. This is stricter than some HTML shorthand.

## Use JavaScript attribute names

Use **className** for an element's CSS class. CSS, Cascading Style Sheets, controls appearance; a class name chooses styling rules defined elsewhere. Most React DOM property names use camelCase: words join with later words starting in capitals. `onClick` is an example you will meet in the events lesson. Accessibility attributes such as `aria-label`, and custom `data-*` attributes, retain their hyphens.

For an inline **style**, pass a JavaScript object rather than an HTML style string. Its property names are generally camelCase, such as `backgroundColor`. The outer braces enter JavaScript from JSX; the inner braces create the object. They are two separate uses of JavaScript syntax, not a special double-brace operator.

This component excerpt uses a fragment and explicit CSS string values. The `notice` class can be defined in the project's stylesheet.

```jsx
function Notice() {
  return (
    <>
      <h2 className="notice">Next step</h2>
      <p style={{
        backgroundColor: 'navy',
        color: 'white',
        padding: '8px'
      }}>
        Read the lesson.<br />
        Then try its questions.
      </p>
    </>
  );
}
```

The DOM contains a heading and a paragraph as siblings. The line break is a child of the paragraph. The fragment does not become an extra `div`. `className="notice"` sets the heading's class; it does not create a new component called `notice`.

A common debugging sequence is to check the returned grouping, then matching tags, then attribute names. A syntax error prevents the file being transformed at all, so do this before investigating state or event behaviour. Valid JSX describes structure; visual layout still depends on the browser and CSS.

## Key takeaways
- Group neighbouring returned elements with a meaningful wrapper or a fragment.
- Close every JSX tag, including tags such as `br`.
- Use `className` and camelCase style properties.
- A `style` value is an object; a fragment adds no DOM wrapper.

## Further reading
- [Writing markup with JSX — React](https://react.dev/learn/writing-markup-with-jsx)
- [JavaScript in JSX with curly braces — React](https://react.dev/learn/javascript-in-jsx-with-curly-braces)
