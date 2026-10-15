# Short lessons and explanatory code comments

The user wants each study lesson to be a manageable 3–5 minute unit, with its own completion date and
a few questions about that unit. They also want code comments that explain meaningful operations and
what any demonstrated outputs show. Preserve the course's depth by dividing material, not deleting it.

Work on the assigned module only. Follow `docs/CONTENT_PROCESS.md`, `CONTENT_SPEC.md`, the formula
and glossary skills. Authors and independent verifiers must be different agents. Never stamp an
author's work before a real independent verification pass.

## Split existing lessons

- Group neighbouring sections around one coherent learning objective. Target roughly 400–900 words
  including code and formula explanations, and a realistic reading time of 3–5 minutes. A shorter unit
  is fine when its topic is naturally small. Preserve all substantive source material, worked examples,
  caveats, code, formulas and diagrams. A difficult topic may need more than one short lesson.
- Give each new lesson a stable, descriptive, subject-unique id and a standalone title, summary and
  `minutes`. Do not reuse an old long lesson id for a new short lesson.
- Add `sourceLesson: <old-lesson-id>` to every new lesson's frontmatter. In `module.json`, replace each
  old lesson in `lessons` with its new lessons in curriculum order. Add a `migrations` map from each old
  lesson id to its ordered new lesson ids, for example:

  ```json
  "migrations": { "old-topic": ["old-topic-basics", "old-topic-tradeoffs"] }
  ```

- Keep original lesson and question files in place as archival source; remove their ids from the active
  `lessons` list. Existing deep links and completion dates use `migrations` to reach the new units.
- Each new lesson needs its own `## Key takeaways` and `## Further reading`. Make takeaways specific
  to that unit rather than copying the original whole lesson's summary into every unit. Reuse the
  verified source links relevant to that unit. Preserve necessary prerequisites in the curriculum order
  and enough local context to understand each example, symbol and question.

## Divide associated questions

- Move every existing question into the short lesson that actually teaches the concepts it tests.
  Keep every original question id and answer key. Aim for 2–4 focused questions per unit; 1–5 is
  acceptable when keeping the existing questions together is pedagogically better.
- A unit's questions must be answerable from that unit and its earlier prerequisites, not a later unit.
  Verify this explicitly. Do not allocate questions by number, difficulty or an even division alone.
- Add a small, verified question only where a unit otherwise has no suitable question. New question
  ids use the new lesson id and must never collide with or replace existing question ids.
- Preserve explanations and worked examples. Improve comments inside their code when helpful.

## Improve code comments

- Explain non-obvious operations, the purpose of branches/loops, mutations and the meaning of any
  shown output. Avoid comments that merely repeat an obvious assignment.
- Keep executable statements unchanged where possible. Do not invent or imply a particular output
  for partial, nondeterministic or environment-dependent examples. Label any illustrative output.
- Respect 44-character code lines in lessons and 40 in questions. Use preceding comment lines when
  an inline explanation would exceed the limit.
- Check executable examples and their stated outputs. Compare comment-stripped code with the original
  to confirm that explanatory edits do not change behaviour.

## Independent verification

The verifier reviews the new grouping, prerequisites, each question's placement, new local takeaways,
comments and any new questions. Check factual claims against fetched primary sources, execute examples,
and preserve the verified original facts. Existing glossary entries need no rewriting, but their
verification records must remain present and their hashes valid.

For author diagnostics before stamping, the coordinator's scratch helper
`/tmp/cs-study-short-lessons/author-dictionary-snapshot.mjs <scratch-output> [root]` runs the real compiler's
pre-write stage and saves its validation errors alongside scratch glossary and renderer modules. It never
stamps, changes repository outputs or turns an invalid build into a pass. Its output has been compared with
the genuine whole build, including namespaced IDs and donated aliases. Final independent verification and
release checks must still use a genuinely stamped whole-build snapshot.

Check ambiguous glossary names in the compiled dictionary as well as local source entries. A phrase may
resolve to another module's definition. Prefer precise existing aliases or narrow local terms: for example,
`server processing time` for request-handling duration, rather than bare `processing time`, which denotes
a stream processor's clock timestamp in system design. Time-window sizes, algorithm sliding windows,
instruction windows and TCP windows likewise need the definition appropriate to their context.

For a diagnostic of every actual rendered link in the active units and complete question fields, run
`/tmp/cs-study-short-lessons/inspect-rendered-term-contexts.mjs <compiler-snapshot> <source-module> <output.json>`.
The snapshot may be the real compiler's scratch dictionary/renderer above or a genuinely built isolated
release. The helper uses that renderer, excludes archived lessons, and records each linked phrase's
compiled identity, full definition and surrounding text. Review the foreign-subject groups first, then
ambiguous terms within the same subject. A foreign definition can be correct; check its meaning rather
than removing links mechanically. This diagnostic does not replace source review or a stamped build.

Return replayable dictionary checks in the verifier report's `dictionaryProbes` array. Each item records
`phrase`, `subject`, `id` (or `null` for an intentionally unlinked phrase), and, for positive checks, the
full expected `definition` and actual `rendered` HTML. Keep summary counts and paths to larger ledgers
in a separate field. The integration checker rejects malformed or empty probe arrays; it must not
silently skip a module because its report uses a different schema.

By default, `id` is the exact lookup for the whole `phrase`. A contextual phrase can contain a linked
word without being a dictionary alias itself, or contain several linked terms. Mark those probes
`lookup: "rendered-context"`; record one row per target with its unchanged full `definition` and
complete `rendered` HTML. Integration then checks that exact target ID occurs in the actual rendered
context, that its full compiled definition matches, and that the entire HTML matches. Exact alias
probes retain their whole-phrase lookup checks; never replace one with a context probe to hide drift.

Formula lint is a heuristic, so also inspect the prose, tables and diagrams. Symbolic indexing ranges
such as “vertices 0 to n − 1” need a card or equivalent natural-language wording. Define coordinates
and other variables locally in each short unit. Inline code formatting is an exception only for real
program code. Keep closing fences on their own lines so they cannot swallow following prose.

Update `verification.json` so `lessons` contains precisely the active new ids, with genuine confidence
scores, sources and a record of the split/comment changes. Original verification entries may be retained
under `archivedLessons` for provenance. Stamp only after reviewing. Run the scoped build, formula lint,
glossary coverage and link checks. Report counts, corrections, uncertainty and any missing coverage.

Do not edit generated data or shared app/compiler files. The coordinating agent builds and checks the
complete app once the module work is verified.
