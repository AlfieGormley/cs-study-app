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
#include <sys/wait.h>
#include <unistd.h>

int main(void) {
    int x = 10;
    pid_t pid = fork();
    if (pid == 0) {          /* child  */
        x += 5;
        printf("child %d\n", x);
        return 0;
    }
    wait(NULL);              /* parent */
    printf("parent %d\n", x);
    return 0;
}
