#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <limits.h>
#include <stddef.h>
struct S {char tag; int n; long v; short k;};
struct T {char c; int x; char d;};
struct P {char a; double b; char c; int d;};
struct R {double b;int d;char a,c;};
extern long linear(long), positives(const long*,long), factorial(long),sum(long*,long);
extern int maximum(int,int);extern void increment(int*,long);
static long count=0;
#define CHECK(x) do{assert(x);++count;}while(0)
int main(void){
CHECK(sizeof(struct S)==24);CHECK(offsetof(struct S,n)==4);CHECK(offsetof(struct S,k)==16);CHECK(sizeof(struct T)==12);CHECK(sizeof(struct P)==24);CHECK(sizeof(struct R)==16);
long a[101];for(int i=0;i<101;i++)a[i]=i-50;
for(long n=-2;n<=101;n++) {long s=0,p=0;for(long j=0;j<n;j++){s+=a[j];p+=a[j]>0;}CHECK(sum(a,n)==s);CHECK(positives(a,n)==p);}
for(long i=-1000;i<=1000;i++)CHECK(linear(i)==i*5+7);
long f=1;for(long n=0;n<=20;n++){if(n>0)f*=n;CHECK(factorial(n)==f);}CHECK(factorial(-2)==1);
int vals[]={INT_MIN,INT_MIN+1,-10,-1,0,1,10,INT_MAX};for(int i=0;i<8;i++)for(int j=0;j<8;j++)CHECK(maximum(vals[i],vals[j])==(vals[i]>vals[j]?vals[i]:vals[j]));
int b[]={0,2,-4};increment(b,1);CHECK(b[0]==0 && b[1]==3 && b[2]==-4);
extern uint64_t constant(void);CHECK(constant()==UINT64_C(0x1234567890abcdef));
printf("%ld\n",count);return 0;}
