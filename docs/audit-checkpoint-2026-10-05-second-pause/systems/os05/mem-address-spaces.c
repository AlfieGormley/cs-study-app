#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int x = 1;

int main(void) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    }
    if (pid == 0) {             /* child */
        x = 2;
        printf("child  %p %d\n",
               (void *)&x, x);
        return 0;
    }
    wait(NULL);                 /* parent */
    printf("parent %p %d\n", (void *)&x, x);
    return 0;
}
