#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <arpa/inet.h>
#define SEC(x)
#define XDP_PASS 2
#define XDP_DROP 1
#define ETH_P_IP 0x0800
#define bpf_htons htons
#define bpf_ntohs ntohs
struct xdp_md{uintptr_t data,data_end;};
struct __attribute__((packed)) ethhdr{unsigned char d[6],s[6];uint16_t h_proto;};
struct __attribute__((packed)) iphdr{unsigned ihl:4,version:4;uint8_t tos;uint16_t tot_len,id,frag_off;uint8_t ttl,protocol;uint16_t check;uint32_t saddr,daddr;};
struct __attribute__((packed)) udphdr{uint16_t source,dest,len,check;};
SEC("xdp")
int drop9999(struct xdp_md *ctx)
{
  void *data =
      (void *)(long)ctx->data;
  void *end =
      (void *)(long)ctx->data_end;
  struct ethhdr *eth = data;
  if ((void *)(eth + 1) > end)
    return XDP_PASS;
  if (eth->h_proto !=
      bpf_htons(ETH_P_IP))
    return XDP_PASS;
  struct iphdr *ip =
      (void *)(eth + 1);
  if ((void *)(ip + 1) > end ||
      ip->protocol != IPPROTO_UDP)
    return XDP_PASS;
  if (ip->version != 4 || ip->ihl < 5)
    return XDP_PASS;
  if (bpf_ntohs(ip->frag_off) & 0x3fff)
    return XDP_PASS; /* MF or offset */
  unsigned hlen = ip->ihl * 4;
  unsigned total = bpf_ntohs(ip->tot_len);
  if (total < hlen + sizeof(struct udphdr))
    return XDP_PASS;
  if ((void *)ip + total > end)
    return XDP_PASS;
  struct udphdr *udp = (void *)ip + hlen;
  if ((void *)(udp + 1) > end)
    return XDP_PASS;
  if (udp->dest == bpf_htons(9999))
    return XDP_DROP;
  return XDP_PASS;
}
int main(void){unsigned char b[128]={0};struct ethhdr *e=(void*)b;struct iphdr *ip=(void*)(e+1);struct udphdr *udp=(void*)(b+34);struct xdp_md ctx={(uintptr_t)b,(uintptr_t)(b+42)};e->h_proto=htons(0x0800);ip->version=4;ip->ihl=5;ip->protocol=17;ip->tot_len=htons(28);udp->dest=htons(9999);assert(drop9999(&ctx)==XDP_DROP);udp->dest=htons(80);assert(drop9999(&ctx)==XDP_PASS);udp->dest=htons(9999);ip->ihl=4;assert(drop9999(&ctx)==XDP_PASS);ip->ihl=5;ip->frag_off=htons(1);assert(drop9999(&ctx)==XDP_PASS);ip->frag_off=htons(0x2000);assert(drop9999(&ctx)==XDP_PASS);ip->frag_off=0;ip->tot_len=htons(20);assert(drop9999(&ctx)==XDP_PASS);ip->tot_len=htons(28);ctx.data_end=(uintptr_t)(b+41);assert(drop9999(&ctx)==XDP_PASS);ctx.data_end=(uintptr_t)(b+42);e->h_proto=htons(0x8100);assert(drop9999(&ctx)==XDP_PASS);return 0;}