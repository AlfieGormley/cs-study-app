#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <limits.h>
#include <assert.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <arpa/inet.h>
int main(void){volatile int x=INT_MAX; return x+1;}