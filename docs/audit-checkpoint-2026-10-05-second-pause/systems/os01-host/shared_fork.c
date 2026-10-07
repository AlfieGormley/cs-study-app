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
int *p=mmap(NULL,4096,PROT_READ|PROT_WRITE,MAP_SHARED|MAP_ANON,-1,0);*p=1;pid_t c=fork();if(!c){*p=42;_exit(0);}waitpid(c,NULL,0);printf("%d\n",*p);
return 0;}