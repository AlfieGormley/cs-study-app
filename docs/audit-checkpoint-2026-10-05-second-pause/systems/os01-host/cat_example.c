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
#include <fcntl.h>
#include <unistd.h>

int main(void) {
    char buf[4096];
    int fd = open("notes.txt", O_RDONLY);
    ssize_t n;
    while ((n = read(fd, buf, 4096)) > 0)
        write(1, buf, n); /* 1 = stdout */
    close(fd);
    return 0;
}
