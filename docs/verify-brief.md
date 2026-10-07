Part of the mandatory procedure in `docs/CONTENT_PROCESS.md` (step 3).

# Brief: independent fact-check of a module

You are an independent technical reviewer. Another author wrote this module and you must not trust them. Your job
is to find anything inaccurate, invented or misleading, and fix it. The module teaches someone who will build real
hardware, so mistakes have real consequences.

Do the work yourself, without starting sub-agents. Read `/Users/alfiegormley/Github/cs-study-app/CONTENT_SPEC.md`
first so your fixes keep to the format.

For every lesson `.md` and `.questions.json` in your module:

1. **Check every factual claim**: numbers, formulas, units, voltages, MIDI byte values, protocol details,
   component behaviour, product capabilities, historical statements and attributions. Check each against a
   primary or authoritative source: specs, datasheets, manufacturer manuals, CCRMA, application notes,
   textbooks. Fetch the source; don't rely on memory for anything specific.
2. **Recompute all maths** and **run all code** (Python) to confirm the stated outputs.
3. **Check every question**:
   - Is the answer key right?
   - Is any other option also defensibly correct?
   - Do the explanations and worked examples agree with the lesson?
4. **Check the links**: each one must load (`node scripts/check-links.mjs content/<subject>/<module-dir>`) and must
   actually support the claim it's attached to.
5. **Fix problems in place**:
   - Correct errors.
   - Soften or remove claims you can't verify.
   - Rewrite misleading explanations.
   - Keep question ids unchanged. If a question can't be fixed, rewrite it to test the same idea correctly.
   - Don't shorten lessons unnecessarily.
6. Write the verification record `content/<subject>/<module-dir>/verification.json` exactly as specified in
   `docs/CONTENT_PROCESS.md` section 4:
   - a confidence score for every lesson (high/medium/low);
   - every low-confidence claim, with its lesson, confidence and reason;
   - the gaps, corrections, sources and counts.
   Then stamp it: `node scripts/stamp-verification.mjs content/<subject>/<module-dir>`.
7. Run `node scripts/build.mjs --check content/<subject>/<module-dir>` until it passes, verification included.

Report back:

- Totals: how many claims you checked, errors you corrected (list each one: what was wrong and what it is now),
  and claims removed or hedged as unverifiable.
- Any topic the module covers too thinly or misses, compared with the scope given in your task (the subject brief and any project documents it names).
- Anything you still aren't fully confident about after checking.
