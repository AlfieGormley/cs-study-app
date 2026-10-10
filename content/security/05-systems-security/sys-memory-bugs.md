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

Two important families are spatial errors and temporal errors. This two-family split does not describe every issue below; uninitialised-value use also needs separate attention.

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

`strcpy` requires enough destination space for all source bytes and the terminating NUL, the zero byte that marks the end of a C string. It is never told the destination's size, so it cannot check. The space needed, and how far a copy goes past the end, are:

```formula
B_need = L + 1
B_over = B_need − C
B_need = 40 B + 1 B = 41 B
B_over = 41 B − 16 B = 25 B
where
B_need: the destination space strcpy needs, in bytes (B)
L: the length of the source string in bytes, not counting its NUL; 40 B for this name
1: the one extra byte for the terminating NUL
B_over: how many bytes the copy needs beyond the destination's capacity; anything above 0 means the call is invalid
C: the destination's capacity in bytes; buf is declared char buf[16], so 16 B
B: byte, a unit of 8 bits of memory
In words: strcpy needs the string's length plus one byte for the NUL, so a 40-byte name needs 41 bytes, 25 more than the 16-byte buf holds.
```

So a valid 40-byte name exceeds `buf` by 25 bytes, and the longest name that fits is 15 bytes (15 + 1 = 16). Calling it here violates that requirement; a neighbouring-data overwrite is one possible result, not a guaranteed execution trace. Include `<string.h>` and `<stdio.h>` when compiling these function fragments.

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

With arguments that are valid and non-overlapping, `snprintf` bounds output by the supplied capacity and terminates it when that capacity is non-zero. Its non-negative return reports the required length excluding NUL; a negative return reports an error. The example rejects both errors and truncation. The source must itself be a valid NUL-terminated string.

The truncation test `(size_t)n >= sizeof buf` comes from this condition for the whole output to fit:

```formula
n + 1 ≤ C
n < C
where
n: the non-negative value snprintf returned: the length the full output would have, in bytes, not counting the NUL
1: the byte needed for the terminating NUL
C: the destination's capacity in bytes, sizeof buf; 16 here
≤: less than or equal to
<: less than
In words: the full text plus its NUL must fit in the buffer, which is the same as the returned length being less than the capacity. A return equal to or above the capacity means the text was cut short.
```

For example, formatting the 11-character `"hello world"` into an 8-byte buffer returns 11. Since 11 is not less than 8, the output was truncated: the buffer holds the first 7 characters (8 − 1) and the NUL.

> [!warning] strncpy is not a safe strcpy
> `strncpy(dst, src, n)` stops at `n` bytes, but if `src` is `n` bytes or longer it does **not** write a terminating NUL. An unbounded string operation on that unterminated destination violates its input requirements and can read past the end. Prefer `snprintf`, or `strlcpy` where available.

### Off-by-one errors

Many overflows are a single element too far:

```c
char id[8];
for (int i = 0; i <= 8; i++)  /* BUG */
    id[i] = src[i];
```

With a source of at least nine bytes, the faulty loop attempts indices 0 through 8: nine writes into an eight-element array, whose valid indices are 0 through 7. For an eight-byte raw copy, use `i < 8` and a source of at least eight bytes. That correction does not create a NUL-terminated string: reserve and write a terminator if string APIs will consume the result.

## Out-of-bounds reads: Heartbleed

Reading beyond an object can disclose memory if the result becomes observable. It may instead fault or have other undefined behaviour. Potential disclosures include secrets and addresses that weaken ASLR.

**Heartbleed** (CVE-2014-0160) in OpenSSL is the famous case. The TLS heartbeat message said "here are N bytes, echo them back". OpenSSL trusted the attacker-supplied N without checking it against how much data had actually arrived. Simplified:

```c
/* len comes from the packet */
memcpy(reply, payload, len);  /* BUG */
```

A malformed request could make vulnerable OpenSSL disclose up to 64 KB of process memory, potentially including secrets. A crash or other outcome was also possible. The 64 KB limit comes from the size of the length field, which is two bytes (16 bits):

```formula
N_max = 2^16 − 1
N_max = 65,536 − 1 = 65,535 B
where
N_max: the largest payload length the heartbeat's length field can claim, in bytes (B)
2^16: 16 copies of 2 multiplied together, 65,536: the number of different values 16 bits can hold
1: subtracted because the values start at 0, so the largest is one less than the count
B: byte, 8 bits
In words: a 16-bit length field can claim at most 65,535 bytes, just under 64 KiB (64 × 1,024 bytes), so one malicious heartbeat could leak up to about 64 KB.
```

A heartbeat message (RFC 6520) is laid out as a one-byte type, the two-byte payload length, the payload, then at least 16 bytes of random padding. Everything the length claims must fit inside what actually arrived:

```formula
1 + 2 + L + 16 ≤ R
L ≤ R − 3 − 16
where
1: the one-byte message type
2: the two-byte payload-length field
L: the payload length the message claims, in bytes; attacker-controlled (len in the code)
16: the minimum padding, in bytes, that RFC 6520 requires after the payload
R: the number of bytes of heartbeat message actually received (record_len in the code)
≤: less than or equal to
In words: the header, the claimed payload and the minimum padding must all fit in the received bytes, so the claimed length can be at most the received size minus 19.
```

For example, if 40 bytes arrive, the payload can be at most 40 − 3 − 16 = 21 bytes, and a claimed length of 65,535 must be rejected. Vulnerable OpenSSL skipped this check and copied as many bytes as were claimed, reading far past the real payload.

So first ensure the three-byte header exists before parsing its length, and reserve the required minimum 16-byte padding too. `size_t` is unsigned, so if `record_len` were below 19, `record_len - 3 - 16` would wrap to a huge number (integer wraparound) and the length check would pass. With non-negative `size_t` lengths and a sufficiently large reply buffer, the following guard prevents that subtraction underflow:

```c
if (record_len < 3 + 16)
    return 0;
if (len > record_len - 3 - 16)
    return 0;  /* discard bad message */
memcpy(reply, payload, len);
```

Treat externally supplied lengths, indices and counts as untrusted. Validate both the arithmetic and the resulting range against actual available storage before parsing or copying.

## Integer overflow leading to a small allocation

Size arithmetic can suffer integer wraparound. Consider:

```c
/* count comes from a file header */
item *arr = malloc(count * sizeof(item));
for (uint32_t i = 0; i < count; i++)
    read_item(&arr[i]);
```

Assume both `count` and `size_t` are 32-bit unsigned types, and `sizeof(item)` is 16. C's unsigned arithmetic does not fail when a result is too big: it keeps only the lowest 32 bits of the result (this is called modular arithmetic).

```formula
S = (n × s) mod 2^32
n × s = 0x10000001 × 16 = 0x100000010
n × s = 268,435,457 × 16 = 4,294,967,312
S = 4,294,967,312 − 4,294,967,296
S = 16 B = 0x10 B
where
S: the byte count actually passed to malloc, in bytes (B)
n: the item count read from the file header (count in the code); here 0x10000001, which is 268,435,457
s: the size of one item in bytes, sizeof(item); 16 here
mod: modulo, the remainder after dividing; a value mod 2^32 keeps only its lowest 32 bits
2^32: 32 copies of 2 multiplied together, 4,294,967,296: the number of different values a 32-bit unsigned type can hold
0x10000001: a hexadecimal (base-16) number, marked by the 0x prefix; each hex digit is 4 bits
B: byte, 8 bits
In words: the true product needs 33 bits, so the 32-bit size type drops the top bit (subtracting 2^32 once), and 268,435,457 items of 16 bytes become a request for just 16 bytes.
```

Only 16 bytes are requested. Allocation may fail; if it succeeds, attempting all those item writes exceeds the allocation and invokes undefined behaviour.

The standard check avoids the multiplication altogether. The product fits only if it is no larger than `SIZE_MAX`, the largest value `size_t` can hold. Dividing both sides by the item size gives a test that cannot itself overflow:

```formula
n × s ≤ M
n ≤ ⌊M / s⌋
M = 2^32 − 1 = 4,294,967,295
⌊M / s⌋ = ⌊4,294,967,295 / 16⌋
⌊M / s⌋ = 268,435,455
where
n: the item count (count in the code)
s: the size of one item in bytes, sizeof(item); 16 here
M: SIZE_MAX, the largest value size_t can hold; 2^32 − 1 for a 32-bit size_t
2^32: 32 copies of 2 multiplied together, 4,294,967,296
⌊ ⌋: floor: round down to a whole number, which is what C's integer division does for non-negative values
≤: less than or equal to
In words: a count is safe only if it is at most SIZE_MAX divided by the item size, rounded down; with 16-byte items that is 268,435,455, so the count 268,435,457 above is rejected.
```

Fixes:

- Check before multiplying: `if (count > SIZE_MAX / sizeof(item)) fail;`
- On documented implementations such as glibc, `calloc(count, sizeof(item))` and `reallocarray` reject size overflow. `reallocarray` is POSIX, not ISO C. Check allocation failure before dereferencing; define a policy for zero counts.
- Reject absurd values early: a sane maximum for `count` is good input validation anyway.

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
- In C++, prefer `std::unique_ptr` when one owner holds the object, using `std::shared_ptr` when ownership really is shared. Raw borrowed aliases and unsynchronised access still require lifetime discipline.

### Double free

Freeing the same allocation twice is undefined behaviour; `free(NULL)` is exempt. Outcomes can include allocator corruption or a diagnostic abort. Whether a double free is detected is implementation-dependent, and detecting it does not make double free safe. Clear ownership and avoiding stale aliases prevent the underlying error.

## Format-string bugs

```c
printf(user_input);          /* BUG */
printf("%s", user_input);    /* fixed */
```

An untrusted format can request conversions such as `%x` or `%n`. Missing or incorrectly typed arguments invoke undefined behaviour; depending on the calling convention and program, this can expose values or attempt a memory write. `%n` stores a character count through its supplied pointer. Use a fixed format and valid string argument. GCC/Clang warnings such as `-Wformat -Wformat-security -Werror=format-security` reject the illustrated no-extra-arguments mistake.

## Uninitialised memory

An uninitialised automatic value is indeterminate in C11/C17, and many uses have undefined behaviour. Do not assume it reliably returns old bytes. Separately, copying a raw structure across a trust boundary can disclose struct padding. Initialising members with `{0}` is not a portable guarantee that padding remains zero after member stores. Encode named fields into an explicitly defined byte representation instead of transmitting `sizeof(struct)` bytes.

## Finding these bugs

You will not find memory bugs reliably by reading code alone. The standard toolkit:

| Tool | How it works | Cost |
|---|---|---|
| AddressSanitizer | Instrumented accesses checked against shadow memory | Depends on the program |
| Valgrind Memcheck | Dynamic binary instrumentation | Depends on the program |
| Fuzzing | Generates varied test inputs | Depends on budget |
| Static analysis | Reasons about code without running it | False positives |

**AddressSanitizer** (`-fsanitize=address` in Clang/GCC) uses poisoned regions and delayed reuse to detect many invalid accesses. It can report errors such as `heap-use-after-free`. What it catches depends on instrumentation, allocation layout and execution: it does not check every object boundary, every uninitialised value or every possible input. Intra-object overwrites and accesses after storage is reused may go undetected.

**Fuzzers** such as libFuzzer and AFL++ use feedback to explore inputs. Combining fuzzing with sanitizers helps expose faults on executed paths; neither proves absence of bugs. OSS-Fuzz provides continuous fuzzing for eligible open-source projects. Valid regression tests remain useful alongside malformed-input tests.

> [!tip] A C/C++ testing baseline
> Enable useful warnings, test with ASan/UBSan where supported, and fuzz untrusted-input parsers. Review unbounded string operations; the unbounded `gets()` function was removed from C11. A clean run under sanitizers is evidence about those executions, not proof of memory safety.

> [!note] Content omitted after review
> A universal current vulnerability percentage, a ranking of the most productive testing method, and fixed costs for sanitizers are omitted because this review did not establish representative measurements. Historical Chromium figures describe only its stated sample.

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
