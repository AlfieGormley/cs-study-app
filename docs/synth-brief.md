# Brief: Synth Building modules

This subject supports a real project: `/Users/alfiegormley/Github/diy-synth`, a DIY hardware synthesiser to be used
with an Elektron Digitakt, an audio interface and Ableton. Before writing, read these in that repo:
`docs/project-brief.md`, `docs/learning/roadmap.md`, `docs/learning/dsp.md`, `docs/learning/electronics.md`,
`docs/research/hardware-options.md`. The lessons should give the builder the knowledge those documents ask for.

Also follow `/Users/alfiegormley/Github/cs-study-app/docs/new-module.md` (format, depth, 10–12 questions per lesson)
and `CONTENT_SPEC.md`. Do the work yourself, without starting sub-agents.

Extra rules for this subject:

- The learner is a strong software engineer but a beginner in DSP, electronics and C++. They are learning C++
  elsewhere, so **don't teach C++**. Use Python for offline DSP experiments and calculations (run every snippet
  and make sure the stated output is real) and short language-neutral pseudocode for embedded and real-time
  topics.
- **Accuracy is critical, because this will be used to build real hardware.** Every specific number, formula,
  voltage, protocol byte value, standard or product detail must come from a primary or authoritative source:
  - MIDI Association specs
  - manufacturer datasheets and manuals (Elektron, Electro-Smith, PJRC, ST and so on)
  - Julius O. Smith's CCRMA books
  - Analog Devices and TI application notes
  - well-established textbooks or Wikipedia where it's standard
  
  Put the source in the lesson's Further reading or the question link. If you can't verify something, leave it
  out or clearly mark it as approximate.
- Electrical safety: keep to low-voltage practice and say so. No mains work. Give correct, conservative guidance on
  connecting circuits to equipment (protect inputs and outputs, check levels in the device manuals).
- Product facts (Digitakt ports, Daisy or Teensy capabilities) change between models and revisions. Name the
  exact model and revision and the date checked, and tell the learner to confirm against current documentation.
- When you finish, your report **must** list:
  - every topic from the diy-synth docs that this module was meant to cover but you left thin or out, and why;
  - every claim you were not fully confident in.
