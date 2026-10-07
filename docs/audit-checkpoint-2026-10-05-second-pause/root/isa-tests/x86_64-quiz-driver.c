#include <assert.h>
#include <stdint.h>
#include <limits.h>
#include <stdio.h>
extern long times(long);extern int mystery(uint64_t),badhalf(int),unguarded(unsigned),unsignedcompare(void),safeindex(int*,uint64_t);extern uint64_t zeroextend(void);
int main(void){long count=0;assert(times(7)==84);assert(zeroextend()==UINT64_C(0x12345678));assert(unsignedcompare()==1);assert(badhalf(-7)==-4);count+=4;
for(uint64_t i=0;i<65536;i++){assert(mystery(i)==__builtin_popcountll(i));++count;}assert(mystery(UINT64_MAX)==64);++count;
for(unsigned i=1;i<1000;i++){assert(unguarded(i)==i*(i+1)/2);++count;}
int array[]={3,7,9};assert(safeindex(array,UINT64_C(0x7777777700000001))==7);++count;printf("%ld\n",count);}
