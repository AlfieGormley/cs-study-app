import struct,socket,subprocess
from pathlib import Path
pkts=[]
def csum(b):
 if len(b)%2:b+=b'\0'
 s=sum(struct.unpack('!%dH'%(len(b)//2),b))
 while s>>16:s=(s&65535)+(s>>16)
 return (~s)&65535
def pkt(flags,port=443,payload=b'',v6=False):
 a=socket.inet_pton(socket.AF_INET6 if v6 else socket.AF_INET,'2001:db8::1' if v6 else '10.0.0.5');b=socket.inet_pton(socket.AF_INET6 if v6 else socket.AF_INET,'2001:db8::2' if v6 else '203.0.113.10')
 tcp=struct.pack('!HHIIBBHHH',51812,port,100,1 if flags&16 else 0,80,flags,64240,0,0)+payload
 pseudo=a+b+(struct.pack('!I3xB',len(tcp),6) if v6 else struct.pack('!BBH',0,6,len(tcp)))
 tcp=tcp[:16]+struct.pack('!H',csum(pseudo+tcp))+tcp[18:]
 if v6:ip=struct.pack('!IHBB',6<<28,len(tcp),6,64)+a+b
 else:
  ip=struct.pack('!BBHHHBBH',69,0,20+len(tcp),1,0,64,6,0)+a+b
  ip=ip[:10]+struct.pack('!H',csum(ip))+ip[12:]
 return bytes.fromhex('00112233445566778899aabb')+struct.pack('!H',0x86dd if v6 else 0x0800)+ip+tcp
pkts=[pkt(2),pkt(18),pkt(16,payload=b'abc'),pkt(24),pkt(2,80),pkt(2,v6=True)]
p=Path('/tmp/audit-system-design/network05-synthetic.pcap')
b=struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1)
for i,x in enumerate(pkts):b+=struct.pack('<IIII',i+1,0,len(x),len(x))+x
p.write_bytes(b)
def capture(f):
 a=subprocess.run(['/usr/sbin/tcpdump','-nn','-r',str(p),f],text=True,capture_output=True,check=True);return a.stdout.splitlines()
assert len(capture('tcp port 443'))==5
assert len(capture('host 10.0.0.5'))==5
assert len(capture('tcp[tcpflags] & (tcp-syn|tcp-ack)\n     == tcp-syn'))==2
lines=capture('tcp port 443');assert any('Flags [.]' in x and 'length 3' in x for x in lines);assert any('Flags [P.]' in x and 'length 0' in x for x in lines)
print('PASS 5 offline libpcap/tcpdump assertions; synthetic IPv4+IPv6, ACK-with-data, PSH-without-data. No live capture.')
