#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <signal.h>
#include <sys/wait.h>
#include <sys/mman.h>
#include <time.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#define N 1000

int main(void) {
    int a[2], b[2];
    char c = 'x';
    pipe(a);
    pipe(b);
    if (fork() == 0) {
        for (int i = 0; i < N; i++) {
            read(a[0], &c, 1);
            write(b[1], &c, 1);
        }
        _exit(0);
    }
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < N; i++) {
        write(a[1], &c, 1);
        read(b[0], &c, 1);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double ns =
        (t1.tv_sec - t0.tv_sec) * 1e9 +
        (t1.tv_nsec - t0.tv_nsec);
    /* Includes IPC and syscall overhead. */
    printf("%.0f ns/half-trip\n", ns/N/2);
    return 0;
}
