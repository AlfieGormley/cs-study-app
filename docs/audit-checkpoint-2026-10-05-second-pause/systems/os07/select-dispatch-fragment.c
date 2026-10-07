#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <assert.h>
#include <string.h>
#include <sys/select.h>
void handle(int fd){char c;assert(read(fd,&c,1)==1&&c==42);exit(0);}
int main(void){int p[2];assert(pipe(p)==0);char c=42;assert(write(p[1],&c,1)==1);int fds[]={p[0]};int n=1;alarm(2);
fd_set rfds;
for (;;) {
    FD_ZERO(&rfds);
    int maxfd = -1;
    for (int i = 0; i < n; i++) {
        if (fds[i] < 0 ||
            fds[i] >= FD_SETSIZE) abort();
        FD_SET(fds[i], &rfds);
        if (fds[i] > maxfd)
            maxfd = fds[i];
    }
    int r = select(maxfd + 1, &rfds,
                   NULL, NULL, NULL);
    if (r < 0) {
        if (errno == EINTR) continue;
        perror("select"); break;
    }
    for (int i = 0; i < n; i++)
        if (FD_ISSET(fds[i], &rfds))
            handle(fds[i]);
}

}