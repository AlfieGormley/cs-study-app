#include <stdint.h>
#include <stddef.h>
#include <assert.h>
uint64_t branch(const uint8_t *data,size_t n,uint64_t sum) { for(size_t i=0;i<n;i++) if(data[i]>=128) sum+=data[i]; return sum; }
uint64_t select_sum(const uint8_t *data,size_t n,uint64_t sum) { for(size_t i=0;i<n;i++) sum+=(data[i]>=128)?data[i]:0; return sum; }
int main(void) {uint8_t data[256]; for(int i=0;i<256;i++)data[i]=(uint8_t)i; for(size_t n=0;n<=256;n++){uint64_t expect=0;for(size_t i=128;i<n;i++)expect+=i;assert(branch(data,n,0)==expect);assert(select_sum(data,n,0)==expect);assert(branch(data,n,UINT64_MAX)==select_sum(data,n,UINT64_MAX));}return 0;}
