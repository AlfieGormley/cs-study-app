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
int p[2];char b[20]={0};pipe(p);write(p[1],"HELLO",5);write(p[1],"WORLD",5);int n=read(p[0],b,7);printf("%d %s\n",n,b);
return 0;}