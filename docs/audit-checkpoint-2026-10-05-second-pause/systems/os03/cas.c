#include <pthread.h>
#include <stdatomic.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
atomic_int l = 0;

void cas_lock(void) {
    int expected = 0;
    while (!atomic_compare_exchange_weak(
               &l, &expected, 1))
        expected = 0;  // CAS wrote the seen
                       // value here; reset
}

void cas_unlock(){atomic_store(&l,0);}
int count;
void *work(void*x){for(int i=0;i<10000;i++){cas_lock();count++;cas_unlock();}return 0;}
int main(){pthread_t t[4];for(int i=0;i<4;i++)assert(!pthread_create(t+i,0,work,0));for(int i=0;i<4;i++)assert(!pthread_join(t[i],0));assert(count==40000);}