---
id: est-i2c-basics
title: Trace an I2C register read
level: basic
minutes: 5
summary: Distinguish a seven-bit target address, wire address byte and the final read NACK.
---

Ordinary bidirectional **I2C** uses two shared signals: **SDA** for data and **SCL** for the clock. Devices pull a signal low or release it; pull-up resistors bring released lines high. Work only with low-voltage development hardware. Check the board, target-device and bus specifications for suitable levels and pull-ups rather than assuming a universal resistor value.

A controller initiates a transfer and addresses a target. We use a single-controller bus with seven-bit addressing in this lesson. Device-specific commands and register layouts still come from the target's datasheet: “uses I2C” does not specify how to read its measurements.

## A fictional one-byte sensor register

Assume a fictional target has seven-bit address `0x48`, selects a register by a one-byte write, and returns that register on a following read with a repeated START. Its register `0x01` currently contains `0x7A`. This is a protocol exercise, not a claim about an actual sensor.

| Step | Sender | What happens |
|---|---|---|
| START | Controller | Begin transfer |
| `0x90` | Controller | Address `0x48`, write direction |
| ACK | Target | Accept address |
| `0x01` | Controller | Select the fictional register |
| ACK | Target | Accept register byte |
| Repeated START | Controller | Begin another address phase |
| `0x91` | Controller | Address `0x48`, read direction |
| ACK | Target | Accept address |
| `0x7A` | Target | Return the fictional register byte |
| NACK, then STOP | Controller | Finish this one-byte read |

The first wire byte combines the seven address bits and the read/write bit. The Pico SDK's I2C API accepts the seven-bit address separately; it supplies the direction bit. Passing `0x90` where that API expects `0x48` confuses two different representations.

**ACK** means the receiving side acknowledged that byte. It is not proof that a measurement is fresh or meaningful. A **NACK** at the end of the controller's last read byte is the normal way to decline another byte, whereas an address NACK can indicate that the selected target did not respond.

> [!analogy] Real-world analogy: addressing a letter and asking for a reply
> A sender identifies the recipient, delivers a request and then allows the recipient to reply before ending the exchange.
>
> **How it maps:** The address selects a target; the write selects the fictional register; the repeated START changes the transfer direction without ending that combined exchange.
>
> **Where it stops:** I2C has precise clocked byte and acknowledgement rules, and a target's command sequence is device-specific. An acknowledged address does not identify which of two incorrectly duplicated-address devices replied.

## Stop failures becoming a frozen loop

Use a driver operation with a suitable timeout and check its result and returned byte count. Devices may stretch the clock in modes that allow it; a broken connection or stuck signal also needs a bounded failure path. A timeout is a software decision to stop waiting, not proof that the underlying wiring has recovered. Retry only under a deliberate policy; report the fault if recovery fails.

## Key takeaways
- Distinguish a seven-bit API address from the address-and-direction byte on the wire.
- Read the target's command protocol; there is no universal sensor register map.
- Interpret NACK in context and bound failed transfers.

## Further reading
- [NXP UM10204: I2C protocol and acknowledgement](https://www.nxp.com/docs/en/user-guide/UM10204.pdf)
- [Pico SDK I2C addressing and timeout APIs](https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/src/rp2_common/hardware_i2c/include/hardware/i2c.h)
