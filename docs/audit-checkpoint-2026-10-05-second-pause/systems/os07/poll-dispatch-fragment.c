#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <assert.h>
#include <string.h>
#include <poll.h>
#define MAXCONN 1
void handle_events(int fd,short ev){assert(ev&POLLIN);char c;assert(read(fd,&c,1)==1&&c==42);exit(0);}
int main(void){int fds[2];assert(pipe(fds)==0);char c=42;assert(write(fds[1],&c,1)==1);int n=1;alarm(2);
struct pollfd p[MAXCONN];
p[0].fd=fds[0];p[0].events=POLLIN;

int r;
do {
    r = poll(p, n, -1);
} while (r < 0 && errno == EINTR);
if (r < 0) { perror("poll"); exit(1); }
for (int i = 0; i < n; i++) {
    if (p[i].revents != 0)
        handle_events(p[i].fd,
                      p[i].revents);
}

}