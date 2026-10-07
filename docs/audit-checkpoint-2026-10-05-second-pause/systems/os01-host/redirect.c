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
pid_t pid = fork();
if (pid == 0) {
    int fd = open("out.txt",
        O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) _exit(126);
    if (dup2(fd, 1) < 0) _exit(126);
    if (fd != 1) close(fd);
    execlp("ls", "ls", NULL);
    _exit(127);
}
waitpid(pid, NULL, 0);

return 0;}