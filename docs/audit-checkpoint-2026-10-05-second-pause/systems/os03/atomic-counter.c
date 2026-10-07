#include <pthread.h>
#include <stdatomic.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
atomic_int hits=0;
void *run(void*x){for(int i=0;i<100000;i++) atomic_fetch_add_explicit(&hits,1,memory_order_relaxed);return 0;}
int main(){pthread_t t[8];for(int i=0;i<8;i++)assert(!pthread_create(t+i,0,run,0));for(int i=0;i<8;i++)assert(!pthread_join(t[i],0));assert(hits==800000);}
