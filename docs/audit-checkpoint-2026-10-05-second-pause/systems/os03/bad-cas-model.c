#include <pthread.h>
#include <stdatomic.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
int main(){atomic_int l=1;int expected=0;assert(!atomic_compare_exchange_strong(&l,&expected,1));assert(expected==1);assert(atomic_compare_exchange_strong(&l,&expected,1));assert(l==1);}