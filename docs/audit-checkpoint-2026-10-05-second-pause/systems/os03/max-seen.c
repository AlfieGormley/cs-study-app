#include <pthread.h>
#include <stdatomic.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdatomic.h>

atomic_long max_seen = 0;

void record(long v) {
    long cur = atomic_load(&max_seen);
    while (v > cur &&
           !atomic_compare_exchange_weak(
               &max_seen, &cur, v))
        ;  // cur now holds the new value
}

void *w(void*x){for(long i=1;i<=100000;i++)record(i);return 0;}
int main(){pthread_t a,c;assert(!pthread_create(&a,0,w,0));assert(!pthread_create(&c,0,w,0));pthread_join(a,0);pthread_join(c,0);assert(max_seen==100000);}