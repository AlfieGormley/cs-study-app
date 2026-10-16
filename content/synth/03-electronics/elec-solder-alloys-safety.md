---
id: elec-solder-alloys-safety
sourceLesson: elec-measurement-soldering
title: "Solder alloys, fume controls and iron temperature"
level: intermediate
minutes: 2
summary: "Capture rosin flux fume at source and use appropriate eye and hand precautions."
---

Capture rosin flux fume at source and use appropriate eye and hand precautions.

### Safety
- **Rosin flux fume:** the HSE states that rosin (colophony)-based solder flux fume is "a common cause of occupational asthma". Work in a well-ventilated space and use suitable local fume extraction that captures fume at the source. A desk fan merely moving fume around the room is not equivalent to extraction. Consider rosin-free or reduced-rosin fluxes.
- **Lead:** if you use leaded solder, wash your hands afterwards and don't eat or drink while soldering.
- **Eyes:** wear safety glasses. Flux can spit and clipped leads fly.
- **Burns:** always put the iron back in its stand. Never catch a falling iron. Keep the cable clear.
- **Unpowered:** never solder a circuit while it's powered.

### Leaded or lead-free
| | Leaded (63/37 Sn-Pb) | Lead-free (e.g. Sn-Ag-Cu) |
|---|---|---|
| Melting point | 183 °C (eutectic) | SAC305: 217–219 °C |
| Ease | Flows easily, forgiving | Needs more heat, less forgiving |
| Joint look | Shiny | Duller, slightly grainy |
| Health/regulation | Contains lead | Used to meet lead restrictions where RoHS applies; exemptions exist |

Use an alloy and flux suited to the component, board and applicable work requirements. Follow their manufacturer’s instructions; this is not a judgement that every hobby use has the same legal or health requirements. A eutectic alloy melts and solidifies at a single temperature, so it has no pasty phase where movement spoils the joint.

### Temperature
Use a **temperature-controlled iron**. SparkFun's through-hole soldering guide suggests a "good medium heat (325-375 degrees C)" as a starting point. Lead-free usually needs the upper end. If the solder smokes heavily or flux burns off instantly, turn the heat down. If the joint won't flow within a few seconds, a bigger tip often helps more than more heat.

## Key takeaways

- Capture rosin flux fume at source and use appropriate eye and hand precautions.
- Follow the alloy, tool and component instructions for temperature.

## Further reading

- [HSE INDG249: rosin flux fume controls](https://www.hse.gov.uk/pubns/indg249.pdf)
- [Kester: alloy temperature chart](https://www.kester.com/knowledge-base/alloy-temperature-chart)
- [Kester SAC305: technical data sheet, 16 March 2022](https://www.kester.com/DesktopModules/Bring2mind/DMX/API/Entries/Download?DownloadMethod=attachment&EntryId=45147&PortalId=0)
- [SparkFun: through-hole soldering](https://learn.sparkfun.com/tutorials/how-to-solder-through-hole-soldering/all)
