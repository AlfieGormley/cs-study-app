#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <limits.h>
#include <assert.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <arpa/inet.h>
uint32_t rd_be32(const uint8_t *b) {
    return (uint32_t)b[0] << 24 |
           (uint32_t)b[1] << 16 |
           (uint32_t)b[2] << 8  |
           (uint32_t)b[3];
}
struct A {
    char a;   /* 1 byte  */
    int  b;   /* 4 bytes */
    char c;   /* 1 byte  */
};
struct B {
    int  b;   /* offset 0 */
    char a;   /* offset 4 */
    char c;   /* offset 5 */
};            /* sizeof = 8 */
int will_overflow(int x) {
    return x + 1 < x;
}

static int errors; void handle_error(void){errors++;}

int main(void){
{
printf("%x %o\n", 181u, 181u);
// prints: b5 265

}
{
int8_t  s = -3;
uint8_t u = 0xFD;  /* same bits */
int32_t a = s;     /* -3  */
int32_t b = u;     /* 253 */
assert(a==-3 && b==253);
}
{
int a=INT_MAX,b=1;int r;
if (__builtin_add_overflow(a, b, &r))
    handle_error();
/* C23 standard version: */
/* #include <stdckdint.h>  */
/* if (ckd_add(&r, a, b))  */
assert(errors==1);
}
{
int x = -1;
unsigned y = 1;
if (x < y) puts("less");
else       puts("not less");
/* prints: not less */

}
{
unsigned x=44,k=3;x |=  (1u << k);   /* set bit k    */
x &= ~(1u << k);   /* clear bit k  */
x ^=  (1u << k);   /* toggle bit k */
if (x & (1u << k)) { /* bit is set */ }
assert(x==44);
}
{
int fd = open("log.txt",
    O_WRONLY | O_CREAT | O_APPEND, 0644);
assert(fd>=0);close(fd);unlink("log.txt");
}
{
uint32_t v = 0x12345678;
unsigned char *p = (unsigned char *)&v;
printf("%02x\n", (unsigned)p[0]);
/* 78 little-endian; 12 big-endian */

}
{
struct sockaddr_in addr;
addr.sin_port = htons(8080);
/* bytes in memory: 1F 90 */
unsigned char *b=(unsigned char*)&addr.sin_port;assert(b[0]==31&&b[1]==144);
}
{
#include <stddef.h>
printf("%zu %zu %zu\n",
       sizeof(struct A),
       offsetof(struct A, c),
       _Alignof(struct A));
/* 12 8 4 */

}
{
unsigned char b[]={0x12,0x34,0x56,0x78};assert(rd_be32(b)==0x12345678);assert(sizeof(struct B)==8);
}
{
int x = 012;
printf("%d\n", x + 1);

}
{
int x = -1;
unsigned y = 1;
puts(x < y ? "less" : "not less");

}
{
struct A {
    char a;
    int  b;
    char c;
};

}
{
struct G {
    uint8_t  t;
    uint64_t x;
    uint16_t y;
    uint32_t z;
};

}
{
struct E {
    char  a;
    short s;
    char  c;
    int   i;
};

}
{
int x = 6;
if (x & 1 == 0)
    puts("even");
else
    puts("odd");

}
{
int x = -21;
printf("%d %d\n", x >> 2, x / 4);

}
{
struct G{uint8_t t;uint64_t x;uint16_t y;uint32_t z;};assert(sizeof(struct G)==24);assert(offsetof(struct G,z)==20);
}
{
struct E{char a;short s;char c;int i;};assert(offsetof(struct E,i)==8);
}
{
for(unsigned x=0;x<65536;x++){assert((x^x)==0);assert((x>>1)==x/2);}
}
{
assert(will_overflow(INT_MAX-1)==0);
}
return 0;}
