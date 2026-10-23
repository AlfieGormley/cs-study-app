---
id: esr-watchdog-reset
title: Plan timeouts, watchdogs and reset recovery
level: intermediate
minutes: 4
summary: Separate a handled device timeout from whole-system loss of progress, then define recovery.
---

A **timeout** limits how long one operation may wait. A **watchdog** can reset parts of a device when required software progress stops being reported. They address different failure levels: a disconnected sensor should first become a handled application fault, not an excuse to retry forever.

## Feed only for meaningful progress

A hardware watchdog is commonly a counter that software periodically refreshes. If it expires, its configured reset action occurs. Exact clocks, reset coverage, timeout limits and debug behaviour are device-specific. The Pico SDK watchdog interface is one concrete example; it is not a universal timer API.

Define a **health policy** before choosing where to feed it. For a small application, a supervisor can require evidence that the main loop ran, the acquisition work reached a completed result, and the indicator/status work completed during the monitoring window. A completed result can include a correctly handled timeout; it need not mean that an unplugged sensor became healthy.

| Observed progress | Policy decision in this example |
|---|---|
| Loop, acquisition outcome and status all progressed | Refresh watchdog |
| Sensor timed out, fault status published, loop responsive | Continue documented degraded operation |
| Main loop stopped, but an ISR still runs | Do not let that ISR hide the stalled loop |

Blindly feeding from a periodic ISR can keep the watchdog satisfied while the main application is stuck. Each progress report should refer to the current monitoring window; stale “healthy” flags are not evidence of fresh progress.

> [!analogy] Real-world analogy: a scheduled check-in
> A worker checks in after completing the agreed checks. Missing the check-in triggers a predefined response rather than an endless wait.
>
> **How it maps:** A watchdog refresh represents current progress evidence, and expiry requests the configured recovery action. The health policy defines what the check-in actually proves.
>
> **Where it stops:** A reset cannot repair broken wiring or prove the software correct. A badly chosen check-in can report success while the important work is stalled.

## Make reset a controlled transition

On boot, read the documented reset-cause information before clearing or overwriting relevant evidence. Initialise the application's outputs and state deliberately, then enter the documented start state. Do not immediately restore a remembered output command without validating whether it is still appropriate.

For this course's indicator project, reset returns to WAITING until a fresh valid sample arrives. A timeout latches a visible FAULT state; the chosen recovery event clears it back to WAITING, not straight to a stale NORMAL reading. If repeated resets occur, preserve enough diagnostic evidence and a recoverable maintenance path to investigate them rather than hiding a reboot loop.

Test the watchdog intentionally on a supported board using its official example and recovery instructions. Check whether it pauses during debugging; a halted processor is not a normal workload. Tests of the host model can check the chosen recovery policy but cannot validate the hardware watchdog clock or reset circuitry.

## Key takeaways
- A timeout bounds one operation; a watchdog supervises selected progress.
- Refresh only from current, meaningful health evidence.
- Plan reset cause, initial outputs and a recoverable startup path.

## Further reading
- [Pico SDK watchdog and reset-cause interfaces](https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/src/rp2_common/hardware_watchdog/include/hardware/watchdog.h)
- [Official Pico watchdog example](https://raw.githubusercontent.com/raspberrypi/pico-examples/master/watchdog/hello_watchdog/hello_watchdog.c)
