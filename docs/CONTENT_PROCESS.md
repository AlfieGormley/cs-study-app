# Content procedure (mandatory)

Every addition or change to study content in this project goes through this procedure. That covers new subjects,
new modules, new lessons, new questions and edits to existing lessons. There are no exceptions for small
changes. The build enforces it (see "Enforcement" below).

The standard: **nothing goes in that hasn't been checked by an independent agent against primary sources, and
anything that couldn't be checked is either removed, hedged in the text, or recorded as low-confidence.**

## 1. Scope and brief

1. Work out exactly what the content must cover. When it serves a project or goal, read the source documents
   (for example `~/Github/diy-synth/docs/learning/`) and list the topics.
2. Agree the structure with the user if it's unclear. Exclude anything the user covers elsewhere.
3. Write a **subject brief** in `docs/` (model: `docs/synth-brief.md`). It covers:
   - the audience and what they already know
   - what to exclude
   - which code languages to use
   - the authoritative sources to rely on
   - safety constraints
   - the report the author must return

## 2. Author: one sub-agent per module

- Every module is written by its own sub-agent, briefed with `docs/new-module.md`, the subject brief and
  `CONTENT_SPEC.md`.
- Authors must:
  - source every specific number, formula, standard or product fact from a primary or authoritative source
  - run every code snippet and confirm stated outputs
  - verify every link
  - make the module pass `node scripts/build.mjs --check content/<subject>/<module>`, apart from the
    verification errors, which are expected at this point
- The author's report must list:
  1. topics from the scope that it left thin or out, and why
  2. **every claim it wasn't fully confident in**

## 3. Verifier: a separate sub-agent per module

- After the author finishes, start a **different** sub-agent, briefed with `docs/verify-brief.md`. Never let the
  author verify its own work, and never have the orchestrating session do the verification itself.
- Give the verifier the author's list of low-confidence claims to check first.
- The verifier assumes the author is wrong until a source shows otherwise:
  - checks every factual claim against a primary source, fetched rather than remembered
  - recomputes all maths
  - runs all code
  - checks every answer key and distractor
  - checks that every link loads and supports its claim
- The verifier fixes problems in place:
  - corrects errors
  - hedges or removes anything it can't verify
  - keeps question ids stable

## 4. Verification record

The verifier writes `content/<subject>/<module>/verification.json` and then runs
`node scripts/stamp-verification.mjs content/<subject>/<module>`.

```json
{
  "module": "<module id>",
  "author":   { "agent": "...", "date": "YYYY-MM-DD" },
  "verifier": { "agent": "...", "date": "YYYY-MM-DD",
                "independent": true,
                "sources": ["primary sources checked"] },
  "summary":  { "claimsChecked": 0, "errorsCorrected": 0,
                "hedgedOrRemoved": 0 },
  "corrections":   ["what was wrong → what it is now"],
  "lowConfidence": [{ "lesson": "<id>", "claim": "...",
                      "confidence": "medium|low",
                      "reason": "why it isn't high" }],
  "gaps":    ["topics thin or missing vs the scope"],
  "lessons": { "<lesson id>": { "confidence": "high|medium|low",
                                "hash": "<written by stamp>" } }
}
```

**Confidence scores**, per lesson and per flagged claim:
- `high`: every specific claim was verified against a primary source.
- `medium`: core content verified, but some specifics rest on secondary sources or are time-sensitive (product
  facts, versions, prices). These must be hedged in the text.
- `low`: important claims couldn't be verified. Fix the lesson before it ships if you can; otherwise tell the user
  explicitly.

Only stamp after a genuine verification pass. Stamping records the lesson files' hashes; any later edit
invalidates them.

## 5. Integrate and check

Run all of these before reporting:
- `node scripts/build.mjs`: the whole project must pass, including the verification checks.
- `node scripts/check-links.mjs content/<subject>`: 0 failing. Re-check rate-limited URLs slowly by hand.
- `node scripts/test-*.mjs`: all pass.
- Render the new pages at iPhone size (390 px) and check there are no errors, no horizontal overflow and no stray
  Markdown.

## 6. Report back to the user

Always include:
- A per-module table: lessons, questions, claims checked, errors corrected.
- The significant corrections, especially any that would have mattered in practice.
- **Gaps**: topics from the scope covered thinly or not at all.
- **Low-confidence areas**, with their confidence score and reason, plus anything time-sensitive the user should
  re-verify.
- Any topic where you don't have good enough knowledge or sources to write reliable material. Say so plainly
  rather than writing it.

## Editing existing content

Any change to a lesson or its questions follows the same procedure, scoped to the changed lessons:
1. Make the change. Using an author sub-agent is the default; for very small fixes, the orchestrating session may
   make the edit.
2. An independent verifier sub-agent checks the changed lessons.
3. The verifier updates `verification.json` and re-stamps it.

## Safety stops

If a safety check stops an author or verifier, don't retry or rephrase to get round it. Ship the module without
that lesson, record it under "Skipped lessons" in `docs/RESUME.md`, and tell the user.

## Enforcement

`scripts/build.mjs` fails when:
- a module has no `verification.json`;
- the record is incomplete or `verifier.independent` isn't `true`;
- a lesson isn't covered by the record;
- a lesson's files changed after it was stamped.

Modules written before this procedure existed are listed in `content/verification-legacy.json`:
- The list is **frozen**. Never add entries to it.
- Editing any legacy lesson fails the build until that module goes through this procedure and gets its own
  `verification.json`. Once it does, remove its entry from the legacy list.
