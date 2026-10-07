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
char *argv[] = {"ls", "-l", NULL};
execvp("ls", argv);
perror("execvp");   /* only on failure */
_exit(127);

return 0;}