#include <assert.h>
#include <stdint.h>
#include <limits.h>
#include <stdio.h>
extern uint32_t absbits(int32_t);extern int post(const int*);
int main(void){long count=0;for(int32_t i=-100000;i<=100000;i++){assert(absbits(i)==(uint32_t)(i<0?-i:i));++count;}assert(absbits(INT_MIN)==UINT32_C(0x80000000));++count;int x[]={7,9};assert(post(x)==16);++count;printf("%ld\n",count);}
