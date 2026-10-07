from pathlib import Path
import json
B=Path('content/architecture/01-data-representation');p=B/'rep-memory-layout.md';s=p.read_text()
def r(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
r('Memory is a long array of bytes,', 'In the common byte-addressed model used here (eight bits per byte), memory is an array of bytes,')
r('| x86, x86-64 | network protocols |', '| x86, x86-64 | TCP/IP multi-byte header fields |')
r('| RISC-V | PNG, JPEG headers |', '| Common RISC-V systems (ISA also defines other modes) | PNG integers, JPEG marker-segment lengths |')
r('| most file formats on PCs | Java class files |','| BMP and ZIP fields specified little-endian | Java class-file multibyte items |')
r('but Linux, Android, iOS and macOS all run ARM little-endian. The result is that almost every machine you will program is little-endian, while the protocols connecting them are big-endian.', 'common Android, iOS and macOS ARM systems use little-endian data. Linux also supports big-endian ARM configurations. Network and file formats specify byte order per format; not every protocol is big-endian.')
r('Little-endian has a mild hardware advantage:', 'One convenient property of little-endian layouts is that')
r('Big-endian is easier to read in a hex dump.', 'Big-endian byte dumps follow the usual written order of a multibyte hexadecimal number. Neither observation proves an overall performance advantage.')
r('`x >> 24` gives the most significant byte on every machine,', 'For a uint32_t value, `x >> 24` gives its most significant octet regardless of byte order,')
r('printf("%02x\\n", p[0]);', 'printf("%02x\\n", (unsigned)p[0]);')
r('/* 78 on x86 and ARM, 12 on big-endian */', '/* 78 little-endian; 12 big-endian */')
r('(one `bswap` or `rev` instruction)', '(the compiler chooses appropriate instructions or folds a constant)')
r('Compilers recognise the pattern and emit a single load, plus a byte swap if needed.', 'Optimising compilers often recognise this pattern; the exact instruction sequence depends on alignment support, target and optimisation settings.')
r('UTF-16 uses a byte order mark, as lesson 5 showed.', 'UTF-16 can use a byte order mark or an externally specified byte-order convention; a BOM is not universally required.')
r('The CPU does not fetch single bytes from memory. It fetches whole cache lines, usually 64 bytes, and its load units are built for aligned chunks.', 'A CPU can issue byte-sized loads. Cacheable misses commonly transfer whole cache lines, often 64 bytes, while load/store execution and uncached or device accesses have additional size and alignment rules.')
r('A naturally aligned value never crosses a cache line or page boundary, so one access suffices.', 'When a power-of-two access size is no larger than and divides the line/page size, natural alignment keeps that access within a boundary. This does not mean every aligned object, arbitrarily wide access or generated instruction requires only one memory transaction.')
r('**Atomicity**: an aligned 8-byte store on a 64-bit CPU is a single, indivisible operation. A misaligned one may be torn, so another thread can see half old and half new bytes.', '**Atomicity** depends on the architecture, memory type and access. For example, x86-64 guarantees indivisibility for suitably aligned ordinary 8-byte loads/stores to normal memory. A misaligned access can lack that guarantee. In C/C++, hardware non-tearing does not permit data races: use atomics or synchronisation for conflicting cross-thread accesses.')
r('In C, dereferencing a misaligned pointer is undefined behaviour,', 'In C, conversion to an object-pointer type with unmet alignment requirements is already undefined, and dereferencing misaligned storage is not made valid by the hardware,')
r('`arr[1]` starts at `arr + sizeof(struct A)`.', '`arr[1]` starts sizeof(struct A) **bytes** after arr[0], namely `(unsigned char *)arr + sizeof(struct A)`. The expression `arr + sizeof(struct A)` would incorrectly scale that count by the element size again.')
r('The rules, on mainstream ABIs such as x86-64 System V and AArch64:', 'For ordinary unpacked structs without bit-fields, explicit over-alignment or unusual members, mainstream ABIs such as x86-64 System V and AArch64 use these rules:')
r('Taking a pointer to a packed member (`&p->b`) produces a misaligned `int *`. Using it on a strict-alignment CPU crashes;', 'Taking a pointer to a packed member (`&p->b`) can produce a misaligned int pointer. Using it can fault or otherwise misbehave;')
r('Padding bytes are not initialised. Copying a struct to a file, a socket or user space copies whatever stale data was in those bytes,', 'Assigning a struct\'s fields does not guarantee defined values for its padding. Copying its entire object representation can therefore disclose stale bytes,')
r('The Linux kernel has fixed many such **infoleaks** by adding `memset(&s, 0, sizeof s)` before filling a struct that is copied to user space.', 'Implementation-specific fixes may zero storage before filling it. Portable C still permits padding to take unspecified values when a struct or member is stored, so a blanket memset-then-fill recipe is not a universal guarantee. Serialise the intended fields into an explicitly defined output buffer, including explicit zero bytes where the format requires them.')
r('For mirroring real C structs, `ctypes.Structure` follows the platform\'s C rules, including tail padding.', 'ctypes.Structure can model supported C ABIs with tail padding; its layout/packing options must match the actual compiler ABI and flags, so it is not a universal mirror of arbitrary structs.')
r('**SIMD**: AVX loads work best on 32-byte-aligned data, and AVX-512 on 64-byte.', '**SIMD**: aligned AVX/AVX-512 load forms require their specified alignment; unaligned forms also exist. Alignment can avoid split accesses, but performance depends on the instruction and processor.')
r('Giving each per-thread counter its own line with `alignas(64)` (C11 `_Alignas`, or `std::hardware_destructive_interference_size` in C++17) can make a multithreaded counter many times faster.', 'Separate counters by the relevant cache-line size, including alignment and stride/padding. alignas(64) on the start of an array alone does not separate adjacent counters. C++17 hardware_destructive_interference_size is an implementation-provided size hint, used with alignas and an appropriate layout; speedups depend on the workload.')
r('**Pages**: memory used for DMA or memory-mapped I/O often has to be page-aligned (4 KiB); `aligned_alloc` and `posix_memalign` provide it.', '**Pages**: mapping and device interfaces may require page or device-specific alignment. Query the page size; 4 KiB is common, not universal. aligned_alloc and posix_memalign align virtual allocations, but do not alone pin memory, ensure physical contiguity or map it for DMA; use the required operating-system device API.')
r('- Little-endian stores the least significant byte at the lowest address (x86, ARM, RISC-V);', '- Little-endian stores the least significant byte at the lowest address (x86 and common ARM/RISC-V configurations);')
r('- A naturally aligned value never spans a cache line;', '- A naturally aligned power-of-two access within the stated size assumptions does not span a cache line;')
p.write_text(s)
p=B/'rep-memory-layout.questions.json';qs=json.loads(p.read_text());q={str(i+1):v for i,v in enumerate(qs)}
q['2']['prompt']=q['2']['prompt'].replace('On x86-64 Linux,', 'Under the ordinary x86-64 Linux System V ABI without packing options,')
q['3']['options'][2]['explanation']='The address is divisible by 2 but not by 8. It is not naturally aligned for an 8-byte value; at this particular address it does not cross a conventional 64-byte line.'
q['4']['prompt']=q['4']['prompt'].replace('calls `bind`.', 'successfully binds and listens, with the other socket fields correctly set.')
q['4']['options'][3]['explanation']='An unconverted port does not inherently make bind fail. The question stipulates that binding and listening succeed.'
q['5']['prompt']=q['5']['prompt'].replace('On x86-64 Linux,', 'Under the ordinary x86-64 Linux System V ABI without packing options,')
q['6']['prompt']=q['6']['prompt'].replace('On a 64-bit Linux or macOS machine,', 'On an x86-64 or AArch64 Linux/macOS ABI with four-byte int size and alignment,')
q['7']['prompt']='For uint32_t x = 0x12345678 on hosts with eight-bit bytes and 32-bit int, which operations expose different byte orders between little- and big-endian systems? Select all that apply.'
q['7']['options'][2]['explanation']='Correct. The raw buffers have different byte sequences; what a receiver makes of them depends on its decoder.'
q['8']['prompt']=q['8']['prompt'].replace('On x86-64,', 'Under the usual x86-64 ABI without packing options,')
q['9']['prompt']=q['9']['prompt'].replace('A kernel driver', 'An x86-64 Linux kernel driver')
q['9']['options'][1]['text']='Seven bytes of padding can retain or acquire unspecified data; copying the entire object can disclose it'
q['9']['options'][1]['explanation']='Correct. Field assignments do not guarantee padding bytes. Explicitly encode fields in a defined output layout; a source-level memset followed by stores is not a universal portable-C padding guarantee.'
q['9']['workedExample']='1. Under the stated ABI, flags is at offset 0 and id at 8, leaving seven padding bytes.\n2. Assigning fields does not specify their values.\n3. Copying the whole representation can leak stale information.\n4. Encode the intended fields into a fully initialised output buffer; do not rely on portable C to preserve zero padding after subsequent member stores. Implementation-specific zeroing fixes require checking the compiler and generated code.'
q['10']['prompt']=q['10']['prompt'].replace('Firmware for a strict-alignment microcontroller parses packets with a packed struct:', 'Firmware for a strict-alignment microcontroller uses this fragment, with h pointing to a valid hdr at a four-byte-aligned address:')
q['10']['options'][3]['explanation']='The compiler extension allows this integer member in a packed struct. A plain pointer can lose the compiler\'s knowledge of reduced member alignment.'
q['10']['workedExample']=q['10']['workedExample'].replace('memcpy(&v, &h->len, 4);', 'memcpy(&v, (const unsigned char *)h + 1, sizeof v);').replace('1. Packed layout:', '1. With eight-bit bytes and the stated compiler extension, packed layout:')
q['11']['options'][1]['text']='A suitably aligned ordinary 8-byte hardware load/store to normal memory on x86-64 is non-tearing; C data-race rules still apply'
q['11']['options'][1]['explanation']='Correct. Hardware atomicity of this access does not make unsynchronised conflicting accesses to a plain C object valid.'
q['11']['workedExample']=q['11']['workedExample'].replace('though you still need atomics for ordering in C', 'though C atomics or other synchronisation are needed to avoid data races, not merely to request ordering').replace("unless the AC flag is set, which ordinary programs don't use", 'some instruction forms require alignment, and alignment-checking modes can also fault')
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
print('memory-layout corrections applied')
