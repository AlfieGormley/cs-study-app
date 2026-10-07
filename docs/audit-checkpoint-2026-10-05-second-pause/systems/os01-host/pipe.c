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
int fd[2];
pipe(fd);
pid_t pid = fork();
if (pid == 0) {          /* child */
    close(fd[1]);
    char buf[64];
    ssize_t n;
    while ((n = read(fd[0], buf,
                     sizeof buf)) > 0)
        write(1, buf, n);
    _exit(0);
}
close(fd[0]);            /* parent */
const char *m = "hello\n";
write(fd[1], m, strlen(m));
close(fd[1]);   /* child now sees EOF */
waitpid(pid, NULL, 0);

return 0;}