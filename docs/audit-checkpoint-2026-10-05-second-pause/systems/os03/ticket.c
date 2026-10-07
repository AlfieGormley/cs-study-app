#include <pthread.h>
#include <stdatomic.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
atomic_int next = 0, serving = 0;

void ticket_lock(void) {
    int me = atomic_fetch_add(&next, 1);
    while (atomic_load(&serving) != me)
        ;  // spin until our number
}

void ticket_unlock(void) {
    atomic_fetch_add(&serving, 1);
}

int count;
void *work(void*x){for(int i=0;i<10000;i++){ticket_lock();count++;ticket_unlock();}return 0;}
int main(){pthread_t t[4];for(int i=0;i<4;i++)assert(!pthread_create(t+i,0,work,0));for(int i=0;i<4;i++)assert(!pthread_join(t[i],0));assert(count==40000);}