Part of the mandatory procedure in `docs/CONTENT_PROCESS.md` ("Editing existing content").

# Brief: formula and glossary retrofit of one existing module

Project: /Users/alfiegormley/Github/cs-study-app. A personal iPhone study app; the reader is a beginner aiming for
expert, reading on a phone with nobody to ask. Your module directory is given in your task. **Edit only files
inside it.** One exception: if you change a fenced block that has an entry in `content/diagram-overrides.json`,
update that entry's `source` to match exactly. Other agents are working on other modules at the same time.

Read first, and follow exactly:
1. `.claude/skills/writing-formulas/SKILL.md`
2. `.claude/skills/glossary-terms/SKILL.md`
3. `CONTENT_SPEC.md` (format and width limits)

## Job 1: every formula explained

- Run `node scripts/lint-formulas.mjs <module-dir>` for the starting list, then read every lesson `.md` and every
  `.questions.json` (prompt, options, explanations, workedExample) in full. The lint misses things.
- Convert every equation, relation and symbolic calculation into a ```formula block:
  - every symbol, constant, function and unit defined;
  - an "In words:" line;
  - substitution steps with units.
- Assume the reader knows **no** symbol.
- Add the sentence before and the worked example after, as the skill requires. Where a lesson uses a formula
  without explaining where it comes from or when it applies, add that explanation. Optimise for understanding,
  not brevity.
- Program code stays in code blocks. When a code block was really maths written as code (`10**(x/20)`), replace
  it with a formula block. When the code is genuinely useful as code, keep it as well, after the formula.
- Keep question ids, answer keys and option order unchanged. Keep every fact unchanged unless it is wrong. If you
  find an error, fix it and list it in your report.

## Job 2: glossary

- Write `<module-dir>/glossary.json`: an entry for every acronym, bolded term, unit, named
  component/protocol/algorithm/product and piece of jargon a beginner could pause on, across all lessons and
  questions in the module. **Too many is better than too few.** Expect dozens of entries for a module, not a
  handful.
- `node scripts/glossary-coverage.mjs <module-dir>` is the minimum list. Everything it prints must end up either
  defined or listed as skipped, with the reason.
- Before adding a term, check whether it already exists in `glossary-data.js` or in another module's
  `glossary.json`:
  `grep -ril '"<term>"' content/*/*/glossary.json glossary-data.js`
  If it does, don't duplicate it; it links everywhere already. If another module is writing the same term at the
  same moment, that's fine: the build keeps the earlier module's entry.
- Source specific facts in definitions from primary or authoritative sources.

## Finish

- `node scripts/build.mjs --check <module-dir>` must pass apart from the verification errors ("changed after it
  was verified", "glossary term … has no verification entry"). Those are expected: an independent verifier
  reviews your changes and re-stamps. **Never edit `verification.json` or run the stamp script.**
- Put scratch files only in `<scratchpad>/<subject>-<module>/`.

## Report

- Formula blocks added, per lesson, plus any lint hits left in place and why.
- The number of glossary terms, and the coverage candidates you skipped and why.
- Any factual errors you found and fixed.
- Anything you're not fully confident about: specific definitions or formula details, for the verifier to check
  first.
