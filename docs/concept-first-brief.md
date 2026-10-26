# Concept-first reading and authoring

The reader wants a sound understanding of fundamentals while reading on a bus. Teach what a concept
means, why it matters, what changes when inputs change, and how to make a practical decision. Do not
turn a lesson into a formula-memorisation exercise.

Apply the rule to all future content and edits. The user has explicitly requested review and revision
across the entire existing library, module by module. Audit every active lesson and question, revise
calculation-heavy material wherever it occurs, and retain lesson/question identities and objectives.
An untouched module needs an honest semantic audit decision, not an assumption based on formula counts.

For each active lesson (use `module.json`, not archival originals):

- Read the whole lesson and its questions. Keep the mechanism, assumptions, limitations and useful
  concrete examples. Explain them in ordinary language before introducing notation.
- Remove equations and arithmetic that merely repeat an explanation or a previous example. Keep an
  equation visible only when the relationship itself is necessary for this lesson's understanding.
  Use a `formula essential` fence for that case, with complete definitions and an In words line.
- A genuinely useful reference formula may remain as a `formula reference` fence. The lesson reader
  will show its In words explanation and offer the equation and definitions in a closed disclosure.
  That visible explanation must stand alone without symbols defined inside the disclosure.
- Remove nonessential implementation listings and long derivations; link to an appropriate source
  instead. Preserve short code when understanding that code is the learning objective.
- Rewrite calculation and formula-recall questions to test the same underlying concept through
  prediction, diagnosis or choice. Preserve each existing question id; do not keep an answer index
  artificially if the new correct option is elsewhere. Preserve question counts unless a separately
  justified change is necessary; keep three questions per DSP lesson.
- A workedExample can be a short reasoning walkthrough. Do not add arithmetic just to satisfy the
  field name. All required facts must be in the visible explanation, with optional maths closed.
- Preserve and re-review useful analogies. Do not use analogy panels to hide maths or core facts.
- Retain dictionary entries unless inaccurate; do not delete useful reference definitions just
  because an associated formula is removed from the main lesson.

Read CLAUDE.md, CONTENT_SPEC.md, docs/CONTENT_PROCESS.md and both writing skills. The rule above
supersedes older briefs that request calculations in every worked example. Authors do not stamp
their own changes. A distinct verifier fetches primary sources, checks the changed lessons and all
questions, recomputes remaining maths, executes retained code, rechecks analogy decisions and hashes,
and updates the verification record honestly. Preserve the earlier review history.

Report per lesson: removed, optional and essential formula counts; question ids rewritten and why;
sources checked; code checks; any missing depth, unresolved claim or gap. Do not count removing
unnecessary maths as an accuracy correction.

## Library-wide review record

The independent verifier adds `conceptFirstReview` to the module verification record, preserving the
previous factual verification history. Use ruleVersion 1, distinct author/verifier identities and fetched
primary sources under verifier.sources. Every active lesson needs a current lessonHash and a specific
rationale explaining its formula choices and question decisions, including unchanged lessons. Record
rewritten question ids and their reasons in that lesson's `questionsRewritten` object. This record is
scoped to the editorial changes and classification; it must not claim fresh full verification of unrelated
unchanged material. Existing verification of unchanged glossary entries can be preserved.

Do not add optional maths simply to save content that should be deleted. Prefer fewer useful reference
cards to a long hidden appendix. Retain code when code behaviour is the concept being taught. A theory
lesson may need visible definitions or a short proof; removing essential notation to meet a numerical
quota is not the goal. Review reading time after trimming, keeping saved IDs and migration mappings stable.
