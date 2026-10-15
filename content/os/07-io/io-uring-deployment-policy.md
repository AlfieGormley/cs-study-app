---
id: io-uring-deployment-policy
title: io_uring security and deployment policy
level: advanced
minutes: 2
summary: Historical vulnerability reports do not establish every current deployment policy.
sourceLesson: io-uring
---

## Security concerns

io_uring is a large, fast-moving subsystem that runs complex code on behalf of unprivileged processes, and it has had many serious bugs.

- In June 2023, Google reported that **60% of the Linux kernel exploits** submitted to its kCTF vulnerability reward programme in the previous year used io_uring, accounting for about **$1 million** of payouts. The same June 2023 post described then-current restrictions on ChromeOS, production servers and Android apps. This is historical reporting, not proof of every current Google deployment policy.
- The inspected upstream **Moby default seccomp profile** uses an allowlist that omits io_uring syscalls, denying them under that profile. Actual Docker/container policy depends on version, capabilities and the selected profile.
- **Visibility.** A monitoring tool limited to ordinary syscall-entry events does not automatically see one read/open/send syscall per SQE. It may see io_uring_setup, io_uring_enter and io_uring_register calls, while SQPOLL can process submissions without an enter call. Other hooks, audit support and io_uring-aware instrumentation may observe operations; syscall-entry visibility alone is not a complete security model.

Mitigations:

- `sysctl kernel.io_uring_disabled` (Linux 6.6): `0` allows everyone, `1` limits creation to privileged processes or members of the `kernel.io_uring_group` group, and `2` disables new ring creation for everyone. Existing io_uring instances remain usable under either restrictive value.
- `IORING_REGISTER_RESTRICTIONS` lets a process constrain opcodes/flags on a ring created with IORING_SETUP_R_DISABLED, before enabling and handing it to less trusted code. It is an allowlist, not a complete isolation mechanism by itself.
- Seccomp can block `io_uring_setup` altogether.

> [!warning] Know your deployment target
> If you build on io_uring, check that your production environment allows it. Many container platforms and hardened kernels do not, so keep an epoll or thread-pool fallback.

## Key takeaways
- Historical vulnerability reports do not establish every current deployment policy.
- Container profiles and new-ring controls can restrict availability.
- Per-syscall monitoring alone misses the meaning of individual SQEs.

## Further reading
- [io_uring(7) — Linux manual page](https://man7.org/linux/man-pages/man7/io_uring.7.html)
- [io_uring_setup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/io_uring_setup.2.html)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
- [Lord of the io_uring (tutorial)](https://unixism.net/loti/)
- [Learnings from kCTF VRP's 42 Linux kernel exploits — Google Security Blog](https://security.googleblog.com/2023/06/learnings-from-kctf-vrps-42-linux.html)
- [io_uring — Wikipedia](https://en.wikipedia.org/wiki/Io_uring)
