---
id: dl-debugging-native-dumps
title: Native and database lock diagnostics
level: advanced
minutes: 3
sourceLesson: dl-debugging
summary: glibc internal owner fields are implementation details, not portable POSIX APIs.
---

### C and C++

Attach gdb and dump every thread:

```
$ gdb -p 4242
(gdb) thread apply all bt
Thread 3 (LWP 4245):
#0 futex_wait ...
#1 __lll_lock_wait ...
#2 pthread_mutex_lock (m=0x...060)
#3 transfer (...) at bank.c:21
Thread 2 (LWP 4244):
#2 pthread_mutex_lock (m=0x...0a0)
#3 transfer (...) at bank.c:21
```

Both threads are blocked inside `pthread_mutex_lock`. For ordinary glibc mutexes, an internal owner field can help identify the holder. It is not portable POSIX API; robust, PI, elision and transient states require implementation-specific interpretation:

```
(gdb) p ((pthread_mutex_t *)
         0x...060)->__data.__owner
$1 = 4244
(gdb) p ((pthread_mutex_t *)
         0x...0a0)->__data.__owner
$2 = 4245
```

Thread 4245 waits for a mutex owned by 4244, which waits for one owned by 4245: a two-thread cycle. Without a debugger, `/proc/<pid>/task/<tid>/wchan` shows which kernel function each thread is sleeping in (a futex wait for a user-space lock), often in an interruptible sleep state for ordinary userspace futex waits. Exact state and wait-channel visibility depend on the wait type, kernel and permissions.

### The kernel itself

Some kernel waits leave tasks in state `D` (uninterruptible sleep), while spinning deadlocks may instead cause lockup warnings. With the relevant configuration enabled, the **hung task detector** checks prolonged uninterruptible waits against `kernel.hung_task_timeout_secs` (commonly 120 s); settings, exclusions and reporting limits affect what is logged. `echo w > /proc/sysrq-trigger` dumps all blocked tasks on demand.

## Databases

Databases detect deadlocks for you (the detection and recovery lessons), but you still need to find out *which code* causes them.

- **PostgreSQL** logs each deadlock with the processes, the locks and the statements involved (`Process 123 waits for ShareLock on transaction 456; blocked by process 789.`). Turn on `log_lock_waits` (off by default up to PostgreSQL 18; the PostgreSQL 19 documentation lists it as on by default; check the documentation for the server version in use) to also log any wait longer than `deadlock_timeout`. For live blocking:

```sql
-- Fragment: use the stated session setup.
SELECT pid,
       pg_blocking_pids(pid) AS blocked_by,
       wait_event_type,
       left(query, 60) AS query
FROM pg_stat_activity
WHERE cardinality(
        pg_blocking_pids(pid)) > 0;
```

- **MySQL InnoDB**: `SHOW ENGINE INNODB STATUS` has a *LATEST DETECTED DEADLOCK* section with both transactions, their statements and their locks. Only the latest is kept unless you set `innodb_print_all_deadlocks`, which writes every one to the error log.
- **SQL Server**: the built-in `system_health` Extended Events session captures deadlock graphs as XML.

Look for the same pair of statements recurring. That's a lock-order bug in the application, and the prevention lessons's fix (touch rows in a consistent order, keep transactions short) applies.

## Key takeaways
- glibc internal owner fields are implementation details, not portable POSIX APIs.
- Kernel hung-task messages concern particular prolonged waits and are not universal deadlock proof.
- Database lock views and deadlock logs identify recurring application statements.

## Further reading
- [GNU GDB: thread backtraces](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Threads.html)
- [PostgreSQL: blocking process IDs](https://www.postgresql.org/docs/current/functions-info.html)
