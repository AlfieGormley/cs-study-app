# Content authoring spec

> **Mandatory:** all new or changed content must go through `docs/CONTENT_PROCESS.md`, which means an independent
> fact-check and a stamped `verification.json`. The build rejects anything that hasn't.

All study content lives under `content/`. Run `node scripts/build.mjs` to validate it and
compile it into `data/` (which the app loads). Run `node scripts/build.mjs --check` to validate
without writing anything.

## Layout

```
content/
  <subject>/
    subject.json                    # { id, title, description, order }
    <NN-module>/                    # e.g. 03-caching
      module.json                   # { id, title, summary, order, lessons: [lessonId, ...] }
      <lessonId>.md                 # lesson body, with frontmatter
      <lessonId>.questions.json     # array of questions for that lesson
```

`lessons` in `module.json` sets the order lessons appear in. Order them basic → advanced.
Every lesson id listed must have both a `.md` and a `.questions.json` file. Ids are
lowercase-kebab-case and must be unique across the whole subject (prefix them, e.g. `cache-eviction`).

## Lesson file (`<lessonId>.md`)

```markdown
---
id: cache-eviction
title: Eviction policies
level: intermediate
minutes: 8
summary: One sentence shown in the lesson list.
---

Intro paragraph...

## A section heading
...

## Key takeaways
- ...

## Further reading
- [Title of source](https://...)
```

- `level` is one of `basic`, `intermediate`, `advanced`.
- `minutes` is an honest reading time.
- Every lesson **must** end with `## Key takeaways` and `## Further reading` sections.

### Supported Markdown (the app has its own small renderer, so stick to this)

- Headings `##` and `###` (don't use `#`; the title comes from frontmatter)
- Paragraphs, `**bold**`, `*italic*`, `` `inline code` ``, `[links](https://...)`
- Bulleted lists (`- `) and numbered lists (`1. `), with one level of nesting (indent 2 spaces)
- Fenced code blocks with ```` ``` ```` (an optional language tag labels the example). Use these for code, config and
  **ASCII diagrams**. Every line inside a code block must be **at most 44 characters** in lessons and **at most
  40 characters** inside questions (prompt, options, explanations, workedExample), because the answer cards are narrower.
  The build rejects wider lines.
- Use `diagram` as the fence language for text drawings without obvious box characters. The build compiles drawings into SVG paths, arrowheads, shapes and labels, and keeps the source as a text alternative. Unambiguous trees become connected node diagrams; complex drawings retain their spatial layout. All examples support copy and an expanded view with zoom.
- Use `flow` for a reviewed, strictly sequential process: one complete step per line. The app draws SVG nodes with downward arrows. Do not use it for branching, cycles, or unlabelled relationships; keep those as text diagrams. The same line-width limits apply.
- Tables using GFM pipes (`| a | b |` + `|---|---|`). Keep them to 2–4 short columns. Write a literal pipe inside a cell as `\|`.
- Callouts are blockquotes whose first line is a tag:
  ```
  > [!note] Optional title
  > Body text...
  ```
  Tags: `[!note]`, `[!tip]`, `[!warning]`, `[!example]`. A plain `>` blockquote also works.
- No raw HTML, images or nested blockquotes. Italic may sit inside bold (`**bold with *italic* inside**`), but don't end both at once (`***`).
- Link URLs may contain one level of brackets, e.g. `https://en.wikipedia.org/wiki/Cache_(computing)`.

### Structured diagrams and reviewed conversions

`scripts/build.mjs` scans fenced blocks in every lesson and question, validates the diagram definitions,
and generates `diagram-catalog.js`. The app loads this catalogue when study content is opened; it is
also included in the offline cache. Do not edit the generated file.

The compiler distinguishes drawings from programs, equations and command output. Supported rendering
families are sequence, graph, tree, flow, memory, matrix and spatial vector layouts. Spatial layouts
replace character strokes with real lines, arrowheads, cells and boxes while preserving label positions.
They do not infer additional connections. Strict tree conversion requires a single root and one parent
per non-root node; ambiguous trees retain their spatial layout.

For a reviewed semantic redraw, add an entry to `content/diagram-overrides.json` with a unique `id`,
its exact fenced `source`, a `title`, and a `diagram` definition. The DNS entry demonstrates participants
and messages; other entries demonstrate nodes/edges, memory rows and matrices. A `mode: "layout"` entry
explicitly identifies a mixed diagram whose code or calculation annotations would otherwise prevent
recognition. Original source text is always retained for copying and comparison. Editing that source
also requires updating its override; unmatched sources and invalid node references fail the build.

`docs/diagram-migration.json` records every converted location and its rendering family, distinguishing
reviewed overrides from automatic conversions. The report is generated, not a claim of human review
of each automatic conversion. Code and equations retain their normal example presentation.

Run `node --test scripts/test-renderer.mjs scripts/test-diagrams.mjs` after renderer/compiler changes.
These checks cover message direction, topology, literal source handling, escaping, classification and
rendering every generated definition. Check desktop/mobile layouts and offline loading in a browser
when changing the renderers or catalogue loading.

## Questions file (`<lessonId>.questions.json`)

A JSON array. Each question:

```json
{
  "id": "cache-eviction-q1",
  "level": "basic",
  "type": "single",
  "prompt": "Markdown allowed. The question.",
  "options": [
    { "text": "Option A", "explanation": "Why A is right or wrong, specifically." },
    { "text": "Option B", "explanation": "..." },
    { "text": "Option C", "explanation": "..." },
    { "text": "Option D", "explanation": "..." }
  ],
  "answer": 1,
  "workedExample": "Markdown. A step-by-step walk-through of how to reach the right answer.",
  "link": { "title": "Source title", "url": "https://..." }
}
```

- `type` is `single` (`answer` is the 0-based index of the one correct option) or `multi`
  ("select all that apply"; `answer` is an array of indices).
- **Aim for 10–12 questions per lesson**: roughly 3 basic, 4–5 intermediate and 3–4 advanced, with at least two `multi`.
- 3–5 options. **Every** option needs an `explanation` saying why it's correct or incorrect.
  Don't just say "Incorrect"; name the misconception.
- `workedExample` is required. Work through the reasoning step by step, the way a tutor would, with
  numbers and calculations where they're relevant. It can use the supported Markdown (lists, code blocks, tables).
- `link` is required and points to a more detailed explanation of the topic.
- Mix the levels within each lesson's questions. Prefer scenario-based questions ("You run a
  service that... what happens when...") over recalling definitions, especially at intermediate and advanced level.
- Vary which option position is correct. Options are shown in the order written, labelled A, B, C...
- Question ids are `<lessonId>-q<N>`. **Never change or reuse an existing question's id**: the app stores the user's
  progress against it. When you add questions, continue the numbering.
- Questions should be answerable from the lesson plus sound reasoning. Don't test trivia the lesson doesn't cover.

## Links

Every URL (in Further reading and in question `link`s) must be verified to load before it's included:

```
curl -s -o /dev/null -w "%{http_code}" -L --max-time 15 "<url>"
```

It must return `200`. Wikipedia rate-limits parallel requests (429), so retry slowly with a browser user-agent
(`-A "Mozilla/5.0"`). `node scripts/check-links.mjs content/<subject>/<module>` checks every link in a module. Prefer stable, reputable sources: Wikipedia, official docs (AWS, Google
Cloud, Azure, Redis, Kafka, PostgreSQL, MDN, IETF RFCs), original papers, engineering blogs from
major companies, martinfowler.com, the System Design Primer on GitHub. Avoid paywalled sites
(Medium-hosted posts are often paywalled) and sites that block curl. If a URL doesn't return 200,
find another source.

## Scratch files

Other authors work at the same time. Put any temporary files in your own folder
(`<scratchpad>/<subject>-<module>/`), never in a shared filename.

## Style

- British English spelling.
- Accurate, specific and practical. Use real numbers, real systems ("this is how DynamoDB / Kafka /
  Postgres do it"), trade-offs and failure modes. Explain *why*, not just *what*.
- Write for someone aiming to become an expert. Basic lessons start from first principles; advanced lessons
  go deep, at the level of a senior or staff engineer interview or *Designing Data-Intensive Applications*.
- Short paragraphs; the app is read on a phone.
- Accuracy matters more than anything. If you aren't sure of a specific figure or default, check the source, or
  phrase it as approximate ("around", "typically"). Don't invent statistics.
- Code examples use Python unless the topic calls for another language (C for OS internals, SQL for databases, etc.).

## Technical terms

The renderer automatically links known terms in prose, including exact term names
in inline code. Add definitions to `glossary-data.js` using a unique stable ID, term,
category, short plain-language definition and explicit aliases. An example and an
HTTPS documentation URL are optional. No special lesson markup is required.

Prefer unambiguous aliases: short uppercase acronyms are case-sensitive, longer
phrases take priority, and matching respects word boundaries. Do not add ordinary
words such as “tries” as aliases for specialised terms. Existing links, fenced code,
diagram labels and quiz answer buttons are not annotated.
