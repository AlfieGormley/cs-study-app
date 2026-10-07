#include <pthread.h>
#include <stdatomic.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdatomic.h>

atomic_flag f = ATOMIC_FLAG_INIT;

void spin_lock(void) {
    while (atomic_flag_test_and_set(&f))
        ;  // old value 1: held, retry
}

void spin_unlock(void) {
    atomic_flag_clear(&f);
}

int count;
void *work(void*x){for(int i=0;i<10000;i++){spin_lock();count++;spin_unlock();}return 0;}
int main(){pthread_t t[4];for(int i=0;i<4;i++)assert(!pthread_create(t+i,0,work,0));for(int i=0;i<4;i++)assert(!pthread_join(t[i],0));assert(count==40000);}