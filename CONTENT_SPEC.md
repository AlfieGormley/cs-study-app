# Content authoring spec

> **Mandatory:** all new or changed content must go through `docs/CONTENT_PROCESS.md`, which means an independent
> fact-check and a stamped `verification.json`. The build rejects anything that hasn't.

All study content lives under `content/`. Run `node scripts/build.mjs` to validate it and
compile it into `data/` (which the app loads). Run `node scripts/build.mjs --check` to validate
without writing anything.

## Concept-first reading (mandatory)

Design for understanding fundamentals while reading on a phone or a bus. Explain what a concept means,
how it behaves, why it matters and when to use it. Use a short concrete example when it improves that
understanding. Keep assumptions, limitations, trade-offs, units and safety guidance in the main prose.

Choose maths deliberately for each lesson:

- **Essential:** seeing the relationship is necessary to understand the objective. Use a `formula essential`
  fence and explain its practical meaning before and after it. It stays visible in the lesson.
- **Reference:** useful when applying the idea, but unnecessary to grasp the concept. Use a `formula reference`
  fence. The lesson shows the `In words:` explanation with a closed “Show the maths” disclosure for the
  equation and definitions. Write that explanation to stand alone without hidden symbol definitions.
- **Redundant:** repeats the prose, another formula or routine arithmetic. Remove it. Link to a detailed
  source for long derivations rather than reproducing them.

Do not add a formula, code listing or worked calculation to every lesson as a template requirement.
Keep short code where understanding the code is the objective. A useful numerical example may state
the result and implication in ordinary language without displaying every substitution.

Questions should test predictions, explanations, diagnosis and practical choices. Avoid pure formula
recall and repetitive arithmetic. A genuinely essential numerical question must provide the relationship
or necessary data; test interpretation, not memory. Every question must be answerable with the optional
maths and analogies closed. The required `workedExample` is a reasoning walkthrough; it need not calculate
anything. Formula cards in quizzes remain expanded so question data and feedback are available directly.

This rule applies to all new content and edits and supersedes conflicting requirements in older briefs.
Advanced depth comes from mechanisms, constraints, failure modes and trade-offs, with essential maths
where needed. Retained equations still follow all formula-writing and independent-verification rules.

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
- `minutes` is an honest reading time for the main explanation. Keep each lesson to one manageable learning
  objective, usually 3–5 minutes. Remove redundant detail before splitting a longer topic.
- When splitting an existing lesson, use new ids, put `sourceLesson: <old-id>` in each new lesson's
  frontmatter and add `"migrations": { "<old-id>": ["<new-id>", "<new-id>"] }` to `module.json`.
  Preserve original files as archival source and keep existing question ids stable when moving them.
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
  Tags: `[!note]`, `[!tip]`, `[!warning]`, `[!example]`, `[!analogy]`. A plain `>` blockquote also works.
  Analogy callouts render as native expandable disclosures, closed on initial load. Other callouts remain visible.
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
- **Aim for 2–4 focused questions per short lesson**, testing the concepts that unit teaches. Use `multi`
  where appropriate. Preserve existing questions when splitting a long lesson; 1–5 per unit is acceptable
  when this keeps related questions together. Add a verified question if a new unit otherwise has none.
- 3–5 options. **Every** option needs an `explanation` saying why it's correct or incorrect.
  Don't just say "Incorrect"; name the misconception.
- `workedExample` is required. Work through the reasoning step by step, the way a tutor would, with
  numbers only when they improve understanding. Do not manufacture a calculation to fill this field.
  It can use the supported Markdown (lists, code blocks, tables).
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
(`-A "Mozilla/5.0"`). `node scripts/check-links.mjs --active content/<subject>/<module>` checks the
reading and question links in the active lessons listed in `module.json`. Without `--active`, the checker
also inventories archived originals and other matching Markdown/JSON files. Report unavailable archival
links separately and preserve the originals; do not describe an active-only pass as an all-file pass.
Glossary source links and factual support still require the separate glossary review. Prefer stable, reputable sources: Wikipedia, official docs (AWS, Google
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
- Basic lessons start from first principles. Advanced lessons deepen mechanisms, constraints and decisions;
  keep them concept-first too, without making interview arithmetic or derivations the default.
- Short paragraphs; the app is read on a phone.
- Accuracy matters more than anything. If you aren't sure of a specific figure or default, check the source, or
  phrase it as approximate ("around", "typically"). Don't invent statistics.
- Code examples use Python unless the topic calls for another language (C for OS internals, SQL for databases, etc.).
  Add concise comments explaining meaningful operations and the meaning of demonstrated outputs.
  Keep executable behaviour intact and verify any claimed output. Avoid comments that repeat obvious syntax.

## Real-world analogies

For each lesson introducing a technical concept, use a familiar real-world comparison when it helps a reader build an accurate
mental model. Review each active lesson individually; do not insert generic filler or repeat one analogy
across unrelated lessons. A short procedure, calculation or worked-code continuation may need no additional
analogy when the comparison would not add understanding.

Use this exact callout format, with every line (including blank lines) prefixed by `>`:

```markdown
> [!analogy] Real-world analogy: <familiar situation>
> Describe the situation in a few short sentences.
>
> **How it maps:** Name the technical concept and explicitly connect its parts or behaviour to the situation.
>
> **Where it stops:** State the important limitation that prevents the reader taking the comparison literally.
```

- Keep each analogy focused on the lesson's learning objective, usually one short callout per concept.
- Place it near the explanation it supports. Use everyday settings that require no specialist knowledge.
- Keep the technical explanation complete with the analogy closed. Definitions, prerequisite facts, formulas,
  safety guidance and information needed to answer questions must remain visible in the main lesson.
- Prefer prose inside the disclosure. Keep required formulas and executable examples outside it.
- An analogy is a teaching aid, not evidence or a proof. Independently verify its technical mapping and limits
  against primary sources, following `docs/CONTENT_PROCESS.md`; preserve question ids and existing verification.
- In questions, optional analogies may appear in feedback or worked examples after answering. Do not put
  analogy disclosures in prompts or answer options, and do not give away answers in an optional hint.
- Do not use raw HTML, an `open` attribute, or JavaScript to expand analogies automatically. The native summary
  must stay usable by touch, keyboard and assistive technology, including offline.
- `node scripts/audit-analogies.mjs` inventories all active lessons and question fields. Candidate matches and
  missing callouts are review leads, not proof of a missing or correct analogy. Record any remaining review
  work honestly; a keyword scan is not a semantic audit.

## Technical terms

Follow `.claude/skills/glossary-terms/SKILL.md`. Every module has a `glossary.json` with an entry for every
acronym, bolded term, unit and piece of jargon a beginner might not know. **Too many is better than too few.**
The renderer links each known term (and its aliases) the first time it appears in each section, including exact
term names in inline code. No lesson markup is needed. Short uppercase acronyms are case-sensitive, longer phrases
take priority, and matching respects word boundaries. Existing links, fenced code, diagram labels and quiz answer
buttons are not annotated. Don't add terms to `glossary-data.js`; it is the frozen core list.

## Formulas

Follow `.claude/skills/writing-formulas/SKILL.md`. Every equation goes in a fenced `formula` block: equation lines,
a `where` line, a `symbol: meaning` line for **every** symbol, unit and function used, then `In words: ...`. The
build rejects undefined symbols, unmatched grouping brackets and missing "In words" lines. Assume the reader
can read basic algebra: use implicit multiplication for unambiguous products, retain signs between numbers or
ambiguous names, and bracket compound numerators, denominators, exponents and function arguments. Equation
lines obey the 44/40 character limits; definitions wrap freely.

Use `formula essential` for relationships that must stay visible in the main lesson. A `formula reference`
fence keeps its In words explanation visible and collapses the equation and definitions in lesson
reading; quiz formula blocks stay expanded. Both forms have identical correctness checks. Existing
unmarked `formula` blocks stay expanded until individually reviewed; do not mechanically hide maths
that older prose or questions depend on. Use an explicit essential/reference choice for new or revised blocks.
