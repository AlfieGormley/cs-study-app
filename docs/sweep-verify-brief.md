Part of the mandatory procedure in `docs/CONTENT_PROCESS.md` ("Editing existing content").

# Brief: independent verification of a formula and glossary retrofit

You are an independent reviewer. Another agent has just retrofitted one module of the study app at
/Users/alfiegormley/Github/cs-study-app. It converted formulas into ```formula blocks and wrote the module's
`glossary.json`. Don't trust it. Do the work yourself, without starting sub-agents. **Edit only files inside the
module directory** given in your task. One exception: if you change a fenced block that has an entry in
`content/diagram-overrides.json`, update that entry's `source` to match exactly.

Read first:
- `docs/verify-brief.md` (your standards)
- `.claude/skills/writing-formulas/SKILL.md`
- `.claude/skills/glossary-terms/SKILL.md`

The author's report is in your task. Check its low-confidence items first.

## Scope

1. **Every change**: `git diff -- <module-dir>` (glossary.json is a new, untracked file; read it in full).
   For each changed lesson and question:
   - Every formula is correct.
   - Every symbol's definition, unit and typical value is correct.
   - The "In words" line says exactly what the maths says.
   - Every worked number is right. Recompute it, for example with python3.
   - The new explanatory prose is accurate.
   - No answer key, question id or existing fact was changed wrongly.
2. **Completeness**:
   - `node scripts/lint-formulas.mjs <module-dir>`: convert any remaining equation the author missed. Rule 6
     exceptions may stay; list them.
   - Read the lessons for unexplained symbols or jargon.
   - `node scripts/glossary-coverage.mjs <module-dir>`: add terms the author missed. Too many is better than too
     few.
3. **Glossary**: check every definition against a primary or authoritative source (fetched, not remembered).
   Aliases must not capture ordinary English words or a different meaning used elsewhere in the app. Fix in place.

4. **Wrong-sense links**: run `node scripts/glossary-links.mjs <module-dir> --suspect` and check that each
   flagged word means the same thing here as in its definition. Fix wrong ones by narrowing aliases or rewording.

## Record and stamp

Update `<module-dir>/verification.json` and keep everything already in it:
- Set the `confidence` of each lesson you re-checked, and add a `"glossary"` object with
  `{ "<term id>": { "confidence": "high|medium|low" } }` for **every** term in `glossary.json`.
- Add new `lowConfidence` items for any medium/low claims, and any `corrections` (prefix them "retrofit:").
- Append to a `"revisions"` array (create it if absent):
  `{ "date": "YYYY-MM-DD", "agent": "<you>", "scope": "formula + glossary retrofit", "authorDate": "YYYY-MM-DD", "claimsChecked": N, "errorsCorrected": N, "hedgedOrRemoved": N, "formulaBlocks": N, "glossaryTerms": N }`.
- Add your counts to `summary`, and set `verifier.date` to today. Add the sources you used to `verifier.sources`.

Then run `node scripts/stamp-verification.mjs <module-dir>`, followed by
`node scripts/build.mjs --check <module-dir>`, which must now pass completely.

## Report

- Counts: formula blocks, glossary terms, claims checked, errors corrected (list each one: what was wrong → what
  it is now), items hedged or removed.
- Low-confidence items, each with a reason.
- Terms or formulas you added that the author missed.
