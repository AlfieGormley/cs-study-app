---
id: emb-control-to-audio-races-volatile
sourceLesson: emb-control-to-audio
title: "Shared data and the limits of volatile"
level: advanced
minutes: 3
summary: "Identify one writer, one reader and possible preemption for every shared-data connection."
---

The real-time audio units split the firmware into two worlds: the **audio callback**, which runs from an interrupt once per block and must never wait, and the **foreground** (main loop and lower-priority work), which reads knobs, parses MIDI and drives the display. Every useful synth needs data to cross between them. A knob moves in the foreground; the filter that reacts lives in the callback.

Getting this wrong produces the worst kind of bug: rare, timing-dependent and hard to reproduce. A stuck note once an hour. A click when two parameters change together. This lesson gives you a small set of safe patterns, described in language-neutral terms so they apply whatever language and platform you end up using.

## The foreground/background split

Draw the shared-data connections explicitly. For a simple synth:

```diagram
 knobs --> [main loop: scan, smooth, map]
                 |
                 | params (atomic)
                 v
 MIDI --> [UART ISR] --> [parse] --> [queue]
                                       |
                                       v
                          [audio callback]
                                       |
                 meters, clip flag <---+
```

For each arrow, ask: who writes, who reads, and can the reader interrupt the writer (or run on another core) halfway through? On a single-core MCU, the callback can interrupt the main loop at *any* instruction. On a multi-core computer such as a Raspberry Pi, both sides may genuinely run at the same time.
## What can go wrong

**Torn reads.** The main loop is writing a value that takes more than one memory operation (a 64-bit number on a 32-bit core, or a group of related fields). The callback interrupts between the two halves and reads half old, half new.

**Stale values.** The compiler sees that a loop never changes a variable and keeps it in a register, so the loop never sees the other side's update.

**Reordering.** The writer does "write data, then set ready flag". The compiler, and on some processors the hardware, may make the flag visible before the data. The reader sees "ready" and reads garbage.

**Lost updates.** Both sides do read-modify-write on the same variable (`count = count + 1`). One side's update overwrites the other's.

> [!analogy] Real-world analogy: Two people updating one tally
> Two people keep a tally on a whiteboard. Each reads the number, works out the new value and writes it back. If both read 5 before either writes, one change disappears.
>
> **How it maps:** Each person is one side of the program doing a read-modify-write. Making both people re-read the board every time, which is roughly what `volatile` does for its accesses, still does not stop the overwrite.
>
> **Where it stops:** On a CPU the interleaving happens between instructions, in nanoseconds, and can also involve tearing and reordering, which a whiteboard does not show.
## Why `volatile` is not synchronisation

C and C++ (and some other languages) have a `volatile` keyword. It tells the compiler that every access to that variable must really happen, in program order *relative to other volatile accesses*, because something outside the program (a hardware register, an interrupt) may change it. It preserves the defined volatile accesses, but it does not make an otherwise unsynchronised C++ thread-sharing program well-defined. Hardware interrupt semantics also depend on the compiler and target.

It does **not**:

- make a read-modify-write such as `x = x + 1` indivisible;
- prevent a multi-word value from tearing;
- order ordinary (non-volatile) memory accesses around it, so "write data, then set volatile flag" can still be reordered as far as the data is concerned;
- provide the memory barriers that multi-core processors need.

The diy-synth roadmap states it directly: "`volatile` alone is not thread synchronisation". The Linux kernel documentation has a whole page explaining why kernel code should not use `volatile` for this, and the C++ reference says the same for threads: use atomics. `volatile` remains correct for its real purpose, memory-mapped hardware registers.

## Key takeaways
- Identify one writer, one reader and possible preemption for every shared-data connection.
- Volatile preserves its defined accesses but does not supply atomicity or payload publication.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Why the "volatile" type class should not be used — Linux kernel documentation](https://github.com/torvalds/linux/blob/master/Documentation/process/volatile-considered-harmful.rst)
- [std::memory_order (acquire/release) — cppreference](https://en.cppreference.com/w/cpp/atomic/memory_order)
- [Circular buffer — Wikipedia](https://en.wikipedia.org/wiki/Circular_buffer)
- [Audio library processor usage and AudioNoInterrupts — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
