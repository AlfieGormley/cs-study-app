---
id: esb-build-flash-run
title: From source code to a running device
level: basic
minutes: 3
summary: Distinguish compiling, linking, transferring firmware and observing its behaviour.
---

Writing a source file changes a file on your computer. It does not change the program already running on a board. A firmware workflow must turn that source into an appropriate image, transfer it using a supported method and then observe what actually runs.

A **toolchain** is the collection of development tools used for that target. A **cross-compiler** runs on one system while producing code for another target. Choosing the wrong target can produce perfectly valid machine code that the intended MCU cannot execute.

## Follow the stages

This is a simplified development sequence, not a set of shell commands:

```flow
Edit the source
Compile target object files
Link the firmware image
Transfer it using the supported tool
Reset or start the application
Observe the required behaviour
```

The **compiler** translates source into target code, often producing **object files**. In a C toolchain, preprocessing handles items such as header inclusion before compilation proper. The **linker** combines object files and libraries, resolves references between them and lays out the result according to the target's build configuration.

A successful compile does not prove that linking will succeed. A function can have a declaration that allows compilation while its implementation is missing from the link. Similarly, successful linking does not prove that the resulting program satisfies the device's behaviour requirements.

> [!analogy] Real-world analogy: preparing and delivering a printed instruction pack
> Different people prepare pages, someone assembles the complete pack, and a delivery step takes it to the place where it will be used. Finishing a page does not prove the pack was delivered or followed correctly.
>
> **How it maps:** Preparing pages represents compilation; assembling the pack represents linking; delivery represents transferring the firmware. Observing the device checks the behaviour of the delivered result.
>
> **Where it stops:** Firmware must match a processor, memory layout and transfer format. A successfully delivered image can still contain logical errors or initialise the wrong hardware.

## A concrete supported route

For an original Raspberry Pi Pico running an appropriate Pico SDK blink image, the official documentation describes entering BOOTSEL mode, which exposes a USB mass-storage interface, then copying a UF2 image through that interface. The bootloader interprets the transfer and the board restarts into the application. This is a Pico workflow, not a universal way of programming MCUs or an ordinary storage drive for arbitrary files.

Other supported routes use a debug interface and a programming tool. Follow the board's current guide for the required image format and procedure. Record the board selection, build configuration and image you transferred so an observation can be tied to a particular build.

## Key takeaways
- Build, transfer and observation are separate steps; success at one does not prove success at the next.
- A cross-compiler and linker must target the actual device and build configuration.
- Use an official board-specific programming method rather than assuming all MCUs accept the same file.

## Further reading
- [Overall compilation and linking options — GCC](https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html)
- [First binaries and BOOTSEL workflow — Raspberry Pi](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/microcontrollers/c_sdk/your_first_binary.adoc)
- [Debug probe programming and debugging — Raspberry Pi](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/microcontrollers/debug-probe/introduction.adoc)
