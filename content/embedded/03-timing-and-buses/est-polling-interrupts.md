---
id: est-polling-interrupts
title: Choose polling or an interrupt
level: basic
minutes: 4
summary: Choose how to notice an event without hiding work or assuming every edge is retained.
---

A button has changed or a serial byte has arrived. Firmware needs to notice, preserve any information that matters, and decide what work to perform. **Polling** and **interrupts** are two ways to arrange that work; neither automatically makes an application responsive.

## Check explicitly or handle an interrupt

With polling, the main loop repeatedly checks a status value. For example: check whether a receive buffer contains a byte, process a bounded amount of work, then check other devices. A blocking driver call can still prevent the next check, even if the rest of the loop looks simple.

With an interrupt, a configured hardware condition requests a processor exception. When the processor accepts it, execution enters an **interrupt service routine** (ISR), then later returns to interrupted work. An interrupt can be pending while another operation runs; masking, priority and current execution context affect when its handler executes. It is not an instantaneous callback.

An ISR should do the necessary bounded work: preserve data or record progress, acknowledge the source as the device requires, and defer longer processing to the main loop. Clearing a processor's pending bit and clearing the peripheral's underlying condition are not necessarily the same operation. Read that peripheral's procedure.

> [!analogy] Real-world analogy: checking a door or hearing a bell
> Someone can repeatedly look at the entrance or respond when a doorbell rings.
>
> **How it maps:** Looking is polling; the bell represents an interrupt request. A short response can record that someone arrived before the person returns to their main task.
>
> **Where it stops:** Hardware has precise masking, priority and acknowledgement rules. Several arrivals can produce one pending indication, and a bell does not guarantee that each arrival is counted.

## Trace the information you can lose

Suppose firmware checks a pin every 5 ms, at 0 ms, 5 ms and 10 ms. A pulse starts at 1 ms and ends at 2 ms. Every check sees the inactive level: polling the level misses that pulse.

An edge-capable peripheral may latch a request, but its behaviour must be configured and checked. A single pending flag can merge several events before service. A serial receive FIFO can retain several bytes but eventually fill. Choose the mechanism by the information required: latest state, a count of events, or every received byte.

Start with a cooperative loop when its measured check intervals meet the device's needs. Add an interrupt where hardware support and response requirements justify it. Measure the longest interval under realistic load, including driver calls and logging, rather than treating an average loop speed as a guarantee.

## Key takeaways
- Polling checks explicitly; an ISR runs when the processor accepts an interrupt request.
- Keep interrupt work bounded and acknowledge the actual device condition correctly.
- A pending indication need not preserve every event.

## Further reading
- [Arm CMSIS interrupt controller interfaces](https://arm-software.github.io/CMSIS_6/latest/Core/group__NVIC__gr.html)
- [Raspberry Pi SDK interrupt handling](https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/src/rp2_common/hardware_irq/include/hardware/irq.h)
