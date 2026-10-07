---
id: sys-memory-bugs
title: Memory-safety bugs
level: basic
minutes: 13
summary: Buffer overflows, out-of-bounds reads, use-after-free, double free, integer overflows and format strings, why they are dangerous and how to fix and find them.
---

C and C++ provide pointer operations without universal run-time bounds or lifetime checks. Accessing an object outside its bounds or lifetime can cause **undefined behaviour**: the language does not promise a clean crash, a particular overwrite, or access to arbitrary addresses. Operating-system mappings and permissions still constrain hardware accesses. The C examples below use the C11/C17 model.

These bugs can expose secrets or alter decisions as well as crash programs. Chromium reports that memory unsafety accounted for around 70% of a sample of 912 high/critical Stable-channel security bugs since 2015. This is a historical, project-specific sample, not a current universal percentage.

## Why a bug becomes a vulnerability

The diagram is an illustrative conventional process layout, not a C requirement (addresses increase upwards). Real systems may use multiple heap mappings; stack direction, saved registers and return-address storage depend on the architecture and compiler.

```
high  +------------------------+
      | stack (grows down)     |
      |  locals, saved regs,   |
      |  return addresses      |
      +------------------------+
      |         ...            |
      +------------------------+
      | heap (grows up)        |
      |  malloc'd objects and  |
      |  allocator metadata    |
      +------------------------+
      | globals, .data, .bss   |
      | program code (.text)   |
low   +------------------------+
```

The security concern is proximity: a buffer can share an allocation or stack frame with sensitive data. Depending on the implementation, nearby data can include control pointers or allocator metadata. Corrupting an authorization flag can also compromise a program without hijacking control flow.

So a bug that writes past the end of a buffer does not just corrupt "some data". It can overwrite something that decides **what the program does next**. That is the step from crash to compromise, and it is why the defences in the next lesson focus on protecting that control data.

Two important families are spatial and temporal errors. This classification does not describe every issue below; uninitialised-value use also needs separate attention.

| Family | Question it breaks | Examples |
|---|---|---|
| Spatial | Is this address inside the object? | Overflow, OOB read |
| Temporal | Is the object still alive? | Use-after-free, double free |

## Stack buffer overflow

The classic bug is copying input into a fixed-size buffer without checking its length.

```c
void greet(const char *name) {
    char buf[16];
    strcpy(buf, name);   /* BUG */
    printf("Hello, %s\n", buf);
}
```

`strcpy` requires enough destination space for all source bytes and the terminating NUL. A valid 40-byte name needs 41 bytes, exceeding `buf` by 25. Calling it here violates that requirement; a neighbouring-data overwrite is one possible outcome, not a guaranteed execution trace. Include `<string.h>` and `<stdio.h>` when compiling these function fragments.

The fix is to pass the destination size and handle truncation deliberately:

```c
void greet(const char *name) {
    char buf[16];
    int n = snprintf(buf, sizeof buf,
                     "%s", name);
    if (n < 0 || (size_t)n >= sizeof buf) {
        /* too long: reject or log */
        return;
    }
    printf("Hello, %s\n", buf);
}
```

With valid, non-overlapping arguments, `snprintf` bounds output by the supplied capacity and terminates it when that capacity is non-zero. Its non-negative return reports the required length excluding NUL; a negative return reports an error. The example rejects both errors and truncation. The source must itself be a valid NUL-terminated string.

> [!warning] strncpy is not a safe strcpy
> `strncpy(dst, src, n)` stops at `n` bytes, but if `src` is `n` bytes or longer it does **not** write a terminating NUL. An unbounded string operation on that unterminated destination violates its input requirements and can read past the end. Prefer `snprintf`, or `strlcpy` where available.

### Off-by-one errors

Many overflows are a single element too far:

```c
char id[8];
for (int i = 0; i <= 8; i++)  /* BUG */
    id[i] = src[i];
```

With a source of at least nine bytes, the faulty loop attempts indices 0 through 8. For an eight-byte raw copy, use `i < 8` and a source of at least eight bytes. That correction does not create a NUL-terminated string: reserve and write a terminator if string APIs will consume the result.

## Out-of-bounds reads: Heartbleed

Reading beyond an object can disclose memory if the result becomes observable. It may instead fault or have other undefined behaviour. Potential disclosures include secrets and addresses that weaken ASLR.

**Heartbleed** (CVE-2014-0160) in OpenSSL is the famous case. The TLS heartbeat message said "here are N bytes, echo them back". OpenSSL trusted the attacker-supplied N without checking it against how much data had actually arrived. Simplified:

```c
/* len comes from the packet */
memcpy(reply, payload, len);  /* BUG */
```

A malformed request could make vulnerable OpenSSL disclose up to 64 KB of process memory, potentially including secrets. A crash or other outcome was also possible. For a TLS heartbeat model, first ensure the three-byte header exists before parsing its length; reserve the required minimum 16-byte padding too. With non-negative `size_t` lengths and a sufficiently large reply buffer, the following guard prevents subtraction underflow:

```c
if (record_len < 3 + 16)
    return 0;
if (len > record_len - 3 - 16)
    return 0;  /* discard bad message */
memcpy(reply, payload, len);
```

Treat externally supplied lengths, indices and counts as untrusted. Validate both the arithmetic and the resulting range against actual available storage before parsing or copying.

## Integer overflow leading to a small allocation

Size arithmetic can wrap around. Consider:

```c
/* count comes from a file header */
item *arr = malloc(count * sizeof(item));
for (uint32_t i = 0; i < count; i++)
    read_item(&arr[i]);
```

Assume both `count` and `size_t` are 32-bit unsigned types, and `sizeof(item)` is 16. Then `0x10000001 * 16 = 0x100000010` wraps to `0x10`: only 16 bytes are requested. Allocation may fail; if it succeeds, attempting all those item writes exceeds the allocation and invokes undefined behaviour.

Fixes:

- Check before multiplying: `if (count > SIZE_MAX / sizeof(item)) fail;`
- On documented implementations such as glibc, `calloc(count, sizeof(item))` and `reallocarray` reject size overflow. `reallocarray` is POSIX, not ISO C. Check allocation failure before dereferencing; define a policy for zero counts.
- Reject absurd values early: a sane upper bound on `count` is good input validation anyway.

## Use-after-free

A **use-after-free** (UAF) is a temporal bug: the program keeps using a pointer after the memory it points to has been released.

```c
struct session *s = load_session();
if (expired(s))
    free(s);
/* ... later, on another path ... */
if (s->is_admin)   /* BUG: s may be freed */
    grant_access();
```

An allocator may reuse freed storage for a later allocation. If request-controlled bytes occupy that storage, a dangling access can influence an authorization decision or a control pointer. Reuse timing is allocator-dependent, and undefined behaviour means no particular result is guaranteed. The fragment assumes `load_session` succeeded; real code must also handle failure.

Defences in C:

- After `free`, setting an owning pointer to `NULL` can support later explicit null checks and makes `free(NULL)` harmless. Dereferencing NULL is still undefined behaviour, not a guaranteed clean crash; other aliases still dangle.
- Give every allocation **one clear owner** responsible for freeing it, and document which functions borrow versus take ownership.
- In C++, prefer `std::unique_ptr` for exclusive ownership, using `std::shared_ptr` when ownership really is shared. Raw borrowed aliases and unsynchronised access still require lifetime discipline.

### Double free

Freeing the same allocation twice is undefined behaviour; `free(NULL)` is exempt. Outcomes can include allocator corruption or a diagnostic abort. Detection is implementation-dependent and does not make double free safe. Clear ownership and avoiding stale aliases prevent the underlying error.

## Format-string bugs

```c
printf(user_input);          /* BUG */
printf("%s", user_input);    /* fixed */
```

An untrusted format can request conversions such as `%x` or `%n`. Missing or incorrectly typed arguments invoke undefined behaviour; depending on the calling convention and program, this can expose values or attempt a memory write. `%n` stores a character count through its supplied pointer. Use a fixed format and valid string argument. GCC/Clang warnings such as `-Wformat -Wformat-security -Werror=format-security` reject the illustrated no-extra-arguments mistake.

## Uninitialised memory

An uninitialised automatic value is indeterminate in C11/C17, and many uses have undefined behaviour. Do not assume it reliably returns old bytes. Separately, copying a raw structure across a trust boundary can disclose padding. Initialising members with `{0}` is not a portable guarantee that padding remains zero after member stores. Encode named fields into an explicitly defined byte representation instead of transmitting `sizeof(struct)` bytes.

## Finding these bugs

You will not find memory bugs reliably by reading code alone. The standard toolkit:

| Tool | How it works | Cost |
|---|---|---|
| AddressSanitizer | Instrumented accesses checked against shadow memory | Workload-dependent |
| Valgrind Memcheck | Dynamic binary instrumentation | Workload-dependent |
| Fuzzing | Generates varied test inputs | Depends on budget |
| Static analysis | Reasons about code without running it | False positives |

**AddressSanitizer** (`-fsanitize=address` in Clang/GCC) uses poisoned regions and delayed reuse to detect many invalid accesses. It can report errors such as `heap-use-after-free`. Coverage depends on instrumentation, allocation layout and execution: it does not check every object boundary, every uninitialised value or every possible input. Intra-object overwrites and accesses after storage is reused may escape detection.

**Fuzzers** such as libFuzzer and AFL++ use feedback to explore inputs. Combining fuzzing with sanitizers helps expose faults on executed paths; neither proves absence of bugs. OSS-Fuzz provides continuous fuzzing for eligible open-source projects. Valid regression tests remain useful alongside malformed-input tests.

> [!tip] A C/C++ testing baseline
> Enable useful warnings, test with ASan/UBSan where supported, and fuzz untrusted-input parsers. Review unbounded string operations; `gets` was removed from C11. A clean sanitizer run is evidence about those executions, not proof of memory safety.

> [!note] Content omitted after review
> A universal current vulnerability percentage, a ranking of the most productive testing technique, and fixed sanitizer costs are omitted because this review did not establish representative measurements. Historical Chromium figures describe only its stated sample.

## Key takeaways
- Spatial and temporal errors are important families; uninitialised-value bugs also need attention.
- They are dangerous because data and control information share memory, so corruption can redirect execution.
- Invalid reads can disclose secrets, invalid writes can corrupt state, and stale aliases can expose reused storage; outcomes are not guaranteed.
- Every externally supplied length, index or count must be checked against the real buffer size, including the arithmetic that computes it.
- Find bugs with sanitizers and fuzzing, not just review, and prevent them with bounded APIs and clear ownership.

## Further reading
- [C11 committee draft, object/lifetime and library rules](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Heartbleed advisory — OpenSSL](https://openssl-library.org/news/secadv/20140407.txt)
- [TLS heartbeat format — RFC 6520](https://www.rfc-editor.org/rfc/rfc6520.html)
- [CWE-416: Use After Free — MITRE](https://cwe.mitre.org/data/definitions/416.html)
- [The Heartbleed Bug](https://heartbleed.com/)
- [AddressSanitizer — Clang documentation](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Memory safety — Chromium security](https://www.chromium.org/Home/chromium-security/memory-safety/)
- [OSS-Fuzz — Google](https://google.github.io/oss-fuzz/)
