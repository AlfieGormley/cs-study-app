---
id: elec-solder-joint-technique
sourceLesson: elec-measurement-soldering
title: "Making and inspecting a through-hole joint"
level: intermediate
minutes: 2
summary: "Heat both pad and lead and hold the joint still while it solidifies."
---

Heat both pad and lead and hold the joint still while it solidifies.

## Technique for a through-hole joint
1. **Clean and tin the tip:** wipe on a damp sponge or brass wool, then melt a little solder on the tip. This helps heat transfer.
2. **Heat both the pad and the lead together** with the side of the tip touching both.
3. **Feed solder into the joint,** not onto the iron. It should flow around the lead and across the pad. Flux in the solder's core cleans oxide so the solder can wet the metal.
4. **Remove the solder, then the iron.** A small joint takes a few seconds in total.
5. **Don't move the joint** until it solidifies.
6. Trim the lead above the joint.

## Inspecting a joint
```diagram
  good:   /‾\      concave cone, wets
         /   \     both pad and lead
  ──────/     \──────

  cold:  ( ● )     ball sitting on pad,
  ──────(     )──  dull, not wetted
```

- **Good:** a smooth, concave "volcano" fillet that wets both the pad and the lead. Shiny with leaded solder, somewhat duller with lead-free.
- **Cold joint:** poor wetting, a balled shape or intermittent contact warrants rework. Insufficient heat, contamination, exhausted flux or movement may be involved. Dullness alone is not proof, especially with lead-free solder; follow a suitable rework procedure with power removed.
- **Bridge** (solder bridge): solder joining adjacent pads. Remove it with desoldering braid or by dragging a clean tip.
- **Insufficient:** the hole isn't filled or the pad isn't covered.
- **Overheated:** burnt flux, discoloured board, or a **lifted pad** (the copper peeling off). Use less time and the right tip.

With power disconnected and capacitors discharged, test the intended nets with **continuity mode** and look for bridges under a magnifier. A beep alone does not prove a mechanically reliable joint or distinguish an intended circuit path from a bridge.

## Key takeaways

- Heat both pad and lead and hold the joint still while it solidifies.
- Inspect wetting, shape, bridges and damage, not shine alone.

## Further reading

- [Adafruit: excellent soldering](https://learn.adafruit.com/adafruit-guide-excellent-soldering)
- [SparkFun: through-hole soldering](https://learn.sparkfun.com/tutorials/how-to-solder-through-hole-soldering/all)
