exec(open('/tmp/audit-system-design/network03-helper.py').read())
n='tcp-performance';url='https://www.cs.utexas.edu/~lam/395t/papers/Mathis1998.pdf'
edit(n,'The ideal one-ACK-per-segment sawtooth yields:','The ideal periodic-loss sawtooth, with one ACK per segment, yields:','Original paper Table1 distinguishes periodic-loss1.22 from random-loss1.31 constants.',[url])
edit(n,'ACK behaviour changes the constant; timeouts and other limits can invalidate the approximation.','ACK behaviour and loss patterns change the constant; timeouts and other limits can invalidate the approximation.','Table1 also distinguishes loss patterns, not only ACK policy.',[url])
old='http://ccr.sigcomm.org/archive/1997/jul97/ccr-9707-mathis.pdf'
edit(n,old,url,'Replace inaccessible original link with successfully retrieved primary-paper university mirror.',[url])
for i in [4,5]:qedit(n,i,'link.url',url,'Retrieved original paper at university mirror; retain directly supporting primary reference.',[url])
edit('tcp-congestion','does **not** specify a particular ECN response;','does **not** specify a particular ECN algorithm; if a connection advertises ECN support, however, CE marks must still be treated as congestion. Thus,','Preserve explicit MUST to respond to CE despite unspecified algorithm.',['https://datatracker.ietf.org/doc/html/draft-ietf-ccwg-bbr-06'])
