#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <assert.h>
#include <string.h>
#include <aio.h>
void do_other_work(void){}
int main(void){char path[]="/tmp/io-audit-XXXXXX";int fd=mkstemp(path);unlink(path);assert(write(fd,"hello",5)==5);char buf[4096];
struct aiocb cb = {0};
cb.aio_fildes = fd;
cb.aio_buf    = buf;
cb.aio_nbytes = sizeof buf;
cb.aio_offset = 0;
cb.aio_sigevent.sigev_notify = SIGEV_NONE;

if (aio_read(&cb) == -1) {
    perror("aio_read"); exit(1);
}
do_other_work();
while (aio_error(&cb) == EINPROGRESS)
    ;                  /* or aio_suspend */
int status = aio_error(&cb);
ssize_t n = aio_return(&cb);
/* status: completion error, or 0. */

assert(status==0 && n==5 && memcmp(buf,"hello",5)==0);close(fd);return 0;}