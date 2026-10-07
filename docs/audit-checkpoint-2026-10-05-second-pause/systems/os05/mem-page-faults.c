#include <stdio.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <unistd.h>

static long minflt(void) {
    struct rusage u;
    getrusage(RUSAGE_SELF, &u);
    return u.ru_minflt;
}

int main(void) {
    size_t len = 64UL << 20; /* 64 MiB */
    char *p = mmap(NULL, len,
        PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1, 0);
    if (p == MAP_FAILED) {
        perror("mmap");
        return 1;
    }
    long step = sysconf(_SC_PAGESIZE);
    if (step <= 0) return 1;
    long before = minflt();
    for (size_t i = 0; i < len; i += step)
        ((volatile char *)p)[i] = 1;
    printf("%ld faults\n",
           minflt() - before);
    munmap(p, len);
}
