from helper import *
base=Path('content/os/06-file-systems');vm=['https://docs.kernel.org/admin-guide/sysctl/vm.html'];nv=['https://docs.kernel.org/block/blk-mq.html']
p=base/'fs-page-cache.md'
edit(p,'and how servers like Kafka and nginx move data at line rate.','and how cached I/O can reduce data movement in servers.','Remove unsupported performance guarantee.',vm)
edit(p,'These `vm` sysctls control it (typical defaults shown):','These `vm` sysctls control it (illustrative configured values shown; inspect the running system):','No universal defaults implied.',vm)
edit(p,'| Setting | Default | Meaning |','| Setting | Example value | Meaning |','Align table with configuration scope.',vm)
edit(p,'| `dirty_expire_centisecs` | 3000 | Write pages dirty > 30 s |','| `dirty_expire_centisecs` | 3000 | Eligible for periodic writeback after 30 s |','Eligibility not guaranteed write time.',vm)
edit(p,'A machine with 64 GiB of RAM and default ratios can hold several gigabytes of dirty data.','In a hypothetical workload, a machine with 64 GiB of RAM and the illustrated ratios can accumulate several gigabytes of dirty data.','Model not observed timing.',vm)
p=base/'fs-storage-devices.md'
edit(p,'| Max throughput | ~550 MB/s | ~7 GB/s (PCIe 4 x4) |','| Throughput | Device and workload dependent | Device, PCIe generation/width and workload dependent |','Remove unsourced achieved-throughput figures.',nv)
edit(p,'AHCI was designed for spinning disks: one queue, 32 outstanding commands, and several uncached register reads per command.','AHCI provides one command list per port with up to 32 outstanding commands.','Remove universal per-command register cost and per-controller queue ambiguity.',nv)
# Repair visibly joined words in our new prose; deliberately no broad token rewrite.
repl={'conversion,10':'conversion, 10','equals12.5':'equals 12.5','rate1 per10':'rate 1 per 10','count is3.84':'count is 3.84','is1−':'is 1−','this16KiB-page model,256 page programs rewrite4MiB, which is1024 times a4KiB':'this 16 KiB-page model, 256 page programs rewrite 4 MiB, which is 1024 times a 4 KiB','Leave20%':'Leave 20%','RAID5 of12TB':'RAID 5 of 12 TB','reads60TB':'reads 60 TB','default16KiB':'default 16 KiB','presents25%':'presents 25%','Installed256GiB':'Installed 256 GiB','simplified256GiB':'simplified 256 GiB','model,10% and20% give25.6 and51.2GiB':'model, 10% and 20% give 25.6 and 51.2 GiB','A2GiB':'A 2 GiB','constant1GB/s':'constant 1 GB/s','about2.15s':'about 2.15 s'}
for p in list(base.glob('*.md'))+list(base.glob('*.questions.json')):
 for a,b in repl.items():
  if a in p.read_text(): edit(p,a,b,'Restore readable spacing in audit corrections.',['Editorial consistency'])
save([*base.glob('*.md'),*base.glob('*.questions.json')])
