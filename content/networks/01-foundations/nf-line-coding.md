---
id: nf-line-coding
sourceLesson: nf-physical-layer
title: Line codes and clock recovery
level: basic
minutes: 3
summary: Trace clock-recovery coding and explain why coded line bits exceed payload bits.
---

## Line coding: why not just send the bits?

The simplest scheme, **NRZ** (non-return-to-zero), maps 1 to high and 0 to low. It has two problems:

1. **Clock recovery.** Assume the receiver has no separate clock and must recover timing from the data. It finds bit boundaries by watching for transitions. A sufficiently long transition-free run can exceed the receiver’s clock-recovery tolerance; not every finite run necessarily causes an error.
2. **Baseline wander (DC balance).** Many links are AC-coupled through electrical transformers or capacitors. A long run of 1s looks like a constant DC level, which the coupling blocks, so the receiver's idea of "zero" drifts.

**Line coding and scrambling** address transition density and baseline wander, but different schemes provide different guarantees.

**Manchester** coding (used by 10 Mbit/s Ethernet) puts a transition in the middle of every bit. In IEEE 802.3's convention, 0 is high-to-low and 1 is low-to-high:

```
bit:        1    0    1    1
NRZ:        HH   LL   HH   HH
Manchester: LH   HL   LH   LH
```

```python
def manchester(bits):
    # IEEE 802.3: 0 -> high,low
    #             1 -> low,high
    out = []
    # Expand each bit into two half-bit
    # levels.
    for b in bits:
        if b not in "01":
            raise ValueError("not binary")
        if b == "1":
            out += [0, 1]
        else:
            out += [1, 0]
    return out


# Each adjacent pair represents one bit.
print(manchester("1011"))
# [0, 1, 1, 0, 0, 1, 0, 1]
```

Manchester is self-clocking and DC-balanced, but it **doubles the signalling rate**: two half-bit signal levels per bit. Other Ethernet PHYs use different tradeoffs.

Some faster links use **block codes**, sometimes combined with scrambling and a separate line modulation. They provide different transition-density and DC-balance guarantees:

| Code | Used by | Overhead |
|---|---|---|
| 4B/5B | 100BASE-TX, FDDI | 25% |
| 8b/10b | 1000BASE-X, SATA, PCIe 1–2 | 25% |
| 64b/66b | 10GBASE-R | 3.125% |

The name says how many line bits replace how many data bits: 8b/10b sends 10 bits on the line for every 8 bits of data. The coded-bit rate must therefore exceed the uncoded data-bit rate.

For example, 10 Gbit/s of data with 64b/66b coding needs 10.3125 Gbit/s of coded line bits. Those additional bits support the code; they are not extra application payload.

Specifically, 100BASE-TX maps its 4B/5B-coded stream to MLT-3 at 125 million symbol intervals/s. Serial binary 10GBASE-R uses 10.3125 Gbaud. Other Fast/Gigabit Ethernet PHYs need not use those rates. Good line codes also leave unused code words that can be used for control, such as marking the start of a frame.

## Key takeaways
- Clock recovery and baseline stability need suitable transition and balance properties.
- Different block codes and scramblers provide different guarantees and overheads.

## Further reading
- [Shannon–Hartley theorem — Wikipedia](https://en.wikipedia.org/wiki/Shannon%E2%80%93Hartley_theorem)
- [Line code — Wikipedia](https://en.wikipedia.org/wiki/Line_code)
- [Optical fiber — Wikipedia](https://en.wikipedia.org/wiki/Optical_fiber)
- [Velocity factor — Wikipedia](https://en.wikipedia.org/wiki/Velocity_factor)
- [Ethernet physical layer — Wikipedia](https://en.wikipedia.org/wiki/Ethernet_physical_layer)
- [Hollow-core optical fiber — Wikipedia](https://en.wikipedia.org/wiki/Hollow-core_optical_fiber)

- [Corning SMF-28 Ultra data sheet (July 2025)](https://www.corning.com/content/dam/corning/media/worldwide/coc/documents/Fiber/product-information-sheets/PI-1424-AEN.pdf)
- [Cisco 10GBASE transceiver specifications](https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/transceiver-modules/data_sheet_c78-455693.html)
- [Texas Instruments DP83825I PHY data sheet](https://www.ti.com/lit/ds/symlink/dp83825i.pdf)
- [Shannon: A Mathematical Theory of Communication](https://web.mit.edu/6.976/www/handout/shannon.pdf)

- [Belden 2433 cable specifications](https://catalog.belden.com/techdata/EN/2433_techdata.pdf)
