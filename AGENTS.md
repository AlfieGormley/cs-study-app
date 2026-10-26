# CS Study app

Read `CLAUDE.md` before investigation or edits. Follow `CONTENT_SPEC.md` and
`docs/CONTENT_PROCESS.md`; changed lessons require an independent verifier.

## Concept-first teaching

Teach fundamentals for someone reading on a phone or a bus. Lead with meaning, behaviour, practical
choices and limitations. Keep only essential equations visible (`formula essential`), put useful reference
maths in `formula reference` blocks, and remove redundant equations, repeated substitutions and long
derivations. Questions should test prediction, explanation and diagnosis rather than formula recall or
routine arithmetic. A `workedExample` can be a reasoning walkthrough. Keep all required facts, safety
guidance and assumptions outside optional maths. This rule applies to future additions and edits and
supersedes conflicting older briefs; retained maths still needs full definitions and verification.

## Real-world analogies

Use a concise, familiar comparison when it improves understanding, in a collapsed
`> [!analogy] Real-world analogy: <short label>` callout with explicit **How it maps:** and
**Where it stops:** paragraphs. Keep the complete technical explanation and required facts outside.
Do not force or repeat comparisons. Audit only active lesson ids from `module.json`, not archival files.
Run `node scripts/audit-analogies.mjs docs/analogy-audit.json` for the inventory. Keyword matches are
review leads, not semantic verification. Keep independent review records and unresolved gaps honest.
