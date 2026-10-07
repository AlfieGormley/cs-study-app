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
#include <stdio.h>
#include <stdlib.h>

int g_init = 42;      /* data   */
int g_zero;           /* BSS    */
const char *s = "hi"; /* pointer: data */

int main(void) {
    int local = 1;               /* stack */
    int *h = malloc(16);         /* heap  */
    printf("text  %p\n", (void *)main);
    printf("data  %p\n", (void *)&g_init);
    printf("bss   %p\n", (void *)&g_zero);
    printf("heap  %p\n", (void *)h);
    printf("stack %p\n", (void *)&local);
    free(h);
    return 0;
}
