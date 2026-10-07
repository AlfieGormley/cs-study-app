#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <assert.h>
#include <string.h>
#include <sys/event.h>
int main(void){int p[2];assert(pipe(p)==0);char c=42;assert(write(p[1],&c,1)==1);int fd=p[0];void *conn=NULL;alarm(2);
int kq = kqueue();
struct kevent ch, ev[64];
EV_SET(&ch, fd, EVFILT_READ, EV_ADD,
       0, 0, conn);

/* register and wait in one call */
int n = kevent(kq, &ch, 1, ev, 64, NULL);

assert(n==1&&ev[0].filter==EVFILT_READ&&ev[0].data==1);close(kq);close(p[0]);close(p[1]);}