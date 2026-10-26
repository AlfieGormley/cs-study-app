# CS Study app

A personal iPhone study app: a static PWA. Content is in `content/`, gets compiled to `data/` by
`node scripts/build.mjs`, and is served with `./scripts/serve.sh`.

## Concept-first teaching (mandatory)

The reader is learning fundamentals on a phone, often on a bus. Lead with meaning, mechanism, practical
use and limitations. Questions should test prediction, explanation, diagnosis and choices. Do not require
formula memorisation or routine arithmetic that a reader could look up when needed.

Keep an equation visible only when seeing its relationship is essential to understanding the lesson;
mark that fence `formula essential`. Keep useful reference maths in a `formula reference` fence: the lesson
reader shows its standalone `In words:` explanation and collapses the equation and symbol definitions.
Remove redundant formulas, repeated substitutions and long derivations. Do not add a calculation merely
because a question requires a `workedExample`; a clear reasoning walkthrough satisfies that field.
Preserve important assumptions, safety guidance, units, trade-offs and facts needed for questions in the
visible prose. Optional maths must never be a prerequisite for answering a conceptual question.

This rule applies to all future additions and edits, including advanced lessons, and supersedes older
briefs that request calculations or derivations for their own sake. It changes how depth is taught;
all retained maths still requires complete symbol definitions and independent verification.

## Content rule (mandatory)

**Any new or changed study content must follow `docs/CONTENT_PROCESS.md`.** This applies to new subjects,
modules, lessons and questions, and to edits to existing lessons. In short:

1. Write a scoped brief.
2. A sub-agent writes each module.
3. A **separate** sub-agent independently fact-checks it against primary sources, fixes it, and writes
   `verification.json` with confidence scores, low-confidence claims and gaps.
4. Stamp it with `node scripts/stamp-verification.mjs`.
5. The build, link checks, tests and render checks all pass.
6. Report the corrections, gaps and low-confidence areas to the user.

The build enforces this. Don't get round it:
- never stamp without a real verification pass
- never add entries to `content/verification-legacy.json`
- never edit lessons and re-stamp yourself

If a safety check stops a writer, skip that lesson and record it; don't retry it.

## Writing skills (mandatory for all content)

- `.claude/skills/writing-formulas/SKILL.md`: every equation goes in a `formula` block that defines every
  symbol, unit and function, with an "In words" line. Assume basic algebra, use conventional implicit
  multiplication where clear, and include every bracket needed to show the intended operation order.
- `.claude/skills/glossary-terms/SKILL.md`: each module's `glossary.json` gets an entry for every term a
  beginner might not know. Too many is better than too few.

## Real-world analogies (mandatory)

When teaching a technical concept, add a concise, familiar real-world analogy where it makes the concept
easier to understand. Put the analogy in a `> [!analogy] Real-world analogy: <short label>` callout, which
the app renders collapsed by default. Explicitly map the familiar situation to the technical mechanism
and state where the comparison stops working. Keep definitions, technical explanations, assumptions,
formulas and information needed to answer questions outside the collapsed block. Do not force an
analogy onto a straightforward procedure or repeat an analogy without adding useful understanding.
Audit active lessons listed in `module.json`, not archival lesson files. See `CONTENT_SPEC.md` for the
format and `docs/CONTENT_PROCESS.md` for independent verification requirements.

## Other references

- Content format: `CONTENT_SPEC.md`
- Briefs: `docs/new-module.md` (author), `docs/verify-brief.md` (verifier), `docs/synth-brief.md` (example subject brief)
- History and skipped lessons: `docs/RESUME.md`
