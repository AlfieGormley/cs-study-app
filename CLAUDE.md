# CS Study app

A personal iPhone study app: a static PWA. Content is in `content/`, gets compiled to `data/` by
`node scripts/build.mjs`, and is served with `./scripts/serve.sh`.

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

## Other references

- Content format: `CONTENT_SPEC.md`
- Briefs: `docs/new-module.md` (author), `docs/verify-brief.md` (verifier), `docs/synth-brief.md` (example subject brief)
- History and skipped lessons: `docs/RESUME.md`
