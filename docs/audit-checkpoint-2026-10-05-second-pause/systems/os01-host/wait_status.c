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
int main(void){
pid_t pid=fork(); if(pid==0) _exit(300);
int status;
pid_t done = waitpid(pid, &status, 0);
if (done < 0) { /* check errno; retry EINTR */
    perror("waitpid");
} else if (WIFEXITED(status))
    printf("exit %d\n",
           WEXITSTATUS(status));
else if (WIFSIGNALED(status))
    printf("signal %d\n",
           WTERMSIG(status));

return 0;}