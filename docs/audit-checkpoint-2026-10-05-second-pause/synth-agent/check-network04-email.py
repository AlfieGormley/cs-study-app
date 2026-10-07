from pathlib import Path
import re,ssl,smtplib
from unittest.mock import patch
src=re.findall(r'```python\n(.*?)```',Path('content/networks/04-application/app-email.md').read_text(),re.S)[0]
ns={};exec(src,ns); calls=[]
class Fixture:
 def __init__(self,host,port,timeout):assert(host,port,timeout)==('smtp.example',587,10);calls.append('connect')
 def __enter__(self):return self
 def __exit__(self,*args):calls.append('close')
 def starttls(self,context):
  assert context.verify_mode==ssl.CERT_REQUIRED and context.check_hostname
  calls.append('tls')
 def login(self,user,password):assert(user,password)==('alice','fixture-only');calls.append('login')
 def send_message(self,msg,from_addr,to_addrs):
  assert from_addr=='bounces@alice.example' and to_addrs==['bob@bob.example']
  assert msg['Date'] and msg['From']=='alice@alice.example'
  calls.append('send');return {}
with patch.object(smtplib,'SMTP',Fixture):assert ns['submit']('smtp.example','alice','fixture-only')=={}
assert calls==['connect','tls','login','send','close']
# Real smtplib serialization through a transport-free subclass.
class Wire(smtplib.SMTP):
 def __init__(self):pass
 def ehlo_or_helo_if_needed(self):pass
 def has_extn(self,x):return False
 def sendmail(self,sender,recipients,data,mail_options,rcpt_options):
  assert b'Bcc:'not in data and b'From: alice@alice.example' in data
  assert recipients==['bob@bob.example','hidden@example']
  assert sender=='bounces@alice.example'
  return {}
ns['msg']['Bcc']='hidden@example'
assert Wire().send_message(ns['msg'],from_addr='bounces@alice.example')=={}
# Dot stuffing uses actual stdlib implementation, independent expected bytes.
assert smtplib._quote_periods(b'.first\r\n..second\r\nlast')==b'..first\r\n...second\r\nlast'
# Prove why a verifying context is supplied instead of relying on legacy default.
legacy=ssl._create_stdlib_context()
assert legacy.verify_mode==ssl.CERT_NONE
print('PASS: extracted Python fence, verifying-context/call-order fixture, real smtplib Bcc/envelope serialization and dot-stuffing; no network mail sent.')
