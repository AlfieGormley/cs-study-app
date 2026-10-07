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
extern long linearatt(long),identity(long),at(long*,int);extern int half(int),choose(int),choose2(int),get2d(int (*)[3],long,long),getn(struct S*,long);
for(int i=-100000;i<=100000;i++){CHECK(half(i)==i/2);CHECK(choose(i)==(i>0?1:2));CHECK(choose2(i)==(i>0?1:2));CHECK(linearatt(i)==i*5L+7);CHECK(identity(i)==i);}
for(int i=0;i<8;i++)CHECK(half(vals[i])==vals[i]/2);
for(int i=-50;i<=50;i++)CHECK(at(a+50,i)==i);
int m[2][3]={{1,2,3},{4,5,6}};for(int i=0;i<2;i++)for(int j=0;j<3;j++)CHECK(get2d(m,i,j)==m[i][j]);
struct S structs[5]={0};for(int i=0;i<5;i++){structs[i].n=19-i;CHECK(getn(structs,i)==19-i);}
printf("%ld\n",count);return 0;}
