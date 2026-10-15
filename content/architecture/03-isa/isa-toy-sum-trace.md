---
id: isa-toy-sum-trace
title: Trace a complete stored program
level: basic
minutes: 4
sourceLesson: isa-stored-program
summary: Trace the summing program and see how writing code cells changes execution.
---

This example uses the preceding toy interpreter: LOAD, ADD, SUB, STORE, JZ and JMP operate on the accumulator and numbered memory cells. Fetch advances the program counter before execution. The same `run(mem)` function executes the program below.

Here is a program that adds up every whole number from a starting value down to 1:

```formula
total = n + (n − 1) + … + 1   for n ≥ 1
total = 0   for n = 0
total = (n(n + 1)) / 2
total = 3 × 4 / 2 = 6
where
total: the sum the program leaves in memory cell 21
n: the starting value, a whole number 0 or more, stored in cell 20 (3 in the run below)
…: and so on: every whole number in between is included
≥: greater than or equal to
In words: zero has an empty sum of 0; for a positive input add n, then one less, all the way down to 1; the shortcut n × (n + 1) / 2 gives the same answer, so starting from 3 the program should end with 6.
```

The code is at addresses 0 to 8, `n` lives at 20, the running total at 21 and the constant 1 at 22:

```
addr  value  meaning
 0     120   LOAD  20     acc = n
 1     508   JZ    8      if n == 0: halt
 2     221   ADD   21     acc = n + total
 3     421   STORE 21     total = acc
 4     120   LOAD  20
 5     322   SUB   22     acc = n - 1
 6     420   STORE 20     n = acc
 7     600   JMP   0      loop
 8     000   HALT
```

```python
prog = [120, 508, 221, 421,
        120, 322, 420, 600,
        0]
# Fill addresses 9–19, then data 20–22.
mem = prog + [0] * 11 + [3, 0, 1]
run(mem)
print(mem[21])   # 6  (3 + 2 + 1)
```

Notice what is going on. The program is a list of integers in the same `mem` list as the data. `run` cannot tell `120` the instruction from `120` the number; it only treats a cell as an instruction because PC points at it. With `n = 3`, the loop body (8 instructions) runs three times, then LOAD, JZ and HALT run once more as the program stops:

```formula
F = 8n + 3
F = 8 × 3 + 3 = 27
where
F: the total number of instructions fetched before the machine halts
n: the starting value in cell 20 (here 3)
8: the loop body, addresses 0 to 7, which runs once for each value n, n − 1, …, 1
3: the final LOAD, JZ (now taken, because acc is 0) and HALT
In words: every pass round the loop costs 8 fetches, and stopping costs 3 more, so starting from 3 the machine makes 27 fetches.
```

> [!warning] Code is data, both ways
> If the program did `STORE 7`, it would overwrite its own `JMP` instruction with whatever number was in `acc`. That is **self-modifying code**. It is also how many attacks work: trick a program into writing attacker-chosen bytes into memory, then trick it into jumping there.

## Key takeaways
- The same memory list holds instructions, inputs and outputs.
- The summing loop updates both the total and the remaining input.
- Each positive input costs eight fetches, followed by three stopping fetches.

## Further reading
- [Von Neumann architecture — Wikipedia](https://en.wikipedia.org/wiki/Von_Neumann_architecture)
- [Instruction cycle — Wikipedia](https://en.wikipedia.org/wiki/Instruction_cycle)
- [Manchester Baby — Wikipedia](https://en.wikipedia.org/wiki/Manchester_Baby)
- [Modified Harvard architecture — Wikipedia](https://en.wikipedia.org/wiki/Modified_Harvard_architecture)
- [Little man computer — Wikipedia](https://en.wikipedia.org/wiki/Little_man_computer)
- [Self-modifying code — Wikipedia](https://en.wikipedia.org/wiki/Self-modifying_code)

### Primary references for this review
- [Manchester’s account of the Baby](https://curation.cs.manchester.ac.uk/computer50/www.computer50.org/mark1/new.baby.html)
- [Intel APX register extension](https://www.intel.com/content/www/us/en/developer/articles/technical/advanced-performance-extensions-apx.html)
- [Arm: implementing cache maintenance](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/caches-self-modifying-code-implementing-clear-cache)
- [Arm: code updates across threads](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/caches-self-modifying-code-working-with-threads)
- [Apple: porting JIT compilers](https://developer.apple.com/documentation/apple-silicon/porting-just-in-time-compilers-to-apple-silicon)
- [QEMU translation internals](https://www.qemu.org/docs/master/devel/tcg.html)
