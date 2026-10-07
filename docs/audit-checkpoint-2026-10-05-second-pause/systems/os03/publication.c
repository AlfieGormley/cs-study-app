#include <pthread.h>
#include <stdatomic.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
int data; atomic_int ready=0;
void *producer(void*x){data=42;atomic_store_explicit(&ready,1,memory_order_release);return 0;}
int main(){pthread_t t;assert(!pthread_create(&t,0,producer,0));while(!atomic_load_explicit(&ready,memory_order_acquire));assert(data==42);assert(!pthread_join(t,0));}
